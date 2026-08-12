"""라이브 DB에서 application_period(자유 텍스트)가 "OOOO년 기준: ..." 같은 과거 회차를
참고값으로 박아둔 채 방치된 항목을 찾는 감사 도구. 읽기 전용 — DB를 수정하지 않음
(audit_deadline_and_url_gaps.py와 동일한 컨벤션).

배경: 2026-08-12 실사용자가 "현대차 정몽구재단 미래산업 인재 학부 장학생"의 신청기간이
"2025년 기준"으로 표시되는 걸 발견 — application_deadline은 원래도 NULL(매년 반복
프로그램이라 의도적으로 안 채움, deadline_matches()가 안 거름)이라 로직 버그는 아니었지만,
같은 재단의 대학원 버전(형제 장학금)은 이미 "2026년 기준"으로 갱신돼 있는데 학부 버전만
방치된 걸 발견 — 데이터가 여러 시점에 나눠서 부분 검증되다 생긴 불일치.

이건 지금까지의 감사 도구(값이 NULL/누락인 경우만 잡음)로는 못 잡는 종류 — "값은 채워져
있지만 오래됐다"는 다른 문제라서, application_period 원문에서 연도를 정규식으로 뽑아
현재 연도보다 오래된 게 있으면 플래그함.

이 스크립트는 값을 안 고침 — 실제로 최신 회차인지는 원문(재단 공식 페이지 등)을 다시
확인해야 함. 여기선 "어디부터 재확인할지"만 추려줌.

사용법:
    python audit_stale_application_period.py [출력경로.md]
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

import psycopg2

_YEAR_PATTERN = re.compile(r"(20\d{2})년\s*기준")


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main() -> None:
    current_year = datetime.date.today().year
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, provider, application_url, application_period FROM scholarship "
        "WHERE application_period ~ %s ORDER BY id",
        (_YEAR_PATTERN.pattern,),
    )
    rows = cur.fetchall()
    conn.close()

    stale: list[tuple] = []
    current: list[tuple] = []
    for row in rows:
        sid, name, provider, url, period = row
        m = _YEAR_PATTERN.search(period or "")
        year = int(m.group(1)) if m else None
        if year is not None and year < current_year:
            stale.append((sid, name, provider, url, period, year))
        else:
            current.append((sid, name, provider, url, period, year))

    lines: list[str] = []
    lines.append(f"# application_period 회차 오래됨 감사 ({datetime.date.today().isoformat()} 기준)")
    lines.append("")
    lines.append(
        f"`application_period`에 'OOOO년 기준' 패턴이 있는 {len(rows)}건 중, "
        f"현재 연도({current_year})보다 오래된 연도를 참고값으로 쓰는 게 **{len(stale)}건**."
    )
    lines.append("")
    lines.append("## 작업 지침")
    lines.append(
        "- `application_url`(재단/기관 공식 신청 페이지)을 다시 열어서 해당 연도 최신 모집공고 "
        "날짜를 확인할 것 — 추측 금지(`data_collection_guide.md` 절대규칙 4번)."
    )
    lines.append(
        "- 최신 회차가 이미 마감됐으면 그 사실을 원문에 명시(예: '2026년 기준: ...(마감됨)') — "
        "`application_deadline`은 그대로 NULL 유지(매년 반복 프로그램이라 다음 회차 날짜를 "
        "확정 못 하는 한 필터링 대상 아님)."
    )
    lines.append(
        "- 재단 사이트가 아직 다음 회차 공고를 안 냈으면 '~월경 모집(202X년 공고 미확인, "
        "직전 회차: ...)' 식으로 최소한 참고 회차 연도만 갱신."
    )
    lines.append("")
    lines.append("## 오래된 항목 (재확인 필요)")
    for sid, name, provider, url, period, year in stale:
        lines.append(f"- id={sid} **{name}**({provider}) — 참고연도 {year}")
        lines.append(f"  - 현재값: `{period}`")
        lines.append(f"  - 신청 페이지: {url or '(없음)'}")
    lines.append("")
    lines.append(f"## 이미 최신(참고용, {current_year}건 대상)")
    for sid, name, provider, url, period, year in current:
        lines.append(f"- id={sid} {name}({provider}) — 참고연도 {year}: `{period}`")

    report = "\n".join(lines)
    out_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1]
        / "audit_reports"
        / f"{datetime.date.today().isoformat()}_stale_application_period.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"done: {out_path} (오래됨 {len(stale)}건 / 전체 {len(rows)}건)")


if __name__ == "__main__":
    main()
