# -*- coding: utf-8 -*-
"""2026-08-11: 촘촘해진 자동검사로 662건을 다시 훑은 결과에서 special_status(특수상황) 의심
26건 중, "이 조건이어야만 지원 가능"(gating)인 4건만 채움.

나머지 22건은 채우지 않음 — 이유:
- 15건: "우선순위"/"가산점"/"배점" 표현 — 필수조건이 아니라 선발 시 가점 요소일 뿐이라
  required_special_status(필수/게이트 조건 칸)에 넣으면 오히려 그 조건 없는 정상 지원자를
  걸러내는 부작용이 생김 (536, 537, 668, 682, 923, 981, 989, 995, 1024, 1096, 1104, 1127,
  1138, 1004, 1007 — 뒤 두 개는 다른 프로그램 참조/연계조건이라 애초에 이 장학금 자체의
  특수상황 조건이 아님).
- 5건: 이미 max_income_bracket으로 사실상 커버됨(1, 304, 526, 663, 989) — 526·663은 특히
  "소득분위 이하 OR 특수상황"구조라 여기에 required_special_status를 추가하면 max_income_bracket
  독립 AND게이트 때문에 오히려 더 좁아짐(id=1046과 동일한 한계, matching_gaps.md에 기록).
- 1건(1085): 선발 인원의 70%/30%가 서로 다른 트랙(성적우수 vs 저소득층·다자녀)이라 하나의
  필드로 통합 표현 불가.
- 1건(1046): 이미 문서화된 기존 한계, 재작업 없음.
- 952: "제외" 방향(배제) — required_special_status는 "포함"만 표현 가능해서 아예 손 못 댐,
  matching_gaps.md에 새 유형으로 기록.

사용법:
    python fix_special_status_2026-08-11.py           # dry-run만
    python fix_special_status_2026-08-11.py --apply    # 실제 반영
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
    {"id": 116, "required_special_status": ["near_poor"]},
    {"id": 119, "required_special_status": ["basic_livelihood_recipient", "near_poor"]},
    {"id": 222, "required_special_status": ["basic_livelihood_recipient", "near_poor"]},
    {"id": 662, "required_special_status": ["basic_livelihood_recipient", "near_poor"]},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, required_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        arr = "{" + ",".join(fix["required_special_status"]) + "}"
        cur.execute(
            "UPDATE scholarship SET required_special_status = %s WHERE id = %s",
            (arr, fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, required_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
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
        report_lines.append(f"  required_special_status: {before[2]!r} -> {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_special_status_2026-08-11_diff.md"
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
