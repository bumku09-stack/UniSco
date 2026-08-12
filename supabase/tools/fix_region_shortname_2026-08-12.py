# -*- coding: utf-8 -*-
"""2026-08-12: `/돌아봐` 매칭 로직 점검에서 발견 — eligible_region에 시/도를 정식 명칭
("전라남도", "충청북도" 등)으로 넣은 레코드가 다수 있었음. 프론트가 실제로 서버에 보내는
값은 항상 짧은 이름("전남","충북" 등, `frontend/src/lib/regions.ts`의 shortName)인데,
`region_matches()`는 `spec.region in scholarship.eligible_region` 부분 문자열 비교라
"전남"이 "전라남도" 안에 부분 문자열로 없으면(전-라-남-도라 중간에 "라"가 끼어서 끊김)
영원히 매칭이 안 됨.

전남/충북/충남은 실제로 이렇게 끊겨서 진짜 매칭 실패(버그)였고, 서울/인천/경기/대전/세종/
강원/제주/울산은 짧은 이름이 정식 명칭의 접두어라 우연히 부분 문자열로 걸려서 지금까지는
동작했음 — 하지만 "우연히 맞았을 뿐"이라 나중에 로직이 조금만 바뀌어도 깨질 수 있는
취약한 상태였음. 그래서 전부 다 짧은 이름 컨벤션으로 통일함(진짜 버그였는지 우연히
맞았는지 구분 없이 전부 정규화).

사용법:
    python fix_region_shortname_2026-08-12.py           # dry-run만
    python fix_region_shortname_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2

FULL_TO_SHORT = [
    ("서울특별시", "서울"), ("부산광역시", "부산"), ("대구광역시", "대구"), ("인천광역시", "인천"),
    ("대전광역시", "대전"), ("울산광역시", "울산"), ("세종특별자치시", "세종"), ("경기도", "경기"),
    ("강원특별자치도", "강원"), ("충청북도", "충북"), ("충청남도", "충남"), ("전북특별자치도", "전북"),
    ("경상북도", "경북"), ("경상남도", "경남"), ("제주특별자치도", "제주"), ("전라남도", "전남"),
    ("광주광역시", "광주"),
]


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    conn.set_client_encoding("UTF8")
    cur = conn.cursor()

    cur.execute("SELECT id, name, eligible_region FROM scholarship WHERE eligible_region IS NOT NULL ORDER BY id")
    rows = cur.fetchall()

    changes = []
    for fid, name, region in rows:
        new_region = region
        for full, short in FULL_TO_SHORT:
            new_region = new_region.replace(full, short)
        if new_region != region:
            changes.append((fid, name, region, new_region))

    for fid, _name, _old, new_region in changes:
        cur.execute("UPDATE scholarship SET eligible_region = %s WHERE id = %s", (new_region, fid))

    report_lines = [f"## eligible_region 지역명 정규화 — {len(changes)}건\n"]
    for fid, name, old, new in changes:
        report_lines.append(f"- id={fid} `{name}`: {old!r} -> {new!r}")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_region_shortname_2026-08-12_diff.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(changes)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(changes)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
