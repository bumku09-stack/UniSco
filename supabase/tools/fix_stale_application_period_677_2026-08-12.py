"""2026-08-12: id=677(현대차 정몽구재단 '미래산업 인재 학부 장학생')의 application_period가
"2025년 기준"에 멈춰 있던 걸 실사용자가 실제 서비스 화면에서 발견해서 신고함.

같은 재단의 형제 장학금(id=678, 대학원 버전)은 이미 "2026년 기준"으로 갱신돼 있었는데
학부 버전만 방치돼 있었음 — application_url(https://www.cmkfoundation-scholarship.org/
FutureCollegeApply, 재단 공식 신청 페이지)을 직접 확인해서 2026년도 실제 접수기간
(2026-03-25 11시 ~ 2026-04-15 15시, 페이지에 "2026년 선발공고"로 명시)을 검증함 —
id=678에 이미 기록돼 있던 값과 정확히 일치해서 교차 확인됨(두 트랙이 같은 시기에
동시 접수).

application_deadline은 그대로 NULL 유지 — 매년 반복되는 프로그램이라 다음(2027년) 회차의
확정 날짜를 아직 모르므로, deadline_matches()가 안 거르는 게 맞음(구조화된 필드를 채워서
"마감된 장학금"으로 자동 숨기면 학생이 이 프로그램의 존재 자체를 다음 해 미리 계획할 수
없게 됨).

이 스크립트는 이미 적용된 변경을 기록/재현하기 위한 것 — 이미 반영됐으면 자동으로 스킵함.

사용법:
    python fix_stale_application_period_677_2026-08-12.py           # dry-run만
    python fix_stale_application_period_677_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

SCHOLARSHIP_ID = 677
NEW_APPLICATION_PERIOD = (
    "매년 3~4월경 모집(2026년 기준: 2026-03-25 ~ 2026-04-15, 마감됨 — 재단 공식 페이지 확인, "
    "2027년 공고는 매년 패턴대로 3~4월경 예상)"
)


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

    cur.execute(
        "SELECT id, name, application_period FROM scholarship WHERE id = %s", (SCHOLARSHIP_ID,)
    )
    before = cur.fetchone()
    if before is None:
        print(f"경고: id={SCHOLARSHIP_ID}를 DB에서 못 찾음")
        cur.close()
        conn.close()
        return

    if before[2] == NEW_APPLICATION_PERIOD:
        print("이미 반영된 값과 동일함 — 처리할 것 없음.")
        conn.rollback()
        cur.close()
        conn.close()
        return

    cur.execute(
        "UPDATE scholarship SET application_period = %s WHERE id = %s",
        (NEW_APPLICATION_PERIOD, SCHOLARSHIP_ID),
    )

    cur.execute(
        "SELECT id, name, application_period FROM scholarship WHERE id = %s", (SCHOLARSHIP_ID,)
    )
    after = cur.fetchone()

    print(f"id={before[0]} {before[1]}")
    print(f"  전: {before[2]!r}")
    print(f"  후: {after[2]!r}")

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
