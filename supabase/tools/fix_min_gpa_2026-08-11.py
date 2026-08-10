# -*- coding: utf-8 -*-
"""2026-08-11: 촘촘해진 자동검사(description_gap_check.py)로 662건을 다시 훑은 결과
(audit_reports/2026-08-10_tightened_scan.md)에서 min_gpa(성적기준) 의심 29건 중, 실제로
확정값을 채울 수 있는 16건(원래 15건 + id=149는 원문 재확인 후 추가)만 반영.

나머지 13건은 의도적으로 빈칸 유지(전부 이미 알려진 스키마 한계 — 등수/석차 조건, 백분위·
자체지수 기준, 향상폭 조건, GPA 구간별 차등지급이라 단일 커트라인이 없는 경우, GPA조건이
명시적으로 면제된 경우, "재외국민장학금"(id=242)은 존재 자체가 불확실해 matching_gaps.md에
별도 기록된 항목이라 이번엔 손대지 않음): 107, 173, 200, 215, 225, 234, 235, 242, 289, 298,
303, 350, 1100.

id=149(한밭대 학생활동 장학금)는 description만으로는 "평점 기준 충족 시"까지만 있어서
확정 못 했고, 원문(hanbat.ac.kr/kor/sub05_090105.do)을 직접 열어 "직전학기 평점평균 3.0
이상=전액, 2.0 이상=50%"라는 실제 기준을 확인함 — 최소 자격 기준인 2.0으로 채우고,
description도 원문 기준 그대로 보강. 같은 페이지에서 12학점 조건도 새로 확인돼서
min_credits도 같이 채움(원래 min_credits 배치 스캔에서는 description에 학점 숫자가 없어서
안 걸렸던 항목).

사용법:
    python fix_min_gpa_2026-08-11.py           # dry-run만
    python fix_min_gpa_2026-08-11.py --apply    # 실제 반영
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
    {"id": 135, "min_gpa": 3.75},
    {
        "id": 149,
        "min_gpa": 2.0,
        "min_gpa_basis": "semester",
        "min_credits": "직전학기 12학점 이상",
        "description": (
            "총학생회·학회연합회·동아리연합회·신문방송국·학군사교육단 등 학생자치단체 임원 "
            "대상. 직전학기 평점평균 3.0 이상+12학점 이상 취득 시 등록금 전액, 2.0 이상+12학점 "
            "이상 취득 시 50% 지원(학군사교육단은 직급별 30만원~150만원)."
        ),
    },
    {"id": 189, "min_gpa": 3.5},
    {"id": 190, "min_gpa": 3.5},
    {"id": 192, "min_gpa": 3.5},
    {"id": 193, "min_gpa": 3.5},
    {"id": 194, "min_gpa": 3.5},
    {"id": 195, "min_gpa": 3.5},
    {"id": 217, "min_gpa": 3.70},
    {"id": 219, "min_gpa": 3.70},
    {"id": 522, "min_gpa": 3.5},
    {"id": 660, "min_gpa": 3.0, "min_gpa_basis": "cumulative"},
    {"id": 1088, "min_gpa": 4.0, "min_gpa_basis": "semester"},
    {"id": 1089, "min_gpa": 3.0},
    {"id": 1091, "min_gpa": 3.0},
    {"id": 1093, "min_gpa": 3.0},
]

ALL_COLS = ["min_gpa", "min_gpa_basis", "min_credits", "description"]


def build_update(fix: dict) -> tuple[str, tuple]:
    cols = [c for c in fix if c != "id"]
    set_parts = [f"{c} = %s" for c in cols]
    params = [fix[c] for c in cols]
    params.append(fix["id"])
    sql = f"UPDATE scholarship SET {', '.join(set_parts)} WHERE id = %s"
    return sql, tuple(params)


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        f"SELECT id, name, {', '.join(ALL_COLS)} FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}
    before_cols = ["id", "name"] + ALL_COLS

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
        f"SELECT id, name, {', '.join(ALL_COLS)} FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        report_lines.append(f"\n## id={fid} {before[1]}")
        for col in [c for c in fix if c != "id"]:
            idx = before_cols.index(col)
            report_lines.append(f"  {col}: {before[idx]!r} -> {after[idx]!r}")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_min_gpa_2026-08-11_diff.md"
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
