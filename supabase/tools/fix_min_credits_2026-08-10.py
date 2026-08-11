# -*- coding: utf-8 -*-
"""2026-08-10: 새로 촘촘하게 만든 description_gap_check.py의 min_credits 규칙으로 662건 전체를
다시 스캔했더니(audit_reports/2026-08-10_tightened_scan.md) 38건이 걸림 — "종류별로 하나씩
순서대로" 처리하기로 한 방침(matching_gaps.md 3단계 재검증)의 첫 배치, 걸린 항목 중 건수가
가장 많은 min_credits(이수학점)부터 시작.

38건 전부 원문 재대조(application_url 재방문) 없이도 처리 가능 — description에 이미 정확한
학점 숫자가 문장으로 적혀 있는데 min_credits 칸만 비어있던 경우였음(38건 전부 실제 조건 확인,
오탐 0건). 여러 조건이 섞인 경우(예: 신입생/재학생 조건이 다르거나, 트랙이 여러 개인 경우)는
그 뉘앙스를 텍스트 그대로 담음(min_credits가 자유텍스트 필드라 가능).

사용법:
    python fix_min_credits_2026-08-10.py           # dry-run만
    python fix_min_credits_2026-08-10.py --apply    # 실제 반영
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
    {"id": 135, "min_credits": "직전학기 12학점 이상(2학기차 이상 유지 조건)"},
    {"id": 257, "min_credits": "매학기 직전학기 15학점 이상"},
    {"id": 259, "min_credits": "직전학기 15학점 이상"},
    {"id": 261, "min_credits": "직전학기 15학점 이상"},
    {"id": 262, "min_credits": "직전학기 15학점 이상"},
    {"id": 521, "min_credits": "직전학기 12학점 이상"},
    {"id": 651, "min_credits": "1학년 24학점 이상 이수(과거 실적) + 해당학기 12학점 이상 신청"},
    {"id": 667, "min_credits": "직전학기 12학점 이상"},
    {"id": 679, "min_credits": "해당학기 12학점 이상"},
    {"id": 680, "min_credits": "해당학기 12학점 이상"},
    {"id": 683, "min_credits": "12학점 이상"},
    {"id": 684, "min_credits": "나눔장학 트랙: 12학점 이상(키움장학 트랙은 학점 조건 없음)"},
    {"id": 973, "min_credits": "직전 2개학기 학기당 12학점 이상"},
    {"id": 977, "min_credits": "직전 2개학기 학기당 12학점 이상"},
    {"id": 990, "min_credits": "매학기 12학점 이상"},
    {"id": 996, "min_credits": "재학생: 학기별 12학점 이상(신입생은 학점 조건 없음)"},
    {"id": 1000, "min_credits": "직전 2학기 24학점 이상"},
    {"id": 1005, "min_credits": "직전 2학기 24학점 이상"},
    {"id": 1008, "min_credits": "직전학기 12학점 이상"},
    {"id": 1010, "min_credits": "직전학기 12학점 이상"},
    {"id": 1027, "min_credits": "직전학기 12학점 이상"},
    {"id": 1028, "min_credits": "직전학기 12학점 이상"},
    {"id": 1030, "min_credits": "직전학기 12학점 이상"},
    {"id": 1032, "min_credits": "직전학기 12학점 이상"},
    {"id": 1034, "min_credits": "직전학기 12학점 이상"},
    {"id": 1035, "min_credits": "직전학기 12학점 이상"},
    {"id": 1042, "min_credits": "12학점 이상(신입생·편입생·재입학생 첫학기는 성적기준과 함께 면제)"},
    {"id": 1100, "min_credits": "12학점 이상(P/NP 제외 평점산정과목 9학점 이상)"},
    {"id": 1101, "min_credits": "직전학기 12학점 이상"},
    {"id": 1116, "min_credits": "연 30학점 이상(계절학기 제외)"},
    {"id": 1125, "min_credits": "재학생: 12학점 이상(신입생은 학점 조건 없음)"},
    {"id": 1126, "min_credits": "재학생: 직전학기 12학점 이상(신입생·편입생·재입학생·장애인학생 면제)"},
    {"id": 1128, "min_credits": "직전학기 12학점 이상"},
    {"id": 1130, "min_credits": "직전학기 12학점 이상"},
    {"id": 1131, "min_credits": "직전학기 12학점 이상"},
    {"id": 1139, "min_credits": "직전학기 12학점 이상"},
    {"id": 1140, "min_credits": "직전학기 12학점 이상"},
    {"id": 1141, "min_credits": "직전학기 12학점 이상"},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, min_credits FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        cur.execute(
            "UPDATE scholarship SET min_credits = %s WHERE id = %s",
            (fix["min_credits"], fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, min_credits FROM scholarship WHERE id = ANY(%s) ORDER BY id",
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
        report_lines.append(f"  min_credits: {before[2]!r} -> {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_min_credits_2026-08-10_diff.md"
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
