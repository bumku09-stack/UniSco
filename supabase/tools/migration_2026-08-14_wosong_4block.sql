-- 우송대학교 16건 4블록(금액/기간/신청방식) 분리 + 내부 매칭한계 메모/행번호 참조 제거

UPDATE scholarship SET
  amount_detail = '등록금 전액 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '직전학기 성적 85점(100점 만점) + 우송지수 10점 + 인성 5점 합산 기준 대상.'
WHERE id = 200;

UPDATE scholarship SET
  amount_detail = '등록금 2/3 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '성적 우수자 대상(자립장학금 다음 등급).'
WHERE id = 201;

UPDATE scholarship SET
  amount_detail = '등록금 1/3 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '성적 우수자 대상(단정장학금 다음 등급).'
WHERE id = 202;

UPDATE scholarship SET
  amount_detail = '등록금 1/6 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '성적 우수자 대상(독행장학금 다음 등급).'
WHERE id = 203;

UPDATE scholarship SET
  amount_detail = '등록금 3/4 범위 내 학비 지급',
  application_period = NULL,
  application_method = '자동선발',
  description = '학과별 해외연수(일본·영어권) 선발고사 합격자 대상.'
WHERE id = 204;

UPDATE scholarship SET
  amount_detail = '등록금 2/3 범위 내 학비 지급',
  application_period = NULL,
  application_method = '자동선발',
  description = '학과별 해외연수(아시아권) 선발고사 합격자 대상.'
WHERE id = 205;

UPDATE scholarship SET
  amount_detail = '등록금 1/2 지급',
  application_period = NULL,
  application_method = '자동선발',
  description = '해외인턴십 실습학기 수강신청 후 선발된 학생 대상.'
WHERE id = 206;

UPDATE scholarship SET
  amount_detail = '등록금 전액 면제(평점 1.69 이상 유지 조건)',
  application_period = NULL,
  application_method = '자동선발',
  description = '국가유공자(본인/자녀 등) 대상.'
WHERE id = 207;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '자동선발',
  description = '2인 이상 직계가족이 동시 재학 중인 학생 대상.'
WHERE id = 208;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '교무위원회 심의',
  description = '재해 발생 학생 대상.'
WHERE id = 209;

UPDATE scholarship SET
  amount_detail = '1등: 50만원
2~3등: 30만원
지역대회: 10만원',
  application_period = NULL,
  application_method = '자동선발',
  description = '국제·전국 규모 경시·경연대회 또는 지역대회 입상자 대상.'
WHERE id = 210;

UPDATE scholarship SET
  amount_detail = '경기 수상실적 고려하여 차등 지급',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '체육특기자 전형 입학생 대상.'
WHERE id = 211;

UPDATE scholarship SET
  amount_detail = '대대장: 등록금 100%
참모·소대장: 등록금 70%
일반: 등록금 50%
(+ 기숙사비 전액 면제)',
  application_period = NULL,
  application_method = '자동선발',
  description = '학군단(ROTC) 후보생 대상.'
WHERE id = 212;

UPDATE scholarship SET
  amount_detail = '평점 4.3 이상(4.5만점 기준): 등록금 100%
4.15 이상: 70%
3.0 이상: 30%',
  application_period = NULL,
  application_method = '자동선발',
  description = '외국인 유학생 대상.'
WHERE id = 213;

UPDATE scholarship SET
  amount_detail = '등록금 전액 면제',
  application_period = NULL,
  application_method = '추천(개발도상국 정부 추천)',
  description = '개발도상국 정부 추천을 받은 외국인 유학생 대상.'
WHERE id = 214;

UPDATE scholarship SET
  amount_detail = '국내연수 1회 + 해외연수 1회 기회 제공',
  application_method = '신청',
  description = '1~4학년 재학생 중 직전학기(들) 15학점 이상 취득·F학점 없음 + 다음 중 하나 충족: 전체 평점평균 4.00 이상(4.5만점), 국제/전국 규모 경시대회 3위 이내 입상, 외국어성적 우수(TOEIC 850점 이상 등), 글로벌 리더(별도 선발).'
WHERE id = 215;
