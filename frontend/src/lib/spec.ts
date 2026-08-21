import { regionShortName, sidoNameFromRegion, SIDO_LIST } from "@/lib/regions";
import { UNIVERSITIES } from "@/lib/universities";

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

// 2026-08-21 추가 — 어학점수를 여러 개(토익+토플+JLPT 등) 넣을 수 있게 하면서 도입한 항목
// 하나의 모양. type은 LANGUAGE_TESTS의 value와 같은 문자열.
export type LanguageTestEntry = {
  type: string;
  score: number;
};

export type UserSpec = {
  // 2026-08-21 추가 — 매칭 조건으로는 안 쓰이고, "OOO님을 위한 장학금" 같은 개인화 표시용으로만
  // 저장함. null=아직 안 입력한 레거시 스펙(이 필드 추가 전 저장된 것).
  display_name: string | null;
  // 2026-08-21 추가 — age(아래)를 대체하는 실제 입력 필드. age는 매칭에 계속 쓰이므로 필드
  // 자체는 남겨두고, 프론트가 이 값으로부터 만 나이를 계산해서 age를 채움(specFormToUserSpec
  // 참고) — 매칭 로직(matching.py)은 age만 보므로 전혀 안 건드림.
  birth_date: string | null;
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
  // 2026-08-21 추가 — 주소 검색(AddressSearchField)으로 받은 전체 도로명주소. 매칭엔 안 쓰고
  // 표시/재입력 시 복원용(마이페이지에서 다시 열었을 때 검색해서 넣은 주소가 그대로 보이게).
  address: string | null;
  // 2026-08-05 추가 (matching_gaps.md 19번) — "본인 또는 부모 중 1인이 OO에 거주" 조건을
  // 표현하기 위한 선택 입력. null="입력 안 함" — OptionalInfo.parentRegionEnabled로 관리됨.
  parent_region: string | null;
  parent_district: string | null; // 2026-08-05 추가 (matching_gaps.md 14번 후속)
  parent_address: string | null; // 2026-08-21 추가 — address와 동일한 이유, 부모님 쪽.
  // 2026-08-21 — 필수에서 선택 입력으로 변경. null="모름/미답변"(다른 선택 입력들과 같은
  // leniency 원칙 — core/matching.py의 is_eligible/discharge_type_matches 참고). 이미 고른
  // 병역 항목을 다시 누르면 이 값이 null로 돌아감(spec-fields.tsx의 PillToggle onChange 참고).
  military_status: "completed" | "exempted" | "not_served" | "rotc_candidate" | "not_applicable" | null;
  // 2026-08-15 추가 — military_status가 "completed"일 때만 의미 있음(그 외엔 항상 null).
  discharge_type: DischargeType | null;
  income_bracket: number | null; // null="모름" — 소득분위 조건이 있는 장학금도 안 거름
  // 2026-08-22 — 병역과 같은 방식으로 필수에서 선택 입력으로 변경. null="모름/안 건드림"
  // (leniency — 장애 조건 있는 장학금도 안 거름). true인데 disability_type이 "해당사항
  // 없음"이면 확정된 "아니오"로 취급되어 오히려 거름 — core/matching.py의
  // disability_matches() 참고.
  has_disability: boolean | null;
  is_foreigner: boolean;
  enrollment_status: EnrollmentStatus;
  grade: number | null;
  degree_level: DegreeLevel | null;
  // null = 아직 이 필드를 안 채운 레거시 스펙 — 매칭 시 서버가 "general"로 간주함(과소매칭
  // 방지, 대다수 학생이 일반전형). 폼에서는 항상 기본값 "general"이 선택된 채로 제출됨.
  admission_track: AdmissionTrack | null;
  // 2026-08-02 추가 (matching_gaps.md 9·10·12번) — 선택 입력, 아래 OptionalInfo 참고.
  // 2026-08-21 — 시험 하나만 넣을 수 있던 걸 여러 개(예: 토익+토플+JLPT) 넣을 수 있게 변경.
  language_tests: LanguageTestEntry[];
  // 2026-08-21 — 단일 값에서 special_status와 같은 복수선택으로 변경. 빈 배열=선택 안 함
  // (leniency 원칙 — core/matching.py의 disability_matches() 참고).
  disability_type: string[];
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
// language_tests/disability_type/special_status는 SpecForm에 안 넣음 — 이 셋은 OptionalInfo
// (아래) 쪽 상태로 따로 관리되고, 제출 시 specFormToUserSpec의 두 번째 인자로 합쳐짐.
export type SpecForm = Omit<
  UserSpec,
  | "display_name"
  | "birth_date"
  | "age"
  | "semester_gpa"
  | "cumulative_gpa"
  | "income_bracket"
  | "region"
  | "district"
  | "address"
  | "parent_region"
  | "parent_district"
  | "parent_address"
  | "grade"
  | "department"
  | "language_tests"
  | "disability_type"
  | "special_status"
  | "admission_track"
  | "credits_last_semester"
> & {
  display_name: string;
  birth_date: string; // yyyy-mm-dd — age는 여기서 계산해서 채움(specFormToUserSpec 참고)
  semester_gpa: string;
  cumulative_gpa: string;
  income_bracket: string;
  sido: string;
  district: string;
  address: string; // 주소 검색으로 받은 전체 도로명주소 — 빈 문자열=아직 검색 안 함
  grade: string;
  department: string; // 빈 문자열 = 학과 선택 안 함(단과대에 학과 목록이 없거나 미선택)
  admission_track: AdmissionTrack; // 폼에서는 항상 정해진 값(기본 "general")
};

// 만 나이(생일이 이미 지났는지로 분기) — 대부분 장학금 자격조건이 만 나이 기준이라 이 방식으로
// 통일함. 생년월일이 비어있거나 형식이 이상하면 0을 반환(폼에서 required로 막지만 방어적으로).
export function calculateAge(birthDate: string): number {
  const birth = new Date(birthDate);
  if (Number.isNaN(birth.getTime())) return 0;
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const hasHadBirthdayThisYear =
    today.getMonth() > birth.getMonth() ||
    (today.getMonth() === birth.getMonth() && today.getDate() >= birth.getDate());
  if (!hasHadBirthdayThisYear) age -= 1;
  return age;
}

// 생년월일 기본값 — 만 20세가 되는 날짜로 채워서 기존 "나이 기본값 20"과 동일한 감을 유지함.
function defaultBirthDate(): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 20);
  return d.toISOString().slice(0, 10);
}

const DEFAULT_SIDO = SIDO_LIST.find((s) => s.name === "대전광역시")!;
const DEFAULT_UNIVERSITY = UNIVERSITIES[0];

// /spec(신규 입력)의 초기값이자, guest.ts가 세션에 저장된 값이 예전 필드 구조(필드 이름이
// 바뀌었거나 새 필드가 추가되기 전)일 때 없는 키를 이 기본값으로 채우는 데도 씀 — 원래
// frontend/src/app/spec/page.tsx에만 있었는데, 폼 구조가 바뀔 때마다 세션에 남아있던 낡은
// JSON을 그대로 믿고 쓰다가 없는 필드에서 터지는 문제(2026-08-21, MultiPillSelect의
// values.includes가 undefined에서 터진 사례)가 있어서 공용 기본값으로 옮김.
export const initialSpec: SpecForm = {
  display_name: "",
  birth_date: defaultBirthDate(),
  university: DEFAULT_UNIVERSITY.name,
  college: DEFAULT_UNIVERSITY.colleges[0]?.name ?? "",
  department: DEFAULT_UNIVERSITY.colleges[0]?.departments[0] ?? "",
  semester_gpa: "4.0",
  cumulative_gpa: "4.0",
  gender: "male",
  sido: DEFAULT_SIDO.name,
  district: DEFAULT_SIDO.districts[0] ?? "",
  address: "",
  // 2026-08-22 — 병역이 장애인처럼 누르면 펼쳐지는 방식으로 바뀌면서, 기본값을 "미필"
  // 대신 null(=아직 안 펼침, 접힌 상태)로 바꿈 — spec-fields.tsx의 병역 CollapsibleToggle
  // 참고(펼치는 순간 "미필"로 채워짐).
  military_status: null,
  discharge_type: null,
  income_bracket: "unknown",
  // 2026-08-22 — 병역과 같은 이유로 false 대신 null(모름/안 건드림) 기본값.
  has_disability: null,
  is_foreigner: false,
  enrollment_status: "undergrad_enrolled",
  grade: "1",
  degree_level: null,
  admission_track: "general",
};

export function specFormToUserSpec(spec: SpecForm, optionalInfo: OptionalInfo): UserSpec {
  return {
    display_name: spec.display_name || null,
    birth_date: spec.birth_date || null,
    university: spec.university,
    college: spec.college,
    department: spec.department || null,
    semester_gpa: Number(spec.semester_gpa),
    cumulative_gpa: Number(spec.cumulative_gpa),
    age: calculateAge(spec.birth_date),
    gender: spec.gender,
    region: regionShortName(spec.sido, spec.district),
    district: spec.district || null,
    address: spec.address || null,
    parent_region: optionalInfo.parentRegionEnabled
      ? regionShortName(optionalInfo.parentSido, optionalInfo.parentDistrict)
      : null,
    parent_district: optionalInfo.parentRegionEnabled ? optionalInfo.parentDistrict || null : null,
    parent_address: optionalInfo.parentRegionEnabled ? optionalInfo.parentAddress || null : null,
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
    language_tests: optionalInfo.languageTests
      .filter((t) => t.score !== "")
      .map((t) => ({ type: t.type, score: Number(t.score) })),
    disability_type: spec.has_disability ? optionalInfo.disabilityTypes : [],
    special_status: optionalInfo.specialStatusEnabled ? optionalInfo.specialStatus : [],
    credits_last_semester:
      optionalInfo.creditsLastSemester !== "" ? Number(optionalInfo.creditsLastSemester) : null,
  };
}

// 아래 세 항목(어학점수/장애인 세부유형/특수상황) — 2026-08-03 백엔드 연결 완료
// (SavedSpec/Scholarship 새 컬럼 추가, supabase/matching_gaps.md 참고). /spec과
// /mypage는 항상 같이 맞출 것 (frontend/README.md "/spec과 /mypage는 필드를 항상
// 같이 맞출 것" 참고).
// 2026-08-21 확장 — 기존 5종(TOEIC/TOEFL/IELTS/TOPIK/기타)에 실제로 자주 쓰이는 시험 5종 추가.
// 만점은 전부 공식 시험 구조 기준으로 확인한 값(HSK만 3~6급 기준 300점 — 1~2급은 200점으로
// 달라서 그 구간까지 하나로 뭉뚱그리면 부정확해지므로 일부러 안 넣고 "기타"로 유도함).
export const LANGUAGE_TESTS: { value: string; label: string; max: number | null }[] = [
  { value: "TOEIC", label: "TOEIC", max: 990 },
  { value: "TOEIC Speaking", label: "TOEIC Speaking", max: 200 },
  { value: "TOEFL", label: "TOEFL(iBT)", max: 120 },
  { value: "TOEFL(PBT)", label: "TOEFL(PBT/ITP)", max: 677 },
  { value: "IELTS", label: "IELTS", max: 9 },
  { value: "TEPS", label: "TEPS(뉴텝스)", max: 600 },
  { value: "TOPIK", label: "TOPIK", max: 6 },
  { value: "JLPT", label: "JLPT", max: 180 },
  { value: "HSK", label: "HSK(3~6급)", max: 300 },
  { value: "기타", label: "기타", max: null },
];

export const DISABILITY_NOT_APPLICABLE = "not_applicable";

// Scholarships.com의 "15 · Physical Disabilities" 카테고리(7개 전체)를 그대로
// 가져옴 — scholarships_com_전체항목_한국어정리.pdf 참고(사용자 컴퓨터에 보관 중).
export const DISABILITY_TYPES = [
  // 2026-08-22 추가(사용자 요청) — 병역의 "해당사항 없음"과 같은 패턴. 장애인 패널을 열었지만
  // 실제로는 해당 안 되는 학생을 위한 명시적 확정 선택지 — 이걸 고르면(다른 유형과 상호배타,
  // applyExclusiveNotApplicable 참고) has_disability는 그대로 true지만 이 값이 "확정된
  // 아니오"로 작동해서, 장애 조건이 있는 장학금은 무조건 제외됨(core/matching.py의
  // disability_matches() 참고) — 아예 패널을 안 건드린 것(모름=leniency)과는 다른 상태.
  // 목록 맨 위로 옮기고 강조색을 준 이유(2026-08-22 사용자 요청): 목록 맨 아래에 묻혀 있으면
  // 학생이 못 보고 지나칠 수 있어서 — 안 눌러도 되는 항목이 아니라 눈에 띄어야 하는 항목.
  { value: DISABILITY_NOT_APPLICABLE, label: "해당사항 없음", highlight: true },
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
  // 2026-08-07 추가 — "해당사항 없음" 명시적 선택지. 지금까지는 특수상황을 하나도 안 고르면
  // "아직 대답 안 함(모름)"으로 취급돼서 leniency로 관련 장학금이 계속 보였는데, "나는 이
  // 중 어디에도 해당 안 함"을 확정하고 싶은 학생을 위한 선택지(사용자 지적으로 추가). 다른
  // 항목과 상호배타적으로 골라지도록 처리함 — applySpecialStatusExclusivity() 참고.
  // 목록 맨 위로 옮기고 강조색을 준 이유(2026-08-22 사용자 요청, 장애인 항목과 동일): 긴
  // 목록 맨 아래에 묻혀 있으면 학생이 못 보고 지나칠 수 있어서.
  { value: SPECIAL_STATUS_NOT_APPLICABLE, label: "해당사항 없음", highlight: true },
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
];

/** SPECIAL_STATUS_OPTIONS의 MultiPillSelect onChange에 그대로 씌워서, "해당사항 없음"과
 * 다른 항목이 동시에 선택되지 않도록 함 — 방금 "해당사항 없음"을 새로 고르면 나머지를 전부
 * 비우고, "해당사항 없음"이 이미 선택된 상태에서 다른 항목을 고르면 "해당사항 없음"만
 * 빼고 나머지를 유지함. */
// 2026-08-22 — 장애 유형에도 같은 "해당사항 없음" 패턴이 필요해져서(DISABILITY_TYPES 참고)
// sentinel 값을 인자로 받는 범용 버전으로 일반화함.
export function applyExclusiveNotApplicable(
  prev: string[],
  next: string[],
  notApplicableValue: string
): string[] {
  const prevHasNone = prev.includes(notApplicableValue);
  const nextHasNone = next.includes(notApplicableValue);
  if (nextHasNone && !prevHasNone) {
    return [notApplicableValue];
  }
  if (nextHasNone && next.length > 1) {
    return next.filter((v) => v !== notApplicableValue);
  }
  return next;
}

export function applySpecialStatusExclusivity(prev: string[], next: string[]): string[] {
  return applyExclusiveNotApplicable(prev, next, SPECIAL_STATUS_NOT_APPLICABLE);
}

// 어학점수 한 줄(종류+점수) — 폼 상태라 score는 문자열로 들고 있음(다른 숫자 입력들과 동일한
// 이유, calculateAge 위 주석 참고).
export type LanguageTestFormEntry = {
  type: string;
  score: string;
};

export type OptionalInfo = {
  // 2026-08-21 — 시험 하나만 넣던 걸 여러 개 넣을 수 있게 변경(사용자 요청 — 토익+토플+JLPT
  // 등 동시 보유 가능). 빈 배열=아직 하나도 안 넣음(어학점수 CollapsibleToggle이 접힌 상태).
  languageTests: LanguageTestFormEntry[];
  // 2026-08-21 — 단일 값에서 특수상황처럼 복수선택으로 변경.
  disabilityTypes: string[];
  specialStatusEnabled: boolean;
  specialStatus: string[];
  // 2026-08-12 추가 — credits_last_semester 참고. 2026-08-21 — 예전엔 별도 토글
  // (creditsEnabled)로 켜야 보이는 입력이었는데, GPA처럼 바로 적을 수 있게 바꾸면서 그 토글
  // 자체가 필요 없어짐(빈 문자열=미입력).
  creditsLastSemester: string;
  // 2026-08-05 추가 (matching_gaps.md 19번·14번). "본인과 동일/다름" 토글 — 다름을 고르면
  // 본인 거주지 폼과 똑같은 시/도+구/군 캐스케이딩 드롭다운으로 부모님 거주지를 따로 입력함
  // (스펙 입력/마이페이지 페이지 쪽에서 SIDO_LIST로 렌더링).
  parentRegionEnabled: boolean;
  parentSido: string;
  parentDistrict: string;
  parentAddress: string; // 2026-08-21 추가 — address와 동일한 이유, 부모님 쪽.
};

export const initialOptionalInfo: OptionalInfo = {
  languageTests: [],
  disabilityTypes: [],
  specialStatusEnabled: false,
  specialStatus: [],
  creditsLastSemester: "",
  parentRegionEnabled: false,
  parentSido: SIDO_LIST[0].name,
  parentDistrict: SIDO_LIST[0].districts[0] ?? "",
  parentAddress: "",
};

// 마이페이지에서 서버에 저장된 스펙(UserSpec)을 불러와 수정 폼(SpecForm)에 채울 때 씀 —
// specFormToUserSpec의 반대 방향. sido는 region(짧은 시/도 단위)에서 복원하고, district는
// 2026-08-05부터 실제로 저장되는 spec.district 값을 그대로 씀(matching_gaps.md 14번 전에는
// district 자체를 안 보내고 버려서 그 시/도의 첫 번째 구/군으로만 근사 복원했었음).
export function userSpecToSpecForm(spec: UserSpec): SpecForm {
  const sido = sidoNameFromRegion(spec.region);
  const district = spec.district || (SIDO_LIST.find((s) => s.name === sido)?.districts[0] ?? "");
  return {
    display_name: spec.display_name ?? "",
    birth_date: spec.birth_date ?? "",
    university: spec.university,
    college: spec.college,
    department: spec.department ?? "",
    semester_gpa: String(spec.semester_gpa),
    cumulative_gpa: String(spec.cumulative_gpa),
    gender: spec.gender,
    sido,
    district,
    address: spec.address ?? "",
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
    languageTests: spec.language_tests.map((t) => ({ type: t.type, score: String(t.score) })),
    disabilityTypes: spec.disability_type,
    specialStatusEnabled: spec.special_status.length > 0,
    specialStatus: spec.special_status,
    creditsLastSemester: spec.credits_last_semester != null ? String(spec.credits_last_semester) : "",
    parentRegionEnabled: spec.parent_region != null,
    parentSido: spec.parent_region != null ? sidoNameFromRegion(spec.parent_region) : SIDO_LIST[0].name,
    parentDistrict:
      spec.parent_district ||
      SIDO_LIST.find(
        (s) => s.name === (spec.parent_region != null ? sidoNameFromRegion(spec.parent_region) : SIDO_LIST[0].name)
      )?.districts[0] ||
      "",
    parentAddress: spec.parent_address ?? "",
  };
}
