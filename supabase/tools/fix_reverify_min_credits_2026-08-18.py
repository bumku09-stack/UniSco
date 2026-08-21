"""Resolves 3 of the 19 records left ambiguous by
fix_backfill_min_credits_last_semester_2026-08-18.py, by actually re-fetching their
application_url (and, for id=962, its linked PDF attachment via the harness's new
extract_pdf()) instead of leaving them as unverified text. Direct source-check results:

- id=684 (강원랜드 멘토링 장학생) — the DB text claimed the 12-credit floor only applies to
  the 나눔장학 track ("키움장학 트랙은 학점 조건 없음"). The source page's requirements table
  has "이수학점" as a single merged cell spanning both 나눔/키움 columns (unlike the adjacent
  "성적기준" row, which has two distinct values per track) — it applies to both. min_credits
  text was wrong, not just under-structured; corrected here.
- id=942 (일반대학생장학금(마루)) — DB text was just "12학점", trimmed from the source's
  "직전 정규 학기 기준: 12학점 이상" (마루 장학 조건, 우양재단 공지). Unambiguous 직전학기
  check; text expanded to keep the qualifier, not just the bare number.
- id=962 (성적우수장학생, 음성군) — DB text was "15학점", trimmed from the attached PDF
  (음성군장학회 2026 공고문): "직전(前) 학년(1~2학기) 각 학기 15학점 이상 이수". Simplified to
  a single-semester 15 check (same accepted under-enforcement as id=973's "직전 2개학기"),
  since the schema only supports one semester's threshold.

Usage:
    python fix_reverify_min_credits_2026-08-18.py          # dry run
    python fix_reverify_min_credits_2026-08-18.py --apply  # commit
"""

import argparse

import psycopg2

UPDATES: dict[int, dict[str, object]] = {
    684: {
        "min_credits": "이수학점 각 학기당 12학점 이상(나눔장학·키움장학 공통 적용 — 원문 표 재확인, 나눔장학만 해당한다는 기존 텍스트는 오류였음)",
        "min_credits_last_semester": 12,
    },
    942: {
        "min_credits": "직전 정규 학기 기준 12학점 이상(마루 장학 조건)",
        "min_credits_last_semester": 12,
    },
    962: {
        "min_credits": "직전(前) 학년(1~2학기) 각 학기 15학점 이상 이수(재학생 기준, 첨부 공고문 PDF)",
        "min_credits_last_semester": 15,
    },
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

    ids = list(UPDATES.keys())
    cur.execute(
        "SELECT id, name, min_credits, min_credits_last_semester FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    print("Before:")
    for id_, name, min_credits, current in cur.fetchall():
        print(f"id={id_} | {name}")
        print(f"   min_credits: {min_credits!r}")
        print(f"   min_credits_last_semester: {current!r}")
        new = UPDATES[id_]
        print(f"   -> min_credits: {new['min_credits']!r}")
        print(f"   -> min_credits_last_semester: {new['min_credits_last_semester']!r}")

    if not args.apply:
        print("\nDry run — pass --apply to commit.")
        cur.close()
        conn.close()
        return

    for id_, fields in UPDATES.items():
        cur.execute(
            "UPDATE scholarship SET min_credits = %s, min_credits_last_semester = %s WHERE id = %s",
            (fields["min_credits"], fields["min_credits_last_semester"], id_),
        )
    conn.commit()
    print(f"\nUpdated {len(UPDATES)} records.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
