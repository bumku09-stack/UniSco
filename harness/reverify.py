"""이미 DB에 들어간 장학금의 application_period/application_method가 실제로 원문에
근거가 있는지 재확인. extract.py/verify.py와 같은 원칙(인용 강제 + 기계적 대조)을 쓰되,
"공고문 1건=호출 1건"이 아니라 "URL 하나(주로 대학 통합 장학금 목록 페이지, 여러 장학금이
한 표에 같이 있음)=그 URL을 쓰는 기존 레코드 여러 건을 한 번에 재확인"하는 형태라 별도
스키마를 씀.

2026-08-15 계기 — id=46(CNU복지 장학금)의 application_period·application_method 둘 다
원문에 없는 값이 들어가 있던 사고. 처음엔 application_period만 원문 대조해서 고치고,
application_method는 "형제 레코드(영탑A/B 등)랑 패턴이 비슷하니 맞겠지"라고 사람이
넘겨짚었다가 나중에 그것도 틀렸던 게 드러남 — 패턴이 그럴듯한 것과 실제로 그 출처에서
확인된 것은 다르다는 교훈. 이 모듈은 그 사람의 "맞겠지" 판단을 코드의 기계적 대조로
대체함: 매번 실제 원문을 다시 읽고, 값마다 원문 인용을 강제하고, 그 인용이 진짜 원문에
있는지 대조한다.

**여기서 끝남. DB에는 아무것도 안 씀** — extract.py 파이프라인과 동일한 원칙(설계안
"실제 운영 DB는 절대 자동화하지 않음"). 발견한 불일치는 리뷰 마크다운으로 정리해서
PR로 올리고, 실제 반영은 지금처럼 사람이 판단해서 supabase/tools/run_sql.py로 함.

실행:
    python -m harness.reverify --university 충남대학교
    python -m harness.reverify --all
"""
from __future__ import annotations

import argparse
import datetime
from dataclasses import dataclass

import anthropic
from bs4 import BeautifulSoup

from harness import build_pr, config, db, http, verify
from harness.budget import reverify_budget

_TOOL = {
    "name": "reverify_items",
    "description": (
        "주어진 원문 텍스트 안에서, 지정된 각 장학금 항목의 신청기간(application_period)과 "
        "신청방식(application_method) 정보를 찾아 근거 인용과 함께 반환한다. 원문에 그 "
        "정보가 없으면 값과 인용 둘 다 빈 문자열로 남긴다 — 지어내지 않는다. 이름 자체를 "
        "원문에서 못 찾은 항목은 not_found_in_source=true로 표시한다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "장학금 id (입력받은 그대로)"},
                        "not_found_in_source": {
                            "type": "boolean",
                            "description": "이 장학금 이름 자체를 원문에서 못 찾았으면 true",
                        },
                        "application_period_value": {
                            "type": "string",
                            "description": "원문에서 확인되는 신청기간/시기. 없으면 빈 문자열.",
                        },
                        "application_period_quote": {
                            "type": "string",
                            "description": "application_period_value의 근거가 된 원문 문장 그대로. "
                            "값이 없으면 빈 문자열.",
                        },
                        "application_method_value": {
                            "type": "string",
                            "description": "원문에서 확인되는 신청방식(자동선발/직접신청 등). "
                            "없으면 빈 문자열.",
                        },
                        "application_method_quote": {
                            "type": "string",
                            "description": "application_method_value의 근거가 된 원문 문장 그대로. "
                            "값이 없으면 빈 문자열.",
                        },
                    },
                    "required": [
                        "id",
                        "not_found_in_source",
                        "application_period_value",
                        "application_period_quote",
                        "application_method_value",
                        "application_method_quote",
                    ],
                },
            },
        },
        "required": ["results"],
    },
}

_SYSTEM_PROMPT = """당신은 대학 장학금 안내 페이지 원문에서, 지정된 각 장학금 항목의
"신청기간"과 "신청방식" 정보를 찾아내는 재검증 도구입니다.

절대 원칙 — 원문에 없으면 지어내지 않는다:
- 값을 채울 때는 반드시 그 근거가 된 원문 문장을 그대로(요약하지 말고) 인용으로 같이 낼 것.
- 이 페이지가 여러 장학금을 표로 나열한 순수 참고표(선정기준·지급액만 있고 신청 절차
  정보 자체가 없는 경우)라면, 모든 항목의 application_period_value/application_method_value를
  빈 문자열로 남길 것 — "아마 이럴 것이다"로 추측하지 말 것.
- "학생과", "장학팀" 같은 부서명이 사이트 네비게이션 메뉴에 등장하는 것과, 그 장학금의
  실제 신청 방법을 설명하는 문장에 등장하는 것은 다르다 — 메뉴/브레드크럼 텍스트를
  신청방식 근거로 쓰지 말 것.

표 읽을 때 주의:
- "〃"(같음표)는 "바로 위 칸과 값이 같다"는 뜻 — 빈 칸이 아니라 위 행에서 그대로 끌어와
  읽을 것.
- 표에 없는 항목(이름이 원문에 아예 안 보이는 경우)은 not_found_in_source=true로 표시."""


def _log(msg: str) -> None:
    print(f"[harness/reverify] {msg}", flush=True)


@dataclass
class Discrepancy:
    scholarship_id: int
    name: str
    field: str  # "application_period" | "application_method"
    current_value: str
    fresh_value: str  # 원문에서 새로 확인된 값(빈 문자열=원문에 근거 없음)
    fresh_quote: str
    kind: str  # "no_source_evidence" | "value_mismatch" | "not_found_in_source"


def _fetch_source_text(url: str) -> str | None:
    try:
        raw = http.get_text(url)
    except Exception as e:  # noqa: BLE001 — 이 URL 하나만 스킵, 나머지는 계속
        _log(f"원문 확보 실패({url}): {e}")
        return None
    return BeautifulSoup(raw, "lxml").get_text(separator="\n", strip=True)


def _call_reverify(
    client: anthropic.Anthropic, source_text: str, items: list[tuple[int, str]]
) -> list[dict]:
    items_desc = "\n".join(f"- id={sid}: {name}" for sid, name in items)
    user_message = (
        f"아래 원문에서 다음 장학금들의 신청기간·신청방식을 확인해줘.\n\n"
        f"=== 확인할 항목 ===\n{items_desc}\n\n"
        f"=== 원문 ===\n{source_text}"
    )
    reverify_budget.check()
    response = client.messages.create(
        model=config.REVERIFY_MODEL,
        max_tokens=config.REVERIFY_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "reverify_items"},
        messages=[{"role": "user", "content": user_message}],
    )
    reverify_budget.record(response.usage)
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return tool_use.input["results"]  # type: ignore[return-value]


def _chunks(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def reverify_url_group(
    client: anthropic.Anthropic,
    url: str,
    records: list[tuple[int, str, str | None, str | None]],
) -> list[Discrepancy]:
    """records: (id, name, current_period, current_method) 목록 — 전부 같은 url을 씀."""
    source_text = _fetch_source_text(url)
    if source_text is None:
        return []

    discrepancies: list[Discrepancy] = []
    id_to_record = {r[0]: r for r in records}
    items = [(r[0], r[1]) for r in records]

    for chunk in _chunks(items, config.REVERIFY_MAX_ITEMS_PER_CALL):
        try:
            results = _call_reverify(client, source_text, chunk)
        except Exception as e:  # noqa: BLE001 — 이 청크만 스킵, 나머지 URL/청크는 계속
            _log(f"재검증 호출 실패({url}, {len(chunk)}건): {e}")
            continue

        for r in results:
            sid = r["id"]
            if sid not in id_to_record:
                continue  # 모델이 요청 안 한 id를 냈으면 무시
            _, name, current_period, current_method = id_to_record[sid]

            if r["not_found_in_source"]:
                for field, current in (
                    ("application_period", current_period),
                    ("application_method", current_method),
                ):
                    if current:
                        discrepancies.append(
                            Discrepancy(sid, name, field, current, "", "", "not_found_in_source")
                        )
                continue

            field_specs = (
                (
                    "application_period",
                    current_period,
                    "application_period_value",
                    "application_period_quote",
                ),
                (
                    "application_method",
                    current_method,
                    "application_method_value",
                    "application_method_quote",
                ),
            )
            for field, current, fresh_value_key, fresh_quote_key in field_specs:
                if not current:
                    continue  # 원래 값이 없던 필드는 "주장"이 없으니 재검증 대상 아님
                fresh_value = r[fresh_value_key].strip()
                fresh_quote = r[fresh_quote_key].strip()

                if not fresh_value:
                    # 지금 값이 있는데 원문에서 아예 못 찾음 — id=46과 같은 유형, 가장 심각.
                    discrepancies.append(
                        Discrepancy(sid, name, field, current, "", "", "no_source_evidence")
                    )
                    continue

                found, _ = verify.quote_exists_in_source(fresh_quote, source_text)
                if not found:
                    # 값은 냈는데 인용이 원문에 없음 — 모델이 지어냈을 가능성, 역시 심각.
                    discrepancies.append(
                        Discrepancy(
                            sid,
                            name,
                            field,
                            current,
                            fresh_value,
                            fresh_quote,
                            "no_source_evidence",
                        )
                    )
                    continue

                if _normalize_loose(fresh_value) != _normalize_loose(current):
                    discrepancies.append(
                        Discrepancy(
                            sid, name, field, current, fresh_value, fresh_quote, "value_mismatch"
                        )
                    )

    return discrepancies


def _normalize_loose(s: str) -> str:
    return "".join(s.split())


def render_review_markdown(discrepancies: list[Discrepancy], scope: str) -> str:
    date_str = datetime.date.today().isoformat()
    lines = [f"# 기존 데이터 재검증 리뷰 — {scope} ({date_str})", ""]
    if not discrepancies:
        lines.append("불일치 없음 — 재검증 대상 전부 원문 인용 확인됨.")
        return "\n".join(lines)

    no_evidence_kinds = ("no_source_evidence", "not_found_in_source")
    no_evidence = [d for d in discrepancies if d.kind in no_evidence_kinds]
    mismatch = [d for d in discrepancies if d.kind == "value_mismatch"]

    lines.append(
        f"불일치 {len(discrepancies)}건 발견 "
        f"(원문 근거 없음 {len(no_evidence)}건, 값 다름 {len(mismatch)}건)"
    )
    lines.append("")

    if no_evidence:
        lines.append("## ⚠️ 원문에 근거 없음 (id=46과 같은 유형 — 우선순위 높음)")
        lines.append("")
        for d in no_evidence:
            lines.append(f"### id={d.scholarship_id} {d.name}")
            lines.append(f"- 필드: `{d.field}`")
            lines.append(f"- 현재 DB 값: `{d.current_value!r}`")
            lines.append("- 원문 재확인 결과: 근거 문장을 찾을 수 없음")
            lines.append("- 제안: 확실한 원문 재조사 전까지 NULL로 비우는 것을 권장")
            lines.append("")

    if mismatch:
        lines.append("## 값이 다름 (원문 근거는 있으나 현재 DB 값과 불일치)")
        lines.append("")
        for d in mismatch:
            lines.append(f"### id={d.scholarship_id} {d.name}")
            lines.append(f"- 필드: `{d.field}`")
            lines.append(f"- 현재 DB 값: `{d.current_value!r}`")
            lines.append(f"- 원문에서 새로 확인: `{d.fresh_value!r}` ← \"{d.fresh_quote}\"")
            lines.append("")

    return "\n".join(lines)


def reverify(university: str | None) -> None:
    scope = university or "전체"
    _log(f"재검증 시작 — 대상: {scope}")
    records = db.fetch_records_for_reverification(university)
    _log(f"재검증할 레코드(period/method 중 하나라도 채워진 것): {len(records)}건")
    if not records:
        _log("대상 없음 — 종료")
        return

    by_url: dict[str, list[tuple[int, str, str | None, str | None]]] = {}
    for sid, name, url, period, method in records:
        by_url.setdefault(url, []).append((sid, name, period, method))

    client = anthropic.Anthropic(api_key=config.load_anthropic_api_key(), timeout=180.0)
    all_discrepancies: list[Discrepancy] = []
    for url, group in by_url.items():
        _log(f"URL 처리 중: {url} ({len(group)}건)")
        try:
            discrepancies = reverify_url_group(client, url, group)
        except Exception as e:  # noqa: BLE001 — 이 URL만 스킵, 나머지 URL은 계속
            _log(f"URL 처리 실패, 스킵({url}): {e}")
            continue
        all_discrepancies.extend(discrepancies)

    _log(f"완료 — 불일치 {len(all_discrepancies)}건 발견")

    review_md = render_review_markdown(all_discrepancies, scope)
    if not all_discrepancies:
        _log("불일치 없음 — PR 안 엶")
        return

    date_str = datetime.date.today().isoformat()
    time_str = datetime.datetime.now().strftime("%H%M%S")
    slug = build_pr._slug(scope)  # noqa: SLF001 — 같은 모듈 내부 규칙 재사용(대학명 슬러그화)
    branch_name = f"harness/reverify-{slug}-{date_str}-{time_str}"
    md_path = f"supabase/reverify_review_{slug}_{date_str}.md"

    try:
        build_pr._create_branch_and_commit(  # noqa: SLF001
            branch_name,
            {md_path: review_md},
            f"[harness] 재검증 리뷰 — {scope} ({date_str})",
        )
        pr_url = build_pr.open_pr(
            branch_name,
            f"[하네스 재검증] {scope} — 불일치 {len(all_discrepancies)}건",
            build_pr._pr_body(review_md, md_path),  # noqa: SLF001
        )
        _log(f"PR 오픈: {pr_url}")
    except Exception as e:  # noqa: BLE001 — 이미 API 비용은 발생한 뒤라 결과를 로그에 남김
        _log(f"git/PR 단계 실패 — 아래 리뷰를 로그에서 복구할 것:\n{review_md}")
        raise e


def main() -> None:
    parser = argparse.ArgumentParser(description="기존 장학금 데이터 재검증(인용 근거 기계적 대조)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--university", help="이 대학의 레코드만 재검증")
    group.add_argument("--all", action="store_true", help="전체 재검증")
    args = parser.parse_args()
    reverify(None if args.all else args.university)


if __name__ == "__main__":
    main()
