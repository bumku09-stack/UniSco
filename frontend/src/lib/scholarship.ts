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
    parts.push(`학년: ${s.min_grade ?? ""}~${s.max_grade ?? ""}학년`);
  }
  if (s.eligible_region) parts.push(`거주지역: ${s.eligible_region}`);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`나이: ${s.min_age ?? ""}~${s.max_age ?? ""}세`);
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
  if (s.required_special_status.length > 0) {
    const labels = s.required_special_status.map(
      (v) => SPECIAL_STATUS_OPTIONS.find((o) => o.value === v)?.label ?? v
    );
    parts.push(`특수상황: ${labels.join(" 또는 ")}`);
  }
  return parts;
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
