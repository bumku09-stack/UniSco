# -*- coding: utf-8 -*-
"""2026-08-12: 실사용자 UX 리서치에서 발견된 매칭 버그 — 국어국문학과 학생 스펙으로 확인했더니
"체육특기자 전형 입학생 대상" 장학금이 노출됨. 원인은 major=None, required_special_status=[]라
구조화된 필터 조건이 전혀 없어서(설명 텍스트에만 "체육특기자 전형 입학생 대상"이라고 적혀
있고, 그걸 매칭 엔진이 읽는 필드로는 옮겨 담지 않았음) — 사실상 전교생에게 노출되던 상태.

DB 전체에서 "특기자"/"특기" 관련 장학금 27건을 전수 조사한 결과, 크게 두 부류로 나뉨:
  (a) "OO특기자 전형 입학생 대상" — 입학 전형 자체가 체육특기자 전형이라 사실상 스포츠 관련
      학과 재학생만 해당(이번에 고치는 8건, 아래 FIXES).
  (b) "최근 1년 이내 전국 규모 대회 3위 이내 입상" 같은 실적/수상 기반 장학금 — 전공과 무관하게
      아무 학과 학생이나 대회 입상 경력만 있으면 지원 가능(예: id=997/998 횡성 인재육성장학금,
      id=529/531 세종 특기적성장학생, id=670 다문화장학재단 등 19건). 이런 건 major를 채우면
      오히려 잘못된 과소매칭이 되므로 그대로 major=None 유지 — 손대지 않음.

major 필드는 major_matches()(backend/app/core/matching.py)에서 `spec.department`와 정확히
문자열 일치하는지 콤마 단위로 비교되므로(과다매칭이 과소매칭보다 낫다는 원칙 하에), 각 대학의
실제 학과명(frontend/src/lib/universities.ts 기준)을 콤마로 나열. "OO특기자 전형" 조건은
엄밀히는 학과가 아니라 입학 전형 기준이라(관련 학과가 아니어도 특기자 전형으로 입학했을 수
있음) 100% 정확한 표현은 아니지만, 최소한 완전히 무관한 학과 학생에게 노출되는 것보다는 훨씬
낫다는 판단으로 관련 학과로 좁힘.

의도적으로 이번 FIXES에서 제외한 것:
  - id=211 (체육특기자장학금, 우송대) — universities.ts의 우송대 전체 학과 목록을 확인했으나
    체육/스포츠 관련 학과가 아예 존재하지 않음. major로 좁힐 방법이 없어 그대로 major=None
    유지(전교생 노출 상태 지속) — 다른 방식(예: 입학전형 전용 필드 신설)이 필요한 케이스로
    남겨둠.
  - id=998 (인재육성장학금(체육특기, 횡성)) — 설명이 "전국(소년)체육대회 3위 이내 입상"이라
    입학전형이 아니라 실적 기반. major 제한이 없는 게 원래 맞음(위 (b) 부류).

사용법:
    python fix_athletic_major_backfill_2026-08-12.py           # dry-run만
    python fix_athletic_major_backfill_2026-08-12.py --apply    # 실제 반영
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


_CNU_SPORTS = "스포츠과학과,무용학과,체육교육과"
_PJU_SPORTS = "레저스포츠학부"
_HNU_SPORTS = "스포츠과학과"
_DJU_SPORTS = "스포츠운동과학과,스포츠건강재활학과,스포츠과학과,파크골프학과"

FIXES: list[dict] = [
    {"id": 26, "major": _CNU_SPORTS},   # 체육특기자 장학금(신입생), 충남대
    {"id": 49, "major": _CNU_SPORTS},   # 체육특기자 장학금(재학생), 충남대
    {"id": 157, "major": _PJU_SPORTS},  # 체육특기장학금, 배재대 ("체육특기자 전형 입학생 대상")
    {"id": 236, "major": _HNU_SPORTS},  # 체육특기자장학금(한남대) ("체육특기자 전형 입학생 대상")
    {"id": 260, "major": _DJU_SPORTS},  # 체육특기자장학금(신입생), 대전대
    {"id": 281, "major": _DJU_SPORTS},  # 체육특기자장학금(재학생), 대전대
    {"id": 282, "major": _DJU_SPORTS},  # 전지훈련장학금, 대전대 ("체육특기자 중 전지훈련 참가자")
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, major, required_special_status FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = set(ids) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    # 안전장치 — 조사 시점 이후 major가 이미 다른 값으로 채워졌다면(다른 작업과 겹쳤을
    # 가능성) 덮어쓰지 않고 건너뜀.
    already_filled = [r for r in before_rows.values() if r[2] is not None]
    if already_filled:
        print("경고: 이미 major가 채워진 항목은 건너뜀:")
        for r in already_filled:
            print(f"  id={r[0]} `{r[1]}`: 이미 {r[2]!r}")
    skip_ids = {r[0] for r in already_filled}

    for fix in FIXES:
        if fix["id"] in skip_ids:
            continue
        cur.execute(
            "UPDATE scholarship SET major = %s WHERE id = %s",
            (fix["major"], fix["id"]),
        )

    cur.execute(
        "SELECT id, name, major FROM scholarship WHERE id = ANY(%s) ORDER BY id", (ids,)
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines: list[str] = []
    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        note = " (건너뜀, 이미 값 있음)" if fid in skip_ids else ""
        report_lines.append(f"## id={fid} {before[1]}{note}")
        report_lines.append(f"  major: {before[2]!r} -> {after[2]!r}")
        report_lines.append("")

    report_lines.append("## 의도적으로 제외 (참고용, DB 변경 없음)")
    report_lines.append("- id=211 체육특기자장학금(우송대): 우송대에 체육/스포츠 관련 학과가 "
                         "없어 major로 좁힐 방법이 없음. major=None 유지.")
    report_lines.append("- id=998 인재육성장학금(체육특기, 횡성): 입학전형이 아니라 대회 입상 "
                         "실적 기반이라 major 제한이 원래 맞음. major=None 유지.")
    report_lines.append("")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_athletic_major_backfill_2026-08-12_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(FIXES) - len(skip_ids)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(FIXES)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
