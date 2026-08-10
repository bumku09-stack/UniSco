# -*- coding: utf-8 -*-
"""2026-08-10: excluded_major/required_special_status_all 신규 컬럼 반영 + matching.py
로직 수정에 맞춰 실제 데이터 채우는 스크립트.

id=257, 1134: excluded_major 채움(원래 계획대로).
id=1019: 원래 required_special_status에 섞여있던 multicultural_family를
  required_special_status_all(AND, 반드시 있어야 함)로 옮기고, required_special_status는
  소득 관련 OR 옵션(basic_livelihood_recipient, near_poor)만 남김.
id=1052: 북한이탈주민(AND, 이미 required_special_status에 있던 걸 required_special_status_all로
  옮김) + 가정형편 OR 옵션(기초수급/차상위/한부모) + 장애인등록도 OR 축에 들어가야 하는데
  disability는 별도 필드라 requires_disability=True로 채워서(유형 무관) 기존
  "장애 조건과 특수상황 조건이 둘 다 있으면 OR로 처리" 분기를 그대로 활용함.

id=1046은 이번에 안 건드림 — max_income_bracket=6이 이미 걸려있는데, 실제 원문은
"6구간 이하 또는 기초수급자·차상위·한부모·중증장애인 등록자(OR조건)"라서 income_bracket과
special_status/disability가 서로 다른 매칭 메커니즘 3개에 걸쳐 OR로 묶여야 함 — 지금 코드는
max_income_bracket을 다른 것들과 무관하게 무조건 먼저 거르는 AND 게이트라, 여기에 섣불리
special_status/disability를 추가하면 "income<=6이면 무조건 통과"였던 기존 동작을
"income<=6 이면서 (장애 또는 태그)"로 잘못 좁혀버림 — 데이터 안 건드리고 matching_gaps.md에
새 유형으로 기록만 함.

사용법:
    python fix_excluded_major_and_special_status_all_2026-08-10.py           # dry-run
    python fix_excluded_major_and_special_status_all_2026-08-10.py --apply   # 실제 반영
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
    {"id": 257, "excluded_major": "한의예과,군사학과"},
    {"id": 1134, "excluded_major": "신학과"},
    {"id": 1019, "required_special_status_all": ["multicultural_family"],
     "required_special_status": ["basic_livelihood_recipient", "near_poor"]},
    {"id": 1052, "required_special_status_all": ["north_korean_defector"],
     "required_special_status": ["basic_livelihood_recipient", "near_poor", "single_parent_family"],
     "requires_disability": True},
]

ARRAY_COLUMNS = {"required_special_status", "required_special_status_all"}


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
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_excluded_major_and_special_status_all_2026-08-10_diff.md"
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
