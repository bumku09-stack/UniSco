"""Layer 1 — 산출물 생성 + PR 오픈. **여기서 끝남, DB에는 아무것도 안 씀.**

기존 `supabase/data_XXX.sql` 포맷 그대로 초안 SQL을 새 파일로 만들고, 필드별 근거 인용과
플래그 목록을 담은 리뷰 마크다운을 만든 다음, 새 브랜치에 커밋해서 GitHub PR을 연다.
자동 머지 없음 — 실제 DB 반영은 지금처럼 사람이 `supabase/tools/run_sql.py`를 직접 실행함
(설계안 제약사항 "실제 운영 DB는 절대 자동화하지 않음").
"""
from __future__ import annotations

import datetime
import os
import re
import subprocess
from pathlib import Path

import requests

from harness import config
from harness.models import (
    LIST_VALUED_FIELDS,
    SCHOLARSHIP_FIELD_NAMES,
    CollectionResult,
    VerifiedScholarship,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _log(msg: str) -> None:
    print(f"[harness] {msg}", flush=True)


def _github_headers() -> dict[str, str] | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

# 기존 supabase/data_*.sql 파일명 관례(로마자 축약)와 맞춤 — 여기 없는 대학은 한글 그대로
# 파일명 세이프하게 치환해서 씀(신규 대학 온보딩 시 여기 추가하면 됨).
UNIVERSITY_SLUGS: dict[str, str] = {
    "충남대학교": "cnu",
    "KAIST": "kaist",
    "한밭대학교": "hanbat",
    "배재대학교": "baejae",
    "목원대학교": "mokwon",
    "우송대학교": "woosong",
    "한남대학교": "hannam",
    "을지대학교": "eulji",
    "대전대학교": "dju",
    "한국침례신학대학교": "kbtus",
}


def _slug(university: str) -> str:
    if university in UNIVERSITY_SLUGS:
        return UNIVERSITY_SLUGS[university]
    return re.sub(r"[^0-9a-zA-Z가-힣]+", "_", university).strip("_") or "unknown"


def _sql_literal(field_name: str, value) -> str:
    if value is None:
        return "NULL"
    if field_name in LIST_VALUED_FIELDS:
        if not value:
            return "'{}'"
        escaped = [str(v).replace("'", "''") for v in value]
        return "ARRAY[" + ",".join(f"'{v}'" for v in escaped) + "]"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def render_sql_insert(university: str, verified_list: list[VerifiedScholarship]) -> str:
    """기존 data_XXX.sql과 같은 컬럼 순서(schema.sql 기준)의 INSERT 문 초안."""
    date_str = datetime.date.today().isoformat()
    columns = ", ".join(SCHOLARSHIP_FIELD_NAMES)
    rows = [
        "(" + ", ".join(_sql_literal(name, v.value(name)) for name in SCHOLARSHIP_FIELD_NAMES) + ")"
        for v in verified_list
    ]
    header = (
        f"-- {university} 장학금 — 하네스 자동 수집 초안 ({date_str})\n"
        f"-- 사람 리뷰 후 이 내용을 supabase/data_{_slug(university)}.sql로 옮길 것.\n"
        f"-- 실제 DB 반영은 지금처럼 supabase/tools/run_sql.py를 사람이 직접 실행함 — 이 파일은 초안임.\n"
        f"-- needs_review로 플래그된 필드가 있는 행은 같은 이름의 harness_review_*.md에서 근거를 먼저 확인할 것.\n\n"
    )
    return f"{header}INSERT INTO scholarship ({columns}) VALUES\n" + ",\n".join(rows) + ";\n"


def render_review_markdown(
    university: str,
    verified_list: list[VerifiedScholarship],
    collection_results: list[CollectionResult],
    skipped_duplicate_count: int,
) -> str:
    lines = [f"# {university} 장학금 하네스 수집 리뷰 — {datetime.date.today().isoformat()}", ""]

    lines.append("## 목록 수집 결과 (원칙 1 — \"다 봤는지\"를 코드가 대조한 결과)")
    for r in collection_results:
        status = "OK" if r.ok else "⚠️ 확인 필요"
        expected = r.expected_count if r.expected_count is not None else "파싱 안 됨"
        note = f" ({r.note})" if r.note else ""
        lines.append(f"- {r.board_name}: 수집 {r.actual_count}건 / 게시판 표시 {expected}건 — {status}{note}")
    lines.append("")
    lines.append(f"이름+기관 유사도로 스킵된 기존 중복: {skipped_duplicate_count}건 · 신규 처리: {len(verified_list)}건")
    lines.append("")

    total_flagged = sum(len(v.flagged_fields) for v in verified_list)
    lines.append(f"## 신규 장학금 {len(verified_list)}건 (플래그된 필드 총 {total_flagged}개)")
    lines.append("")

    for v in verified_list:
        name_field = v.fields.get("name")
        title = (name_field.value if name_field and name_field.value else None) or v.listing_title or "(이름 미확인)"
        lines.append(f"### {title}")
        lines.append(f"- 출처: {v.source_url}")
        if v.has_flags:
            lines.append(f"- ⚠️ 확인 필요 필드 {len(v.flagged_fields)}개:")
            for f in v.flagged_fields:
                lines.append(f"  - `{f.name}` = `{f.value!r}` — {f.reason} (인용: {f.source_quote!r})")
        else:
            lines.append("- 플래그된 필드 없음(값이 채워진 모든 필드의 인용이 원문과 일치, 원칙 2 통과)")
        confirmed = [f for f in v.fields.values() if f.status == "confirmed"]
        if confirmed:
            lines.append("- 확인된 근거 (원문 인용):")
            for f in confirmed:
                lines.append(f"  - `{f.name}` = `{f.value!r}` ← \"{f.source_quote}\"")
        lines.append("")

    return "\n".join(lines)


def _run_git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=REPO_ROOT, check=True)


def _create_branch_and_commit(branch_name: str, files: dict[str, str], commit_message: str) -> None:
    # -B(대문자)로 이미 같은 이름의 로컬 브랜치가 있어도 강제로 새로 만듦 — 브랜치명에
    # 초 단위 타임스탬프가 들어가서(아래 build_and_open_pr) 실무상 거의 안 일어나지만,
    # 로컬 재실행 등 예외 상황에서 "이미 존재함" 에러로 죽는 것보다 안전함.
    _run_git("checkout", "-B", branch_name)
    for rel_path, content in files.items():
        full_path = REPO_ROOT / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        _run_git("add", rel_path)
    _run_git("commit", "-m", commit_message)
    _run_git("push", "-u", "origin", branch_name)


def _delete_remote_branch(branch_name: str) -> None:
    """push는 성공했는데 그 다음 단계(PR 오픈)가 실패했을 때 뒷정리용. 실패해도(예: 권한
    부족) 무시함 — 뒷정리 실패가 원래 에러를 가리면 안 되므로 여기서 예외를 삼킴."""
    try:
        subprocess.run(
            ["git", "push", "origin", "--delete", branch_name],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        _log(f"뒷정리: 실패한 브랜치 {branch_name} 삭제함")
    except Exception as e:  # noqa: BLE001 — 뒷정리 실패는 무시하고 원래 에러를 그대로 전파
        _log(f"뒷정리 실패(무시하고 계속): {branch_name} 삭제 안 됨 — {e}")


def find_existing_open_pr(university: str) -> str | None:
    """오늘 날짜로 이 대학의 하네스 PR이 이미 열려있으면 그 URL을 반환, 없으면 None.

    재실행(수동 workflow_dispatch로 같은 대학을 같은 날 다시 돌리는 경우 등)이 이미 성공한
    작업을 또 하면서 Anthropic API 토큰을 이중으로 쓰는 걸 막기 위함 — run.py가 수집·추출
    (비용 발생 구간) 시작 전에 이 함수로 먼저 확인함."""
    headers = _github_headers()
    if headers is None:
        return None
    date_str = datetime.date.today().isoformat()
    prefix = f"harness/{_slug(university)}-{date_str}"
    resp = requests.get(
        f"https://api.github.com/repos/{config.GITHUB_REPO}/pulls",
        headers=headers,
        params={"state": "open", "per_page": 100},
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    for pr in resp.json():
        if pr["head"]["ref"].startswith(prefix):
            return pr["html_url"]
    return None


def open_pr(branch_name: str, title: str, body: str, *, draft: bool = True) -> str:
    headers = _github_headers()
    if headers is None:
        raise RuntimeError(
            "GITHUB_TOKEN이 없음 — PR을 열 수 없음. GitHub Actions에서는 자동 제공되지만 "
            "로컬 실행 시엔 브랜치 푸시까지만 확인하고 PR은 웹에서 직접 열 것."
        )
    resp = requests.post(
        f"https://api.github.com/repos/{config.GITHUB_REPO}/pulls",
        headers=headers,
        json={"title": title, "head": branch_name, "base": config.PR_BASE_BRANCH, "body": body, "draft": draft},
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()["html_url"]


def build_and_open_pr(
    university: str,
    verified_list: list[VerifiedScholarship],
    collection_results: list[CollectionResult],
    skipped_duplicate_count: int,
) -> str | None:
    """신규 항목이 없으면 아무것도 안 하고 None 반환 — 빈 PR을 만들지 않음."""
    if not verified_list:
        return None

    date_str = datetime.date.today().isoformat()
    time_str = datetime.datetime.now().strftime("%H%M%S")
    slug = _slug(university)
    # 날짜만 쓰면 같은 날 재실행(예: 이전 실행이 실패해서 다시 돌리는 경우) 시 브랜치명이
    # 겹쳐서 push가 non-fast-forward로 거부됨(2026-08-10 실제 발생) — 초 단위 시각까지
    # 붙여서 실행마다 항상 고유하게 만듦. find_existing_open_pr()이 날짜 프리픽스로 대조하는
    # 것과는 별개(그쪽은 "오늘 이미 PR 있나" 판단용, 이건 "브랜치명이 겹치나" 방지용).
    branch_name = f"harness/{slug}-{date_str}-{time_str}"

    sql_path = f"supabase/data_{slug}_harness_draft_{date_str}.sql"
    md_path = f"supabase/harness_review_{slug}_{date_str}.md"
    review_md = render_review_markdown(university, verified_list, collection_results, skipped_duplicate_count)
    sql_draft = render_sql_insert(university, verified_list)

    files = {
        sql_path: sql_draft,
        md_path: review_md,
    }

    flagged_total = sum(len(v.flagged_fields) for v in verified_list)
    commit_message = f"[harness] {university} 장학금 신규 {len(verified_list)}건 초안 ({date_str})"
    title = f"[하네스 초안] {university} 신규 {len(verified_list)}건 · 확인 필요 {flagged_total}건"

    pushed = False
    try:
        _create_branch_and_commit(branch_name, files, commit_message)
        pushed = True
        return open_pr(branch_name, title, review_md)
    except Exception:
        # 여기까지 오는 시점엔 이미 Anthropic API로 수집·추출을 다 끝낸 뒤라(비용 발생 완료),
        # git/PR 단계에서 죽어서 그 결과물을 통째로 날리면 손해가 큼 — 최소한 워크플로 로그에
        # 원문 그대로 남겨서 사람이 수동으로 복구할 수 있게 함.
        _log("git/PR 단계 실패 — 아래 산출물을 워크플로 로그에서 복구할 것:")
        _log(f"=== {sql_path} ===\n{sql_draft}")
        _log(f"=== {md_path} ===\n{review_md}")
        if pushed:
            _delete_remote_branch(branch_name)
        raise
