"""Remove 3 scholarship records whose claimed source (대전대 장학공지 게시판) does not
actually contain them — confirmed by paginating the full board (29 pages, 2025-06-11
~2026-07-03) via direct POST requests and finding zero matching titles. All three came
from the same commit (f52700c, 2026-08-03) with no application_url and identical vague
"자체 기준에 준해" phrasing. User confirmed deletion after review.

Usage:
    python fix_remove_unsourced_2026-08-15.py          # dry run
    python fix_remove_unsourced_2026-08-15.py --apply  # commit
"""

import argparse

import psycopg2

TARGET_IDS = [299, 300, 301]  # 의용소방대자녀장학금, 새마을지도자자녀장학금, 서울희망장학금


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
        "SELECT id, name, provider FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (TARGET_IDS,),
    )
    rows = cur.fetchall()
    print("Scholarships to remove:")
    for id_, name, provider in rows:
        print(f"  id={id_} | {name} | {provider}")

    cur.execute(
        "SELECT id, user_id, scholarship_id FROM savedscholarship WHERE scholarship_id = ANY(%s)",
        (TARGET_IDS,),
    )
    saved = cur.fetchall()
    print(f"\nDependent savedscholarship rows: {len(saved)}")
    for row in saved:
        print(f"  {row}")

    if not args.apply:
        print("\nDry run — pass --apply to commit.")
        cur.close()
        conn.close()
        return

    cur.execute("DELETE FROM savedscholarship WHERE scholarship_id = ANY(%s)", (TARGET_IDS,))
    deleted_saved = cur.rowcount
    cur.execute("DELETE FROM scholarship WHERE id = ANY(%s)", (TARGET_IDS,))
    deleted_scholarships = cur.rowcount
    conn.commit()
    print(f"\nDeleted {deleted_saved} savedscholarship rows, {deleted_scholarships} scholarship rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
