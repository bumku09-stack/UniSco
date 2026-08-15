"""2026-08-15: religious_or_career_intent_condition(확인 불가 랭킹 전용 태그) 21건을
전수 재검토해서, 그중 "부모가 목회자 또는 선교사"라는 명확한 자기신고 가능 사실인 8건만
새로 승격한 PARENT_CLERGY_OR_MISSIONARY로 교체 — parent_university_staff/alumni,
righteous_person_family_condition 승격과 동일한 패턴.

나머지 13건은 그대로 둠(학생 본인 상태·지망이거나 추천서·신앙에세이 같은 진짜 확인 불가
절차 요건) — 상세는 audit_reports/fix_promote_parent_clergy_2026-08-15_diff.md 참고.

8건 전부 required_special_status가 [religious_or_career_intent_condition] 단일값이라
(사전 확인 완료) 배열 전체를 새 값으로 교체해도 안전함 — 다른 태그가 섞여있는 배열이었으면
그 값만 골라 빼는 로직이 필요했을 것.

사용법:
    python fix_promote_parent_clergy_2026-08-15.py           # dry-run만
    python fix_promote_parent_clergy_2026-08-15.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

TARGET_IDS = [170, 235, 252, 324, 325, 358, 945, 1135]
OLD_TAG = "religious_or_career_intent_condition"
NEW_TAG = "parent_clergy_or_missionary"


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
        "SELECT id, name, required_special_status FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (TARGET_IDS,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = [i for i in TARGET_IDS if i not in before_rows]
    if missing:
        print(f"경고: DB에 없는 id {missing} — 스킵")

    unexpected = [
        sid for sid, row in before_rows.items() if row[2] != [OLD_TAG]
    ]
    if unexpected:
        print(f"경고: 예상과 다른 태그 조합 발견, 안전을 위해 스킵함: {unexpected}")
        for sid in unexpected:
            print(f"  id={sid}: {before_rows[sid][2]}")

    changed = 0
    for sid in TARGET_IDS:
        if sid not in before_rows or sid in unexpected:
            continue
        cur.execute(
            "UPDATE scholarship SET required_special_status = %s WHERE id = %s",
            ([NEW_TAG], sid),
        )
        changed += 1

    cur.execute(
        "SELECT id, name, required_special_status FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (TARGET_IDS,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for sid in TARGET_IDS:
        if sid not in before_rows:
            continue
        before, after = before_rows[sid], after_rows[sid]
        if before == after:
            continue
        print(f"id={sid} {before[1]}: {before[2]} -> {after[2]}")

    print(f"\n총 {len(TARGET_IDS)}건 대상, {changed}건 변경.")

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
