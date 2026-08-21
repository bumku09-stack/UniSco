import { DISABILITY_TYPES, LANGUAGE_TESTS, SPECIAL_STATUS_OPTIONS } from "@/lib/spec";

export type Scholarship = {
  id: number;
  name: string;
  provider: string | null;
  description: string | null;
  amount: number | null;
  // 2026-08-14 추가 — 금액 상세 서술(지급주기/지급기간, 순위별 차등 등). 상세페이지 "금액"
  // 블록 표시용, 매칭에는 안 씀.
  amount_detail: string | null;
  application_url: string | null;
  application_period: string | null; // 신청 기간 (순수 날짜/기간만)
  application_deadline: string | null; // ISO date (YYYY-MM-DD) — application_period가 자유 텍스트라 정렬용으로 따로 있는 구조화된 값
  // 2026-08-14 추가 — 신청방식(자동선발/직접신청 등). 상세페이지 "신청방식" 블록 표시용.
  application_method: string | null;
  min_age: number | null;
  max_age: number | null;
  required_gender: "male" | "female" | null;
  eligible_region: string | null;
  required_military_status: "completed" | "exempted" | "not_served" | "rotc_candidate" | null;
  // 2026-08-15 추가 — required_military_status="completed"일 때만 의미 있음.
  required_discharge_type: "enlisted" | "officer_or_nco" | null;
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
  // 2026-08-14 추가 — "이 학과만 빼고 나머지 전부 됨"(major와 정반대 의미). 실제 매칭
  // 필터링에 씀(core/matching.py) — major와 동일하게 여태 상세페이지에 안 보이던 버그 발견.
  excluded_major: string | null;
  // 2026-08-14 추가 — 체육특기자 전형 등 입학전형 구분. 필드 자체는 있었는데 화면 어디에도
  // 안 보이던 버그 발견(체육특기자 장학금에서 "체육진흥원 추천자"를 admission_score_condition에
  // 잘못 넣어뒀던 걸 정리하다가 드러남).
  admission_track: "general" | "athletic_specialty" | "other_specialty" | null;
  min_credits: string | null;
  // 실제 매칭 필터링에 씀(core/matching.py의 credits_matches()) — min_credits(원문 텍스트)와
  // 별개. 채워져 있으면 상세페이지에서 파란 점(시스템이 확인한 조건)으로 표시.
  min_credits_last_semester: number | null;
  admission_score_condition: string | null;
  headcount: string | null;
  // 2026-08-21 추가 — 여러 조건 중 하나만 만족하면 통과하는 OR 그룹(core/matching.py의
  // alt_groups_match() 참고). 각 그룹은 이 표의 다른 필드와 같은 이름의 키를 담은 부분 객체
  // (예: [{language_test_type: "TOEFL", language_test_min_score: 90}, {...}]) — 실제
  // 필터링(백엔드)엔 이미 2026-08-14부터 쓰이고 있었는데, 화면(conditionParts)이 이 필드를
  // 몰라서 파란 점에 아예 안 보이던 버그를 여기서 같이 고침(major/min_credits_last_semester와
  // 동일한 종류의 반복 버그 — eligibilityParts 참고).
  eligibility_alt_groups: Record<string, unknown>[] | null;
};

export function formatAmount(amount: number | null) {
  if (amount == null) return null;
  return `${amount.toLocaleString("ko-KR")}원`;
}

// 2026-08-15 추가 — "신청하러 가기" 버튼이 실제로는 신청 폼이 아니라 학교 안내 목록
// 페이지로만 연결되는 자동선발 장학금(예: plus.cnu.ac.kr 재학생 장학금 목록)에서, 학생이
// 신청할 게 있는 줄 알고 눌렀다가 정보만 나와서 헷갈리는 문제 발견(사용자 지적) — 버튼
// 자체는 안 건드리고(잘못 판정해도 신청 기능이 사라지진 않게) 위에 안내 문구만 조건부로
// 추가하는 안전한 접근.
//
// application_method는 자유텍스트라 표현이 제각각(자동선발/자동지급/"자동 선발"처럼
// 띄어쓰기 있는 것/"학생 신청 대상 아님"/"~할 필요는 없음" 등) — 실제 운영 DB의 고유값
// 104개를 전부 검토해서 잡은 패턴. "단, ~는 본인이 직접 신청해야 함"처럼 예외조항이 있으면
// (자동선발 문구가 있어도) 안내를 안 띄움 — 잘못 숨겨서 학생이 진짜 필요한 신청을 놓치는
// 쪽이 버튼 문구가 부정확한 쪽보다 훨씬 나쁨.
const AUTO_SELECTED_SIGNAL =
  /자동\s?선발|자동\s?지급|별도\s?신청\s?(절차\s?)?(없|불필요)|신청\s?대상\s?아님|신청\s?(할)?\s?필요\s?(는\s?)?없|신청\s?불필요/;
const AUTO_SELECTED_OVERRIDE = /직접\s?신청해야|본인이.{0,4}신청|별도\s?기한/;

export function isAutoSelected(s: Scholarship): boolean {
  const method = s.application_method;
  if (!method) return false;
  return AUTO_SELECTED_SIGNAL.test(method) && !AUTO_SELECTED_OVERRIDE.test(method);
}

// 2026-08-15 추가 — 위 isAutoSelected()는 application_method 텍스트가 있어야만 판단
// 가능한데, harness/reverify.py가 원문에 근거 없는 값을 정리하면서(id=59 등 62건)
// application_method가 null이 된 레코드들에선 이 판정 자체가 항상 false가 돼서 안내
// 문구가 안 뜨는 구멍이 생김(사용자 지적, scholarship/59) — application_url을 직접
// fetch+파싱해서 재확인해보니(2026-08-15) 이 URL 자체에 신청기간/신청방식/신청기한/
// 접수기간/지원신청/신청서/신청방법 키워드가 전부 0건 — 65건 전체가 공유하는 이 URL은
// 애초에 "안내 목록" 페이지일 뿐 신청 관련 정보가 아예 없음(개별 레코드의 값 추측이
// 아니라 페이지 자체를 직접 확인한 사실). application_method 값 유무와 무관하게 이
// URL로 연결되는 건 항상 캡션을 띄움.
const KNOWN_LISTING_ONLY_URLS = new Set([
  "https://plus.cnu.ac.kr/html/hub/support/support_030302.html",
]);

export function isListingOnlyUrl(url: string | null): boolean {
  return url != null && KNOWN_LISTING_ONLY_URLS.has(url);
}

const MILITARY_LABEL: Record<string, string> = {
  completed: "군필",
  exempted: "면제",
  not_served: "미필",
  rotc_candidate: "학군사관후보생(ROTC)",
};

const DISCHARGE_TYPE_LABEL: Record<string, string> = {
  enlisted: "병사 전역",
  officer_or_nco: "장교/부사관 전역",
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

// 2026-08-14: 학점 만점 기준은 대학마다 다름(예: KAIST 4.3만점) — min_gpa는 항상 4.5만점
// 기준으로 저장돼 있는데(backend/app/core/matching.py 주석 참고), 그대로 보여주면 4.3만점
// 대학 학생은 자기 학점표랑 숫자가 안 맞아서 헷갈림. 학생이 스펙에 대학을 등록해뒀으면
// (viewerGpaScale로 전달됨) 그 대학 기준으로 환산해서 보여주고, 모르면 기존처럼 4.5만점
// 기준 그대로 보여줌.
// eligibilityParts와 그룹 표시(altGroupsText) 둘 다 재사용 — 장학금 "몸통"이든
// eligibility_alt_groups의 그룹 하나든 같은 모양(부분 객체)이면 똑같은 필드 판독 로직을
// 그대로 쓰게 뜯어냄(2026-08-21). 예전엔 이 로직이 몸통 하나만 받게 짜여있어서, 새 필드가
// 생길 때마다(major, min_credits_last_semester 등 — 아래 주석 참고) 몸통 표시만 챙기고
// 그룹 표시는 깜빡하는 사고가 반복됐음 — 로직을 하나로 합쳐서 필드 하나만 추가하면 몸통·
// 그룹 둘 다 자동으로 반영되게 함.
function conditionParts(s: Partial<Scholarship>, viewerGpaScale?: number): string[] {
  const parts: string[] = [];
  if (s.eligible_university) parts.push(`대학: ${s.eligible_university}`);
  if (s.eligible_college) parts.push(`단과대: ${s.eligible_college}`);
  // major_matches()가 실제로 필터링에 쓰는 필드인데(backend/app/core/matching.py) 프론트
  // 목록에서 빠져있던 버그 — 2026-08-11 발견, 여기로 옮김(예전엔 "참고조건"으로 잘못 표시).
  if (s.major) parts.push(`전공: ${s.major}`);
  if (s.excluded_major) parts.push(`제외 전공: ${s.excluded_major}`);
  if (s.admission_track === "athletic_specialty") parts.push("입학전형: 체육특기자 전형");
  if (s.admission_track === "other_specialty") parts.push("입학전형: 기타 특기자·특별전형(농어촌·정원외 등)");
  if (s.required_enrollment_status) {
    parts.push(`재학상태: ${ENROLLMENT_STATUS_LABEL[s.required_enrollment_status]}`);
  }
  if (s.required_degree_level) parts.push(`과정: ${DEGREE_LEVEL_LABEL[s.required_degree_level]}`);
  if (s.min_grade != null || s.max_grade != null) {
    parts.push(`학년: ${formatRange(s.min_grade ?? null, s.max_grade ?? null, "학년")}`);
  }
  if (s.eligible_region) parts.push(`거주지역: ${s.eligible_region}`);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`나이: ${formatRange(s.min_age ?? null, s.max_age ?? null, "세")}`);
  }
  if (s.max_income_bracket != null) parts.push(`소득분위 ${s.max_income_bracket} 이하`);
  if (s.min_gpa != null) {
    const basis = s.min_gpa_basis ? `${GPA_BASIS_LABEL[s.min_gpa_basis]} ` : "";
    if (viewerGpaScale != null && viewerGpaScale !== 4.5) {
      const converted = Math.round((s.min_gpa * (viewerGpaScale / 4.5)) * 100) / 100;
      parts.push(`${basis}학점 ${converted} 이상 (${viewerGpaScale}만점 기준)`);
    } else {
      parts.push(`${basis}학점 ${s.min_gpa} 이상`);
    }
  }
  if (s.required_military_status) {
    const discharge = s.required_discharge_type
      ? `(${DISCHARGE_TYPE_LABEL[s.required_discharge_type]})`
      : "";
    parts.push(`병역: ${MILITARY_LABEL[s.required_military_status]}${discharge}`);
  }
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
  const selectableSpecialStatus = (s.required_special_status ?? []).filter(
    (v) => v in SPECIAL_STATUS_LABEL_MAP
  );
  if (selectableSpecialStatus.length > 0) {
    const labels = selectableSpecialStatus.map((v) => SPECIAL_STATUS_LABEL_MAP[v] ?? v);
    parts.push(`특수상황: ${labels.join(" 또는 ")}`);
  }
  // 2026-08-14: min_credits_last_semester가 실제로 필터링에 쓰이는데(matching.py의
  // credits_matches()) 지금까지 화면 어디에도 안 보이던 버그 발견 — 여기로 추가(major와
  // 동일한 케이스). min_credits(원문 텍스트)는 이 값이 없을 때만 노란 점 참고용으로 따로 보임.
  // 파란 목록 맨 끝에 둠 — 졸업학기 예외처럼 description(노란 점) 맨 앞에 이 값을 보충
  // 설명하는 문장이 오는 경우가 많아서, 두 점이 화면에서 바로 붙어 보이게(사용자 요청).
  if (s.min_credits_last_semester != null) {
    parts.push(`이수학점: 직전학기 ${s.min_credits_last_semester}학점 이상`);
  }
  return parts;
}

// eligibility_alt_groups(OR 조건) 표시 — 그룹 하나하나를 conditionParts로 판독해서 문장으로
// 만든 뒤 "또는"으로 이어붙임(2026-08-21 추가). 지금까지 이 필드가 화면 어디에도 안 보여서,
// (a) 다른 조건이 하나라도 있으면 그 OR 조건 자체는 안 뜨고, (b) 이 필드가 유일한 조건인
// 장학금(예: 소득분위 OR 특수상황만 있는 경우)은 "별도 제한 없음"으로 완전히 잘못 표시되고
// 있었음 — 실제로 조건이 있는데 없다고 나오는 심각한 정보 오류였음.
function altGroupsParts(s: Scholarship, viewerGpaScale?: number): string[] {
  if (!s.eligibility_alt_groups || s.eligibility_alt_groups.length === 0) return [];
  const groupTexts = s.eligibility_alt_groups
    .map((group) => conditionParts(group as Partial<Scholarship>, viewerGpaScale).join(" · "))
    .filter((text) => text.length > 0);
  return groupTexts.length > 0 ? [groupTexts.join(" 또는 ")] : [];
}

function eligibilityParts(s: Scholarship, viewerGpaScale?: number): string[] {
  return [...conditionParts(s, viewerGpaScale), ...altGroupsParts(s, viewerGpaScale)];
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

// 뭉뚱그린 라벨을 보여주는 태그인데, 구체적인 내용이 이미 다른 칸(보통 description, 이 태그를
// 넣을 때는 항상 구체적인 원문 설명도 같이 적어두는 게 컨벤션이라 — 2026-08-14 여러 건에서
// 확인)에 적혀 있으면 화면에 중복으로 안 보이게 뺌 — id=7(수능 조건), id=10(출신 학교 조건),
// 이후 id=74 등에서 반복 발견돼서 태그별로 하나씩 나열하는 대신 기본값을 "description 있으면
// 숨김"으로 일반화함. suneung_score_condition만 예외 — 이 태그는 랭킹 페널티에도 쓰여서
// required_special_status 자체는 그대로 두고, 화면에서 중복 여부만 admission_score_condition
// 기준으로 따로 판단.
const REDUNDANT_UNVERIFIABLE_OVERRIDES: Partial<Record<string, (s: Scholarship) => boolean>> = {
  suneung_score_condition: (s) => Boolean(s.admission_score_condition),
};

function isRedundantUnverifiableTag(v: string, s: Scholarship): boolean {
  const override = REDUNDANT_UNVERIFIABLE_OVERRIDES[v];
  if (override) return override(s);
  return Boolean(s.description);
}

// 상세페이지 "직접 확인 필요"(노란 점) 목록용 — required_special_status 중 학생이 선택할
// 방법이 없는 태그들을 한글 라벨로 변환.
export function unverifiableConditionParts(s: Scholarship): string[] {
  return s.required_special_status
    .filter((v) => !isRedundantUnverifiableTag(v, s))
    .map((v) => UNVERIFIABLE_SPECIAL_STATUS_LABELS[v])
    .filter((label): label is string => Boolean(label));
}

// 목록 카드용 — 한 줄 요약
export function eligibilitySummary(s: Scholarship): string {
  const parts = eligibilityParts(s);
  return parts.length > 0 ? parts.join(" · ") : "제한 없음";
}

// 상세페이지용 — 항목별로 나눠서 bullet list로 보여주기 위한 배열. viewerGpaScale을 넘기면
// min_gpa를 그 대학 만점 기준으로 환산해서 보여줌(로그인+스펙 등록된 학생만 해당).
export function eligibilityList(s: Scholarship, viewerGpaScale?: number): string[] {
  const parts = eligibilityParts(s, viewerGpaScale);
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
