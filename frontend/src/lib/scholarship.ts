import { DISABILITY_TYPES, LANGUAGE_TESTS, SPECIAL_STATUS_OPTIONS } from "@/lib/spec";

export type Scholarship = {
  id: number;
  name: string;
  provider: string | null;
  description: string | null;
  amount: number | null;
  application_url: string | null;
  application_period: string | null;
  application_deadline: string | null; // ISO date (YYYY-MM-DD) — application_period가 자유 텍스트라 정렬용으로 따로 있는 구조화된 값
  min_age: number | null;
  max_age: number | null;
  required_gender: "male" | "female" | null;
  eligible_region: string | null;
  required_military_status: "completed" | "exempted" | "not_served" | null;
  max_income_bracket: number | null;
  min_gpa: number | null;
  min_gpa_basis: "semester" | "cumulative" | "both" | null;
  requires_disability: boolean | null;
  required_disability_type: string | null;
  foreigner_eligibility: "korean_only" | "foreigner_only" | null;
  language_test_type: string | null;
  language_test_min_score: number | null;
  required_special_status: string[];
  eligible_university: string | null;
  eligible_college: string | null;
  required_enrollment_status: "undergrad_enrolled" | "undergrad_transfer" | "undergrad_leave" | "post_undergrad" | null;
  min_grade: number | null;
  max_grade: number | null;
  required_degree_level: "masters" | "doctoral" | "integrated_ms_phd" | null;
  category_l1: "school_internal" | "school_external" | "support_fund" | null;
  category_l2: string | null;
  // 매칭 로직에는 안 쓰이지만(수동 확인 필요 원문 텍스트), 상세 페이지 참고용 표시엔 씀
  major: string | null;
  min_credits: string | null;
  admission_score_condition: string | null;
  headcount: string | null;
};

export function formatAmount(amount: number | null) {
  if (amount == null) return null;
  return `${amount.toLocaleString("ko-KR")}원`;
}

const MILITARY_LABEL: Record<string, string> = {
  completed: "군필",
  exempted: "면제",
  not_served: "미필",
};

const GPA_BASIS_LABEL: Record<string, string> = {
  semester: "직전학기",
  cumulative: "누적",
  both: "직전학기·누적 모두",
};

const ENROLLMENT_STATUS_LABEL: Record<string, string> = {
  undergrad_enrolled: "학부 재학",
  undergrad_transfer: "학부 편입",
  undergrad_leave: "학부 휴학",
  post_undergrad: "대학원 등",
};

const DEGREE_LEVEL_LABEL: Record<string, string> = {
  masters: "석사",
  doctoral: "박사",
  integrated_ms_phd: "석박사통합",
};

// min/max 둘 다 있는데 값이 같으면(예: 신입생 전용 장학금이 min_grade=max_grade=1로 저장됨)
// "1~1학년"처럼 범위 표기가 무의미하게 중복돼서 보이던 문제(2026-08-11 발견) — 케이스별로
// 자연스러운 문구를 고름. 학년/나이 둘 다 이 함수를 씀.
function formatRange(min: number | null, max: number | null, unit: string): string {
  if (min != null && max != null) {
    return min === max ? `${min}${unit}` : `${min}~${max}${unit}`;
  }
  if (min != null) return `${min}${unit} 이상`;
  return `${max}${unit} 이하`;
}

function eligibilityParts(s: Scholarship): string[] {
  const parts: string[] = [];
  if (s.eligible_university) parts.push(`대학: ${s.eligible_university}`);
  if (s.eligible_college) parts.push(`단과대: ${s.eligible_college}`);
  // major_matches()가 실제로 필터링에 쓰는 필드인데(backend/app/core/matching.py) 프론트
  // 목록에서 빠져있던 버그 — 2026-08-11 발견, 여기로 옮김(예전엔 "참고조건"으로 잘못 표시).
  if (s.major) parts.push(`전공: ${s.major}`);
  if (s.required_enrollment_status) {
    parts.push(`재학상태: ${ENROLLMENT_STATUS_LABEL[s.required_enrollment_status]}`);
  }
  if (s.required_degree_level) parts.push(`과정: ${DEGREE_LEVEL_LABEL[s.required_degree_level]}`);
  if (s.min_grade != null || s.max_grade != null) {
    parts.push(`학년: ${formatRange(s.min_grade, s.max_grade, "학년")}`);
  }
  if (s.eligible_region) parts.push(`거주지역: ${s.eligible_region}`);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`나이: ${formatRange(s.min_age, s.max_age, "세")}`);
  }
  if (s.max_income_bracket != null) parts.push(`소득분위 ${s.max_income_bracket} 이하`);
  if (s.min_gpa != null) {
    const basis = s.min_gpa_basis ? `${GPA_BASIS_LABEL[s.min_gpa_basis]} ` : "";
    parts.push(`${basis}학점 ${s.min_gpa} 이상`);
  }
  if (s.required_military_status) parts.push(`병역: ${MILITARY_LABEL[s.required_military_status]}`);
  if (s.required_gender) parts.push(`성별: ${s.required_gender === "male" ? "남성" : "여성"}`);
  if (s.requires_disability) {
    const type = s.required_disability_type
      ? DISABILITY_TYPES.find((d) => d.value === s.required_disability_type)?.label
      : null;
    parts.push(type ? `장애인 한정 (${type})` : "장애인 한정");
  }
  if (s.foreigner_eligibility) {
    parts.push(s.foreigner_eligibility === "foreigner_only" ? "외국인 한정" : "내국인 한정");
  }
  if (s.language_test_type) {
    const test = LANGUAGE_TESTS.find((t) => t.value === s.language_test_type)?.label ?? s.language_test_type;
    parts.push(
      s.language_test_min_score != null ? `어학점수: ${test} ${s.language_test_min_score} 이상` : `어학점수: ${test}`
    );
  }
  // 학생이 프로필에서 실제로 선택 가능한 태그만 여기 포함 — UNVERIFIABLE_SPECIAL_STATUS_LABELS에
  // 있는 "확인 불가"(랭킹 전용, 선택 불가) 태그는 여기서 빼고 unverifiableConditionParts()로
  // 따로 뺌(2026-08-11, "parent_occupation_condition"이라는 원본 값 그대로 노출되던 버그 수정).
  const selectableSpecialStatus = s.required_special_status.filter((v) => v in SPECIAL_STATUS_LABEL_MAP);
  if (selectableSpecialStatus.length > 0) {
    const labels = selectableSpecialStatus.map((v) => SPECIAL_STATUS_LABEL_MAP[v] ?? v);
    parts.push(`특수상황: ${labels.join(" 또는 ")}`);
  }
  return parts;
}

const SPECIAL_STATUS_LABEL_MAP: Record<string, string> = Object.fromEntries(
  SPECIAL_STATUS_OPTIONS.map((o) => [o.value, o.label])
);

// 학생이 프로필에서 고를 방법 자체가 없는 "확인 불가"(랭킹 전용) 특수상황 태그 — 프론트
// SPECIAL_STATUS_OPTIONS에는 의도적으로 빠져있음(backend/app/models/enums.py의
// UNVERIFIABLE_CONDITIONS와 동일한 목록). 상세페이지에서 "직접 확인 필요"(노란 점)로
// 따로 보여주기 위한 한글 라벨.
const UNVERIFIABLE_SPECIAL_STATUS_LABELS: Record<string, string> = {
  parent_occupation_condition: "부모님 직업/소속 조건",
  religious_or_career_intent_condition: "종교기관 소속·직분 또는 진로 지향 조건",
  hometown_school_region_condition: "출신 학교/출신지 기준 조건",
  suneung_score_condition: "수능 성적 기준 조건",
  school_record_condition: "내신 성적 기준 조건",
  credit_requirement_condition: "이수학점 조건(원문 확인 필요)",
  extracurricular_program_condition: "학교 자체 비교과 프로그램 이수 조건",
};

// 상세페이지 "직접 확인 필요"(노란 점) 목록용 — required_special_status 중 학생이 선택할
// 방법이 없는 태그들을 한글 라벨로 변환.
export function unverifiableConditionParts(s: Scholarship): string[] {
  return s.required_special_status
    .map((v) => UNVERIFIABLE_SPECIAL_STATUS_LABELS[v])
    .filter((label): label is string => Boolean(label));
}

// 목록 카드용 — 한 줄 요약
export function eligibilitySummary(s: Scholarship): string {
  const parts = eligibilityParts(s);
  return parts.length > 0 ? parts.join(" · ") : "제한 없음";
}

// 상세페이지용 — 항목별로 나눠서 bullet list로 보여주기 위한 배열
export function eligibilityList(s: Scholarship): string[] {
  const parts = eligibilityParts(s);
  return parts.length > 0 ? parts : ["별도 제한 없음"];
}

export const CATEGORY_L2_LABEL: Record<string, string> = {
  academic_merit: "성적",
  welfare_living: "복지생활지원",
  special_target: "특수대상",
  activity_merit: "활동공로",
  research: "연구",
  international_exchange: "국제교류",
  department_alumni: "학과동문회",
  national_scholarship: "국가장학금",
  local_gov: "지자체",
  private_foundation: "민간재단",
  association: "협회학회",
  youth_living_support: "청년생활지원",
  activity_participation_support: "활동참여지원",
};

export type CategoryL1 = "school_internal" | "school_external" | "support_fund";

// backend/app/models/enums.py의 CategoryL1/CategoryL2, CATEGORY_L2_BY_L1과 동일하게 유지할 것.
export const CATEGORY_L1_LABEL: Record<CategoryL1, string> = {
  school_internal: "교내장학금",
  school_external: "교외장학금",
  support_fund: "지원금",
};

export const CATEGORY_L2_BY_L1: Record<CategoryL1, string[]> = {
  school_internal: [
    "academic_merit",
    "welfare_living",
    "special_target",
    "activity_merit",
    "research",
    "international_exchange",
    "department_alumni",
  ],
  school_external: ["national_scholarship", "local_gov", "private_foundation", "association"],
  support_fund: ["youth_living_support", "activity_participation_support"],
};

export type SortBy = "relevance" | "amount" | "deadline";

export function sortScholarships(list: Scholarship[], sortBy: SortBy): Scholarship[] {
  const copy = [...list];
  if (sortBy === "amount") {
    copy.sort((a, b) => (b.amount ?? -1) - (a.amount ?? -1));
  } else if (sortBy === "relevance") {
    // 백엔드가 core/matching.py의 personal_fit_key()로 이미 적합도순 정렬해서 내려줌 — 여기선 재정렬 없이 그대로 둠.
  } else {
    // application_deadline(구조화된 date)이 있는 항목은 가까운 마감일순으로, 없는 항목은
    // (상시/반복 공고 등, matching_gaps.md #7) 뒤로 보내고 application_period 원문 텍스트로 보조 정렬.
    copy.sort((a, b) => {
      if (a.application_deadline && b.application_deadline) {
        return a.application_deadline.localeCompare(b.application_deadline);
      }
      if (a.application_deadline) return -1;
      if (b.application_deadline) return 1;
      return (a.application_period ?? "").localeCompare(b.application_period ?? "", "ko");
    });
  }
  return copy;
}
