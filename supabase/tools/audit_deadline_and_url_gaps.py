# -*- coding: utf-8 -*-
"""라이브 DB의 scholarship 테이블에서 (1) application_deadline이 구조화 안 됐는데
application_period(자유 텍스트)에 날짜로 보이는 힌트가 있는 항목, (2) application_url이
아예 없는 항목을 뽑아서 마크다운 리포트를 생성하는 감사 도구. 읽기 전용 — DB를 수정하지
않음(supabase/tools/audit_description_gaps.py와 동일한 구조/컨벤션).

배경: 2026-08-11 배포 전 점검에서 발견 — 661건 중 application_deadline이 채워진 건
10.3%뿐이라 나머지는 실제로 마감이 지났어도 deadline_matches()가 못 걸러냄(구조화된 값이
있어야만 필터링됨, backend/app/core/matching.py 참고). application_url도 130건(19.7%)이
없어서 상세페이지에서 "신청하러 가기" 버튼 자체가 안 뜸.

이 스크립트는 값을 채우지 않음 — 원문을 다시 확인해서 실제 값을 넣는 건 사람(또는 원문을
직접 조사하는 에이전트)의 몫. 여기서는 "어디부터 볼지"만 우선순위별로 추려줌:
- A그룹: application_period에 숫자가 있어서(대부분 날짜) 마감일 파싱 가능성이 높은 항목 —
  이미 DB에 있는 텍스트를 다시 해석하는 거라 원문 재방문 없이도 처리 가능한 경우가 많음.
- B그룹: application_period도 비어있거나 날짜 힌트가 전혀 없는 항목 — "상시모집"류일 가능성이
  높아서 우선순위 낮음(참고용으로만 개수 표기, 목록은 안 뽑음 — 328건이라 리스트가 의미 없음).
- C그룹: application_url이 아예 없는 항목 — 원문(공고문·기관 홈페이지)을 다시 찾아야 함.

사용법:
    python audit_deadline_and_url_gaps.py [출력경로.md]
    (출력경로 생략 시 supabase/audit_reports/YYYY-MM-DD_HHMMSS_deadline_url_gaps.md 에 저장)
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

import psycopg2


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def fetch_all_rows() -> list[dict]:
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, provider, application_deadline, application_period, "
        "application_url FROM scholarship ORDER BY id"
    )
    columns = [c.name for c in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


_HAS_DIGIT = re.compile(r"[0-9]")


def snippet(text: str | None, length: int = 100) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= length else text[:length] + "..."


def build_report(rows: list[dict]) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [f"# 마감일·신청링크 보강 대상 리포트 ({now})", ""]
    lines.append(
        f"전체 {len(rows)}건 대상. 읽기 전용 자동 스캔 — 여기 값을 채운 게 아니라 "
        "우선순위만 추림. 실제 값은 원문 재확인 후 채울 것(추정 금지, 기존 프로젝트 원칙과 동일)."
    )
    lines.append("")

    group_a = [
        r
        for r in rows
        if r["application_deadline"] is None
        and r["application_period"]
        and _HAS_DIGIT.search(r["application_period"])
    ]
    group_b_count = sum(
        1
        for r in rows
        if r["application_deadline"] is None
        and not (r["application_period"] and _HAS_DIGIT.search(r["application_period"]))
    )
    group_c = [r for r in rows if not r["application_url"]]

    lines.append(
        f"## A) 마감일 파싱 가능성 높음 — application_period에 날짜 힌트 있음, {len(group_a)}건"
    )
    lines.append(
        "`application_period`가 이미 DB에 있는 텍스트라 원문 재방문 없이도 "
        "날짜만 정확히 뽑아 `application_deadline`에 채울 수 있는 경우가 많음. "
        "단 매년 반복 공고(예: '매년 3월')처럼 특정 연도가 아닌 경우는 채우지 말 것."
    )
    lines.append("")
    for row in group_a:
        lines.append(
            f"- id={row['id']} `{row['name']}` ({row.get('provider') or '기관 미상'}): "
            f"application_period=\"{snippet(row['application_period'], 80)}\""
        )
    lines.append("")

    lines.append(
        f"## B) 마감일 힌트 전혀 없음(상시모집 등으로 추정, 참고용) — {group_b_count}건"
    )
    lines.append(
        "목록은 안 뽑음(너무 많고 대부분 정상적으로 상시/반복 프로그램이라 NULL이 맞는 "
        "케이스일 가능성이 높음) — 개수만 참고."
    )
    lines.append("")

    lines.append(f"## C) 신청 링크(application_url) 없음 — {len(group_c)}건")
    lines.append(
        "상세페이지에서 \"신청하러 가기\" 버튼 자체가 안 뜨는 항목들 — "
        "기관 홈페이지/공고문에서 실제 신청 링크를 다시 찾아야 함."
    )
    lines.append("")
    for row in group_c:
        lines.append(f"- id={row['id']} `{row['name']}` ({row.get('provider') or '기관 미상'})")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    rows = fetch_all_rows()
    report = build_report(rows)

    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])
    else:
        out_dir = Path(__file__).resolve().parents[1] / "audit_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        out_path = out_dir / f"{ts}_deadline_url_gaps.md"

    out_path.write_text(report, encoding="utf-8")
    print(f"done: {out_path}")


if __name__ == "__main__":
    main()
