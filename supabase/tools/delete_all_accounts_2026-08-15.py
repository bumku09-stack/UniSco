"""2026-08-15: 배포 전/후 테스트 중 쌓인 계정을 전부 정리 — 카카오 전용 계정 포함, 가입된
모든 유저를 지움. FK가 CASCADE로 안 걸려있어서(schema.sql 기준) app/api/users.py의
delete_account()와 동일한 순서로 참조 테이블부터 지우고 마지막에 user를 지움.

되돌릴 수 없는 작업이라 dry-run이 기본값 — 몇 명이 지워질지 먼저 보고, 맞으면 --apply로
실행할 것.

사용법:
    python delete_all_accounts_2026-08-15.py           # dry-run만 (개수만 보여줌)
    python delete_all_accounts_2026-08-15.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

_DEPENDENT_TABLES = ["savedscholarship", "savedspec", "emailverification", "passwordreset"]


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    cur.execute('SELECT count(*) FROM "user"')
    total = cur.fetchone()[0]
    cur.execute('SELECT count(*) FROM "user" WHERE kakao_id IS NOT NULL')
    kakao = cur.fetchone()[0]
    print(f"삭제 대상: 전체 {total}명 (카카오 전용 {kakao}명 포함)")

    if not apply:
        print("dry-run만 수행 — 실제 반영하려면 --apply로 다시 실행할 것.")
        cur.close()
        conn.close()
        return

    for table in _DEPENDENT_TABLES:
        cur.execute(f'DELETE FROM {table}')  # noqa: S608 — 하드코딩된 테이블명, 유저 입력 아님
        print(f"{table}: {cur.rowcount}건 삭제")

    cur.execute('DELETE FROM "user"')
    print(f'user: {cur.rowcount}건 삭제')

    conn.commit()
    print("반영 완료(commit).")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
