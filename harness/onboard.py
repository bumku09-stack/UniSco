"""온보딩 에이전트 — 새 대학 게시판을 조사해서 `BoardConfig` 초안을 만든다.

`prompts/onboarding_spec.md`가 시스템 프롬프트고, 이 모듈이 그 문서 5장("이 프롬프트를
감싸는 하네스 코드가 지켜야 할 최소 규칙")의 구현부다. extract.py("문서 1건 = 호출 1건,
상태 없음")와 달리 이건 에이전트가 fetch_raw_html/fetch_rendered_html/diff_raw_vs_rendered
세 도구를 스스로 여러 턴 호출하며 조사를 이어가는 에이전틱 루프다 — 그래도 원칙은 동일하게
지킨다: (1) "다 조사했다"는 판단을 에이전트에게 전적으로 맡기지 않고 정해진 절차와 기계적
재검증으로 다시 확인하고, (2) 모든 값에 원문 근거를 강제한다.

실행:
    python -m harness.onboard --university 한밭대학교 --seed-url https://www.hanbat.ac.kr/...

절대 하지 않는 것(설계 원칙, extraction 파이프라인과 동일):
- 에이전트의 제안을 harness/sites.py에 직접 쓰지 않는다 — 항상 별도 브랜치에 초안 파일 +
  기계적 재검증 결과를 커밋해 PR로 올리고, 사람이 검토 후 SITES 리스트에 직접 옮긴다.
- 데이터베이스에 접근하지 않는다.
- 장학금 공고 내용을 추출하지 않는다(그건 extract.py의 일).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import time
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import anthropic
from bs4 import BeautifulSoup

from harness import build_pr, collect_links, config, http, sites
from harness.sites import BoardConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _log(msg: str) -> None:
    print(f"[harness/onboard] {msg}", flush=True)


@lru_cache(maxsize=1)
def load_onboarding_spec() -> str:
    return (_PROMPTS_DIR / "onboarding_spec.md").read_text(encoding="utf-8")


# ── 에이전트가 쓸 수 있는 도구 세 개 (온보딩 스펙 2장) ──────────────────────

_INVESTIGATION_TOOLS: list[dict] = [
    {
        "name": "fetch_raw_html",
        "description": "JS 실행 없이 서버가 준 원본 HTML을 그대로 가져온다.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "fetch_rendered_html",
        "description": "헤드리스 브라우저로 JS까지 실행한 뒤의 최종 HTML을 가져온다.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "diff_raw_vs_rendered",
        "description": (
            "원본 HTML과 렌더링 후 HTML을 각각 가져와 <a> 요소 개수·본문 길이를 비교해서 "
            "JS 렌더링이 필요한지 판단하는 데 참고할 신호를 돌려준다(최종 판단은 에이전트 몫)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
]

# 온보딩 스펙 4장 출력 스키마를 그대로 옮김 — 딱 한 가지만 보강함: view_url_template.
# link_style=onclick_js일 때(3-2절) BoardConfig가 실제로 URL을 조립하려면 이 값이 반드시
# 필요한데(sites.py의 BoardConfig 주석 "id_source_attr + view_url_template은 반드시 같이
# 설정" 참고) 원본 스펙 문서의 출력 스키마엔 빠져 있었음 — required는 아니고(onclick_js가
# 아니면 null) optional property로만 추가해서 원본 스펙의 required 목록은 그대로 둠(2026-08-14).
_PROPOSE_TOOL: dict = {
    "name": "propose_board_config",
    "description": "새 대학 게시판에 대한 BoardConfig 초안과 그 근거를 제출한다.",
    "input_schema": {
        "type": "object",
        "required": [
            "university", "board_name", "discovery_path",
            "list_url_template", "list_url_template_confidence",
            "link_selector", "link_selector_confidence", "selector_match_examples",
            "link_style", "onclick_id_pattern",
            "total_count_pattern", "total_count_pattern_confidence", "total_count_evidence",
            "items_per_page", "items_per_page_confidence",
            "requires_js", "requires_js_confidence", "js_diff_note",
            "pagination_verified",
            "dry_run_result",
            "known_limitations_note",
            "unresolved_issues",
            "overall_confidence",
        ],
        "properties": {
            "university": {"type": "string"},
            "board_name": {"type": "string"},
            "discovery_path": {
                "type": "array",
                "items": {"type": "string"},
                "description": "seed_url이 메인페이지였을 경우, 게시판을 찾기까지 따라간 링크 경로. 바로 게시판이면 빈 배열.",
            },
            "list_url_template": {"type": ["string", "null"]},
            "list_url_template_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "link_selector": {"type": ["string", "null"]},
            "link_selector_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "selector_match_examples": {
                "type": "array",
                "items": {"type": "string"},
                "description": "link_selector로 실제 매칭된 HTML 조각 원문 (요약 금지, 최소 2개)",
            },
            "link_style": {"type": "string", "enum": ["href", "onclick_js"]},
            "onclick_id_pattern": {
                "type": ["string", "null"],
                "description": "link_style이 onclick_js일 때만: onclick 속성에서 게시글 ID를 뽑는 정규식",
            },
            "view_url_template": {
                "type": ["string", "null"],
                "description": (
                    "link_style이 onclick_js일 때만: onclick_id_pattern으로 뽑은 ID로 실제 "
                    "상세페이지 URL을 조립하는 템플릿({id} 플레이스홀더 포함, sites.py의 "
                    "view_url_template과 동일). href 방식이면 null."
                ),
            },
            "total_count_pattern": {"type": ["string", "null"]},
            "total_count_pattern_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "total_count_evidence": {
                "type": ["string", "null"],
                "description": "total_count_pattern의 근거가 된 원문 문구 그대로",
            },
            "items_per_page": {"type": ["integer", "null"]},
            "items_per_page_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "requires_js": {"type": ["boolean", "null"]},
            "requires_js_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "js_diff_note": {"type": "string"},
            "pagination_verified": {
                "type": "boolean",
                "description": "2페이지 이상에서 실제로 다른 항목이 나오는 것을 직접 확인했는지",
            },
            "dry_run_result": {
                "type": "string",
                "description": "3-7 교차 검증에서 무엇을 시도했고 무엇이 맞았는지/틀렸는지 서술",
            },
            "known_limitations_note": {"type": "string"},
            "unresolved_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "확정하지 못한 항목과 이유. 없으면 빈 배열이 아니라 명시적으로 빈 배열을 넣는다.",
            },
            "overall_confidence": {
                "type": "string",
                "enum": ["ready_for_review", "needs_manual_setup"],
                "description": (
                    "confidence가 low인 필드가 하나라도 있거나 unresolved_issues가 비어있지 "
                    "않으면 needs_manual_setup. 이 규칙은 _enforce_confidence_rule()이 최종적으로 "
                    "다시 계산해서 덮어쓰므로, 에이전트가 여기서 틀리게 내도 안전함."
                ),
            },
        },
    },
}


@dataclasses.dataclass
class OnboardingProposal:
    """propose_board_config 호출 입력을 그대로 담는 그릇. 필드 구성은 온보딩 스펙 4장의
    출력 스키마 + view_url_template(위 주석 참고)와 정확히 일치함."""

    university: str
    board_name: str
    discovery_path: list[str]
    list_url_template: str | None
    list_url_template_confidence: str
    link_selector: str | None
    link_selector_confidence: str
    selector_match_examples: list[str]
    link_style: str
    onclick_id_pattern: str | None
    view_url_template: str | None
    total_count_pattern: str | None
    total_count_pattern_confidence: str
    total_count_evidence: str | None
    items_per_page: int | None
    items_per_page_confidence: str
    requires_js: bool | None
    requires_js_confidence: str
    js_diff_note: str
    pagination_verified: bool
    dry_run_result: str
    known_limitations_note: str
    unresolved_issues: list[str]
    overall_confidence: str


def _enforce_confidence_rule(proposal: OnboardingProposal) -> OnboardingProposal:
    """온보딩 스펙 4장: overall_confidence는 에이전트가 임의로 매기는 값이 아니라 기계적
    규칙 — 여기서 다시 계산해서 덮어씀(에이전트가 규칙을 어기고 냈어도 무시함). "판단을
    스스로 못 내리게 한다"는 하네스 전체 원칙 1을 이 필드에도 그대로 적용한 것."""
    confidence_fields = [
        proposal.list_url_template_confidence,
        proposal.link_selector_confidence,
        proposal.total_count_pattern_confidence,
        proposal.items_per_page_confidence,
        proposal.requires_js_confidence,
    ]
    needs_manual = any(c == "low" for c in confidence_fields) or bool(proposal.unresolved_issues)
    proposal.overall_confidence = "needs_manual_setup" if needs_manual else "ready_for_review"
    return proposal


def _parse_proposal(raw_input: dict) -> OnboardingProposal:
    """tool_use.input을 OnboardingProposal로 옮김. 필수 필드가 비어 있어도(모델이 스키마를
    어겼을 드문 경우) KeyError로 전체 실행을 죽이지 않고, 안전한 쪽(low/needs_manual_setup)
    으로 기본값을 채움 — verify.py의 "애매하면 needs_review" 철학과 동일."""

    def g(key: str, default: Any = None) -> Any:
        return raw_input.get(key, default)

    proposal = OnboardingProposal(
        university=g("university", ""),
        board_name=g("board_name", ""),
        discovery_path=list(g("discovery_path", []) or []),
        list_url_template=g("list_url_template"),
        list_url_template_confidence=g("list_url_template_confidence", "low"),
        link_selector=g("link_selector"),
        link_selector_confidence=g("link_selector_confidence", "low"),
        selector_match_examples=list(g("selector_match_examples", []) or []),
        link_style=g("link_style", "href"),
        onclick_id_pattern=g("onclick_id_pattern"),
        view_url_template=g("view_url_template"),
        total_count_pattern=g("total_count_pattern"),
        total_count_pattern_confidence=g("total_count_pattern_confidence", "low"),
        total_count_evidence=g("total_count_evidence"),
        items_per_page=g("items_per_page"),
        items_per_page_confidence=g("items_per_page_confidence", "low"),
        requires_js=g("requires_js"),
        requires_js_confidence=g("requires_js_confidence", "low"),
        js_diff_note=g("js_diff_note", ""),
        pagination_verified=bool(g("pagination_verified", False)),
        dry_run_result=g("dry_run_result", ""),
        known_limitations_note=g("known_limitations_note", ""),
        unresolved_issues=list(g("unresolved_issues", []) or []),
        overall_confidence=g("overall_confidence", "needs_manual_setup"),
    )
    return _enforce_confidence_rule(proposal)


# ── 도구 구현 ────────────────────────────────────────────────────────────

# 도구 결과(특히 원본 HTML)를 대화 맥락에 그대로 계속 쌓으면 몇 턴 안 가 컨텍스트/비용이
# 터짐 — build_pr.py의 PR 본문 길이 상한(_GITHUB_PR_BODY_MAX_CHARS)과 같은 이유로 여기도
# 상한을 둠. 잘려도 에이전트가 필요하면 셀렉터를 좁히거나 특정 구간을 다시 요청하면 됨.
_MAX_TOOL_RESULT_CHARS = 15000


def _truncate(text: str) -> str:
    if len(text) <= _MAX_TOOL_RESULT_CHARS:
        return text
    cut = len(text) - _MAX_TOOL_RESULT_CHARS
    return f"{text[:_MAX_TOOL_RESULT_CHARS]}\n\n...[{cut}자 잘림 — 필요하면 더 좁은 범위로 다시 요청할 것]"


def _render_with_playwright(url: str) -> str:
    """collect_links._fetch_js와 같은 방식(Playwright, networkidle까지 대기)이지만 이건
    BoardConfig 없이 임의 URL 하나를 렌더링하는 범용 도구용이라 별도로 둠 — 재시도 로직도
    없음(도구 실행 실패는 에이전트에게 그대로 알려주고 에이전트가 판단하게 하는 편이 이
    쓰임새엔 더 맞음, collect_links의 크롤링 안정성 목적과는 다른 상황)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=config.REQUEST_USER_AGENT)
            page.goto(url, timeout=config.REQUEST_TIMEOUT_SECONDS * 1000)
            page.wait_for_load_state("networkidle")
            return page.content()
        finally:
            browser.close()


def _tool_fetch_raw_html(url: str) -> str:
    return http.get_text(url)


def _tool_fetch_rendered_html(url: str) -> str:
    return _render_with_playwright(url)


def _tool_diff_raw_vs_rendered(url: str) -> dict:
    raw = http.get_text(url)
    rendered = _render_with_playwright(url)
    return {
        "raw_link_count": len(BeautifulSoup(raw, "lxml").find_all("a")),
        "rendered_link_count": len(BeautifulSoup(rendered, "lxml").find_all("a")),
        "raw_html_length": len(raw),
        "rendered_html_length": len(rendered),
    }


_TOOL_IMPLS: dict[str, Callable[..., Any]] = {
    "fetch_raw_html": _tool_fetch_raw_html,
    "fetch_rendered_html": _tool_fetch_rendered_html,
    "diff_raw_vs_rendered": _tool_diff_raw_vs_rendered,
}


# ── 에이전틱 루프 ────────────────────────────────────────────────────────


def _default_existing_configs_sample(n: int = 2) -> str:
    samples = sites.SITES[:n]
    if not samples:
        return ""
    return "\n\n".join(repr(dataclasses.asdict(s)) for s in samples)


def _build_system_prompt(existing_configs_sample: str | None) -> str:
    """온보딩 스펙 본문 + (있으면) 참고용 기존 설정 예시를 하나의 system 블록으로 합침.

    예시를 유저 메시지가 아니라 여기 넣는 이유는 순전히 캐싱 때문 — 기본값(sites.py 앞 2개)은
    어느 대학을 온보딩하든 항상 똑같은 텍스트인데, 유저 메시지 쪽에 두면 실행마다 매번
    새로 과금됨. system 블록으로 옮기고 1시간 캐시(아래 run_onboarding_agent 참고)를 걸면
    같은 세션에서 대학 여러 곳을 연달아 온보딩할 때 이 부분을 공유해서 씀
    (2026-08-14, 토큰 낭비 점검 중 발견)."""
    base = load_onboarding_spec()
    if not existing_configs_sample:
        return base
    return f"{base}\n\n## 참고용 기존 BoardConfig 예시 (그대로 베끼지 말 것)\n\n{existing_configs_sample}"


def _initial_user_message(university: str, seed_url: str, target_hint: str | None) -> str:
    parts = [f"university: {university}", f"seed_url: {seed_url}"]
    if target_hint:
        parts.append(f"target_hint: {target_hint}")
    return "\n".join(parts)


# ── 프롬프트 캐싱 — 성장하는 대화 히스토리에 "움직이는" 브레이크포인트 하나만 유지 ──
#
# system 블록엔 이미 cache_control이 있지만, 그것만으로는 messages(도구 결과가 계속
# 쌓이는 부분)는 매 턴 통째로 재과금됨 — 시스템 프롬프트는 대화 전체의 일부일 뿐이고,
# fetch_raw_html/fetch_rendered_html 같은 대용량 도구 결과가 진짜 비용을 차지함
# (2026-08-14, 실제 토큰 사용량 추정 중 발견). 매 턴 "직전까지의 히스토리 끝"에만
# cache_control을 걸고, 새 턴이 오면 이전 마커를 지우고 새 끝으로 옮기는 식으로 처리함 —
# 캐시는 프리픽스 매칭이라 오래된 마커를 남겨둘 필요가 없고(그 바이트 프리픽스는 이미
# 한 번 쓰였으면 계속 유효한 캐시 진입점으로 남음), 매번 하나씩만 옮기면 대화가 아무리
# 길어져도(ONBOARD_MAX_TURNS까지) 요청당 브레이크포인트 4개 상한(system 1개 + 이동 마커
# 1개 = 2개)에 절대 안 걸림.
def _strip_cache_control(msg: dict) -> None:
    content = msg.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                block.pop("cache_control", None)


def _mark_cache_breakpoint(msg: dict) -> None:
    content = msg.get("content")
    if isinstance(content, list) and content:
        last = content[-1]
        if isinstance(last, dict):
            last["cache_control"] = {"type": "ephemeral"}


def run_onboarding_agent(
    university: str,
    seed_url: str,
    *,
    target_hint: str | None = None,
    existing_configs_sample: str | None = None,
    model: str | None = None,
    max_turns: int = config.ONBOARD_MAX_TURNS,
) -> tuple[OnboardingProposal | None, list[str]]:
    """온보딩 에이전트를 propose_board_config 호출까지(또는 max_turns 소진까지) 실행.

    (제안 또는 None, 사람이 읽을 실행 로그)를 돌려줌 — 실패해도 예외를 던지지 않고 None을
    돌려줌: "조사를 못 끝냈다"는 것 자체가 유효한 결과이지 시스템 오류가 아님(온보딩 스펙
    0장 원칙 1과 같은 이유)."""
    client = anthropic.Anthropic(api_key=config.load_anthropic_api_key(), timeout=180.0)

    if existing_configs_sample is None:
        existing_configs_sample = _default_existing_configs_sample()
    system_prompt = _build_system_prompt(existing_configs_sample)
    tools = [*_INVESTIGATION_TOOLS, _PROPOSE_TOOL]

    # system 프롬프트(대학이 바뀌어도 거의 항상 동일)는 1시간 TTL로 캐싱 — 온보딩을
    # 한 세션에서 대학 여러 곳 연달아 돌릴 때 이 프롬프트 재작성 비용을 공유하기 위함
    # (기본 5분 TTL이면 대학 하나 조사하는 사이에 만료될 수 있음). 쓰기는 2배 비싸지만,
    # 이 프롬프트가 반복 재사용되는 만큼 5분 TTL보다 총비용이 낮음(prompt-caching.md
    # "Economics" 참고 — 3회 이상 재사용되면 1시간 TTL이 유리함).
    system_blocks = [
        {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral", "ttl": "1h"}}
    ]

    initial_msg: dict = {
        "role": "user",
        "content": [{"type": "text", "text": _initial_user_message(university, seed_url, target_hint)}],
    }
    _mark_cache_breakpoint(initial_msg)
    messages: list[dict] = [initial_msg]
    # 매 턴 히스토리 끝으로 옮겨가는 "움직이는" 캐시 브레이크포인트 — 위 모듈 주석 참고.
    cache_anchor: dict | None = initial_msg
    transcript: list[str] = []

    for turn in range(max_turns):
        response = client.messages.create(
            model=model or config.ONBOARD_MODEL,
            max_tokens=config.ONBOARD_MAX_TOKENS,
            system=system_blocks,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            transcript.append(f"[turn {turn}] 도구 호출 없이 텍스트만 응답 — 계속 진행 요청")
            if cache_anchor is not None:
                _strip_cache_control(cache_anchor)
            nudge_msg: dict = {
                "role": "user",
                "content": [
                    {"type": "text", "text": "계속 진행해줘. 조사가 끝났으면 propose_board_config를 호출해."}
                ],
            }
            _mark_cache_breakpoint(nudge_msg)
            messages.append(nudge_msg)
            cache_anchor = nudge_msg
            continue

        propose_call = next((t for t in tool_uses if t.name == "propose_board_config"), None)
        if propose_call is not None:
            transcript.append(f"[turn {turn}] propose_board_config 호출 — 종료")
            return _parse_proposal(propose_call.input), transcript

        tool_results = []
        for call in tool_uses:
            impl = _TOOL_IMPLS.get(call.name)
            if impl is None:
                result_text = f"알 수 없는 도구: {call.name}"
            else:
                try:
                    raw_result = impl(**call.input)
                    result_text = raw_result if isinstance(raw_result, str) else json.dumps(raw_result, ensure_ascii=False)
                    result_text = _truncate(result_text)
                except Exception as e:  # noqa: BLE001 — 도구 실행 실패를 숨기지 않고 에이전트에게
                    # 그대로 알려서 스스로 대응하게 함("확인 안 되면 unresolved_issues로 남길 것"과 같은 이유).
                    result_text = f"도구 실행 실패: {e}"
            transcript.append(f"[turn {turn}] {call.name}({call.input}) -> {result_text[:200]}")
            tool_results.append({"type": "tool_result", "tool_use_id": call.id, "content": result_text})

        if cache_anchor is not None:
            _strip_cache_control(cache_anchor)
        tool_result_msg = {"role": "user", "content": tool_results}
        _mark_cache_breakpoint(tool_result_msg)
        messages.append(tool_result_msg)
        cache_anchor = tool_result_msg

    transcript.append(f"max_turns({max_turns}) 안에 propose_board_config를 못 부름 — 사람이 직접 조사 필요")
    return None, transcript


# ── 기계적 재검증 (온보딩 스펙 5장 규칙 2·3) ────────────────────────────


def _mechanical_reverify(university: str, proposal: OnboardingProposal) -> tuple[bool, list[str]]:
    """에이전트가 제안한 설정을 코드가 다시 실행해서 재현되는지 확인. 전체 게시판을 순회하는
    게 아니라(그건 실제 나이트런이 할 일) 1~3페이지 정도로 가볍게 대조하는 드라이런임.

    예외를 던지지 않고 (통과여부, 실패사유 목록)을 돌려줌 — 이 결과가 PR 제목/본문의
    "사람이 직접 확인 필요" 여부를 그대로 결정함(규칙 4: 검증 실패는 needs_manual_setup과
    동일하게 취급, 조용히 기본값으로 채우지 않음)."""
    problems: list[str] = []

    if not proposal.list_url_template or not proposal.link_selector:
        problems.append("list_url_template 또는 link_selector가 비어 있어 재검증 자체를 못 함")
        return False, problems

    board = BoardConfig(
        university=university,
        board_name=proposal.board_name or "(온보딩 에이전트 제안)",
        department=None,
        list_url_template=proposal.list_url_template,
        link_selector=proposal.link_selector,
        total_count_pattern=proposal.total_count_pattern,
        items_per_page=proposal.items_per_page or 10,
        requires_js=bool(proposal.requires_js),
        id_source_attr="onclick" if proposal.link_style == "onclick_js" else None,
        id_pattern=proposal.onclick_id_pattern if proposal.link_style == "onclick_js" else None,
        view_url_template=proposal.view_url_template if proposal.link_style == "onclick_js" else None,
    )

    if proposal.link_style == "onclick_js" and not proposal.view_url_template:
        problems.append(
            "link_style=onclick_js인데 view_url_template이 없어 실제 상세페이지 URL을 "
            "조립할 수 없음 — 에이전트가 이 값을 못 냄"
        )

    try:
        first_html = collect_links.fetch_page(board.list_url_template.format(page=board.first_page_index), board)
    except Exception as e:  # noqa: BLE001 — 재검증 실패는 예외를 전파하지 않고 사유로 남김
        problems.append(f"1페이지 요청 자체가 실패함: {e}")
        return False, problems

    _expected_count, total_pages = collect_links.parse_expected_count(first_html, board)
    if total_pages is None:
        problems.append(
            "제안된 total_count_pattern/total_pages_pattern으로 1페이지에서 총 개수/총 "
            "페이지 파싱이 안 됨 — total_count_evidence가 실제 페이지 문구와 다를 수 있음"
        )

    page1_links = collect_links.extract_links(first_html, board)
    if not page1_links:
        problems.append("제안된 link_selector로 1페이지에서 매칭되는 링크가 0개")

    # 규칙 2: 3페이지 정도 순회해서 링크 개수 추이가 모순되지 않는지 — 페이지네이션이 진짜
    # 동작하는지(파라미터가 무시되고 매번 같은 페이지가 나오는 게 아닌지)만 가볍게 확인.
    seen_urls = {u for u, _title in page1_links}
    pages_confirmed = 1
    for page_num in range(board.first_page_index + 1, board.first_page_index + 3):
        try:
            html = collect_links.fetch_page(board.list_url_template.format(page=page_num), board)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{page_num}페이지 요청 실패: {e}")
            break
        page_links = collect_links.extract_links(html, board)
        if not page_links:
            break
        new_urls = {u for u, _title in page_links} - seen_urls
        if not new_urls:
            problems.append(
                f"{page_num}페이지가 이전 페이지와 겹치는 링크만 반환함 — pagination_verified가 "
                "실제로는 재현 안 됨(페이지 파라미터가 무시되고 있을 가능성)"
            )
            break
        seen_urls |= new_urls
        pages_confirmed += 1
        time.sleep(config.REQUEST_DELAY_SECONDS)

    if pages_confirmed < 2:
        problems.append("2페이지 이상에서 새 링크가 확인되지 않아 pagination_verified를 재현하지 못함")

    # 규칙 3: onclick_js면 실제 상세페이지 URL 최소 2건이 200으로 응답하는지 확인.
    if proposal.link_style == "onclick_js" and proposal.view_url_template:
        checked = 0
        for url, _title in page1_links[:3]:
            try:
                http.get(url)
                checked += 1
            except Exception as e:  # noqa: BLE001
                problems.append(f"onclick_js 상세페이지 확인 실패({url}): {e}")
            if checked >= 2:
                break
        if checked < 2:
            problems.append("onclick_js 상세페이지 URL이 최소 2건 200 응답을 못 받음")

    return not problems, problems


# ── 산출물 생성 + PR 오픈 (온보딩 스펙 5장 규칙 1·5) ────────────────────


def render_review_markdown(
    university: str,
    seed_url: str,
    proposal: OnboardingProposal | None,
    transcript: list[str],
    verification_problems: list[str],
) -> str:
    lines = [f"# {university} 온보딩 에이전트 조사 결과 — {datetime.date.today().isoformat()}", ""]
    lines.append(f"seed_url: {seed_url}")
    lines.append("")

    if proposal is None:
        lines.append("## ⚠️ 실패 — 에이전트가 propose_board_config를 호출하지 못함")
        lines.append("아래 실행 로그를 참고해 사람이 직접 조사할 것.")
    else:
        status = "✅ ready_for_review" if proposal.overall_confidence == "ready_for_review" else "⚠️ needs_manual_setup"
        lines.append(f"## 종합 판단: {status}")
        if proposal.discovery_path:
            lines.append(f"- 게시판 탐색 경로: {' → '.join(proposal.discovery_path)}")
        lines.append(f"- board_name: {proposal.board_name}")
        lines.append(f"- link_style: {proposal.link_style}")
        lines.append("")
        lines.append("### 제안된 설정값과 근거")
        lines.append(f"- `list_url_template` = `{proposal.list_url_template}` (confidence: {proposal.list_url_template_confidence})")
        lines.append(f"- `link_selector` = `{proposal.link_selector}` (confidence: {proposal.link_selector_confidence})")
        if proposal.selector_match_examples:
            lines.append("  - 매칭 예시:")
            for ex in proposal.selector_match_examples:
                lines.append(f"    - `{ex}`")
        lines.append(
            f"- `total_count_pattern` = `{proposal.total_count_pattern}` "
            f"(confidence: {proposal.total_count_pattern_confidence})"
        )
        if proposal.total_count_evidence:
            lines.append(f'  - 근거 원문: "{proposal.total_count_evidence}"')
        lines.append(f"- `items_per_page` = `{proposal.items_per_page}` (confidence: {proposal.items_per_page_confidence})")
        lines.append(f"- `requires_js` = `{proposal.requires_js}` (confidence: {proposal.requires_js_confidence})")
        if proposal.js_diff_note:
            lines.append(f"  - {proposal.js_diff_note}")
        lines.append(f"- `pagination_verified`(에이전트 자체 확인) = `{proposal.pagination_verified}`")
        if proposal.link_style == "onclick_js":
            lines.append(f"- `onclick_id_pattern` = `{proposal.onclick_id_pattern}`")
            lines.append(f"- `view_url_template` = `{proposal.view_url_template}`")
        lines.append("")
        lines.append("### 드라이런 결과 (에이전트 자체 보고)")
        lines.append(proposal.dry_run_result or "(없음)")
        if proposal.known_limitations_note:
            lines.append("")
            lines.append(f"### 알려진 한계\n{proposal.known_limitations_note}")
        lines.append("")
        lines.append("### 미해결 항목 (에이전트 보고)")
        if proposal.unresolved_issues:
            for issue in proposal.unresolved_issues:
                lines.append(f"- {issue}")
        else:
            lines.append("(없음)")

    lines.append("")
    lines.append("## 기계적 재검증 (하네스 코드가 별도로 재실행한 결과, 규칙 2·3)")
    if verification_problems:
        lines.append(f"⚠️ 문제 {len(verification_problems)}건 발견:")
        for p in verification_problems:
            lines.append(f"- {p}")
    else:
        lines.append("✅ 문제 없음 — 1페이지 파싱, 2페이지 이상 페이지네이션, (해당 시) onclick_js 상세 URL 확인 전부 통과")

    lines.append("")
    lines.append("## 실행 로그")
    lines.append("```")
    lines.extend(transcript)
    lines.append("```")
    return "\n".join(lines)


def render_config_draft(university: str, proposal: OnboardingProposal) -> str:
    """harness/sites.py의 SITES 리스트에 그대로 옮겨 붙일 수 있는 형태의 초안. 이 파일 자체는
    sites.py가 읽지 않음 — 사람이 검토 후 값을 확인/수정해서 직접 옮기는 참고용."""

    def lit(v: Any) -> str:
        return "None" if v is None else repr(v)

    lines = [
        f"# {university} — 온보딩 에이전트 제안 초안({datetime.date.today().isoformat()}).",
        "# 사람이 검토 후 아래 값을 확인/수정해서 harness/sites.py의 SITES 리스트에 옮길 것.",
        "# 이 파일 자체는 sites.py가 읽지 않음 — 참고용 초안일 뿐임.",
        "BoardConfig(",
        f"    university={lit(university)},",
        f"    board_name={lit(proposal.board_name)},",
        "    department=None,",
        f"    list_url_template={lit(proposal.list_url_template)},",
        f"    link_selector={lit(proposal.link_selector)},",
        f"    total_count_pattern={lit(proposal.total_count_pattern)},",
        f"    items_per_page={proposal.items_per_page or 10},",
        f"    requires_js={bool(proposal.requires_js)},",
    ]
    if proposal.link_style == "onclick_js":
        lines.append("    id_source_attr='onclick',")
        lines.append(f"    id_pattern={lit(proposal.onclick_id_pattern)},")
        lines.append(f"    view_url_template={lit(proposal.view_url_template)},")
    lines.append(")")
    return "\n".join(lines)


def build_and_open_onboarding_pr(
    university: str,
    seed_url: str,
    proposal: OnboardingProposal | None,
    transcript: list[str],
    verification_problems: list[str],
) -> str | None:
    date_str = datetime.date.today().isoformat()
    time_str = datetime.datetime.now().strftime("%H%M%S")
    slug = build_pr._slug(university)
    # 규칙 5: 데이터 추출 PR 브랜치(harness/{slug}-...)와 접두어를 분리 — 리뷰 큐에서
    # "설정 온보딩"과 "데이터 추출"을 한눈에 구분하기 위함.
    branch_name = f"harness/onboard-{slug}-{date_str}-{time_str}"

    review_md_path = f"harness/onboarding_review_{slug}_{date_str}.md"
    review_md = render_review_markdown(university, seed_url, proposal, transcript, verification_problems)
    files = {review_md_path: review_md}

    if proposal is not None:
        draft_path = f"harness/onboarding_draft_{slug}_{date_str}.py"
        files[draft_path] = render_config_draft(university, proposal)

    if proposal is None:
        title = f"[온보딩 에이전트 실패] {university} — propose_board_config 미호출"
    elif verification_problems:
        title = f"[온보딩 에이전트] {university} — needs_manual_setup (기계적 재검증 실패 {len(verification_problems)}건)"
    elif proposal.overall_confidence == "needs_manual_setup":
        title = f"[온보딩 에이전트] {university} — needs_manual_setup"
    else:
        title = f"[온보딩 에이전트] {university} — ready_for_review"

    commit_message = f"[harness] {university} 온보딩 조사 초안 ({date_str})"

    pushed = False
    try:
        build_pr._create_branch_and_commit(branch_name, files, commit_message)
        pushed = True
        return build_pr.open_pr(branch_name, title, build_pr._pr_body(review_md, review_md_path))
    except Exception:
        # build_pr.build_and_open_pr와 동일한 이유 — 여기까지 왔으면 이미 Anthropic API로
        # 조사(비용 발생)를 끝낸 뒤라, git/PR 단계 실패로 산출물을 통째로 날리면 손해가 큼.
        _log("git/PR 단계 실패 — 아래 산출물을 워크플로 로그에서 복구할 것:")
        for path, content in files.items():
            _log(f"=== {path} ===\n{content}")
        if pushed:
            build_pr._delete_remote_branch(branch_name)
        raise


def onboard_university(university: str, seed_url: str, target_hint: str | None = None) -> str | None:
    _log(f"조사 시작 — university={university}, seed_url={seed_url}")
    proposal, transcript = run_onboarding_agent(university, seed_url, target_hint=target_hint)

    verification_problems: list[str] = []
    if proposal is not None:
        _ok, verification_problems = _mechanical_reverify(university, proposal)
        if verification_problems:
            # 규칙 4: 재검증 실패는 needs_manual_setup과 동일하게 취급 — 에이전트가 스스로
            # ready_for_review라고 냈어도 코드가 덮어씀. unresolved_issues에도 남겨서
            # render_review_markdown의 "미해결 항목" 절에 같이 보이게 함.
            proposal.overall_confidence = "needs_manual_setup"
            proposal.unresolved_issues = [
                *proposal.unresolved_issues,
                *[f"[기계적 재검증 실패] {p}" for p in verification_problems],
            ]
        _log(
            f"조사 완료 — overall_confidence={proposal.overall_confidence}, "
            f"재검증 문제 {len(verification_problems)}건"
        )
    else:
        _log("조사 실패 — propose_board_config를 끝내 호출 못 함")

    pr_url = build_and_open_onboarding_pr(university, seed_url, proposal, transcript, verification_problems)
    if pr_url:
        _log(f"PR 오픈: {pr_url}")
    return pr_url


def main() -> None:
    parser = argparse.ArgumentParser(description="새 대학 게시판 온보딩 에이전트 — BoardConfig 초안 생성")
    parser.add_argument("--university", required=True, help="대학 이름 (예: 한밭대학교)")
    parser.add_argument("--seed-url", required=True, help="조사를 시작할 게시판 또는 대학 메인 URL")
    parser.add_argument("--target-hint", default=None, help="어떤 게시판을 찾아야 하는지 힌트 (예: 장학금)")
    args = parser.parse_args()
    onboard_university(args.university, args.seed_url, args.target_hint)


if __name__ == "__main__":
    main()
