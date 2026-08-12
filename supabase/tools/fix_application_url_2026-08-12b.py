# -*- coding: utf-8 -*-
"""2026-08-12: `/돌아봐` 신청 링크 정확성 점검(45건 재검증, matching_gaps.md 참고)에서
"부정확함"/"깨짐"으로 분류된 14건을 별도 에이전트로 재조사해서 더 나은 URL로 교체.
10건은 그 장학금 이름/조건이 원문에 정확히 일치하는 전용 페이지를 찾음(확신 높음), 4건은
완벽한 전용 페이지는 못 찾았지만 기존보다는 훨씬 나은 대안(확신 중간 — 아래 주석 참고).

찾지 못한 특이사항(참고용, 이 스크립트가 건드리는 범위 밖):
- id=536: provider가 "세종특별자치시교원단체총연합회"로 돼 있는데, 실제 운영 주체는
  전국 단위 "한국교총장학회"(kftas.or.kr, 시도별 배정)로 보임 — provider 필드 자체가
  부정확할 가능성, 이 스크립트는 손대지 않음(재확인 필요, matching_gaps.md에 기록).
- id=529/530: 재단법인 세종연구원(구 세종특별자치시 인재육성평생교육진흥원, sjhle.or.kr)의
  세부 장학사업 게시글 자체가 신·구 도메인 모두 500 에러라, 기관 홈페이지(sri.re.kr)까지만
  대안으로 교체 — 완전한 해결은 아님.

사용법:
    python fix_application_url_2026-08-12b.py           # dry-run만
    python fix_application_url_2026-08-12b.py --apply    # 실제 반영
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

FIXES: list[dict] = [
    {"id": 183, "url": "https://www.mokwon.ac.kr/kr/html/sub04/04010301.html"},
    {"id": 217, "url": "http://janghak.hannam.ac.kr/sub2/menu_2.html"},
    {"id": 220, "url": "http://janghak.hannam.ac.kr/sub2/menu_2.html"},
    {"id": 228, "url": "http://janghak.hannam.ac.kr/sub2/menu_2.html"},  # 최선 대안: 2026년 안내문에 이 이름 자체가 더 이상 없음
    {"id": 233, "url": "http://janghak.hannam.ac.kr/sub2/menu_2.html"},  # 최선 대안: 독립 프로그램인지 불확실
    {"id": 529, "url": "https://www.sri.re.kr/"},  # 최선 대안: 세부 게시글은 신·구 도메인 다 500 에러
    {"id": 530, "url": "https://www.sri.re.kr/"},  # 최선 대안: 위와 동일
    {"id": 536, "url": "http://www.kftas.or.kr/selection/standard.do"},
    {"id": 920, "url": "https://www.jntle.kr/main/uBusiness4/2026009"},
    {"id": 930, "url": "https://www.jntle.kr/main/uBusiness3/2026014"},
    {"id": 937, "url": "https://www.jntle.kr/main/uBusiness4/2026109"},
    {"id": 951, "url": "https://www.wooyang.org/News/?bmode=view&idx=157916400"},
    {"id": 954, "url": "https://www.ascholarship.or.kr/bbs/board.php?bo_table=asc_notice&wr_id=360"},
    {
        "id": 1059,
        "url": "http://sido.jeju.go.kr/citynet/jsp/sap/SAPGosiBizProcess.do?command=searchDetail&flag=gosiGL&svp=Y&sido=&sno=65725&gosiGbn=A",
    },
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

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, application_url FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    for fix in FIXES:
        cur.execute(
            "UPDATE scholarship SET application_url = %s WHERE id = %s",
            (fix["url"], fix["id"]),
        )

    cur.execute(
        "SELECT id, name, application_url FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines = ["## 신청 링크 14건 재조사 후 수정\n"]
    for fix in FIXES:
        fid = fix["id"]
        before = before_rows.get(fid)
        after = after_rows.get(fid)
        if before is None or after is None:
            continue
        report_lines.append(f"### id={fid} {before[1]}")
        report_lines.append(f"  before: {before[2]!r}")
        report_lines.append(f"  after:  {after[2]!r}\n")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_application_url_2026-08-12b_diff.md"
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
