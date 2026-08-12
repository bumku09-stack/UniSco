"""2026-08-12: 경쟁 서비스(이루리) 회원가입 폼 검토 중 발견한 신규 특수상황 태그 2종
(rural_student, parent_university_staff/alumni)을 실제 DB에 반영.

## 농어촌자녀(rural_student) — "농어촌" 키워드로 걸린 5건을 전부 개별로 읽고 판단함
- id=91 '농촌출신대학(원)생 학자금대출', id=231 '농어촌학생장학금(한남대)': 학생 본인이
  농어촌(읍·면) 출신이라는 조건 → rural_student 추가.
- id=298 '농업인자녀장학금': 학생이 아니라 **부모**가 농업인이라는 조건(직업) — 다른 개념,
  건드리지 않음(parent_occupation_condition 유지가 맞음).
- id=259 '신입생 전형별 수석·차석 장학금': "농어촌학생전형"은 10개 전형 중 하나로 언급된
  것뿐 실제로 농어촌 출신만 받는 조건이 아님(전형 무관하게 전부 수상 대상) — 태그 추가 안 함.
- id=945 '농어촌목회자자녀및신학생': 실제 조건은 "농어촌 지역에서 사역하는 감리교 목회자의
  자녀"라 학생의 출신이 아니라 **부모의 종교적 소속/직분**이 핵심 조건 — rural_student가
  아니라 religious_or_career_intent_condition(확인 불가)에 해당하는데 지금까지 태그가
  아예 안 붙어 있었음(기존 태깅 누락 발견) → 이번에 같이 바로잡음.

## 부모가 재학 대학 교직원/동문 (parent_university_staff / parent_university_alumni)
기존 parent_occupation_condition(확인 불가) 태그 34건을 전수 재검토하다 발견 — 그중 10건은
"아무 직업"이 아니라 정확히 "그 학생이 재학 중인 대학 자체의 교직원/동문 자녀"라는 훨씬
구체적이고 학생이 예/아니오로 답할 수 있는 조건이었음. staff/alumni 둘 다 해당하는 경우(을지
가족장학금)는 두 태그를 같이 넣음. parent_occupation_condition은 이제 정확하지 않으므로
제거함(부모 직업 자체가 아니라 "이 학교 소속"이 핵심이라서).

같은 재검토에서 나온 id=171(초중고 교사 자녀, 학교 무관)과 id=249(충청권 교육회 소속
교육자 자녀, 학교 무관)는 "이 대학 소속"이 아니라 진짜 직업(교육자) 조건이라 그대로
parent_occupation_condition 유지 — 건드리지 않음.

사용법:
    python fix_rural_and_staff_tags_2026-08-12.py           # dry-run만
    python fix_rural_and_staff_tags_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

RURAL_STUDENT_IDS = [91, 231]
# id=231은 "농어촌특별전형 수석합격자"(출신 학교 소재지 기준)라 hometown_school_region_
# condition으로 뭉뚱그려져 있었는데, rural_student가 이제 이 조건을 정확히 표현하므로 중복
# 제거.
REMOVE_HOMETOWN_TAG_IDS = [231]
RELIGIOUS_TAG_ADD_IDS = [945]  # 기존 태깅 누락분 바로잡기
STAFF_IDS = [124, 163, 183, 268, 269]
ALUMNI_IDS = [160, 198, 239, 271]
STAFF_AND_ALUMNI_IDS = [305]  # 을지가족장학금 — 교직원/동문 둘 다 별도 트랙으로 지원 가능
# staff/alumni로 재정리되는 10건은 이제 부모 "직업"이 아니라 "소속 학교"가 핵심 조건이라
# parent_occupation_condition을 제거함.
REMOVE_PARENT_OCCUPATION_IDS = STAFF_IDS + ALUMNI_IDS + STAFF_AND_ALUMNI_IDS

ALL_IDS = sorted(
    set(RURAL_STUDENT_IDS + RELIGIOUS_TAG_ADD_IDS + STAFF_IDS + ALUMNI_IDS + STAFF_AND_ALUMNI_IDS)
)


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def add_tag(cur, sid: int, tag: str) -> None:
    cur.execute(
        "UPDATE scholarship SET required_special_status = "
        "array_append(required_special_status, %s) WHERE id = %s "
        "AND NOT (%s = ANY(required_special_status))",
        (tag, sid, tag),
    )


def remove_tag(cur, sid: int, tag: str) -> None:
    cur.execute(
        "UPDATE scholarship SET required_special_status = "
        "array_remove(required_special_status, %s) WHERE id = %s",
        (tag, sid),
    )


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, required_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ALL_IDS,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}
    missing = set(ALL_IDS) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    for sid in RURAL_STUDENT_IDS:
        add_tag(cur, sid, "rural_student")
    for sid in RELIGIOUS_TAG_ADD_IDS:
        add_tag(cur, sid, "religious_or_career_intent_condition")
    for sid in STAFF_IDS:
        add_tag(cur, sid, "parent_university_staff")
    for sid in ALUMNI_IDS:
        add_tag(cur, sid, "parent_university_alumni")
    for sid in STAFF_AND_ALUMNI_IDS:
        add_tag(cur, sid, "parent_university_staff")
        add_tag(cur, sid, "parent_university_alumni")
    for sid in REMOVE_PARENT_OCCUPATION_IDS:
        remove_tag(cur, sid, "parent_occupation_condition")
    for sid in REMOVE_HOMETOWN_TAG_IDS:
        remove_tag(cur, sid, "hometown_school_region_condition")

    cur.execute(
        "SELECT id, name, required_special_status FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ALL_IDS,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines: list[str] = []
    for sid in ALL_IDS:
        before = before_rows.get(sid)
        after = after_rows.get(sid)
        if before is None or after is None:
            continue
        report_lines.append(f"## id={sid} {before[1]}")
        report_lines.append(f"  required_special_status: {before[2]!r} -> {after[2]!r}")
        report_lines.append("")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_rural_and_staff_tags_2026-08-12_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(ALL_IDS)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(ALL_IDS)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
