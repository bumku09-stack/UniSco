# -*- coding: utf-8 -*-
"""라이브 DB의 scholarship 테이블 전체에 대해 description_gap_check.py의 세 가지 검사
(A: 플레이스홀더 값, B/C: 자격조건·금액·인원·기간 키워드 vs NULL, 포괄 제한문구 catch-all)를
돌려서 마크다운 리포트를 생성하는 감사 도구. 읽기 전용 — DB를 수정하지 않음.

사용법:
    python audit_description_gaps.py [출력경로.md]
    (출력경로 생략 시 supabase/audit_reports/YYYY-MM-DD_HHMMSS.md 에 저장)
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from description_gap_check import (  # noqa: E402
    find_gaps,
    find_generic_restriction_flag,
    find_placeholder_values,
)


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def fetch_all_rows() -> list[dict]:
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()
    cur.execute("SELECT * FROM scholarship ORDER BY id")
    columns = [c.name for c in cur.description]
    rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def snippet(text: str | None, length: int = 120) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return text if len(text) <= length else text[:length] + "..."


def build_report(rows: list[dict]) -> str:
    placeholder_hits: list[tuple[dict, dict]] = []
    gap_hits: dict[str, list[dict]] = {}
    generic_hits: list[dict] = []

    for row in rows:
        found = find_placeholder_values(row)
        if found:
            placeholder_hits.append((row, found))

        for field in find_gaps(row):
            gap_hits.setdefault(field, []).append(row)

        if find_generic_restriction_flag(row):
            generic_hits.append(row)

    lines: list[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"# 장학금 데이터 감사 리포트 ({now})")
    lines.append("")
    lines.append(f"전체 {len(rows)}건 대상. 읽기 전용 자동 스캔 결과 — 사람이 원문 대조로")
    lines.append("재확인하기 전까지는 확정된 문제가 아님(특히 B/C, 포괄 규칙은 오탐 가능).")
    lines.append("")

    # A) placeholder
    lines.append(f"## A) 플레이스홀더 값 (오탐 거의 없음) — {len(placeholder_hits)}건")
    lines.append("")
    if not placeholder_hits:
        lines.append("(없음)")
    for row, found in placeholder_hits:
        lines.append(f"- id={row['id']} `{row['name']}` ({row.get('provider') or '기관 미상'})")
        for col, val in found.items():
            lines.append(f"  - `{col}` = `{val}`")
    lines.append("")

    # B/C) field-keyword gaps
    total_gap_rows = len({row["id"] for rows_ in gap_hits.values() for row in rows_})
    lines.append(f"## B/C) 자격조건·금액·인원·기간 키워드 vs NULL — 필드별, 총 {total_gap_rows}건(중복 포함 아님)")
    lines.append("")
    if not gap_hits:
        lines.append("(없음)")
    for field, field_rows in sorted(gap_hits.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"### `{field}` — {len(field_rows)}건")
        for row in field_rows:
            lines.append(
                f"- id={row['id']} `{row['name']}` ({row.get('provider') or '기관 미상'}): "
                f"{snippet(row.get('description'))}"
            )
        lines.append("")

    # generic catch-all
    lines.append(f"## 포괄 제한문구 catch-all (필드 미특정, 구조화 조건 전무) — {len(generic_hits)}건")
    lines.append("")
    if not generic_hits:
        lines.append("(없음)")
    for row in generic_hits:
        lines.append(
            f"- id={row['id']} `{row['name']}` ({row.get('provider') or '기관 미상'}): "
            f"{snippet(row.get('description'))}"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    rows = fetch_all_rows()
    report = build_report(rows)

    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])
    else:
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        out_dir = Path(__file__).resolve().parents[1] / "audit_reports"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"{ts}.md"

    out_path.write_text(report, encoding="utf-8")
    print(f"done: {out_path}")


if __name__ == "__main__":
    main()
