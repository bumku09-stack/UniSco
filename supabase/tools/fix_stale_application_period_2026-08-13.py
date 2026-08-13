"""2026-08-13: handoff_2026-08-12.md 작업 A — 2026-08-12_stale_application_period.md의
"오래된 항목" 15건(id=524,533,536,537,641,642,643,644,645,646,647,648,664,668,683)을
각 기관 공식 페이지/공지사항 게시판에서 재확인한 결과 반영.

확인 결과 요약(상세 근거는 audit_reports/fix_stale_application_period_2026-08-13_diff.md 참고):
- 645(관정재단 학부), 646(관정재단 대학원), 647(인재림 6기)은 2026년 실제 일정을 확인해서
  반영(이미 마감된 회차 포함).
- 나머지 12건은 2026-08-13 확인 시점 기준 2026년 새 공고가 아직 게시되지 않아서, 직전
  확인된 회차(대부분 2025년)를 유지하되 "2026년 공고 미확인"이라는 문구로 갱신 —
  추측해서 날짜를 채우지 않음(data_collection_guide.md 절대규칙 4번).
- id=533(당진 학자금대출 이자지원)은 DB에 저장된 application_url
  (dangjin.go.kr/cop/bbs/BBSMSTR_000000000013/...)이 500 에러를 반환해서 실제로는
  열리지 않는 죽은 링크였음 — 이건 작업 A 범위가 아니라 작업 C(신청 링크 없음/오류) 대상이라
  이 스크립트에서는 손대지 않음, 별도 보고 필요.

사용법:
    python fix_stale_application_period_2026-08-13.py           # dry-run만
    python fix_stale_application_period_2026-08-13.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

FIXES: dict[int, str] = {
    524: "매년 9월경 모집(2026년 공고 미확인, 직전 회차: 2025-09-01 ~ 2025-09-26)",
    533: "매년 9월경 모집(2026년 공고 미확인, 직전 회차: 2025-09-01 ~ 2025-09-26)",
    536: (
        "매년 8월 말경 모집(2026년 공고 미확인, 직전 회차: 2025-08-25 ~ 2025-09-12, "
        "2026년 공고는 8월 하순 예상)"
    ),
    537: (
        "매년 8월경 모집(2026년 공고 미확인, 직전 회차: 2025-08-18 ~ 2025-09-11, "
        "2026년 공고는 8월경 예상)"
    ),
    641: "매년 10월경 모집(2026년 공고 미확인, 직전 회차: 2025-10-02 ~ 2025-10-27)",
    642: "매년 10월경 모집(2026년 공고 미확인, 직전 회차: 2025-10-02 ~ 2025-10-27)",
    643: "매년 10월경 모집(2026년 공고 미확인, 직전 회차: 2025-10-02 ~ 2025-10-27)",
    644: "매년 10월경 모집(2026년 공고 미확인, 직전 회차: 2025-10-02 ~ 2025-10-27)",
    645: (
        "매년 10~12월경 모집(2026년 기준: 21기 학부장학생 학교추천 마감 2025년 11월 "
        "중하순경[대학별 상이], 온라인 지원서 최종제출 마감 2025-12-31, 마감됨)"
    ),
    646: (
        "매년 10월~다음해 2~3월경 모집(2026년 기준: 신규 대학원 장학생 학과별 추천 마감 "
        "2026-01-30~2026-02-18경[학과마다 상이], 마감됨)"
    ),
    647: (
        "연 1~2회 모집(2026년 기준: 6기 2026-04-20~05-11 마감, 7기 공고 미확인 — "
        "통상 10~11월경 예상)"
    ),
    648: "매년 10~11월경 모집(2026년 공고 미확인, 직전 회차: 2025-10-01 ~ 2025-11-10)",
    664: "매년 8월경 모집(2026년 공고 미확인, 직전 회차: 2025-08-01 ~ 2025-08-29)",
    668: "매년 12월경 모집(2026년 공고 미확인, 직전 회차: 2025-12-22 ~ 2025-12-29)",
    683: "매년 9월경 모집(2026년 공고 미확인, 직전 회차: 2025-09-22 ~ 2025-10-24)",
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

    ids = list(FIXES)
    cur.execute(
        "SELECT id, name, application_period FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    already_done = [sid for sid, r in before_rows.items() if r[2] == FIXES[sid]]
    for sid in already_done:
        print(f"id={sid}: 이미 반영된 값과 동일함 — 스킵")

    for sid, new_text in FIXES.items():
        if sid in already_done:
            continue
        cur.execute(
            "UPDATE scholarship SET application_period = %s WHERE id = %s", (new_text, sid)
        )

    cur.execute(
        "SELECT id, name, application_period FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for sid in FIXES:
        before = before_rows[sid]
        after = after_rows[sid]
        print(f"id={sid} {before[1]}")
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
