# -*- coding: utf-8 -*-
"""장학금 데이터의 description(원문 설명글)과 구조화 컬럼이 서로 앞뒤가 맞는지 확인하는
공용 판정 함수 모음.

배경: "문화예술인재학부장학금"(현대차 정몽구 재단) 레코드에 description엔 "음악·무용 전공...
해당 전공자 외 지원불가"라고 다 적혀 있는데 major 컬럼은 NULL로 남아있던 사례, "대전 인재육성
장학사업(꿈돌이장학금 등)" 레코드엔 amount가 NULL인데 다른 컬럼엔 '확인 필요'라는 플레이스홀더
문자열이 실제 값처럼 박혀있던 사례가 발견됨(2026-08-07). matching.py의 거의 모든 매칭 함수는
"구조화 필드가 비어있으면 무조건 통과"로 설계돼 있어서(의도적 — 과다매칭이 과소매칭보다
덜 해로움), description에 조건이 명시돼 있는데 구조화 컬럼 전사를 빠뜨리면 정반대로 작동해서
조건 없는 것처럼 전 국민에게 노출됨.

이 파일의 함수들은 두 곳에서 재사용됨:
1. 배치 SQL 생성 스크립트(gen_batchN.py 패턴) — 새 데이터를 넣기 전 하드 게이트.
2. supabase/tools/audit_description_gaps.py — 기존 라이브 DB 전체 재감사.

규칙(키워드/정규식)은 이 파일 하나에서만 관리 — 감사 스크립트와 배치 스크립트가 서로 다른
규칙을 쓰면 어긋날 수 있으므로.

한계: 정규식/키워드 기반이라 100% 못 잡음(자연어 표현은 무한하므로). 그래서 이 자동 검사는
"1차 그물"이고, 원문 재검증(사람 또는 조사 에이전트가 실제 공고 원문과 다시 대조하는 것)이
최종 확인 단계 — matching_gaps.md에 새 놓친 사례가 나올 때마다 아래 패턴 목록에 반영해서
그물을 계속 키워나갈 것.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# A) 플레이스홀더 값 스캔 — 컬럼 값 자체가 "확인 필요" 류 메모인 경우 (오탐 거의 없음)
# ---------------------------------------------------------------------------

# 값이 "포함"만 해도 걸리도록(짧은 메모가 다른 텍스트 없이 그 컬럼의 전부인 경우가 대부분이라
# contains로도 충분히 정밀함 — 예: "확인 필요(4월 중 공지 예정)"도 잡아야 함).
PLACEHOLDER_PATTERNS = [
    "확인 필요", "확인필요", "확인 요망", "확인요망",
    "미정", "추후 공지", "추후공지", "추후 확인", "추후확인",
    "별도 공지", "별도공지", "별도 문의", "별도문의",
    "재확인 필요", "재확인필요", "TBD", "tbd",
]

# 플레이스홀더가 실제 값 자리에 들어갈 위험이 있는 자유 텍스트 컬럼만 검사.
# (description은 원문 설명 산문이라 이런 문구가 캐주얼하게 섞여 있어도 정상 — 검사 대상 아님.
#  amount/application_deadline 등 숫자/날짜 타입 컬럼은애초에 문자열이 안 들어가므로 제외.)
PLACEHOLDER_CHECK_COLUMNS = [
    "provider",
    "eligible_region",
    "major",
    "grade_level",
    "affiliated_institution",
    "min_credits",
    "admission_score_condition",
    "headcount",
    "application_period",
    "eligible_university",
    "eligible_college",
]


def find_placeholder_values(row: dict) -> dict[str, str]:
    """row(컬럼명→값 dict)에서 플레이스홀더 문자열이 실제 값처럼 박혀있는 컬럼을 찾음.
    반환값: {컬럼명: 걸린 값}. 비어있으면 문제 없음."""
    found: dict[str, str] = {}
    for col in PLACEHOLDER_CHECK_COLUMNS:
        value = row.get(col)
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if not stripped:
            continue
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.lower() in stripped.lower():
                found[col] = value
                break
    return found


# ---------------------------------------------------------------------------
# B) 자격조건 키워드 vs NULL, C) 금액/인원/기간 키워드 vs NULL
# ---------------------------------------------------------------------------

# field label -> (이 중 하나라도 값이 있으면 통과시킬 컬럼 목록, description에서 찾을 정규식 목록)
FIELD_GAP_RULES: dict[str, tuple[list[str], list[str]]] = {
    "major": (
        ["major"],
        [r"전공", r"학과.{0,4}(만|한정)", r"해당\s*전공", r"전공자\s*외", r"전공.{0,4}지원\s*불가"],
    ),
    # "차상위"/"기초생활수급자" 등은 소득분위 숫자가 아니라 특수상황 태그로 표현하는 게 맞는
    # 경우가 많아(2026-08-10, id=232 사례) max_income_bracket 규칙에서 빼고 아래
    # special_status 규칙으로 옮김. 여기는 "소득분위 N" 형태의 숫자 조건만 남김.
    "min_gpa": (
        ["min_gpa"],
        [r"평점", r"학점\s*[0-9]", r"GPA", r"성적.{0,3}등급\s*이내"],
    ),
    "max_income_bracket": (
        ["max_income_bracket"],
        [r"소득분위", r"중위소득"],
    ),
    "disability": (
        ["requires_disability", "required_disability_type"],
        [r"장애인", r"장애.{0,2}등급", r"장애\s*[0-9]급"],
    ),
    "foreigner_eligibility": (
        ["foreigner_eligibility"],
        [r"외국인", r"재외동포", r"유학생"],
    ),
    "language_test_type": (
        ["language_test_type"],
        [r"토익", r"TOEIC", r"TOEFL", r"IELTS", r"어학\s*성적", r"어학\s*점수"],
    ),
    "enrollment_or_degree": (
        ["required_enrollment_status", "required_degree_level"],
        [r"대학원생만", r"학부생만", r"재학생만", r"신입생만"],
    ),
    "amount": (
        ["amount"],
        [r"[0-9][0-9,]{2,}\s*만?\s*원"],
    ),
    "headcount": (
        ["headcount"],
        [r"[0-9]+\s*명"],
    ),
    "period_or_deadline": (
        ["application_period", "application_deadline"],
        [r"매년\s*[0-9]+\s*월", r"20[0-9]{2}[-./]\s*[0-9]{1,2}[-./]\s*[0-9]{1,2}", r"20[0-9]{2}년\s*[0-9]+월"],
    ),
    # 2026-08-10 추가 — 지금까지 자동검사에 아예 없었던 항목들(data_collection_guide.md
    # 체크리스트 21개 중 아래 8개는 이번까지 자동검사 커버리지가 0건이었음).
    "special_status": (
        ["required_special_status"],
        [
            r"다문화가정", r"새터민", r"북한이탈주민", r"한부모가정", r"조손가정",
            r"다자녀", r"자녀\s*[2-9]\s*(명|인)", r"국가유공자", r"보훈대상자",
            r"기초생활수급자", r"기초수급", r"차상위", r"중증질병", r"실직가정",
            r"재난.{0,4}(피해|가정)", r"긴급가계곤란", r"의사상자",
            r"학생회.{0,4}(임원|회장)", r"학생자치단체.{0,4}임원", r"아동양육시설",
        ],
    ),
    "excluded_major": (
        ["excluded_major"],
        [r"전공.{0,6}제외", r"학과.{0,6}제외"],
    ),
    "degree_level": (
        ["required_degree_level"],
        [r"석사", r"박사", r"석·박사", r"석박사"],
    ),
    "region": (
        ["eligible_region"],
        [r"거주자", r"거주.{0,4}[0-9]\s*년", r"관내\s*(거주|주민)", r"주민등록", r"전입"],
    ),
    "gender": (
        ["required_gender"],
        [r"여학생", r"남학생", r"여성\s*(만|한정)", r"남성\s*(만|한정)", r"^사모\b|\s사모\b"],
    ),
    "military_status": (
        ["required_military_status"],
        [r"군필", r"병역\s*(특례|의무|필)", r"미필자"],
    ),
    "age": (
        ["min_age", "max_age"],
        [r"만\s*[0-9]{1,2}\s*세", r"[0-9]{1,2}\s*세\s*(이하|미만|이상)"],
    ),
    "min_credits": (
        ["min_credits"],
        [r"[0-9]+\s*학점\s*(이상|이수)"],
    ),
    "admission_score_condition": (
        ["admission_score_condition"],
        [r"수능\s*(성적|등급|백분위)", r"내신\s*(성적|등급)", r"학생부.{0,4}(교과|종합)"],
    ),
}


def find_gaps(row: dict) -> list[str]:
    """description에 특정 필드의 조건을 암시하는 키워드가 있는데, 대응하는 구조화 컬럼이
    전부 비어있는 필드 이름 목록을 반환. row에 `_reviewed_gaps`(set)가 있으면 그 안에 있는
    필드는 "확인해봤는데 오탐"으로 간주하고 제외함(배치 스크립트에서 사용)."""
    desc = row.get("description") or ""
    reviewed = row.get("_reviewed_gaps") or set()
    flags: list[str] = []
    for field_name, (cols, patterns) in FIELD_GAP_RULES.items():
        if field_name in reviewed:
            continue
        if any(row.get(c) for c in cols):
            continue
        if any(re.search(p, desc) for p in patterns):
            flags.append(field_name)
    return flags


# ---------------------------------------------------------------------------
# 포괄적 제한문구 catch-all — 특정 필드를 몰라도 "여기 뭔가 제한이 있다"는 신호만 잡음
# ---------------------------------------------------------------------------

GENERIC_RESTRICTION_PATTERNS = [
    r"외\s*지원\s*불가", r"만\s*해당", r"에\s*한함", r"에\s*한정", r"만\s*지원\s*가능",
    r"만\s*지원가능", r"만\s*신청\s*가능", r"한정함", r"에\s*국한",
]

# 이미 이 정도로 구조화된 자격조건이 걸려있으면 "제한이 있다"는 사실 자체는 이미 반영된
# 것으로 보고, 포괄 규칙은 "전부 비어서 완전히 열려 보이는" 행에서만 최우선으로 울리게 함.
RESTRICTIVE_FIELDS = [
    "major", "min_gpa", "max_income_bracket", "requires_disability",
    "required_disability_type", "foreigner_eligibility", "language_test_type",
    "required_enrollment_status", "required_degree_level", "eligible_university",
    "eligible_college", "eligible_region", "required_gender", "required_military_status",
]


def find_generic_restriction_flag(row: dict) -> bool:
    """description에 강한 배제 문구가 있는데 구조화된 자격조건 필드가 전부(또는 거의) 비어
    있으면 True — 어느 필드에 대한 제한인지 특정 못 해도 "재확인 필요"로 행 전체를 플래그."""
    desc = row.get("description") or ""
    special_status = row.get("required_special_status") or []
    set_count = sum(1 for f in RESTRICTIVE_FIELDS if row.get(f)) + (1 if special_status else 0)
    if set_count > 0:
        return False
    return any(re.search(p, desc) for p in GENERIC_RESTRICTION_PATTERNS)
