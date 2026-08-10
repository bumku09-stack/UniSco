"""Layer 2 — LLM 구조화 추출. 문서 1건 = 호출 1건, 상태 없음.

Anthropic API를 직접 호출함(LangChain 없음). 출력은 tool-use로 스키마를 강제해서 필드마다
`field_value` + `source_quote`를 같이 받고, enum 필드는 JSON Schema의 `enum`으로 값 자체를
제한함 — 모델이 존재하지 않는 분류값을 만들어내는 걸 스키마 레벨에서 막는다(설계안 3.2절
"출력 스키마를 구조화로 강제" 참고).

숫자 핵심 필드의 2중 추출은 이 함수를 그대로 두 번 호출하는 방식으로 구현됨(verify.py가
호출) — extract.py 자체엔 "이번이 몇 번째 호출인지" 같은 상태가 없음.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import anthropic

from harness import config
from harness.models import SCHOLARSHIP_FIELD_NAMES, ExtractedField, ExtractedScholarship

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# enums.py/supabase/README.md와 정확히 값이 같아야 함 — backend를 하네스의 의존성으로
# 끌어오지 않기 위해(harness/requirements.txt에 FastAPI/SQLModel을 추가하고 싶지 않음)
# 여기 값을 그대로 미러링함. 백엔드 enum이 바뀌면 여기와 extraction_spec.md도 같이 고칠 것.
_GENDER = ["male", "female"]
_MILITARY_STATUS = ["completed", "exempted", "not_served"]
_GPA_BASIS = ["semester", "cumulative", "both"]
_DISABILITY_TYPE = [
    "physical_impairment",
    "learning_disability",
    "medical_disability",
    "mental_impairment",
    "muscular_dystrophy",
    "developmental_impairment",
    "disabled_parent",
]
_FOREIGNER_ELIGIBILITY = ["korean_only", "foreigner_only"]
_LANGUAGE_TEST_TYPE = ["TOEIC", "TOEFL", "IELTS", "TOPIK", "기타"]
_SPECIAL_STATUS = [
    "north_korean_defector",
    "multicultural_family",
    "child_care_facility",
    "student_council_officer",
    "single_parent_family",
    "grandparent_family",
    "multi_child_family",
    "national_merit",
    "basic_livelihood_recipient",
    "near_poor",
    "severe_illness_or_injury",
    "job_loss_or_disaster",
    "financial_emergency",
    # 2026-08-10 승격 — national_merit과 같은 명확한 법적 지위라 일반 선택 항목으로 옮김
    # (예전엔 UNVERIFIABLE_CONDITIONS였음, backend/app/models/enums.py 참고).
    "righteous_person_family_condition",
    # UNVERIFIABLE_CONDITIONS (매칭 필드는 없지만 표시·랭킹용으로 태그만 하는 것들 — 2026-08-10
    # 기준 sub_region_residence_condition은 district 매칭으로 실제 해결돼서 여기서 빠짐)
    "parent_occupation_condition",
    "religious_or_career_intent_condition",
    "hometown_school_region_condition",
    "suneung_score_condition",
    "school_record_condition",
    "credit_requirement_condition",
    "extracurricular_program_condition",
]
_ENROLLMENT_STATUS = ["undergrad_enrolled", "undergrad_transfer", "undergrad_leave", "post_undergrad"]
_DEGREE_LEVEL = ["masters", "doctoral", "integrated_ms_phd"]
_CATEGORY_L1 = ["school_internal", "school_external", "support_fund"]
_CATEGORY_L2 = [
    "academic_merit",
    "welfare_living",
    "special_target",
    "activity_merit",
    "research",
    "international_exchange",
    "department_alumni",
    "national_scholarship",
    "local_gov",
    "private_foundation",
    "association",
    "youth_living_support",
    "activity_participation_support",
]

# 필드별 field_value의 JSON Schema. "null 허용"으로 "원문에 근거 없어 비움"을 표현함.
_FIELD_VALUE_SCHEMAS: dict[str, dict] = {
    "name": {"type": ["string", "null"]},
    "provider": {"type": ["string", "null"]},
    "description": {"type": ["string", "null"]},
    "amount": {"type": ["integer", "null"]},
    "application_url": {"type": ["string", "null"]},
    "min_age": {"type": ["integer", "null"]},
    "max_age": {"type": ["integer", "null"]},
    "required_gender": {"type": ["string", "null"], "enum": [*_GENDER, None]},
    "eligible_region": {"type": ["string", "null"]},
    "required_military_status": {"type": ["string", "null"], "enum": [*_MILITARY_STATUS, None]},
    "max_income_bracket": {"type": ["integer", "null"]},
    "min_gpa": {"type": ["number", "null"]},
    "min_gpa_basis": {"type": ["string", "null"], "enum": [*_GPA_BASIS, None]},
    "requires_disability": {"type": ["boolean", "null"]},
    "required_disability_type": {"type": ["string", "null"], "enum": [*_DISABILITY_TYPE, None]},
    "foreigner_eligibility": {"type": ["string", "null"], "enum": [*_FOREIGNER_ELIGIBILITY, None]},
    "language_test_type": {"type": ["string", "null"], "enum": [*_LANGUAGE_TEST_TYPE, None]},
    "language_test_min_score": {"type": ["number", "null"]},
    "required_special_status": {
        "type": "array",
        "items": {"type": "string", "enum": _SPECIAL_STATUS},
        "description": "빈 배열 = 특수상황 조건 없음",
    },
    "application_deadline": {"type": ["string", "null"], "description": "YYYY-MM-DD, 확정 마감일이 있을 때만"},
    "grade_level": {"type": ["string", "null"]},
    "major": {"type": ["string", "null"]},
    "affiliated_institution": {"type": ["string", "null"]},
    "min_credits": {"type": ["string", "null"]},
    "admission_score_condition": {"type": ["string", "null"]},
    "headcount": {"type": ["string", "null"]},
    "application_period": {"type": ["string", "null"]},
    "eligible_university": {"type": ["string", "null"]},
    "eligible_college": {"type": ["string", "null"]},
    "required_enrollment_status": {"type": ["string", "null"], "enum": [*_ENROLLMENT_STATUS, None]},
    "min_grade": {"type": ["integer", "null"]},
    "max_grade": {"type": ["integer", "null"]},
    "required_degree_level": {"type": ["string", "null"], "enum": [*_DEGREE_LEVEL, None]},
    "category_l1": {"type": ["string", "null"], "enum": [*_CATEGORY_L1, None]},
    "category_l2": {"type": ["string", "null"], "enum": [*_CATEGORY_L2, None]},
}

assert set(_FIELD_VALUE_SCHEMAS) == set(SCHOLARSHIP_FIELD_NAMES), (
    "extract.py의 _FIELD_VALUE_SCHEMAS가 models.SCHOLARSHIP_FIELD_NAMES와 어긋남 — "
    "필드 추가/삭제 시 둘 다 같이 고칠 것."
)


@lru_cache(maxsize=1)
def load_extraction_spec() -> str:
    return (_PROMPTS_DIR / "extraction_spec.md").read_text(encoding="utf-8")


def _build_input_schema() -> dict:
    properties = {}
    for name in SCHOLARSHIP_FIELD_NAMES:
        properties[name] = {
            "type": "object",
            "properties": {
                "field_value": _FIELD_VALUE_SCHEMAS[name],
                "source_quote": {
                    "type": "string",
                    "description": "field_value의 근거가 된 원문 문장 그대로. 값이 없으면 빈 문자열.",
                },
            },
            "required": ["field_value", "source_quote"],
        }
    return {"type": "object", "properties": properties, "required": list(SCHOLARSHIP_FIELD_NAMES)}


def extract_scholarship(source_text: str, source_url: str) -> ExtractedScholarship:
    """공고문 원문 1건을 구조화된 필드로 변환. 상태 없음 — 이전 호출 결과를 참조하지 않음."""
    client = anthropic.Anthropic()
    tool = {
        "name": "extract_scholarship",
        "description": (
            "장학금 공고문 원문에서 구조화된 필드를 추출한다. "
            "각 필드는 값(field_value)과 그 근거가 된 원문 인용(source_quote)을 함께 반환해야 한다."
        ),
        "input_schema": _build_input_schema(),
    }
    response = client.messages.create(
        model=config.EXTRACTION_MODEL,
        max_tokens=config.EXTRACTION_MAX_TOKENS,
        system=load_extraction_spec(),
        tools=[tool],
        tool_choice={"type": "tool", "name": "extract_scholarship"},
        messages=[
            {
                "role": "user",
                "content": f"공고문 원문 (출처: {source_url}):\n\n{source_text}",
            }
        ],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    raw: dict = tool_use_block.input  # type: ignore[assignment]

    fields: dict[str, ExtractedField] = {}
    for name in SCHOLARSHIP_FIELD_NAMES:
        entry = raw.get(name) or {}
        is_list_field = _FIELD_VALUE_SCHEMAS[name].get("type") == "array"
        value = entry.get("field_value")
        if value is None and is_list_field:
            value = []
        fields[name] = ExtractedField(value=value, source_quote=entry.get("source_quote") or "")

    return ExtractedScholarship(source_url=source_url, fields=fields)
