export type Scholarship = {
  id: number;
  name: string;
  provider: string | null;
  description: string | null;
  amount: number | null;
  application_url: string | null;
  application_period: string | null;
  min_age: number | null;
  max_age: number | null;
  required_gender: "male" | "female" | null;
  eligible_region: string | null;
  required_military_status: "completed" | "exempted" | "not_served" | null;
  max_income_bracket: number | null;
  min_gpa: number | null;
  requires_disability: boolean | null;
  foreigner_eligibility: "korean_only" | "foreigner_only" | null;
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

function eligibilityParts(s: Scholarship): string[] {
  const parts: string[] = [];
  if (s.eligible_region) parts.push(`거주지역: ${s.eligible_region}`);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`나이: ${s.min_age ?? ""}~${s.max_age ?? ""}세`);
  }
  if (s.max_income_bracket != null) parts.push(`소득분위 ${s.max_income_bracket} 이하`);
  if (s.min_gpa != null) parts.push(`학점 ${s.min_gpa} 이상`);
  if (s.required_military_status) parts.push(`병역: ${MILITARY_LABEL[s.required_military_status]}`);
  if (s.required_gender) parts.push(`성별: ${s.required_gender === "male" ? "남성" : "여성"}`);
  if (s.requires_disability) parts.push("장애인 한정");
  if (s.foreigner_eligibility) {
    parts.push(s.foreigner_eligibility === "foreigner_only" ? "외국인 한정" : "내국인 한정");
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
    // 매칭적합도 산정 알고리즘은 호성이 백엔드에서 설계 중 — 결과가 생기면 그 값 기준으로
    // 정렬하도록 여기만 교체하면 됨. 그 전까지는 /match가 준 순서를 그대로 신뢰(재정렬 없음).
  } else {
    // 마감일(application_period)이 아직 자유 텍스트라 정확한 날짜 정렬은 불가능함
    // (supabase/matching_gaps.md #7) — 문자열 기준 임시 정렬, 구조화된 date 컬럼이 생기면 교체할 것.
    copy.sort((a, b) => (a.application_period ?? "").localeCompare(b.application_period ?? "", "ko"));
  }
  return copy;
}
