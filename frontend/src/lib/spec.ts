import { regionShortName, sidoNameFromRegion, SIDO_LIST } from "@/lib/regions";

export type EnrollmentStatus =
  | "undergrad_enrolled"
  | "undergrad_transfer"
  | "undergrad_leave"
  | "post_undergrad";
export type DegreeLevel = "masters" | "doctoral" | "integrated_ms_phd";
// 2026-08-12 추가 — "무슨 학과인지"(department)와 별개인 "어떻게 입학했는지" 축. major(전공)
// 기반 필터로는 "체육특기자 전형 입학생 대상" 같은 조건을 정확히 표현할 수 없어서(우송대처럼
// 관련 학과 자체가 없는 대학도 있음) 전용 필드로 분리함. 실제 DB에서 확인된 유형은 체육특기자
// 전형뿐이라 나머지(예능특기자·농어촌전형 등)는 OTHER_SPECIALTY로 뭉뚱그려 둠 — 확인된 사례가
// 쌓이면 전용 값으로 분리할 것(backend/app/models/enums.py의 AdmissionTrack 참고).
export type AdmissionTrack = "general" | "athletic_specialty" | "other_specialty";
// 2026-08-15 추가 — military_status가 "completed"(군필)일 때만 의미 있는 세부 구분(id=652
// "10년 이상 장기복무 제대군인 대상"에서 발견). enrollment_status=post_undergrad일 때만
// 의미 있는 DegreeLevel과 같은 패턴 — backend/app/models/enums.py의 DischargeType 참고.
export type DischargeType = "enlisted" | "officer_or_nco";

export type UserSpec = {
  university: string;
  college: string;
  department: string | null; // 2026-08-03 추가 (matching_gaps.md 2번) — 단과대 밑 학과
  semester_gpa: number;
  cumulative_gpa: number;
  age: number;
  gender: "male" | "female";
  region: string;
  // 2026-08-05 추가 (matching_gaps.md 14번) — "정읍시 거주자만" 같은 시/군/구 단위 지자체
  // 장학금 매칭용. 세종처럼 하위 구/군이 없으면 빈 문자열/null일 수 있음.
  district: string | null;
  // 2026-08-05 추가 (matching_gaps.md 19번) — "본인 또는 부모 중 1인이 OO에 거주" 조건을
  // 표현하기 위한 선택 입력. null="입력 안 함" — OptionalInfo.parentRegionEnabled로 관리됨.
  parent_region: string | null;
  parent_district: string | null; // 2026-08-05 추가 (matching_gaps.md 14번 후속)
  military_status: "completed" | "exempted" | "not_served" | "rotc_candidate";
  // 2026-08-15 추가 — military_status가 "completed"일 때만 의미 있음(그 외엔 항상 null).
  discharge_type: DischargeType | null;
  income_bracket: number | null; // null="모름" — 소득분위 조건이 있는 장학금도 안 거름
  has_disability: boolean;
  is_foreigner: boolean;
  enrollment_status: EnrollmentStatus;
  grade: number | null;
  degree_level: DegreeLevel | null;
  // null = 아직 이 필드를 안 채운 레거시 스펙 — 매칭 시 서버가 "general"로 간주함(과소매칭
  // 방지, 대다수 학생이 일반전형). 폼에서는 항상 기본값 "general"이 선택된 채로 제출됨.
  admission_track: AdmissionTrack | null;
  // 2026-08-02 추가 (matching_gaps.md 9·10·12번) — 전부 선택 입력, 아래 OptionalInfo 참고.
  language_test_type: string | null;
  language_test_score: number | null;
  disability_type: string | null;
  special_status: string[];
  // 2026-08-12 추가 — GPA와 동일한 방식(학생 자기입력)으로 이수학점 조건도 실제 매칭에 씀.
  // null="입력 안 함/모름" — 이수학점 조건이 있는 장학금도 안 거름. 아래 OptionalInfo 참고.
  credits_last_semester: number | null;
};

// 의예과·수의예과·한의예과(2년제 예과) — 여기 1학년은 진짜 신입생.
const PREP_DEPARTMENTS = new Set(["의예과", "수의예과", "한의예과"]);
// 의학과·수의학과·한의학과(예과 2년을 마친 뒤 진입하는 4년제 본과) — 학교 관례상 "학년"이
// 본과 진입 시점부터 1로 리셋되는데(본과 1학년=전체 재학 3년차), min_grade/max_grade는
// "전체 재학연차" 기준으로 매칭하는 필드라 그대로 "1"을 보내면 신입생 전용 장학금에 실제로는
// 신입생이 아닌 학생이 잘못 매칭됨(2026-08-03, 사용자가 본인이 수의학과라 직접 알려줘서 발견).
// 그래서 이 학과들만 학년 선택값 자체를 전체 재학연차(3~6)로 보정해서 보냄 — 화면엔 학생들이
// 익숙한 "본과 N학년" 표기를 유지하되, 실제 전송 값은 전체 연차로 어긋나지 않게 함.
const MAIN_AFTER_PREP_DEPARTMENTS = new Set(["의학과", "수의학과", "한의학과"]);

// 소득분위 드롭다운 공용 옵션 — "모름"은 UserSpec.income_bracket=null로 변환됨(아래
// specFormToUserSpec 참고). 자기 소득분위를 모르는 사용자가 많아서 추가함(2026-08-03).
export const INCOME_BRACKET_OPTIONS: { value: string; label: string }[] = [
  { value: "unknown", label: "모름 — 관련 장학금 다 보여드려요" },
  { value: "0", label: "0구간 (기초생활수급자)" },
  ...Array.from({ length: 10 }, (_, i) => ({ value: String(i + 1), label: `${i + 1}구간` })),
];

// 스펙 입력/마이페이지 둘 다 학과에 따라 학년 선택지를 다르게 보여주기 위한 공용 헬퍼.
// 편입생은 1학년으로 들어오는 경우가 거의 없어서 항상 첫 옵션(1학년)을 제외함.
export function gradeOptions(
  department: string,
  enrollmentStatus: EnrollmentStatus
): { value: string; label: string }[] {
  let options: { value: string; label: string }[];
  if (PREP_DEPARTMENTS.has(department)) {
    options = [1, 2].map((g) => ({ value: String(g), label: `${g}학년` }));
  } else if (MAIN_AFTER_PREP_DEPARTMENTS.has(department)) {
    options = [3, 4, 5, 6].map((overall) => ({
      value: String(overall),
      label: `본과 ${overall - 2}학년(전체 ${overall}학년차)`,
    }));
  } else {
    options = [1, 2, 3, 4].map((g) => ({ value: String(g), label: `${g}학년` }));
  }
  return enrollmentStatus === "undergrad_transfer" ? options.slice(1) : options;
}

// 숫자 입력 필드는 폼에서 문자열로 들고 있다가 제출할 때만 숫자로 변환함.
// (타이핑 도중 바로 Number()로 바꿔서 value에 되먹이면 "4." 같은 중간 입력이
// 매번 리셋되면서 방금 친 글자가 씹히는 문제가 있었음 — 그래서 07, 04.5처럼
// 앞에 0을 하나 더 쳐야 입력되는 현상이 발생했음)
// language_test_type/language_test_score/disability_type/special_status는 SpecForm에
// 안 넣음 — 이 넷은 OptionalInfo(아래) 쪽 상태로 따로 관리되고, 제출 시 specFormToUserSpec의
// 두 번째 인자로 합쳐짐.
export type SpecForm = Omit<
  UserSpec,
  | "age"
  | "semester_gpa"
  | "cumulative_gpa"
  | "income_bracket"
  | "region"
  | "district"
  | "parent_region"
  | "parent_district"
  | "grade"
  | "department"
  | "language_test_type"
  | "language_test_score"
  | "disability_type"
  | "special_status"
  | "admission_track"
  | "credits_last_semester"
> & {
  age: string;
  semester_gpa: string;
  cumulative_gpa: string;
  income_bracket: string;
  sido: string;
  district: string;
  grade: string;
  department: string; // 빈 문자열 = 학과 선택 안 함(단과대에 학과 목록이 없거나 미선택)
  admission_track: AdmissionTrack; // 폼에서는 항상 정해진 값(기본 "general")
};

export function specFormToUserSpec(spec: SpecForm, optionalInfo: OptionalInfo): UserSpec {
  return {
    university: spec.university,
    college: spec.college,
    department: spec.department || null,
    semester_gpa: Number(spec.semester_gpa),
    cumulative_gpa: Number(spec.cumulative_gpa),
    age: Number(spec.age),
    gender: spec.gender,
    region: regionShortName(spec.sido, spec.district),
    district: spec.district || null,
    parent_region: optionalInfo.parentRegionEnabled
      ? regionShortName(optionalInfo.parentSido, optionalInfo.parentDistrict)
      : null,
    parent_district: optionalInfo.parentRegionEnabled ? optionalInfo.parentDistrict || null : null,
    military_status: spec.military_status,
    // 2026-08-15 추가 — 군필이 아니면 세부구분 자체가 성립 안 하므로 항상 null로 정리
    // (프론트가 폼에서 이미 군필일 때만 보여주지만, 이전에 군필→다른 값으로 바꾼 뒤에도
    // discharge_type이 남아있을 수 있어 제출 시점에 한 번 더 확실히 함).
    discharge_type: spec.military_status === "completed" ? spec.discharge_type : null,
    income_bracket: spec.income_bracket === "unknown" ? null : Number(spec.income_bracket),
    has_disability: spec.has_disability,
    is_foreigner: spec.is_foreigner,
    enrollment_status: spec.enrollment_status,
    grade: spec.enrollment_status === "post_undergrad" ? null : Number(spec.grade),
    degree_level: spec.enrollment_status === "post_undergrad" ? spec.degree_level : null,
    admission_track: spec.admission_track,
    language_test_type:
      optionalInfo.languageTestEnabled && optionalInfo.languageTestScore !== ""
        ? optionalInfo.languageTestType
        : null,
    language_test_score:
      optionalInfo.languageTestEnabled && optionalInfo.languageTestScore !== ""
        ? Number(optionalInfo.languageTestScore)
        : null,
    disability_type: spec.has_disability ? optionalInfo.disabilityType : null,
    special_status: optionalInfo.specialStatusEnabled ? optionalInfo.specialStatus : [],
    credits_last_semester:
      optionalInfo.creditsEnabled && optionalInfo.creditsLastSemester !== ""
        ? Number(optionalInfo.creditsLastSemester)
        : null,
  };
}

// 아래 세 항목(어학점수/장애인 세부유형/특수상황) — 2026-08-03 백엔드 연결 완료
// (SavedSpec/Scholarship 새 컬럼 추가, supabase/matching_gaps.md 참고). /spec과
// /mypage는 항상 같이 맞출 것 (frontend/README.md "/spec과 /mypage는 필드를 항상
// 같이 맞출 것" 참고).
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

// 2026-08-12 추가 — AdmissionTrack 참고. 기본값은 항상 "일반전형"(첫 옵션).
export const ADMISSION_TRACK_OPTIONS: { value: AdmissionTrack; label: string }[] = [
  { value: "general", label: "일반전형(수시/정시 등 일반 입학)" },
  { value: "athletic_specialty", label: "체육특기자 전형" },
  { value: "other_specialty", label: "기타 특기자·특별전형(농어촌·정원외 등)" },
];

// 2026-08-15 추가 — military_status="completed"(군필) 선택 시 이어서 보여주는 세부 선택지.
export const DISCHARGE_TYPE_OPTIONS: { value: DischargeType; label: string }[] = [
  { value: "enlisted", label: "병사 전역" },
  { value: "officer_or_nco", label: "장교/부사관 전역" },
];

export const SPECIAL_STATUS_NOT_APPLICABLE = "not_applicable";

export const SPECIAL_STATUS_OPTIONS = [
  { value: "north_korean_defector", label: "북한이탈주민" },
  { value: "multicultural_family", label: "다문화가정" },
  { value: "child_care_facility", label: "아동양육시설 생활자·퇴소자" },
  { value: "student_council_officer", label: "학생회장(임원)" },
  { value: "single_parent_family", label: "한부모가정" },
  { value: "grandparent_family", label: "조손가정" },
  { value: "multi_child_family", label: "다자녀가정(2자녀 이상)" },
  { value: "national_merit", label: "국가보훈대상자" },
  // 2026-08-10 추가 — 원래 크롤링 데이터 전용 "확인 불가" 랭킹 태그였는데, national_merit과
  // 마찬가지로 명확한 법적 지위(의사상자 등 예우 및 지원에 관한 법률, 보건복지부 소관)라
  // 사용자가 직접 선택할 수 있는 항목으로 승격함(matching_gaps.md 20번).
  { value: "righteous_person_family_condition", label: "의사상자 유족·가족" },
  // 2026-08-03 추가 — 배재대 희망복지장학금·대전대 장학사정관장학금 같은 복합조건
  // 장학금을 재분류하면서 새로 필요해진 항목들 (matching_gaps.md 참고)
  { value: "basic_livelihood_recipient", label: "기초생활수급자" },
  { value: "near_poor", label: "차상위계층" },
  { value: "severe_illness_or_injury", label: "중증질병 및 상해" },
  { value: "job_loss_or_disaster", label: "실직가정·재난 및 재해" },
  { value: "financial_emergency", label: "긴급가계곤란" },
  // 2026-08-12 추가 — 경쟁 서비스(이루리) 회원가입 폼 검토 중 발견, 실제 DB 재검토로 확인.
  { value: "rural_student", label: "농어촌(읍·면) 출신" },
  { value: "parent_university_staff", label: "부모가 재학 대학 교직원" },
  { value: "parent_university_alumni", label: "부모가 재학 대학 동문(졸업생)" },
  // 2026-08-15 추가 — religious_or_career_intent_condition(확인 불가) 21건 재검토 중 발견,
  // national_merit·righteous_person_family_condition과 같은 이유(명확한 자기신고 가능
  // 사실)로 승격. backend/app/models/enums.py의 PARENT_CLERGY_OR_MISSIONARY 참고.
  { value: "parent_clergy_or_missionary", label: "부모가 목회자·선교사" },
  // 2026-08-07 추가 — "해당사항 없음" 명시적 선택지. 지금까지는 특수상황을 하나도 안 고르면
  // "아직 대답 안 함(모름)"으로 취급돼서 leniency로 관련 장학금이 계속 보였는데, "나는 이
  // 중 어디에도 해당 안 함"을 확정하고 싶은 학생을 위한 선택지(사용자 지적으로 추가). 다른
  // 항목과 상호배타적으로 골라지도록 처리함 — applySpecialStatusExclusivity() 참고.
  { value: SPECIAL_STATUS_NOT_APPLICABLE, label: "해당사항 없음" },
];

/** SPECIAL_STATUS_OPTIONS의 MultiPillSelect onChange에 그대로 씌워서, "해당사항 없음"과
 * 다른 항목이 동시에 선택되지 않도록 함 — 방금 "해당사항 없음"을 새로 고르면 나머지를 전부
 * 비우고, "해당사항 없음"이 이미 선택된 상태에서 다른 항목을 고르면 "해당사항 없음"만
 * 빼고 나머지를 유지함. */
export function applySpecialStatusExclusivity(prev: string[], next: string[]): string[] {
  const prevHasNone = prev.includes(SPECIAL_STATUS_NOT_APPLICABLE);
  const nextHasNone = next.includes(SPECIAL_STATUS_NOT_APPLICABLE);
  if (nextHasNone && !prevHasNone) {
    return [SPECIAL_STATUS_NOT_APPLICABLE];
  }
  if (nextHasNone && next.length > 1) {
    return next.filter((v) => v !== SPECIAL_STATUS_NOT_APPLICABLE);
  }
  return next;
}

export type OptionalInfo = {
  languageTestEnabled: boolean;
  languageTestType: string;
  languageTestScore: string;
  disabilityType: string;
  specialStatusEnabled: boolean;
  specialStatus: string[];
  // 2026-08-12 추가 — credits_last_semester 참고.
  creditsEnabled: boolean;
  creditsLastSemester: string;
  // 2026-08-05 추가 (matching_gaps.md 19번·14번). "본인과 동일/다름" 토글 — 다름을 고르면
  // 본인 거주지 폼과 똑같은 시/도+구/군 캐스케이딩 드롭다운으로 부모님 거주지를 따로 입력함
  // (스펙 입력/마이페이지 페이지 쪽에서 SIDO_LIST로 렌더링).
  parentRegionEnabled: boolean;
  parentSido: string;
  parentDistrict: string;
};

export const initialOptionalInfo: OptionalInfo = {
  languageTestEnabled: false,
  languageTestType: LANGUAGE_TESTS[0].value,
  languageTestScore: "",
  disabilityType: DISABILITY_TYPES[0].value,
  specialStatusEnabled: false,
  specialStatus: [],
  creditsEnabled: false,
  creditsLastSemester: "",
  parentRegionEnabled: false,
  parentSido: SIDO_LIST[0].name,
  parentDistrict: SIDO_LIST[0].districts[0] ?? "",
};

// 마이페이지에서 서버에 저장된 스펙(UserSpec)을 불러와 수정 폼(SpecForm)에 채울 때 씀 —
// specFormToUserSpec의 반대 방향. sido는 region(짧은 시/도 단위)에서 복원하고, district는
// 2026-08-05부터 실제로 저장되는 spec.district 값을 그대로 씀(matching_gaps.md 14번 전에는
// district 자체를 안 보내고 버려서 그 시/도의 첫 번째 구/군으로만 근사 복원했었음).
export function userSpecToSpecForm(spec: UserSpec): SpecForm {
  const sido = sidoNameFromRegion(spec.region);
  const district = spec.district || (SIDO_LIST.find((s) => s.name === sido)?.districts[0] ?? "");
  return {
    university: spec.university,
    college: spec.college,
    department: spec.department ?? "",
    semester_gpa: String(spec.semester_gpa),
    cumulative_gpa: String(spec.cumulative_gpa),
    age: String(spec.age),
    gender: spec.gender,
    sido,
    district,
    military_status: spec.military_status,
    discharge_type: spec.military_status === "completed" ? spec.discharge_type : null,
    income_bracket: spec.income_bracket != null ? String(spec.income_bracket) : "unknown",
    has_disability: spec.has_disability,
    is_foreigner: spec.is_foreigner,
    enrollment_status: spec.enrollment_status,
    grade: spec.grade != null ? String(spec.grade) : "1",
    degree_level: spec.degree_level,
    admission_track: spec.admission_track ?? "general",
  };
}

// userSpecToSpecForm과 짝 — 서버에서 불러온 UserSpec으로 OptionalInfo(어학점수/장애인
// 세부유형/특수상황) 폼 상태를 복원할 때 씀 (마이페이지에서 기존 저장값을 보여주기 위함).
export function userSpecToOptionalInfo(spec: UserSpec): OptionalInfo {
  return {
    languageTestEnabled: spec.language_test_type != null,
    languageTestType: spec.language_test_type ?? LANGUAGE_TESTS[0].value,
    languageTestScore: spec.language_test_score != null ? String(spec.language_test_score) : "",
    disabilityType: spec.disability_type ?? DISABILITY_TYPES[0].value,
    specialStatusEnabled: spec.special_status.length > 0,
    specialStatus: spec.special_status,
    creditsEnabled: spec.credits_last_semester != null,
    creditsLastSemester: spec.credits_last_semester != null ? String(spec.credits_last_semester) : "",
    parentRegionEnabled: spec.parent_region != null,
    parentSido: spec.parent_region != null ? sidoNameFromRegion(spec.parent_region) : SIDO_LIST[0].name,
    parentDistrict:
      spec.parent_district ||
      SIDO_LIST.find(
        (s) => s.name === (spec.parent_region != null ? sidoNameFromRegion(spec.parent_region) : SIDO_LIST[0].name)
      )?.districts[0] ||
      "",
  };
}
