"""Fix application_url for id=679/680 (고리원자력본부장학) — was pointing to the KHNP 고리원자력
사업소 top-level homepage (no scholarship info at all), which turned out to be the same
"URL points to the org but not the specific post" problem as CNU id=46/plus.cnu.ac.kr.

User found the real board and pointed at a specific post; that one turned out to be this
year's *selection-results* announcement (2026-08-12), not the original eligibility notice —
re-searched the same board (key=1163&bbsNo=131) for "장학" and found the actual recruitment
post: "(안내사항 추가)2026년 고리원자력본부 주변지역 장학생 선발 공고" (nttNo=75605).

Note: the credit/GPA eligibility text itself (min_credits, description) is NOT re-verified
here — the recruitment post's attached HWP extracts empty (pyhwp fails silently on this
file) and its attached PNG poster's OCR doesn't surface the eligibility table either. Only
the link is corrected; min_credits stays in the unverified bucket until a source-check
actually succeeds.

Usage:
    python fix_kori_application_url_2026-08-18.py          # dry run
    python fix_kori_application_url_2026-08-18.py --apply  # commit
"""

import argparse

import psycopg2

NEW_URL = "https://www.khnp.co.kr/kori/selectBbsNttView.do?key=1163&bbsNo=131&nttNo=75605"
TARGET_IDS = [679, 680]


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

    cur.execute(
        "SELECT id, name, application_url FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (TARGET_IDS,),
    )
    print("Before:")
    for id_, name, url in cur.fetchall():
        print(f"id={id_} | {name} | {url}")
    print(f"\n-> {NEW_URL}")

    if not args.apply:
        print("\nDry run — pass --apply to commit.")
        cur.close()
        conn.close()
        return

    cur.execute(
        "UPDATE scholarship SET application_url = %s WHERE id = ANY(%s)", (NEW_URL, TARGET_IDS)
    )
    conn.commit()
    print(f"\nUpdated {cur.rowcount} records.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
