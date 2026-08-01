import { regionShortName, sidoNameFromRegion, SIDO_LIST } from "@/lib/regions";

export type EnrollmentStatus =
  | "undergrad_enrolled"
  | "undergrad_transfer"
  | "undergrad_leave"
  | "post_undergrad";
export type DegreeLevel = "masters" | "doctoral" | "integrated_ms_phd";

export type UserSpec = {
  university: string;
  college: string;
  gpa: number;
  age: number;
  gender: "male" | "female";
  region: string;
  military_status: "completed" | "exempted" | "not_served";
  income_bracket: number;
  has_disability: boolean;
  is_foreigner: boolean;
  enrollment_status: EnrollmentStatus;
  grade: number | null;
  degree_level: DegreeLevel | null;
};

// 숫자 입력 필드는 폼에서 문자열로 들고 있다가 제출할 때만 숫자로 변환함.
// (타이핑 도중 바로 Number()로 바꿔서 value에 되먹이면 "4." 같은 중간 입력이
// 매번 리셋되면서 방금 친 글자가 씹히는 문제가 있었음 — 그래서 07, 04.5처럼
// 앞에 0을 하나 더 쳐야 입력되는 현상이 발생했음)
export type SpecForm = Omit<UserSpec, "age" | "gpa" | "income_bracket" | "region" | "grade"> & {
  age: string;
  gpa: string;
  income_bracket: string;
  sido: string;
  district: string;
  grade: string;
};

export function specFormToUserSpec(spec: SpecForm): UserSpec {
  return {
    university: spec.university,
    college: spec.college,
    gpa: Number(spec.gpa),
    age: Number(spec.age),
    gender: spec.gender,
    region: regionShortName(spec.sido, spec.district),
    military_status: spec.military_status,
    income_bracket: Number(spec.income_bracket),
    has_disability: spec.has_disability,
    is_foreigner: spec.is_foreigner,
    enrollment_status: spec.enrollment_status,
    grade: spec.enrollment_status === "post_undergrad" ? null : Number(spec.grade),
    degree_level: spec.enrollment_status === "post_undergrad" ? spec.degree_level : null,
  };
}

// 아래 세 항목(어학점수/장애인 세부유형/특수상황)은 아직 백엔드·DB에 저장할 칸이
// 없어서 일단 화면(/spec, /mypage 둘 다)에서만 입력받고 제출 시 서버로는 안 보냄 —
// 호성 확인 받고 스키마(SavedSpec/Scholarship 새 컬럼) 추가되면 그때 실제로 연결함
// (supabase/matching_gaps.md 참고). /spec과 /mypage는 항상 같이 맞출 것
// (frontend/README.md "/spec과 /mypage는 필드를 항상 같이 맞출 것" 참고).
export const LANGUAGE_TESTS: { value: string; label: string; max: number | null }[] = [
  { value: "TOEIC", label: "TOEIC", max: 990 },
  { value: "TOEFL", label: "TOEFL(iBT)", max: 120 },
  { value: "IELTS", label: "IELTS", max: 9 },
  { value: "TOPIK", label: "TOPIK", max: 6 },
  { value: "기타", label: "기타", max: null },
];

// Scholarships.com의 "15 · Physical Disabilities" 카테고리(7개 전체)를 그대로
// 가져옴 — scholarships_com_전체항목_한국어정리.pdf 참고(사용자 컴퓨터에 보관 중).
export const DISABILITY_TYPES = [
  { value: "physical_impairment", label: "신체적 장애" },
  { value: "learning_disability", label: "학습장애" },
  { value: "medical_disability", label: "의료적 장애(질환)" },
  { value: "mental_impairment", label: "정신적 장애" },
  { value: "muscular_dystrophy", label: "근이영양증" },
  { value: "developmental_impairment", label: "발달장애" },
  { value: "disabled_parent", label: "장애가 있는 부모(자녀 대상)" },
];

export const SPECIAL_STATUS_OPTIONS = [
  { value: "north_korean_defector", label: "북한이탈주민" },
  { value: "multicultural_family", label: "다문화가정" },
  { value: "child_care_facility", label: "아동양육시설 생활자·퇴소자" },
  { value: "student_council_officer", label: "학생회장(임원)" },
  { value: "single_parent_family", label: "한부모가정" },
  { value: "grandparent_family", label: "조손가정" },
  { value: "multi_child_family", label: "다자녀가정(3자녀 이상)" },
  { value: "national_merit", label: "국가보훈대상자" },
];

export type OptionalInfo = {
  languageTestEnabled: boolean;
  languageTestType: string;
  languageTestScore: string;
  disabilityType: string;
  specialStatusEnabled: boolean;
  specialStatus: string[];
};

export const initialOptionalInfo: OptionalInfo = {
  languageTestEnabled: false,
  languageTestType: LANGUAGE_TESTS[0].value,
  languageTestScore: "",
  disabilityType: DISABILITY_TYPES[0].value,
  specialStatusEnabled: false,
  specialStatus: [],
};

// 마이페이지에서 서버에 저장된 스펙(UserSpec)을 불러와 수정 폼(SpecForm)에 채울 때 씀 —
// specFormToUserSpec의 반대 방향. region은 구/군 정보 없이 짧은 시/도 단위로만 저장돼
// 있어서, sido는 복원되지만 district는 그 시/도의 첫 번째 값으로 기본 설정됨.
export function userSpecToSpecForm(spec: UserSpec): SpecForm {
  const sido = sidoNameFromRegion(spec.region);
  const district = SIDO_LIST.find((s) => s.name === sido)?.districts[0] ?? "";
  return {
    university: spec.university,
    college: spec.college,
    gpa: String(spec.gpa),
    age: String(spec.age),
    gender: spec.gender,
    sido,
    district,
    military_status: spec.military_status,
    income_bracket: String(spec.income_bracket),
    has_disability: spec.has_disability,
    is_foreigner: spec.is_foreigner,
    enrollment_status: spec.enrollment_status,
    grade: spec.grade != null ? String(spec.grade) : "1",
    degree_level: spec.degree_level,
  };
}
