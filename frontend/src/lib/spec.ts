import { regionShortName } from "@/lib/regions";

export type EnrollmentStatus = "undergrad_enrolled" | "undergrad_leave" | "post_undergrad";
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

// 로그인이 아직 없어서, 스펙 입력 폼(/spec)과 매칭 결과(/matches)가 브라우저
// localStorage로 값을 주고받음 (실제 로그인 붙으면 서버 저장으로 교체 예정).
export const SPEC_STORAGE_KEY = "unisco_spec";

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
