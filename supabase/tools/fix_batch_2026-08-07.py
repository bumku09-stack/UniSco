# -*- coding: utf-8 -*-
"""2026-08-07 전수 재검증(12개 병렬 에이전트, 662건 감사)에서 발견된 문제 중 "확신도 높음 +
기존 컬럼에 값만 채우면 되는 것"만 모은 1단계 수정 스크립트. matching_gaps.md 7번 사고
(전공 조건 미반영) 재발 방지 작업의 일부.

대상 기준: 원래 있던 컬럼인데 description에 명시된 값이 안 채워졌거나(NULL) 명백히 잘못
채워진 경우만 포함. 새 필드/새 로직이 필요한 것(전공 "제외" 조건, 해외대학 재학, AND 조건
미지원 등)은 여기 안 들어있음 — 2단계로 별도 처리.

사용법:
    python fix_batch_2026-08-07.py           # dry-run만 (트랜잭션 롤백, before/after 리포트)
    python fix_batch_2026-08-07.py --apply    # 실제 반영(커밋)
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


# 각 dict: "id" + 고칠 컬럼들. None이면 NULL로 비움.
FIXES: list[dict] = [
    # --- 청크 A ---
    {"id": 21, "min_gpa_basis": "cumulative"},
    {"id": 22, "min_gpa_basis": "cumulative"},
    {"id": 14, "major": None,
     "admission_score_condition": "인문계: 국어·영어 3등급 이내 / 자연계: 수학·영어 3등급 이내"},
    # --- 청크 B ---
    {"id": 59, "required_special_status": ["student_council_officer"]},
    {"id": 74, "required_special_status": ["parent_occupation_condition"]},
    {"id": 77, "required_enrollment_status": None},
    {"id": 94, "required_special_status": ["religious_or_career_intent_condition"]},
    {"id": 95, "major": "인문사회계열"},
    {"id": 110, "required_special_status": ["student_council_officer"]},
    {"id": 111, "required_special_status": ["student_council_officer"]},
    {"id": 112, "required_special_status": ["student_council_officer"]},
    # --- 청크 C ---
    {"id": 114, "required_enrollment_status": None},
    {"id": 122, "required_enrollment_status": None},
    {"id": 123, "required_enrollment_status": None},
    {"id": 151, "language_test_type": "TOPIK", "language_test_min_score": 3, "min_gpa": 3.0},
    {"id": 152, "language_test_type": "IELTS", "language_test_min_score": 6.0, "min_gpa": 3.0},
    # --- 청크 D ---
    {"id": 217, "headcount": "3명"},
    {"id": 218, "headcount": "6명"},
    # --- 청크 E ---
    {"id": 226, "min_grade": 3, "max_grade": 4},
    {"id": 228, "min_grade": 1, "max_grade": 1, "headcount": "1명"},
    {"id": 231, "headcount": "1명"},
    {"id": 232, "headcount": "1명"},
    {"id": 234, "min_grade": None, "max_grade": None},
    {"id": 238, "min_grade": 1, "max_grade": 1},
    {"id": 239, "min_grade": 1, "max_grade": 1},
    {"id": 254, "application_deadline": "2026-04-12"},
    # --- 청크 F ---
    {"id": 294, "headcount": "70명 이내", "admission_score_condition": None},
    {"id": 297, "application_deadline": "2026-08-19"},
    {"id": 316, "min_grade": 3, "max_grade": 6},
    # --- 청크 G ---
    {"id": 641, "required_degree_level": None, "required_enrollment_status": "post_undergrad"},
    {"id": 642, "required_degree_level": None, "required_enrollment_status": "post_undergrad"},
    {"id": 644, "required_degree_level": None, "required_enrollment_status": "post_undergrad",
     "application_url": "https://www.asanfoundation.or.kr"},
    {"id": 646, "required_degree_level": None, "required_enrollment_status": "post_undergrad"},
    {"id": 358, "major": "신학"},
    {"id": 532, "max_age": 29},
    # --- 청크 H ---
    {"id": 651, "major": "물리학과,화학과,생물학과,수학과,의예과"},
    {"id": 653, "required_special_status": ["national_merit"]},
    {"id": 654, "required_special_status": ["national_merit"]},
    {"id": 672, "foreigner_eligibility": "foreigner_only"},
    {"id": 683, "eligible_region": "양양군,인제군"},
    # --- 청크 I ---
    {"id": 942, "min_credits": "12학점"},
    {"id": 945, "application_deadline": "2026-04-09"},
    {"id": 947, "application_deadline": "2026-04-09"},
    {"id": 954, "application_deadline": "2026-04-03"},
    {"id": 956, "application_deadline": "2026-04-03"},
    {"id": 957, "application_deadline": "2026-04-03"},
    {"id": 958, "application_deadline": "2026-04-03"},
    {"id": 955, "admission_score_condition": "수능 4개영역 백분위 평균 80점 이상 또는 내신 3개학기 평균 80점 이상",
     "application_deadline": "2026-04-03"},
    {"id": 962, "min_credits": "15학점",
     "admission_score_condition": "(신입생) 수능 4개영역 중 3개영역 이상 3등급 이내 또는 고2~3-1 전과목 석차등급평균 3등급 이내"},
    {"id": 985, "admission_score_condition": "수능성적입학생(한국사+국어+수학+영어+탐구(2) 등급합 12이내)/내신성적입학생(상위10% 이내)"},
    {"id": 986, "min_credits": "12학점"},
    # --- 청크 J ---
    {"id": 1028, "major": None},
    # --- 청크 K ---
    {"id": 1067, "min_credits": "12학점"},
    {"id": 1069, "min_grade": None},
    {"id": 1072, "min_credits": "12학점"},
    {"id": 1076, "min_credits": "12학점"},
    {"id": 1082, "required_special_status": ["suneung_score_condition"]},
    {"id": 1087, "min_credits": "12학점"},
    {"id": 1089, "min_credits": "12학점"},
    {"id": 1096, "min_credits": "15학점"},
    # --- 청크 L ---
    {"id": 1105, "required_enrollment_status": None},
    {"id": 1116, "min_grade": 2},
    {"id": 1117, "min_grade": 2},
    {"id": 1140, "required_special_status": ["basic_livelihood_recipient", "near_poor", "multicultural_family"]},
]

ARRAY_COLUMNS = {"required_special_status"}


def render_set_clause(col: str, value) -> tuple[str, tuple]:
    if col in ARRAY_COLUMNS:
        return f"{col} = %s", ("{" + ",".join(value) + "}",)
    return f"{col} = %s", (value,)


def build_update(fix: dict) -> tuple[str, tuple]:
    cols = [c for c in fix if c != "id"]
    set_parts = []
    params: list = []
    for c in cols:
        clause, p = render_set_clause(c, fix[c])
        set_parts.append(clause)
        params.extend(p)
    params.append(fix["id"])
    sql = f"UPDATE scholarship SET {', '.join(set_parts)} WHERE id = %s"
    return sql, tuple(params)


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    all_cols = sorted({c for f in FIXES for c in f if c != "id"})
    cur.execute(
        f"SELECT id, name, {', '.join(all_cols)} FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}
    before_cols = ["id", "name"] + all_cols

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        sql, params = build_update(fix)
        cur.execute(sql, params)
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        f"SELECT id, name, {', '.join(all_cols)} FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        name = before[1]
        report_lines.append(f"\n## id={fid} {name}")
        for col in [c for c in fix if c != "id"]:
            idx = before_cols.index(col)
            report_lines.append(f"  {col}: {before[idx]!r} -> {after[idx]!r}")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_batch_2026-08-07_diff.md"
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(FIXES)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(FIXES)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
