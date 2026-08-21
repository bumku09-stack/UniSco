"""Backfill min_credits_last_semester by parsing the already-sourced min_credits free text —
this is NOT guessing a new fact (min_credits itself was already verified from source during
data entry); it's structuring an existing verified value. Only records where min_credits
unambiguously means "직전학기 N학점 이상"(previous-semester completed credits, matching
UserSpec.credits_last_semester's own "직전학기 이수학점" semantics, frontend/src/components/
spec-fields.tsx label) are backfilled. Ambiguous phrasing ("해당학기" = current enrolling
term, a different concept), different concepts (major-specific course credits, annual
totals, per-track conditions), or bare numbers with no time qualifier are left as text-only
in min_credits, matching the original data-enterer's own judgment call to not structure them.

Usage:
    python fix_backfill_min_credits_last_semester_2026-08-18.py          # dry run
    python fix_backfill_min_credits_last_semester_2026-08-18.py --apply  # commit
"""

import argparse

import psycopg2

# id -> min_credits_last_semester. Only records where min_credits explicitly says
# "직전학기"/"매학기"/"학기별" (or equivalent recurring-per-semester phrasing) are included.
# id=1042/1125 ("재학생: N학점 이상, 신입생은 면제") were deliberately EXCLUDED even though
# they share the same freshman-exemption shape as id=996 — unlike 996 ("학기별 N학점 이상"),
# they lack an explicit per-semester qualifier (just bare "N학점 이상"), so backfilling would
# be inferring intent rather than reading it — the exact "sibling pattern looks similar"
# mistake this project has been burned by before.
# id=973 (직전 2개학기 학기당 12학점 이상) is simplified to a single-semester 12 check —
# under-enforces the "two consecutive semesters" nuance but that's an accepted over-matching
# simplification (matches the project's existing leniency principle), not a correctness error
# in the unsafe direction.
BACKFILL: dict[int, int] = {
    135: 12,
    147: 12,
    257: 15,
    259: 15,
    261: 15,
    262: 15,
    667: 12,
    973: 12,
    990: 12,
    996: 12,
    1008: 12,
    1010: 12,
    1027: 12,
    1028: 12,
    1030: 12,
    1032: 12,
    1034: 12,
    1035: 12,
    1139: 12,
    1140: 12,
    1141: 12,
}


def load_database_url() -> str:
    with open("/Users/master/UniSco/backend/.env") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("DATABASE_URL not found in backend/.env")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = list(BACKFILL.keys())
    cur.execute(
        "SELECT id, name, min_credits, min_credits_last_semester FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    rows = cur.fetchall()
    print(f"Backfilling {len(rows)} records:\n")
    for id_, name, min_credits, current in rows:
        new_value = BACKFILL[id_]
        print(f"id={id_} | {name}")
        print(f"   min_credits: {min_credits!r}")
        print(f"   min_credits_last_semester: {current!r} -> {new_value}")

    if not args.apply:
        print("\nDry run — pass --apply to commit.")
        cur.close()
        conn.close()
        return

    for id_, value in BACKFILL.items():
        cur.execute(
            "UPDATE scholarship SET min_credits_last_semester = %s WHERE id = %s", (value, id_)
        )
    conn.commit()
    print(f"\nUpdated {cur.rowcount and len(BACKFILL)} records.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
