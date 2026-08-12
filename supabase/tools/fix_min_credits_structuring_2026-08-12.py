"""2026-08-12: 이수학점 조건을 GPA와 동일한 방식(학생 자기입력 숫자 vs 임계값 비교)으로
구조화. 지금까지 이 조건은 `credit_requirement_condition`이라는 "확인 불가" 태그로만
처리돼서 24건이 전부 랭킹만 밀리고 필터링은 안 됐음 — 경쟁 서비스(이루리) 회원가입 폼이
"직전학기 이수학점"을 GPA처럼 숫자로 직접 받는 걸 보고, 우리도 새 필드를 만들면 같은
방식으로 실제 매칭이 가능하다는 걸 확인함.

24건의 `min_credits` 원문을 전부 직접 읽고 분류함:
  - 22건: "직전학기 N학점 이상" 형태로 안전하게 파싱됨 → 이번에 반영
  - id=91: min_credits 원문 자체가 없음(다른 근거로 태그된 것으로 보임) → 반영 안 함
  - id=294 "동일학기 융복합전공 교과목 6학점 이상": "직전학기 총 이수학점"이 아니라 특정
    전공 교과목 학점이라 다른 개념 → 반영 안 함(그대로 확인 불가로 남김)

"OO학점 이상(졸업학기/최종학년은 M학점만 돼도 됨)" 같은 예외가 있는 5건(id=221,263,268,274,
그리고 각각의 최종학년 예외)은 더 낮은(관대한) 쪽 숫자를 채택함 — 과다매칭이 과소매칭보다
낫다는 이 프로젝트의 기존 원칙과 같은 방향(예외를 놓쳐서 정말 그 학기인 학생을 잘못
탈락시키는 것보다, 예외 아닌 학생 일부가 과다 매칭되는 게 나음).

반영된 22건은 credit_requirement_condition 태그를 제거함(이제 진짜 필드로 매칭되므로
"확인 불가"로 둘 이유가 없음).

사용법:
    python fix_min_credits_structuring_2026-08-12.py           # dry-run만
    python fix_min_credits_structuring_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

# {id: (min_credits_last_semester, 비고)}
FIXES: dict[int, tuple[int, str]] = {
    51: (15, "직전학기 15학점 이상 이수"),
    75: (9, "9학점 이상"),
    99: (12, "12"),
    100: (12, "12"),
    107: (15, "15"),
    108: (15, "15"),
    109: (15, "15"),
    134: (12, "직전학기 12학점 이상"),
    138: (12, "직전학기 12학점 이상"),
    147: (12, "직전학기 12학점 이상"),
    175: (17, "17학점 이상"),
    215: (15, "직전학기(들) 15학점 이상, F학점 없음(F학점 조건은 구조화 못 함, 원문은 min_credits에 남음)"),
    221: (12, "15학점 이상(졸업학기 12학점 이상) — 더 낮은 쪽 채택"),
    223: (15, "15학점 이상"),
    263: (10, "직전학기 15학점 이상(최종학년 10학점) — 더 낮은 쪽 채택"),
    264: (12, "직전학기 12학점 이상"),
    265: (12, "직전학기 12학점 이상"),
    268: (10, "직전학기 15학점 이상(최종학년 10학점) — 더 낮은 쪽 채택"),
    274: (10, "직전학기 15학점 이상(최종학년 10학점) — 더 낮은 쪽 채택"),
    279: (15, "직전학기 15학점 이상"),
    292: (15, "직전학기 15학점 이상"),
    298: (12, "직전학기 12학점 이상"),
}


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

    ids = list(FIXES)
    cur.execute(
        "SELECT id, name, min_credits, min_credits_last_semester, required_special_status "
        "FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = set(ids) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    already_filled = [r for r in before_rows.values() if r[3] is not None]
    if already_filled:
        print("경고: 이미 min_credits_last_semester가 채워진 항목은 건너뜀:")
        for r in already_filled:
            print(f"  id={r[0]} `{r[1]}`: 이미 {r[3]!r}")
    skip_ids = {r[0] for r in already_filled}

    for sid, (threshold, _note) in FIXES.items():
        if sid in skip_ids:
            continue
        cur.execute(
            "UPDATE scholarship SET min_credits_last_semester = %s WHERE id = %s",
            (threshold, sid),
        )
        cur.execute(
            "UPDATE scholarship SET required_special_status = "
            "array_remove(required_special_status, 'credit_requirement_condition') WHERE id = %s",
            (sid,),
        )

    cur.execute(
        "SELECT id, name, min_credits, min_credits_last_semester, required_special_status "
        "FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines: list[str] = []
    for sid, (threshold, note) in FIXES.items():
        before = before_rows.get(sid)
        after = after_rows.get(sid)
        if before is None or after is None:
            continue
        skip_note = " (건너뜀, 이미 값 있음)" if sid in skip_ids else ""
        report_lines.append(f"## id={sid} {before[1]}{skip_note}")
        report_lines.append(f"  min_credits(원문): {before[2]!r}")
        report_lines.append(f"  min_credits_last_semester: {before[3]!r} -> {after[3]!r} ({note})")
        report_lines.append(f"  required_special_status: {before[4]!r} -> {after[4]!r}")
        report_lines.append("")

    report_lines.append("## 의도적으로 제외 (참고용, DB 변경 없음)")
    report_lines.append("- id=91: min_credits 원문 자체가 없어서 근거 없이 채울 수 없음.")
    report_lines.append("- id=294: '동일학기 융복합전공 교과목 6학점 이상' — 직전학기 총 "
                         "이수학점과 다른 개념(특정 전공 교과목 학점)이라 이 필드로 표현 불가.")
    report_lines.append("")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_min_credits_structuring_2026-08-12_diff.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    processed = len(FIXES) - len(skip_ids)
    if apply:
        conn.commit()
        print(f"반영 완료(commit). {processed}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(FIXES)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
