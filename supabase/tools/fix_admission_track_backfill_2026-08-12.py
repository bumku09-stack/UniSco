"""2026-08-12: `admission_track` 필드 신설에 맞춰 체육특기자 장학금 8건을 재정리.

배경: 국어국문학과 학생에게 체육특기자 장학금이 노출된 사고를 처음엔
fix_athletic_major_backfill_2026-08-12.py로 `major`(전공)에 관련 학과를 채우는 방식으로
막았음. 하지만 이건 우회 프록시였음 — "체육특기자 전형 입학생 대상"은 학과 조건이 아니라
입학전형 조건이라, major로는 완전히 정확하게 표현이 안 됐고(관련 학과가 아닌 전형 출신도
있을 수 있고, 반대로 우송대처럼 관련 학과 자체가 없는 대학도 있어서 major로 아예 표현
불가능한 경우가 있었음 — id=211이 그 케이스라 그때는 못 고치고 남겨뒀음).

이제 `admission_track` 전용 필드가 생겼으므로:
- 그때 major에 채워둔 관련 학과 값 7건(id 26,49,157,236,260,281,282)을 다시 NULL로 되돌림
  (major_matches()가 계속 걸리면 "관련 학과 학생이지만 일반전형으로 입학한 사람"까지 잘못
  거르거나, admission_track과 이중으로 걸려서 과소매칭이 될 수 있음).
- 8건(위 7건 + id=211 우송대) 전부 admission_track='athletic_specialty'로 채움 — 이제
  우송대도 학과 무관하게 정확히 표현 가능.

사용법:
    python fix_admission_track_backfill_2026-08-12.py           # dry-run만
    python fix_admission_track_backfill_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

ATHLETIC_SPECIALTY_IDS = [26, 49, 157, 211, 236, 260, 281, 282]
# 이 중 major를 다시 NULL로 되돌릴 대상 — 우송대(211)는 애초에 major를 안 채웠어서 제외.
CLEAR_MAJOR_IDS = [26, 49, 157, 236, 260, 281, 282]


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, major, admission_track FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (ATHLETIC_SPECIALTY_IDS,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = set(ATHLETIC_SPECIALTY_IDS) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    # 안전장치 — 지난번 major backfill 이후 이 필드들이 다른 값으로 또 바뀌었으면 덮어쓰지
    # 않고 건너뜀(다른 작업과 겹쳤을 가능성).
    already_has_track = [r for r in before_rows.values() if r[3] is not None]
    if already_has_track:
        print("경고: 이미 admission_track이 채워진 항목은 건너뜀:")
        for r in already_has_track:
            print(f"  id={r[0]} `{r[1]}`: 이미 {r[3]!r}")
    skip_ids = {r[0] for r in already_has_track}

    for sid in ATHLETIC_SPECIALTY_IDS:
        if sid in skip_ids:
            continue
        cur.execute(
            "UPDATE scholarship SET admission_track = 'athletic_specialty' WHERE id = %s",
            (sid,),
        )
        if sid in CLEAR_MAJOR_IDS:
            cur.execute("UPDATE scholarship SET major = NULL WHERE id = %s", (sid,))

    cur.execute(
        "SELECT id, name, major, admission_track FROM scholarship "
        "WHERE id = ANY(%s) ORDER BY id",
        (ATHLETIC_SPECIALTY_IDS,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines: list[str] = []
    for sid in ATHLETIC_SPECIALTY_IDS:
        before = before_rows.get(sid)
        after = after_rows.get(sid)
        if before is None or after is None:
            continue
        note = " (건너뜀, 이미 값 있음)" if sid in skip_ids else ""
        report_lines.append(f"## id={sid} {before[1]}{note}")
        report_lines.append(f"  major: {before[2]!r} -> {after[2]!r}")
        report_lines.append(f"  admission_track: {before[3]!r} -> {after[3]!r}")
        report_lines.append("")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_admission_track_backfill_2026-08-12_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    processed = len(ATHLETIC_SPECIALTY_IDS) - len(skip_ids)
    if apply:
        conn.commit()
        print(f"반영 완료(commit). {processed}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(ATHLETIC_SPECIALTY_IDS)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
