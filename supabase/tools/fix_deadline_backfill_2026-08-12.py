# -*- coding: utf-8 -*-
"""2026-08-12: 사용자 UX 리서치에서 "마감 지난 장학금이 계속 뜬다"가 가장 거슬리는 문제로
꼽힘 — application_deadline이 661건 중 68건(10.3%)만 채워져 있어서, 나머지는
deadline_matches()가 구조화된 값이 없으면 걸러내지 않는 leniency 규칙 때문에 실제로 마감이
지났어도 계속 노출됨(backend/app/core/matching.py 참고).

application_deadline이 비어있고 application_period(자유 텍스트)에 날짜가 있는 265건 중,
정규식으로 안전하게(범위/단일 종료일 패턴이 명확하고, "매년"/"연 O회"/"추정"/"미확인"/
"추가접수" 같은 불확실 표현이 없고, 매칭된 날짜 구간 밖에 다른 날짜 조각이 안 남는) 파싱
가능한 65건만 반영. 나머지 200건(반복공고·다단계 일정·모호한 경우)은 자동 처리 안 함 —
supabase/audit_reports/2026-08-11_172654_deadline_url_gaps.md의 A그룹 나머지 항목으로
남아있으며 사람이 원문 재확인 후 처리할 것(추측 금지 원칙, data_collection_guide.md 참고).

파싱 스크립트 자체는 커밋 안 함(1회성 정규식 실험, harness 코드가 아님) — 이 파일은 그
결과값(FIXES)만 담은 최종 반영용 스크립트. 파싱 로직 재현이 필요하면 이 파일의 커밋 메시지
참고.

사용법:
    python fix_deadline_backfill_2026-08-12.py           # dry-run만
    python fix_deadline_backfill_2026-08-12.py --apply    # 실제 반영
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


# {id: (application_deadline, 근거가 된 application_period 원문)} — 값은 전부 DB에 이미
# 있던 application_period 텍스트에서 그대로 파싱한 것(원문 재방문 없음, 새 정보 추가 아님).
FIXES: list[dict] = [
    {"id": 72, "application_deadline": "2026-07-27"},
    {"id": 73, "application_deadline": "2026-07-31"},
    {"id": 74, "application_deadline": "2026-08-11"},
    {"id": 75, "application_deadline": "2026-07-27"},
    {"id": 76, "application_deadline": "2026-08-04"},
    {"id": 78, "application_deadline": "2026-08-14"},
    {"id": 79, "application_deadline": "2026-07-26"},
    {"id": 81, "application_deadline": "2026-09-30"},
    {"id": 82, "application_deadline": "2026-09-11"},
    {"id": 83, "application_deadline": "2026-07-28"},
    {"id": 84, "application_deadline": "2026-07-28"},
    {"id": 85, "application_deadline": "2026-08-31"},
    {"id": 91, "application_deadline": "2026-07-28"},
    {"id": 93, "application_deadline": "2026-08-14"},
    {"id": 96, "application_deadline": "2026-07-31"},
    {"id": 173, "application_deadline": "2026-08-10"},
    {"id": 174, "application_deadline": "2026-08-30"},
    {"id": 500, "application_deadline": "2026-07-31"},
    {"id": 948, "application_deadline": "2026-04-09"},
    {"id": 949, "application_deadline": "2026-04-09"},
    {"id": 1004, "application_deadline": "2026-04-30"},
    {"id": 1005, "application_deadline": "2026-04-30"},
    {"id": 1007, "application_deadline": "2026-06-08"},
    {"id": 1040, "application_deadline": "2026-06-24"},
    {"id": 1041, "application_deadline": "2026-06-24"},
    {"id": 1042, "application_deadline": "2026-06-24"},
    {"id": 1055, "application_deadline": "2026-04-27"},
    {"id": 1056, "application_deadline": "2026-04-27"},
    {"id": 1057, "application_deadline": "2026-04-27"},
    {"id": 1058, "application_deadline": "2026-04-27"},
    {"id": 1059, "application_deadline": "2026-04-27"},
    {"id": 1060, "application_deadline": "2026-04-27"},
    {"id": 1061, "application_deadline": "2026-04-27"},
    {"id": 1062, "application_deadline": "2026-04-27"},
    {"id": 1063, "application_deadline": "2026-04-27"},
    {"id": 1064, "application_deadline": "2026-05-08"},
    {"id": 1065, "application_deadline": "2026-03-31"},
    {"id": 1066, "application_deadline": "2026-03-20"},
    {"id": 1067, "application_deadline": "2026-03-20"},
    {"id": 1068, "application_deadline": "2026-03-20"},
    {"id": 1070, "application_deadline": "2026-03-31"},
    {"id": 1072, "application_deadline": "2026-04-28"},
    {"id": 1075, "application_deadline": "2026-04-28"},
    {"id": 1078, "application_deadline": "2026-04-28"},
    {"id": 1079, "application_deadline": "2026-04-28"},
    {"id": 1081, "application_deadline": "2026-01-30"},
    {"id": 1082, "application_deadline": "2026-01-30"},
    {"id": 1083, "application_deadline": "2026-01-30"},
    {"id": 1084, "application_deadline": "2026-01-30"},
    {"id": 1085, "application_deadline": "2026-01-30"},
    {"id": 1086, "application_deadline": "2026-01-31"},
    {"id": 1095, "application_deadline": "2026-05-18"},
    {"id": 1098, "application_deadline": "2026-02-06"},
    {"id": 1099, "application_deadline": "2026-02-06"},
    {"id": 1116, "application_deadline": "2026-05-08"},
    {"id": 1117, "application_deadline": "2026-05-08"},
    {"id": 1118, "application_deadline": "2026-05-08"},
    {"id": 1119, "application_deadline": "2026-05-08"},
    {"id": 1120, "application_deadline": "2026-05-08"},
    {"id": 1121, "application_deadline": "2026-05-08"},
    {"id": 1122, "application_deadline": "2026-05-08"},
    {"id": 1123, "application_deadline": "2026-05-08"},
    {"id": 1124, "application_deadline": "2026-04-10"},
    {"id": 1125, "application_deadline": "2026-04-10"},
    {"id": 1127, "application_deadline": "2026-04-10"},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, application_deadline, application_period "
        "FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = set(ids) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    # 안전장치 — 파싱 근거로 삼았던 시점 이후 application_deadline이 이미 다른 값으로
    # 채워졌다면(다른 작업과 겹쳤을 가능성) 덮어쓰지 않고 건너뜀.
    already_filled = [r for r in before_rows.values() if r[2] is not None]
    if already_filled:
        print("경고: 이미 application_deadline이 채워진 항목은 건너뜀:")
        for r in already_filled:
            print(f"  id={r[0]} `{r[1]}`: 이미 {r[2]}")
    skip_ids = {r[0] for r in already_filled}

    report_lines: list[str] = []
    for fix in FIXES:
        if fix["id"] in skip_ids:
            continue
        cur.execute(
            "UPDATE scholarship SET application_deadline = %s WHERE id = %s",
            (fix["application_deadline"], fix["id"]),
        )

    cur.execute(
        "SELECT id, name, application_deadline FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        note = " (건너뜀, 이미 값 있음)" if fid in skip_ids else ""
        report_lines.append(f"## id={fid} {before[1]}{note}")
        report_lines.append(f"  application_period: {before[3]!r}")
        report_lines.append(f"  application_deadline: {before[2]!r} -> {after[2]!r}")
        report_lines.append("")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_deadline_backfill_2026-08-12_diff.md"
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
