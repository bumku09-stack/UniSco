"""2026-08-12: audit_stale_application_period.py가 잡은 17건 중, 실제로 각 기관 공식
페이지를 열어서 2026년도 새 정보를 확인할 수 있었던 2건만 반영. 나머지 15건은 페이지
구조상(공지사항 게시판 안에 있어서 목록만 있고 상세 글은 별도 탐색 필요, 또는 아직
공고 자체가 안 올라옴) 자동 조회로는 확정 정보를 못 찾아서 그대로 둠 — 추측해서 채우지
않음(data_collection_guide.md 절대규칙 4번).

- id=522 성취장학금(대전청년내일재단): 정확한 접수기간은 아직 미공지, "2026년 9월 선발일정
  공지 예정"이라는 재단 공식 문구만 확인됨 — 그 사실 그대로 반영.
- id=650 동교인재 장학생(수림재단): "제13회 동교인재상" 공고 2026-09-01, 접수 10월 예정,
  선발 11월, 시상 12월이라는 재단 공식 일정표 확인 — 정확한 접수 시작/종료일은 아직 없어서
  월 단위로만 반영.

나머지 15건(id=524,533,536,537,641,642,643,644,646,647,648,664,668,683)은 이번에
확인 안 함 — 자동 조회로 확정 정보를 못 찾았고, 하네스처럼 게시판을 여러 단계로 탐색하는
도구가 아니면 정확한 재확인이 어려움. audit_stale_application_period.py를 다시 돌려서
계속 추적할 것.

사용법:
    python fix_stale_application_period_batch_2026-08-12.py           # dry-run만
    python fix_stale_application_period_batch_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

FIXES: dict[int, str] = {
    522: (
        "매년 9월경 모집(2026년 기준: 정확한 접수기간 미공지, 재단이 2026-09 선발일정 "
        "공지 예정이라고 밝힘 — 2026-08-12 재단 공식페이지 확인)"
    ),
    650: (
        "매년 9~10월경 모집(2026년 기준: 공고 2026-09-01, 접수 2026-10 예정, 선발 2026-11 "
        "예정, 시상 2026-12 예정 — 2026-08-12 재단 공식페이지 확인, 정확한 접수 시작/종료일은 "
        "9월 공고 후 재확인 필요)"
    ),
}


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

    ids = list(FIXES)
    cur.execute(
        "SELECT id, name, application_period FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    already_done = [sid for sid, (r) in before_rows.items() if r[2] == FIXES[sid]]
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
