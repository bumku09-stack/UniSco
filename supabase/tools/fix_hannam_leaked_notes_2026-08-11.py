# -*- coding: utf-8 -*-
"""2026-08-11: 2026-08-10에 47건 정리했던 "description에 내부 메모가 섞여 들어간" 문제가
한남대 "존재 자체가 불확실한 장학금 5건"(matching_gaps.md)에도 똑같이 있었음 — 이 5건은
"존재 불확실" 목록으로 따로 빠져있어서 그때 같이 정리가 안 됐고, 지금까지 상세페이지
"장학금 소개"란에 "2026-08-02 재검증: ... 여전히 저신뢰 상태, 추후 재확인 권장" 같은 내부
검증 메모가 그대로 노출되고 있었음.

"이 장학금이 실제로 존재하는지"는 여전히 미해결이라 matching_gaps.md에 그대로 남겨두고,
여기서는 description에서 내부 메모만 걷어내서 사용자에게 최소한 깔끔하고 사실에 부합하는
텍스트만 보이게 함(추측으로 내용을 보태지 않음 — 확실히 아는 것만 남김).

사용법:
    python fix_hannam_leaked_notes_2026-08-11.py           # dry-run만
    python fix_hannam_leaked_notes_2026-08-11.py --apply    # 실제 반영
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


FIXES: list[dict] = [
    {"id": 227, "description": "어학 성적 우수 신입생 대상."},
    {"id": 230, "description": "사회통합전형 등 고른기회 특별전형 입학생 대상."},
    {"id": 233, "description": "검정고시 출신 신입생 대상."},
    {"id": 241, "description": "영어 능력시험 성적 우수 학생 대상."},
    {"id": 242, "description": "재외국민 전형 입학생 대상."},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, description FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        cur.execute(
            "UPDATE scholarship SET description = %s WHERE id = %s",
            (fix["description"], fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, description FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        report_lines.append(f"\n## id={fid} {before[1]}")
        report_lines.append(f"  before: {before[2]!r}")
        report_lines.append(f"  after:  {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_hannam_leaked_notes_2026-08-11_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(FIXES)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(FIXES)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
