"""기존 DB(Supabase) 읽기 전용 접근 — dedup.py가 기존 (name, provider) 목록을 가져오는 데만 씀.

**쓰기 함수가 이 파일에 없는 건 의도적임.** 설계안 제약사항 "실제 운영 DB는 절대 자동화하지
않음"에 따라, 하네스는 DB에 아무것도 쓰지 않고 PR을 여는 데서 끝남 — 실제 반영은 사람이
supabase/tools/run_sql.py를 직접 실행함(기존 워크플로 그대로).
"""
from __future__ import annotations

import time
from pathlib import Path

import psycopg2

_MAX_RETRIES = 2


def load_database_url() -> str:
    """환경변수 우선(GitHub Actions Secret), 없으면 로컬 개발용으로 backend/.env를 읽음
    — supabase/tools/run_sql.py와 동일한 폴백 순서."""
    import os

    env_value = os.environ.get("DATABASE_URL")
    if env_value:
        return env_value

    env_path = Path(__file__).resolve().parents[1] / "backend" / ".env"
    if not env_path.exists():
        raise RuntimeError(
            "DATABASE_URL이 환경변수에도 없고 backend/.env에도 없음 — "
            "로컬에서는 backend/.env에 DATABASE_URL을 채우거나, CI에서는 Secret으로 등록할 것."
        )
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def fetch_existing_scholarships() -> list[tuple[str, str]]:
    """중복 판정용 (name, provider) 전체 목록. provider가 NULL이면 빈 문자열로 취급."""
    url = load_database_url()
    for attempt in range(_MAX_RETRIES + 1):
        try:
            conn = psycopg2.connect(url)
            break
        except psycopg2.OperationalError:
            # Supabase 쪽 순간적인 연결 거부/타임아웃 대비(harness/http.py의 재시도와 같은
            # 이유, 2026-08-10) — 이 단계는 LLM 추출 이전이라 실패해도 토큰 손실은 없지만,
            # 매번 나이트런을 통째로 실패시키는 것보다는 재시도가 나음.
            if attempt == _MAX_RETRIES:
                raise
            time.sleep(3 * (attempt + 1))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, COALESCE(provider, '') FROM scholarship")
            return [(name, provider) for name, provider in cur.fetchall()]
    finally:
        conn.close()
