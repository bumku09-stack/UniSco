# -*- coding: utf-8 -*-
"""2026-08-11: 새로 만든 excluded_special_status(특수상황 "제외" 조건, excluded_major와
동일한 컨벤션) 필드를 실제 데이터에 적용. 청년밥상(id=952, 우양재단)이 description에서
발견한 사례 — "2026년부터 자립준비청년·북한이탈주민은 지원 대상에서 제외(과거엔 우대
대상이었음)". child_care_facility="아동양육시설 생활자·퇴소자" 태그가 "자립준비청년"
(보호종료아동의 현재 공식 명칭)에 해당함.

사용법:
    python fix_excluded_special_status_2026-08-11.py           # dry-run만
    python fix_excluded_special_status_2026-08-11.py --apply    # 실제 반영
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
    {"id": 952, "excluded_special_status": ["child_care_facility", "north_korean_defector"]},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, excluded_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    report_lines = []
    for fix in FIXES:
        arr = "{" + ",".join(fix["excluded_special_status"]) + "}"
        cur.execute(
            "UPDATE scholarship SET excluded_special_status = %s WHERE id = %s",
            (arr, fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, excluded_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
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
        report_lines.append(f"  excluded_special_status: {before[2]!r} -> {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_excluded_special_status_2026-08-11_diff.md"
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
