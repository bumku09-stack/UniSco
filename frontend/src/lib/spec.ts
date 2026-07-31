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
