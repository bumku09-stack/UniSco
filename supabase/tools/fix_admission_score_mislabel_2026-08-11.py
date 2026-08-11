# -*- coding: utf-8 -*-
"""2026-08-11: 사용자가 "성취장학금"(id=522) 상세페이지에서 지원조건에 "입학성적: B+ 이상"이
뜨는 게 이상하다고 지적 — 확인해보니 `admission_score_condition`("내신/입학성적 조건" 전용
칸, 고교 때 성적/수능 등 "입학 당시" 조건만 담는 칸)에 **재학 중 성적 유지 조건**(평점평균)이
잘못 들어가 있었음. 전체 DB를 다시 훑어서 같은 실수 7건을 전부 찾음.

- 21, 22, 76, 522: min_gpa가 이미 정확히 변환돼서 채워져 있어 완전히 중복 — 지움.
- 75, 173, 688: 100점 만점/백분위 기준이라 min_gpa(4.5만점 전용)로 변환은 못 하지만, 이것도
  "입학성적"이 아니라 "재학 중 성적"이므로 이 칸에 있으면 안 됨. 원문 정보는 description에
  이미 있어서 지워도 정보 손실 없음.

사용법:
    python fix_admission_score_mislabel_2026-08-11.py           # dry-run만
    python fix_admission_score_mislabel_2026-08-11.py --apply    # 실제 반영
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


IDS = [21, 22, 75, 76, 173, 522, 688]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, admission_score_condition FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (IDS,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    cur.execute(
        "UPDATE scholarship SET admission_score_condition = NULL WHERE id = ANY(%s)",
        (IDS,),
    )
    affected = cur.rowcount

    report_lines = []
    for fid in IDS:
        before = before_rows.get(fid)
        if before is None:
            continue
        report_lines.append(f"\n## id={fid} {before[1]}")
        report_lines.append(f"  admission_score_condition: {before[2]!r} -> None")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_admission_score_mislabel_2026-08-11_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {affected}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {affected}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
