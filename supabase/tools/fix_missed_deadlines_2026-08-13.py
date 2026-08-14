"""2026-08-13: 사용자 재지적으로 발견한 남은 deadline 누락 64건 반영.
1) 작업 A의 원래 15건(당시엔 application_period만 건드리고 deadline은 일부러 안 건드렸는데,
   그 뒤 확립된 "정확하면 지난 연도 날짜라도 deadline까지 채운다" 규칙을 소급 적용 안 했었음).
2) 충남대 자동선발 43건 — "학생이 지켜야 할 마감일이 아니다"라는 자체 판단으로 deadline을
   안 채웠던 것 — 사용자 규칙은 무조건("정확하면 채운다")이었으므로 그 예외를 철회하고 반영.
3) 기타 텍스트에 이미 날짜가 있었는데 빠졌던 6건.

사용법:
    python fix_missed_deadlines_2026-08-13.py           # dry-run만
    python fix_missed_deadlines_2026-08-13.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

DEADLINE_FIXES: dict[int, str] = {
    # 작업 A 15건 원복 소급 반영
    524: "2025-09-26",
    533: "2025-09-26",
    536: "2025-09-12",
    537: "2025-09-11",
    641: "2025-10-27",
    642: "2025-10-27",
    643: "2025-10-27",
    644: "2025-10-27",
    645: "2025-12-31",
    646: "2026-02-18",
    647: "2026-05-11",
    648: "2025-11-10",
    664: "2025-08-29",
    668: "2025-12-29",
    683: "2025-10-24",

    # 충남대 신입생 자동선발 16건 — 선발일자 2026-02-02
    7: "2026-02-02", 8: "2026-02-02", 9: "2026-02-02", 11: "2026-02-02",
    12: "2026-02-02", 13: "2026-02-02", 14: "2026-02-02", 17: "2026-02-02",
    18: "2026-02-02", 19: "2026-02-02", 23: "2026-02-02", 26: "2026-02-02",
    27: "2026-02-02", 28: "2026-02-02", 29: "2026-02-02", 30: "2026-02-02",

    # 충남대 재학생 자동선발 27건 — 확정일 2026-08-21
    38: "2026-08-21", 39: "2026-08-21", 40: "2026-08-21", 41: "2026-08-21",
    42: "2026-08-21", 43: "2026-08-21", 44: "2026-08-21", 45: "2026-08-21",
    46: "2026-08-21", 49: "2026-08-21", 50: "2026-08-21", 51: "2026-08-21",
    53: "2026-08-21", 54: "2026-08-21", 55: "2026-08-21", 56: "2026-08-21",
    59: "2026-08-21", 60: "2026-08-21", 61: "2026-08-21", 62: "2026-08-21",
    63: "2026-08-21", 64: "2026-08-21", 65: "2026-08-21", 66: "2026-08-21",
    67: "2026-08-21", 68: "2026-08-21", 69: "2026-08-21",

    # 기타 텍스트엔 이미 날짜 있었는데 deadline 누락됐던 6건
    520: "2026-04-30",
    521: "2026-04-30",
    534: "2026-03-27",
    535: "2026-01-26",
    667: "2026-03-18",
    651: "2026-04-30",
    1071: "2024-09-25",
}


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = sorted(DEADLINE_FIXES)
    cur.execute(
        "SELECT id, name, application_deadline FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    changed = 0
    for sid, new_deadline in DEADLINE_FIXES.items():
        if sid not in before_rows:
            continue
        before = before_rows[sid]
        if str(before[2]) == new_deadline:
            continue
        changed += 1
        cur.execute(
            "UPDATE scholarship SET application_deadline = %s WHERE id = %s",
            (new_deadline, sid),
        )

    cur.execute(
        "SELECT id, name, application_deadline FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for sid in ids:
        before = before_rows.get(sid)
        after = after_rows.get(sid)
        if not before or before[2] == after[2]:
            continue
        print(f"id={sid} {before[1]}: {before[2]!r} -> {after[2]!r}")

    print(f"\n총 {len(ids)}건 대상, {changed}건 변경.")

    if apply:
        conn.commit()
        print("반영 완료(commit).")
    else:
        conn.rollback()
        print("dry-run만 수행(rollback, 실제 반영 안 됨).")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
