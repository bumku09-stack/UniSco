# -*- coding: utf-8 -*-
"""2026-08-11: 촘촘해진 자동검사로 662건을 다시 훑은 결과(2026-08-10_tightened_scan.md)에서
amount(지급금액) 의심 28건 중, 하나의 숫자로 정직하게 표현 가능한 9건만 채움.

적용한 기준:
- 범위(예: "50~100만원")면 낮은 쪽 숫자로 채움 — 실제보다 커 보이는 것보다 작아 보이는 게 안전.
- "등록금 전액 + 부수적 소액"(도서비/학업장려금 등) 구조는 안 채움 — 부수적 소액만 넣으면
  핵심 혜택(등록금 전액)이 빠져서 실제보다 훨씬 작은 장학금처럼 오해될 위험이 있음.
- 대상자별로 서로 다른 트랙(트랙마다 금액이 다름)이 하나의 레코드에 통합 기재된 경우도 안 채움
  — 하나만 고르면 다른 트랙 대상자가 헷갈림.

빈칸 유지 19건: 1, 5, 6, 10, 73, 144, 149, 193, 194, 217, 219, 243, 250, 304, 305, 312, 313,
534, 672 — 전부 위 두 가지 구조적 이유 중 하나.

사용법:
    python fix_amount_2026-08-11.py           # dry-run만
    python fix_amount_2026-08-11.py --apply    # 실제 반영
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
    {"id": 125, "amount": 500000},    # 김인섭장학금: "50~100만원" 범위 하한
    {"id": 182, "amount": 700000},    # 목원곰두리장학금: A급100/B급70만원 중 하한
    {"id": 253, "amount": 10000000},  # 인천 청년 해외배낭연수: "팀당 최대 1,000만원"
    {"id": 270, "amount": 300000},    # 열정장학금(대전대): 중증100/경증30만원 중 하한
    {"id": 314, "amount": 1000000},   # 을지한마음봉사장학금: 150만원/100만원 중 하한
    {"id": 321, "amount": 450000},    # 마일리지장학금(을지대): "최대 45만원"
    {"id": 364, "amount": 200000},    # BTS장학금(침례신학대): "20~100만원" 범위 하한
    {"id": 652, "amount": 5000000},   # 제대군인대부지원: "학기당500만원 한도"
    {"id": 685, "amount": 1000000},   # 강원랜드 SOS 장학: "100~300만원" 범위 하한
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, amount FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        cur.execute(
            "UPDATE scholarship SET amount = %s WHERE id = %s",
            (fix["amount"], fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, amount FROM scholarship WHERE id = ANY(%s) ORDER BY id",
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
        report_lines.append(f"  amount: {before[2]!r} -> {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_amount_2026-08-11_diff.md"
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
