# -*- coding: utf-8 -*-
"""2026-08-11: 사용자가 상세페이지에서 "이수학점 · 해당 없음"이 왜 보이냐고 지적함 — 확인해보니
`min_credits`/`admission_score_condition` 칸에 "조건이 없다"는 뜻으로 문자열 "해당 없음"이
실제 값처럼 그대로 들어가 있었음(예전 배치 작업 때 빈칸 대신 이렇게 채워 넣은 것). 이 두 필드는
프론트(`scholarship/[id]/page.tsx`)에서 "값이 있으면(truthy) 보여준다" 로직이라, 조건이 없으면
그냥 NULL로 둬서 아예 안 보이게 하는 게 맞음(빈칸=조건없음이 기존 스키마 컨벤션과도 일치).

대상(정확히 이 문자열과 일치하는 것만 — "학점 조건 없음" 같은 실제 의미 있는 문장 안의
"없음"은 안 건드림):
- min_credits = '해당 없음' 또는 '해당 없음 (재학 여부 무관)' → 68건
- admission_score_condition = '해당 없음' → 36건

headcount(4건)·application_period·grade_level·affiliated_institution에도 비슷한 값이 있지만
headcount는 StatBox에 항상 표시되는 필드라 "해당 없음(전원 지원)"처럼 오히려 정보성이 있는
경우가 섞여 있고, grade_level/affiliated_institution은 애초에 프론트에 안 쓰이는 레거시
필드라 이번엔 손대지 않음 — 필요하면 별도로 논의.

사용법:
    python fix_naeum_placeholder_2026-08-11.py           # dry-run만
    python fix_naeum_placeholder_2026-08-11.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


TARGETS: dict[str, list[str]] = {
    "min_credits": ["해당 없음", "해당 없음 (재학 여부 무관)"],
    "admission_score_condition": ["해당 없음"],
}


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    report_lines = []
    total = 0
    for col, values in TARGETS.items():
        cur.execute(
            f"SELECT id, name FROM scholarship WHERE {col} = ANY(%s) ORDER BY id",
            (values,),
        )
        affected = cur.fetchall()
        cur.execute(
            f"UPDATE scholarship SET {col} = NULL WHERE {col} = ANY(%s)",
            (values,),
        )
        total += cur.rowcount
        report_lines.append(f"\n## {col} — {cur.rowcount}건 NULL로 변경")
        for fid, name in affected:
            report_lines.append(f"  id={fid} {name}")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_naeum_placeholder_2026-08-11_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). 총 {total}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). 총 {total}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
