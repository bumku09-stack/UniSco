"""2026-08-15: harness/reverify.py(신설, 인용 강제 재검증)를 충남대학교 전체(78건)에 대해
처음 실제로 돌린 결과 — id=46(CNU복지 장학금) 하나만의 문제가 아니라, plus.cnu.ac.kr
통합 안내표를 쓰는 배치 전체(id=7~71 대부분)와 일부 학과별 공지(88,89,90,92,96 등)까지
application_period/application_method가 원문에 전혀 근거 없이 채워져 있었음이 드러남 —
72건, 137개 필드.

이 목록은 harness/reverify.py가 각 출처 페이지 원문을 실제로 다시 읽고, 지정된 값의 근거
문장을 찾아 원문과 대조(quote_exists_in_source)한 결과 "근거 문장 자체를 찾을 수 없음"으로
판정된 것만 담음 — 형제 레코드 패턴이 비슷해 보인다고 사람이 넘겨짚은 게 아니라 매 건
기계적으로 확인됨(전체 리뷰는 supabase/reverify_review_충남대학교_2026-08-15.md 참고).

값을 추측해서 채우지 않고(data_collection_guide.md 절대규칙 4번) 정직하게 NULL로 비움 —
실제 신청기간/방식은 별도 재조사 필요.

별도 "값이 다름"(원문 근거는 있으나 현재 값과 표현이 다른) 13건은 이 스크립트에 안 넣음 —
그중 일부(id=11/12/13)는 오히려 현재 DB 값이 fresh 추출값보다 더 정확해서 자동으로 덮어쓰면
안 되는 경우라 사람이 개별 판단 필요.

사용법:
    python fix_reverify_cnu_no_evidence_2026-08-15.py           # dry-run만
    python fix_reverify_cnu_no_evidence_2026-08-15.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

# id -> 지울 필드 목록 ("both" 아니면 period만 걸린 7건)
BOTH_FIELDS_IDS = [
    7, 8, 9, 10, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,
    68, 69, 70, 71, 78, 88, 89, 90, 92, 96,
]
PERIOD_ONLY_IDS = [11, 12, 13, 15, 16, 643, 645]


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

    all_ids = sorted(set(BOTH_FIELDS_IDS) | set(PERIOD_ONLY_IDS))
    cur.execute(
        "SELECT id, name, application_period, application_method FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (all_ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}
    missing = [i for i in all_ids if i not in before_rows]
    if missing:
        print(f"경고: DB에 없는 id {missing} — 스킵")

    changed = 0
    for sid in BOTH_FIELDS_IDS:
        if sid not in before_rows:
            continue
        cur.execute(
            "UPDATE scholarship SET application_period = NULL, application_method = NULL "
            "WHERE id = %s",
            (sid,),
        )
        changed += 1
    for sid in PERIOD_ONLY_IDS:
        if sid not in before_rows:
            continue
        cur.execute("UPDATE scholarship SET application_period = NULL WHERE id = %s", (sid,))
        changed += 1

    cur.execute(
        "SELECT id, name, application_period, application_method FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (all_ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for sid in all_ids:
        if sid not in before_rows:
            continue
        before, after = before_rows[sid], after_rows[sid]
        if before == after:
            continue
        print(f"id={sid} {before[1]}")
        print(f"  전: period={before[2]!r}, method={before[3]!r}")
        print(f"  후: period={after[2]!r}, method={after[3]!r}")

    print(f"\n총 {len(all_ids)}건 대상, {changed}건 변경.")

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
