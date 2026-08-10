# -*- coding: utf-8 -*-
"""2026-08-10: description 내부메모 정리(fix_description_notes_2026-08-10.py) 작업 중,
같은 47건을 description_gap_check.py의 find_gaps()로 돌려봤더니 24건에서 구조화 필드 공백이
걸림. 대부분은 이미 알려진 스키마 한계(시험 종류 여러 개라 단일 필드로 OR 표현 불가, GPA
등급별 차등 지급이라 "합격 커트라인" 개념이 아님 등)라 억지로 채우지 않았고, 원문에 값이
명확히 있는데 진짜로 빈칸이었던 9건만 이 스크립트로 채움.

사용법:
    python fix_structured_gaps_2026-08-10.py           # dry-run만
    python fix_structured_gaps_2026-08-10.py --apply    # 실제 반영
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
    {"id": 166, "language_test_type": "TOEIC", "language_test_min_score": 900},
    {"id": 232, "required_special_status": ["basic_livelihood_recipient", "near_poor"]},
    {"id": 244, "headcount": "최우수상 3명 이내, 우수상 6명 이내"},
    {"id": 245, "headcount": "대상 4명 이내, 최우수상 4명 이내"},
    {"id": 251, "headcount": "대상 1명 이내, 금상 2명 이내"},
    {"id": 253, "application_period": "매년 재공고되는 사업(정확한 신청 기간은 그 해 공고문에서 확인 가능)"},
    {"id": 266, "required_special_status": [
        "multi_child_family", "severe_illness_or_injury", "job_loss_or_disaster",
        "financial_emergency", "multicultural_family", "disabled_parent",
    ]},
    {"id": 302, "min_gpa": 2.0, "min_credits": "12학점"},
    {"id": 309, "required_special_status": ["disabled_parent"]},
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
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_structured_gaps_2026-08-10_diff.md"
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
