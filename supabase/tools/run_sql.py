# -*- coding: utf-8 -*-
"""supabase/data_*.sql 같은 INSERT 스크립트를 실제 DB(Supabase)에 실행하는 도구.

사용법:
    python run_sql.py <파일경로.sql>

파일 안의 SQL을 그대로 실행하고 커밋함. RETURNING 절이 있으면 결과를
run_sql_result.txt로 저장함(콘솔은 한글 인코딩이 깨져서 출력 대신 파일로 남김).

DB 접속 정보는 backend/.env의 DATABASE_URL을 그대로 읽어서 씀 — 비밀번호를
이 파일에 직접 적어두지 않음(레포에 커밋되는 파일이라 자격증명 노출 방지).
"""
import sys
from pathlib import Path

import psycopg2


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        sql = f.read()

    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()
    cur.execute(sql)
    rows = None
    if cur.description:
        rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if rows is not None:
        with open("run_sql_result.txt", "w", encoding="utf-8") as f:
            for row in rows:
                f.write("\t".join(str(v) for v in row) + "\n")
        print(f"done, {len(rows)} rows returned, see run_sql_result.txt")
    else:
        print("done")


if __name__ == "__main__":
    main(sys.argv[1])
