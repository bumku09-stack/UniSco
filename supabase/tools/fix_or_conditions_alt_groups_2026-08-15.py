"""2026-08-15: matching_gaps.md의 두 "🟢 코드 변경 없이 데이터 작업만" 항목 반영 —
eligibility_alt_groups(2026-08-14 추가된 OR 조건 기능)로 표현 가능한데 아직 구조화 안 된
케이스들.

## A. 여러 어학시험 중 하나만 맞으면 되는 조건 (6건)
LanguageTestType이 TOEIC/TOEFL/IELTS/TOPIK 4종만 지원함(TEPS/HSK/JLPT/TOEIC Speaking은
학생이 애초에 선택할 옵션 자체가 없음) — 원문에 이 4종 밖의 시험이 같이 걸려있으면 그
갈래만 구조화 대상에서 뺌(과다매칭 방지 원칙과 무관하게, 그냥 표현 불가능한 값이라 뺌).
빠진 갈래가 있다고 기존보다 더 나빠지는 건 아님 — 지금까지 이 6건은 language_test_type
자체가 전부 NULL이라(무필터, 전원 노출) 구조화된 갈래만이라도 실제로 걸러지기 시작하는
쪽이 순수 개선임.

- id=52: TOEIC 900 또는 TOEFL 102
- id=31: TOPIK 5급 또는 TOEFL 95 또는 IELTS 6.5 또는 TOEIC 800 (TEPS 386 갈래는 미지원이라 제외)
- id=32: TOPIK 4급 또는 TOEFL 71 또는 IELTS 5.5 또는 TOEIC 700 (TEPS 327 갈래 제외)
- id=343: TOEFL 90 또는 TOEIC 850 (TOEIC Speaking 중상급 갈래는 질적 등급이라 표현 불가, 제외)
- id=197: TOEIC 900 또는 TOEFL 100
- id=317: TOEIC 950 또는 TOEFL 110 (TEPS 500/HSK 6급/JLPT 1급 갈래는 전부 미지원 시험이라 제외)

## B. 학위과정이 "석사 또는 박사" 둘 다 대상인데 단일값이라 한쪽이 배제되던 조건 (7건)
- id=79: 현재 doctoral 단독 → 원문("석박사통합과정도 준함")대로 doctoral 또는 integrated_ms_phd
- id=649,653,671,672,673,674: 현재 masters 단독인데 원문은 "석·박사과정"(석박사통합 언급
  없음, 그래서 masters/doctoral 2종만 — integrated_ms_phd는 원문에 없는 값이라 추가 안 함)

## C. 곁다리로 발견한 진짜 다른 버그 1건 (id=678) — alt_groups 아니라 그냥 단일필드 수정
원문 "석/박사/석박사통합과정" = 3종 전부 대상인데 required_degree_level=masters로
좁혀놓아서 박사/석박사통합 학생이 부당하게 걸러지고 있었음. 3종 전부면 그냥 "제한
없음"(NULL)이 정확한 표현이라 alt_groups 안 씀. required_enrollment_status도 이 레코드는
None(대학원 한정 안 걸림)인데 이건 이번 스코프(학위과정 OR) 밖이라 안 건드림 — 별도 항목.

사용법:
    python fix_or_conditions_alt_groups_2026-08-15.py           # dry-run만
    python fix_or_conditions_alt_groups_2026-08-15.py --apply    # 실제 반영
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2

# ── A. 어학시험 OR ──────────────────────────────────────────────────────
LANGUAGE_ALT_GROUPS: dict[int, list[dict]] = {
    52: [
        {"language_test_type": "TOEIC", "language_test_min_score": 900},
        {"language_test_type": "TOEFL", "language_test_min_score": 102},
    ],
    31: [
        {"language_test_type": "TOPIK", "language_test_min_score": 5},
        {"language_test_type": "TOEFL", "language_test_min_score": 95},
        {"language_test_type": "IELTS", "language_test_min_score": 6.5},
        {"language_test_type": "TOEIC", "language_test_min_score": 800},
    ],
    32: [
        {"language_test_type": "TOPIK", "language_test_min_score": 4},
        {"language_test_type": "TOEFL", "language_test_min_score": 71},
        {"language_test_type": "IELTS", "language_test_min_score": 5.5},
        {"language_test_type": "TOEIC", "language_test_min_score": 700},
    ],
    343: [
        {"language_test_type": "TOEFL", "language_test_min_score": 90},
        {"language_test_type": "TOEIC", "language_test_min_score": 850},
    ],
    197: [
        {"language_test_type": "TOEIC", "language_test_min_score": 900},
        {"language_test_type": "TOEFL", "language_test_min_score": 100},
    ],
    317: [
        {"language_test_type": "TOEIC", "language_test_min_score": 950},
        {"language_test_type": "TOEFL", "language_test_min_score": 110},
    ],
}

# ── B. 학위과정 OR ──────────────────────────────────────────────────────
DEGREE_ALT_GROUPS: dict[int, list[dict]] = {
    79: [{"required_degree_level": "doctoral"}, {"required_degree_level": "integrated_ms_phd"}],
    649: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
    653: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
    671: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
    672: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
    673: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
    674: [{"required_degree_level": "masters"}, {"required_degree_level": "doctoral"}],
}

# ── C. 곁다리 단일필드 수정 ─────────────────────────────────────────────
DIRECT_DEGREE_LEVEL_NULL = [678]  # 3종 전부 대상 → "제한 없음"이 정확한 값


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

    all_ids = sorted(
        set(LANGUAGE_ALT_GROUPS) | set(DEGREE_ALT_GROUPS) | set(DIRECT_DEGREE_LEVEL_NULL)
    )
    cur.execute(
        "SELECT id, name, language_test_type, language_test_min_score, "
        "required_degree_level, eligibility_alt_groups FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (all_ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = [i for i in all_ids if i not in before_rows]
    if missing:
        print(f"경고: DB에 없는 id {missing} — 스킵")

    changed = 0
    for sid in all_ids:
        if sid not in before_rows:
            continue
        if sid in LANGUAGE_ALT_GROUPS:
            cur.execute(
                "UPDATE scholarship SET eligibility_alt_groups = %s, "
                "language_test_type = NULL, language_test_min_score = NULL WHERE id = %s",
                (json.dumps(LANGUAGE_ALT_GROUPS[sid], ensure_ascii=False), sid),
            )
            changed += 1
        elif sid in DEGREE_ALT_GROUPS:
            cur.execute(
                "UPDATE scholarship SET eligibility_alt_groups = %s, "
                "required_degree_level = NULL WHERE id = %s",
                (json.dumps(DEGREE_ALT_GROUPS[sid], ensure_ascii=False), sid),
            )
            changed += 1
        elif sid in DIRECT_DEGREE_LEVEL_NULL:
            cur.execute(
                "UPDATE scholarship SET required_degree_level = NULL WHERE id = %s", (sid,)
            )
            changed += 1

    cur.execute(
        "SELECT id, name, language_test_type, language_test_min_score, "
        "required_degree_level, eligibility_alt_groups FROM scholarship "
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
        print(
            f"  전: language_test={before[2]}/{before[3]}, "
            f"degree_level={before[4]}, alt_groups={before[5]}"
        )
        print(
            f"  후: language_test={after[2]}/{after[3]}, "
            f"degree_level={after[4]}, alt_groups={after[5]}"
        )

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
