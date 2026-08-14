# -*- coding: utf-8 -*-
"""admission_score_condition("입학성적" 라벨로 표시됨)에 수능/입학성적과 무관한 내용이
잘못 들어가 있던 것들을 정리. 이미 다른 구조화 필드(특수상황 태그/foreigner_eligibility/
admission_track/min_grade)로 중복되는 건 그냥 지우고, 안 겹치는 정보는 description으로
옮김(라벨 없이 순수 텍스트로만 남게).
"""
import sys
sys.path.insert(0, "supabase/tools")
from run_sql import load_database_url
import psycopg2

conn = psycopg2.connect(load_database_url())
cur = conn.cursor()

# 1) 이미 다른 구조화 필드로 완전히 중복되는 것 — admission_score_condition만 지움
clear_only = [26, 28, 33, 34, 49, 55, 57, 58, 97, 98]
for sid in clear_only:
    cur.execute("UPDATE scholarship SET admission_score_condition = NULL WHERE id = %s", (sid,))

# 2) '페이지에 명시 안 됨' 같은 플레이스홀더 — 그냥 NULL
placeholder = [15, 16, 45]
for sid in placeholder:
    cur.execute("UPDATE scholarship SET admission_score_condition = NULL WHERE id = %s", (sid,))

# 3) 수능/입학성적이 아닌 실제 정보 — description으로 이동(기존 description 있으면 이어붙임)
move_to_description = {
    27: "6.25 유엔참전용사 후손(직계비속)임이 확인된 외국인 유학생(국제교류본부 추천자)",
    35: "학생자치기구 임원 등",
    36: "학·석사연계과정 석사과정 전일제 신입생",
    37: "석·박사통합과정 전일제 신입생",
    43: "성적우수자, 경제·사회적 취약계층, 봉사활동으로 본교에 기여한 자",
    44: "성적우수자, 경제·사회적 취약계층, 봉사활동으로 본교에 기여한 자",
    46: "경제적 사정이 곤란한 자",
    50: "정부초청 외국인 장학생",
    51: "국제교류본부장 추천자",
    52: "TOEIC 900점 이상 또는 TOEFL iBT 102점 이상(ETS 주관 시험)",
    53: "6.25 유엔참전용사 후손(직계비속)임이 확인된 외국인 유학생(국제교류본부 추천자)",
    54: "외국인 유학생(국적이 대한민국인 경우 제외)",
    56: "해외 교류대학 복수학위 참가자",
    59: "학생자치기구 임원 등",
    60: "대학원 정원 외 군(육·해·공) 위탁교육생",
    61: "학·석사연계과정 계속 유지자로 학부과정 매학기 이수 이후 지급",
    62: "학·석사연계과정(학부) 최종학기 재학생으로 BK21 교육연구단(팀)의 교육과정 및 연구활동에 참여하는 자",
    63: "학생군사교육단 해외프로그램 공모에 선발된 자",
    68: "논문게재, 학술대회 참가 등 일반대학원장이 정한 실적을 충족한 자",
    69: "연구지원이 필요한 전일제 대학원생으로 일반대학원장이 추천한 자",
    77: "전국 대학(원)생 대상 논문공모(휴학생 제외)",
    79: "박사과정 입학예정자 또는 박사과정 정규학기 2학기 이상 잔여자(석박사통합과정도 준함). 신입생은 석사 전체학기 평균 A학점 이상, 재학생은 직전학기 및 박사과정 전체학기 평균 A학점 이상",
    81: "행정학부 학부생 대상 사회공헌·자기소개서·면접 종합평가",
    87: "품행이 단정하며 향학열이 높은 학생",
    93: "국내 대학 박사학위 취득자(2022.9 이후), 이중국적자·영주권자 제외, 우수 연구성과 보유자, J-1비자 결격사유 없는 자",
    94: "AI 핵심분야 진로 희망자",
    95: "인문사회계열 일반대학원 석사과정(전일제)",
    96: "학·석사연계과정 석사 신입생/재학생, 석·박사통합과정 유형1·유형2 신입생 및 재학생(전일제)",
    125: "학부 3학년 이상, 경제적 어려움이 있는 학생 우선 선발",
    126: "학부/대학원 성적·연구 우수자",
    127: "우수 학부/대학원생",
    129: "성적우수자(별도기준, 2~4학년)",
    130: "우수논문 저자",
    131: "신소재공학과 학부 3~4학년, 경제적 어려움이 있는 학생",
    132: "화학과 학부생 대상, 봉사활동·생활고·리더십 등을 고려해 선발",
    133: "화학과 대학원 신입생 우수자",
}

cur.execute("SELECT id, description FROM scholarship WHERE id = ANY(%s)", (list(move_to_description.keys()),))
existing = dict(cur.fetchall())

for sid, text in move_to_description.items():
    prev = existing.get(sid)
    new_desc = (prev + " " + text) if prev else text
    cur.execute(
        "UPDATE scholarship SET admission_score_condition = NULL, description = %s WHERE id = %s",
        (new_desc, sid),
    )

# 4) 체육특기자 — admission_track이 이미 있어서(athletic_specialty) 그걸로 대체, 지우기만
cur.execute("UPDATE scholarship SET admission_score_condition = NULL WHERE id = 49")

conn.commit()
print("done")
