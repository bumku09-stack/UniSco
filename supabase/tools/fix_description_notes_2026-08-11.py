# -*- coding: utf-8 -*-
"""2026-08-11: 사용자가 관정재단 학부장학생(id=645)에서 "충남대학교 참여 확인... 나머지 9개
대학 참여 여부는 미확인" 같은 내부 조사 메모가 상세페이지에 그대로 보인다고 지적함 —
2026-08-10에 47건 정리했던 것과 똑같은 문제인데, 그때 안 걸린 나머지가 더 있는지 전체 662건을
"⚠️/미확인/재확인/확인 필요/저신뢰/CSV/재검증" 키워드로 다시 훑어서 26건을 찾음.

그중 2건(id=153, 924)은 "매 학기 초 공지 확인 필요", "온라인 신청 후 전화 확인 필요"처럼
학생한테 실제로 유용한 신청 안내문이라 손대지 않음 — 나머지 24건만 정리.

원칙(2026-08-10과 동일): 내부 조사 메모(필드명 언급, "확실치 않음"/"미확인"/"재확인 필요"류
불확실성 표현, "CSV 자료" 같은 우리 쪽 데이터소스 언급, ⚠️ 마커)는 삭제하고, 그 안에 학생한테
실제로 유용한 사실 정보(예: 관정재단의 대학별 배정 인원)가 섞여 있으면 그 부분만 남겨서 자연스러운
문장으로 정리.

사용법:
    python fix_description_notes_2026-08-11.py           # dry-run만
    python fix_description_notes_2026-08-11.py --apply    # 실제 반영
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
    {"id": 76, "description": "경제적 이유로 학업지속이 어려운 학생 대상, 생활비성 지원."},
    {"id": 521, "description": (
        "실적인정기간 내 인문사회/과학/예체능 등 분야 국제 및 전국대회 3위 이내 입상 + "
        "학교장 추천. 직전학기 12학점 이상 수강. 공고일 기준 6개월 전부터 대전광역시에 "
        "주민등록상 주소를 둔 학생. 징계·타도시 전학·허위기재 시 제외, 휴학생/수료생/초과학기/"
        "직전학기 1학점 미만 취득자 제외."
    )},
    {"id": 533, "description": (
        "2016년 2학기 이후 한국장학재단 학자금대출(취업후상환/일반상환) 받은 대학생(휴학생 포함) "
        "대상, 최근 반기 발생 이자(생활비 제외) 지원(대출금 상환계좌로 상환). 공고일 기준 본인 "
        "또는 직계존속이 당진시에 1년 이상 주민등록. 소득분위 8분위 이하만 지원 가능하나, "
        "다자녀(3자녀 이상) 가정은 소득분위 무관하게 지원. 대학교 졸업생/수료생/제적생/자퇴생·"
        "대학원생, 대출 전액 상환자 제외."
    )},
    {"id": 643, "description": (
        "정부기관의 보호결정을 받은 북한이탈청소년 중 재단이 지정한 전국 4년제 대학에 재학 "
        "중으로 2·3·4학년 진학 예정인 대학생. 전체 학업성적 평점과 직전학기 평점이 모두 3.0 "
        "이상. 학기당300만원(연600만원), 재단 지정 오리엔테이션·장학증서 수여식·봉사캠프 등 "
        "참여 필수. 지도교수 추천."
    )},
    {"id": 645, "description": (
        "2026년 1학기 기준 5학기(3학년1학기) 진학 예정, 대한민국 국적으로 대한민국 고등학교 "
        "졸업, 만24세 이하. 학부1~3학기 총평균평점 4.0/4.5(3.8/4.3) 이상. 관정성적우수장학금"
        "(A형, 학기당600만원)/관정학업장려장학금(B형, 학기당400만원) 중 선택, 최대4학기. 대학 "
        "총장 추천 필요(재단이 지원하는 대학만 해당). 편입생 제외. 충남대학교 배정: 학부 5명"
        "(자연이공 4·인문사회 1)."
    )},
    {"id": 646, "description": (
        "대한민국 국적 보유자로서 대한민국 고등학교 졸업, 일반대학원 석사/석박사통합/박사과정 "
        "입학예정자·재학생. 前과정 총평균평점 4.0/4.5(3.8/4.3) 이상. 학기당600만원, 최대4학기. "
        "대학 총장 추천 필요. 일반대학원 이외 과정(MBA·전문대학원·특수대학원 등) 제외, 타 "
        "민간재단 장학금 중복수혜 불가. KAIST 배정: 학과별 최대 2명."
    )},
    {"id": 679, "description": (
        "국내소재 정규대학에 재학 중인 자. 부산 기장군 장안읍·일광읍에 공고일 포함 최근 만3년 "
        "이상 계속 거주(또는 만1년 이상+과거 합산 만15년 이상). 2026학년도 1학기 12학점 이상 "
        "이수, 평점평균 2.5/4.5 이상. 100만원(1회성 생활지원금). 한국수력원자력·한국전력·"
        "한전KPS 및 발전자회사 직원 및 가족, 사이버대·방송통신대 등 제외."
    )},
    {"id": 682, "description": (
        "국내소재 정규대학(교) 재학 중, 울주군 서생면·온양읍 지역 거주자(발전소건설 이주민 및 "
        "직계비속, 반경1km 이내 거주자, 기초생활수급자 등 세부 요건에 따라 지원금 차등: "
        "100~150만원). 실제 만3년 이상 거주(또는 만1년 이상+과거합산 만15년 이상). 2026학년도 "
        "1학기 평균평점 2.0~2.5/4.5 이상(세부기준별 상이). 대학생·고등학생 합산 620명, 총 6억원 "
        "규모(2026년 \"새울 희망미래 장학생\"으로 통합 운영). 한수원·한전·한전KPS 직원 및 가족, "
        "대학원생, 정규학기 초과자 제외."
    )},
    {"id": 683, "description": (
        "학생 본인 또는 보호자가 강원 양양군 서면 또는 인제군 기린면에 장학생 선발 공고일 기준으로 "
        "주민등록을 두고 1년 이상 실제 거주 중일 것. 12학점 이상 수강, 성적 4.5만점 기준 3.0 "
        "이상. 200만원. 거주지/소득수준/성적 순 선발. 휴학생 제외."
    )},
    {"id": 685, "description": (
        "갑작스러운 가정·경제 위기상황(부모의 사망·질병 등)으로 학업에 심각한 어려움을 겪는 대학 "
        "재학생 중, 전국 폐광지역(정선·태백·영월·삼척·보령·문경·화순 등 7개 시/군) 소재 고등학교를 "
        "졸업한 자. 100~300만원(사례 경중·위기상황·장학금 사용계획 등 종합평가). 2024년도 "
        "강원랜드 멘토링 장학 나눔/키움 장학생 수혜자는 지원 불가, 1가구당 연1회 제한. 상시 접수. "
        "현재 거주지가 아니라 출신 고등학교 소재지 기준."
    )},
    {"id": 934, "description": (
        "일반 대학생이 새로 신청 불가 — 고교 3학년 때 '유형1(신규선발)'로 선정된 학생만 대학 "
        "진학 후 졸업까지 '유형2(계속지원)'로 받는 트랙(2025년 이전 유형1 선발자 한정). 연 2회 "
        "지급(연 400만원), 최대 7년(휴학 최대 2년, 군휴학 별도 제외)."
    )},
    {"id": 946, "description": (
        "국내 정규 대학원 1학기 이상 수료한 석사과정생 대상. 우양재단 기존 장학금 수혜 대학 "
        "졸업생 또는 재단 프로그램 참가 경험 탈북 학생만 지원 가능. 매 학기 신청 가능, 최대 2회."
    )},
    {"id": 990, "description": "용인시에 30년 이상 계속 거주하는 가구 중 학생 1인만 신청 가능. 매학기 12학점 이상+B+ 이상."},
    {"id": 994, "description": (
        "신규 지원자를 뽑는 게 아니라, '진학장학금'에서 수능 최고득점자로 선발된 학생이 매년 "
        "성적(A 이상) 유지 시 졸업까지 자동으로 계속 받는 트랙(별도 신청 없음, 진학장학금 "
        "수능전형 수석 합격자 전용)."
    )},
    {"id": 1007, "description": (
        "학생 또는 보호자가 3년 이상 계속 실거주. 고등교육법 제2조 학교 재학 대학생, 해당학기 "
        "국가장학금 I유형(또는 다자녀) 신청자. 본인부담금 없거나 1만원 미만이면 제외."
    )},
    {"id": 1010, "description": (
        "타 지역 학생으로 공고일 현재 '3개월 이상~1년 미만' 춘천시 주민등록 이전한 관내 대학"
        "(교) 재학생. 직전학기12학점 이상. 성적50%+생활수준40%+봉사10%, 총장(학장) 추천 필요."
    )},
    {"id": 1026, "description": (
        "영암 출신 향우자녀(향우회 소속) — 현재 거주 여부와 무관, 타지 거주 가능. 직전학년 B+ "
        "이상. 향우회장 추천 필요."
    )},
    {"id": 1035, "description": (
        "독립유공자의 대학생 증손자녀(4대~6대). 직전학기 12학점 이상+평균B학점 이상(등록금 "
        "지원분). 생활비 지원분 별도 100만원(5명, 이중수혜 가능)."
    )},
    {"id": 1037, "description": (
        "신규 신청이 아니라 '기 선발된 옥당골 인재장학생' 중 계속지원 대상자만 해당(총 4회 지원)."
    )},
    {"id": 1040, "description": "한빛원전주변지역 백수읍·홍농읍·법성면 3개 읍면 한정. 등록장애인 조건 포함."},
    {"id": 1045, "description": (
        "SK인천석유화학㈜ 지정기부금, 기업 인근지역 학생 지원. 서구 내 신현원창동·석남1~3동·"
        "가정1동·가좌1~3동 거주자로 한정. 생활비성(이중수혜 가능)."
    )},
    {"id": 1079, "description": (
        "관외 1년 이상 거주 후 공주시 전입, 전입 6개월 경과자. 효/선행/봉사 등, 1회 한정. "
        "대학총장(단과대학장) 추천 필요."
    )},
    {"id": 1083, "description": (
        "부모가 '거창군 재경 향우회'에 가입되어 있는 대학 재(입)학생으로 학업성적 우수 또는 "
        "가정형편 곤란(거창군 거주와 무관, 타지 거주 향우회원 자녀 대상). 재경향우회장 추천 필요."
    )},
]


def main() -> None:
    apply = "--apply" in sys.argv
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in FIXES]
    cur.execute(
        "SELECT id, name, description FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    if len(before_rows) != len(set(ids)):
        missing = set(ids) - set(before_rows)
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    report_lines = []
    for fix in FIXES:
        cur.execute(
            "UPDATE scholarship SET description = %s WHERE id = %s",
            (fix["description"], fix["id"]),
        )
        if cur.rowcount != 1:
            report_lines.append(f"!! id={fix['id']}: UPDATE 영향받은 행 수 = {cur.rowcount} (예상: 1)")

    cur.execute(
        "SELECT id, name, description FROM scholarship WHERE id = ANY(%s) ORDER BY id",
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
        report_lines.append(f"  before: {before[2]!r}")
        report_lines.append(f"  after:  {after[2]!r}")

    report = "\n".join(report_lines)
    out_path = (
        Path(__file__).resolve().parents[1]
        / "audit_reports"
        / "fix_description_notes_2026-08-11_diff.md"
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
