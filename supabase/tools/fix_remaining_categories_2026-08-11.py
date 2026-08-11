# -*- coding: utf-8 -*-
"""2026-08-11: 촘촘해진 자동검사로 남은 카테고리(headcount/admission_score_condition/
language_test_type/max_income_bracket/disability/foreigner_eligibility/age/degree_level/
excluded_major/region/period_or_deadline/gender)를 전부 확인해서, 실제로 채울 수 있는 것만
반영. 대부분(특히 language_test_type 11건 전부, degree_level 5건 전부)은 이미 알려진
구조적 한계(여러 시험종류/학위과정이 OR로 묶여서 단일값 필드로 표현 불가, 우선순위/가산점일
뿐 필수조건 아님, 상대순위라 절대 커트라인 없음 등)라 채우지 않음 — 아래 FIXES가 전부.

버그 수정 포함: id=266/309는 "부모님 장애" 조건인데 required_special_status에
"disabled_parent"(SpecialStatus 열거형에 없는 값 — DisabilityType 전용 값이 잘못 들어감)가
박혀있어서 절대 매칭 안 되던 상태 — requires_disability/required_disability_type으로 옮김.
(단, disabled_parent를 실제로 선택하려면 프론트 "본인 장애" 토글을 먼저 켜야 하는 별도 UI
버그가 이미 matching_gaps.md에 기록돼 있음 — 그건 이번에 안 건드림, 데이터는 최소한 맞게
고쳐둠.)

max_income_bracket 3건은 이미 만들어둔 "중위소득 N% → 학자금지원구간" 변환표
(matching_gaps_resolved.md, 1구간≤30%/2≤50%/3≤70%/4≤90%/5≤100%/6≤130%/7≤150%/8≤200%/
9≤300%) 그대로 적용: 150%→7구간, 100%→5구간.

사용법:
    python fix_remaining_categories_2026-08-11.py           # dry-run만
    python fix_remaining_categories_2026-08-11.py --apply    # 실제 반영
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


FIXES: list[dict] = [
    # headcount
    {"id": 322, "headcount": "1명"},
    {"id": 670, "headcount": "약 30명"},
    # admission_score_condition
    {"id": 662, "admission_score_condition": "수능 4개 영역(국어·수학·영어·탐구) 중 3개 영역 이상 4등급 이내 또는 고교 내신 이수과목 1/2 이상 4등급 이내(탐구 2과목 평균)"},
    {"id": 1088, "admission_score_condition": "신입생 고3 12학기 평균90점 이상 또는 수능 백분위 평균90점 이상"},
    {"id": 1089, "admission_score_condition": "신입생 고3 12학기 평균80점 이상 또는 수능 백분위80점 이상"},
    {"id": 1091, "admission_score_condition": "신입생 고3 평균80점 이상 또는 수능 백분위80점 이상"},
    {"id": 1093, "admission_score_condition": "신입생 고3 평균80점 이상 또는 수능 백분위80점 이상"},
    {"id": 1110, "admission_score_condition": "『3+1체제』 수능 성적 전국 평균등급 1.5등급 이내"},
    {"id": 1119, "admission_score_condition": "신입생 수능 백분위50점 이상 또는 내신5등급 이내"},
    {"id": 1138, "admission_score_condition": "전년도 수능 성적(국·영·수·탐구 평균) 평균1.5등급 이내"},
    # max_income_bracket (중위소득% -> 학자금지원구간 변환표 적용)
    {"id": 527, "max_income_bracket": 7},
    {"id": 528, "max_income_bracket": 7},
    {"id": 669, "max_income_bracket": 5},
    # disability
    {"id": 225, "requires_disability": True, "required_disability_type": None},
    {"id": 266, "requires_disability": True, "required_disability_type": "disabled_parent",
     "required_special_status": ["multi_child_family", "severe_illness_or_injury", "job_loss_or_disaster", "financial_emergency", "multicultural_family"]},
    {"id": 309, "requires_disability": True, "required_disability_type": "disabled_parent",
     "required_special_status": []},
    {"id": 1058, "requires_disability": True, "required_disability_type": "disabled_parent",
     "required_special_status": ["multicultural_family"]},
    # foreigner_eligibility
    {"id": 669, "foreigner_eligibility": "korean_only"},
    # age
    {"id": 645, "max_age": 24},
    {"id": 656, "max_age": 34},
    {"id": 658, "min_age": 35},
    {"id": 664, "min_age": 19, "max_age": 34},
    {"id": 973, "max_age": 34},
    # excluded_major
    {"id": 78, "excluded_major": "기록학과"},
    # period_or_deadline (application_period, 자유텍스트라 확정 마감일은 아님)
    {"id": 80, "application_period": "2027년 1월학기 정식모집 / 4월학기 사전신청(정확한 마감일은 홈페이지 참고)"},
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
    before_rows = {}
    for r in cur.fetchall():
        before_rows.setdefault(r[0], []).append(r)
    before_cols = ["id", "name"] + all_cols

    report_lines = []
    for i, fix in enumerate(FIXES):
        sql, params = build_update(fix)
        cur.execute(sql, params)
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        f"SELECT id, name, {', '.join(all_cols)} FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {}
    for r in cur.fetchall():
        after_rows.setdefault(r[0], []).append(r)

    lines_by_id: dict[int, list[str]] = {}
    order: list[int] = []
    for fix in FIXES:
        fid = fix["id"]
        before_list = before_rows.get(fid)
        after_list = after_rows.get(fid)
        if not before_list or not after_list:
            continue
        before = before_list[0]
        after = after_list[0]
        if fid not in lines_by_id:
            lines_by_id[fid] = [f"\n## id={fid} {before[1]}"]
            order.append(fid)
        for col in [c for c in fix if c != "id"]:
            cidx = before_cols.index(col)
            lines_by_id[fid].append(f"  {col}: {before[cidx]!r} -> {after[cidx]!r}")
    for fid in order:
        report_lines.extend(lines_by_id[fid])

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_remaining_categories_2026-08-11_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
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
