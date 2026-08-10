# -*- coding: utf-8 -*-
"""외부 장학금 3차 배치 사전 필터.

national_foundations_source_20260722.csv를 읽어서:
1. 이미 라이브 DB에 있는 기관/상품과 이름이 비슷한 행을 "이미 처리됨(dedup 후보)"으로 표시
2. 자격제한/특정자격에 "고등학" 등 대학생 아닐 가능성 신호가 있는 행을 표시(자동 제외 아님,
   원문 대조 전 우선 검토용 표시일 뿐)
3. dedup 후보를 뺀 나머지를 기관별로 묶어서 상품 수 내림차순으로 정렬해 출력

DB는 조회(SELECT)만 함 — 아무것도 쓰지 않음. 접속 정보는 run_sql.py와 동일하게
backend/.env의 DATABASE_URL을 읽음.

사용법: python prefilter_national_foundations.py
출력: prefilter_report.txt (이 폴더에 생성)
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

import psycopg2

CSV_PATH = Path(__file__).parent / "national_foundations_source_20260722.csv"
REPORT_PATH = Path(__file__).parent / "prefilter_report.txt"

# 기관명 비교용 정규화 — 흔한 접두/접미사, 공백, 괄호를 제거해서 "재단법인 OO재단"과
# "(재)OO재단"이 같은 기관으로 매칭되게 함.
NORMALIZE_STRIP = ["재단법인", "사단법인", "(재)", "(사)", "주식회사", "(주)", "㈜", " "]
HIGH_SCHOOL_SIGNAL = "고등학"

# 1·2차 배치에서 이미 기관 단위로 원문 대조 조사를 마친 곳(포함/제외/보류 전부 판단
# 완료됨, EXTERNAL_SCHOLARSHIPS_PLAN.md 참고) — 개별 상품이 DB에 다 안 들어갔어도
# (예: 관정재단은 충남대·KAIST 확인분만 채택) 기관 자체는 이미 조사가 끝났으므로
# 3차 배치 "신규 후보" 순위에서 통째로 제외함. 행 단위 dedup(provider+name 조합
# 매칭)과는 별개의, 더 강한 "기관째로 스킵" 필터.
ALREADY_INVESTIGATED_INSTITUTIONS = {
    # 1차 배치 (대전·충남·세종 지자체)
    "재단법인 대전청년내일재단",
    "재단법인 대전광역시서구인재육성장학재단",  # 보류(전화 확인 대기)지만 조사는 이미 함
    "충남평생교육진흥원",
    "재단법인 세종연구원",
    "충청남도 아산시청",
    "충청남도 당진시청",
    "충청남도 천안시청",
    "충청남도 예산군청",  # 보류(전화 확인 대기)지만 조사는 이미 함
    "대전광역시청",
    "대전광역시교원단체총연합회",
    "세종특별자치시교원단체총연합회",
    # 2차 배치 (전국 대기업/유명 재단·공공기관)
    "(재단법인)아산사회복지재단",
    "관정재단",
    "(재)한국고등교육재단",
    "(재)수림재단",
    "국가보훈부",
    "남북하나재단",
    "롯데장학재단",
    "재단법인 DB김준기문화재단",
    "재단법인 신한장학재단",
    "IBK행복나눔재단",
    "KT그룹희망나눔재단",
    "(재)유한재단",
    "우리다문화장학재단",
    "재단법인 숲과나눔",
    "국립국제교육원",
    "현대차 정몽구 재단",
    "한국수력원자력(주)",
    "강원랜드사회공헌위원회",
    "재단법인 빙그레공익재단",
    "포스코청암재단",
    "한국장애인개발원",
    "삼성꿈장학재단",  # 조사 후 제외 확정
    "방일영문화재단",  # 조사 후 제외 확정(학교추천제, 화이트리스트 대학 한정)
}


def normalize(name: str) -> str:
    n = name or ""
    for token in NORMALIZE_STRIP:
        n = n.replace(token, "")
    n = re.sub(r"[^\w가-힣]", "", n)
    return n.strip().lower()


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def fetch_existing_pairs() -> set[tuple[str, str]]:
    """(정규화된 provider, 정규화된 name) 조합 — 행 단위 정밀 매칭용."""
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()
    cur.execute("SELECT name, provider FROM scholarship")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {(normalize(r[1]), normalize(r[0])) for r in rows if r[0] and r[1]}


def main() -> None:
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    existing_pairs = fetch_existing_pairs()
    already_investigated_norm = {normalize(i) for i in ALREADY_INVESTIGATED_INSTITUTIONS}

    likely_dup = []
    inst_skip = []
    hs_signal = []
    fresh = []

    for r in rows:
        provider_norm = normalize(r["운영기관명"])
        name_norm = normalize(r["상품명"])
        has_hs_signal = HIGH_SCHOOL_SIGNAL in (r.get("자격제한 상세내용") or "") or HIGH_SCHOOL_SIGNAL in (
            r.get("특정자격 상세내용") or ""
        )
        if provider_norm in already_investigated_norm:
            inst_skip.append(r)
        elif (provider_norm, name_norm) in existing_pairs:
            likely_dup.append(r)
        else:
            fresh.append(r)
        if has_hs_signal:
            hs_signal.append(r)

    by_inst = defaultdict(list)
    for r in fresh:
        by_inst[r["운영기관명"]].append(r["상품명"])

    ranked = sorted(by_inst.items(), key=lambda kv: -len(kv[1]))

    out = []
    out.append(f"전체 CSV 행: {len(rows)}")
    out.append(f"1·2차 배치에서 이미 조사한 기관이라 통째로 제외: {len(inst_skip)}")
    out.append(f"dedup 후보로 표시(라이브 DB와 기관+상품명 동시 일치): {len(likely_dup)}")
    out.append(f"'고등학' 신호 포함(우선 검토 대상, 자동 제외 아님): {len(hs_signal)}")
    out.append(f"신규 후보(위 두 제외 후 남은 행): {len(fresh)}")
    out.append(f"신규 후보에 속한 고유 기관 수: {len(by_inst)}")
    out.append("")
    out.append("=== 상품 수 내림차순 기관 목록 (신규 후보만) ===")
    for inst, products in ranked:
        out.append(f"\n[{inst}] {len(products)}건")
        for p in products:
            out.append(f"  - {p}")

    out.append("\n\n=== dedup 후보로 표시된 행 (검증 생략 대상, 참고용) ===")
    for r in likely_dup:
        out.append(f"  {r['운영기관명']} | {r['상품명']}")

    out.append("\n\n=== '고등학' 신호 포함 행 (원문 대조 시 대학생 대상 여부 먼저 확인) ===")
    for r in hs_signal:
        out.append(f"  {r['운영기관명']} | {r['상품명']}")

    REPORT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"done -> {REPORT_PATH}")
    print(f"dedup 후보 {len(likely_dup)}건 / 고등학 신호 {len(hs_signal)}건 / 신규 후보 {len(fresh)}건, 기관 {len(by_inst)}개")


if __name__ == "__main__":
    main()
