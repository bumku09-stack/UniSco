"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  CollapsibleToggle,
  Field,
  inputClass,
  MultiPillSelect,
  PillToggle,
  SelectField,
  ToggleChip,
  TopBar,
} from "@/components/form-ui";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { SIDO_LIST } from "@/lib/regions";
import {
  DegreeLevel,
  DISABILITY_TYPES,
  EnrollmentStatus,
  initialOptionalInfo,
  LANGUAGE_TESTS,
  OptionalInfo,
  specFormToUserSpec,
  SpecForm,
  SPECIAL_STATUS_OPTIONS,
  UserSpec,
} from "@/lib/spec";
import { UNIVERSITIES } from "@/lib/universities";

const DEFAULT_SIDO = SIDO_LIST.find((s) => s.name === "대전광역시")!;
const DEFAULT_UNIVERSITY = UNIVERSITIES[0];

const initialSpec: SpecForm = {
  university: DEFAULT_UNIVERSITY.name,
  college: DEFAULT_UNIVERSITY.colleges[0]?.name ?? "",
  department: DEFAULT_UNIVERSITY.colleges[0]?.departments[0] ?? "",
  semester_gpa: "4.0",
  cumulative_gpa: "4.0",
  age: "20",
  gender: "male",
  sido: DEFAULT_SIDO.name,
  district: DEFAULT_SIDO.districts[0] ?? "",
  military_status: "not_served",
  income_bracket: "1",
  has_disability: false,
  is_foreigner: false,
  enrollment_status: "undergrad_enrolled",
  grade: "1",
  degree_level: null,
};

function ProgressBar({ step }: { step: 1 | 2 | 3 }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
      <div
        className="h-full rounded-full bg-blue-500 transition-all duration-300"
        style={{ width: `${(step / 3) * 100}%` }}
      />
    </div>
  );
}

export default function SpecWizard() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);
  const [optionalInfo, setOptionalInfo] = useState<OptionalInfo>(initialOptionalInfo);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) router.replace("/");
  }, [router]);

  const currentUniversity = UNIVERSITIES.find((u) => u.name === spec.university) ?? UNIVERSITIES[0];
  const gpaScale = currentUniversity.gpaScale;
  const currentColleges = currentUniversity.colleges;
  const currentDepartments =
    currentColleges.find((c) => c.name === spec.college)?.departments ?? [];
  const currentDistricts = SIDO_LIST.find((s) => s.name === spec.sido)?.districts ?? [];

  async function handleFinalSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: UserSpec = specFormToUserSpec(spec, optionalInfo);
      const res = await authFetch("/users/me/spec", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail ?? `status ${res.status}`);
      }
      router.push("/home");
    } catch {
      setError("스펙 저장에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <TopBar />

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">
          {step === 1 && "어느 학교에 다니시나요?"}
          {step === 2 && "몇 가지만 더 알려주세요"}
          {step === 3 && "해당하는 항목이 있으면 알려주세요"}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {step === 1 && "학교 정보에 맞는 장학금부터 찾아드릴게요"}
          {step === 2 && "공통 조건까지 확인하면 매칭이 끝나요"}
          {step === 3 && "선택 항목이라 없으면 그냥 넘어가도 돼요"}
        </p>

        <div className="mt-5 flex items-center gap-3">
          <ProgressBar step={step} />
          <span className="shrink-0 text-xs font-semibold text-gray-400">{step} / 3</span>
        </div>

        {step === 1 && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(2);
            }}
            className="mt-6 flex flex-col gap-5"
          >
            <SelectField
              label="소속 대학"
              value={spec.university}
              onChange={(v) => {
                const next = UNIVERSITIES.find((u) => u.name === v)!;
                setSpec({
                  ...spec,
                  university: next.name,
                  college: next.colleges[0]?.name ?? "",
                  department: next.colleges[0]?.departments[0] ?? "",
                });
              }}
              options={UNIVERSITIES.map((u) => ({ value: u.name, label: u.name }))}
            />

            {currentColleges.length > 0 && (
              <SelectField
                label="단과대"
                value={spec.college}
                onChange={(v) => {
                  const nextCollege = currentColleges.find((c) => c.name === v)!;
                  setSpec({ ...spec, college: v, department: nextCollege.departments[0] ?? "" });
                }}
                options={currentColleges.map((c) => ({ value: c.name, label: c.name }))}
              />
            )}

            {currentDepartments.length > 0 ? (
              <SelectField
                label="학과"
                value={spec.department}
                onChange={(v) => setSpec({ ...spec, department: v })}
                options={currentDepartments.map((d) => ({ value: d, label: d }))}
              />
            ) : (
              <Field label="학과 (선택)">
                <input
                  type="text"
                  value={spec.department}
                  onChange={(e) => setSpec({ ...spec, department: e.target.value })}
                  placeholder="예: 컴퓨터공학과"
                  className={inputClass}
                />
              </Field>
            )}

            <Field label="재학 상태">
              <PillToggle
                value={spec.enrollment_status === "post_undergrad" ? "post_undergrad" : "undergrad"}
                onChange={(v) =>
                  setSpec({
                    ...spec,
                    enrollment_status: v === "post_undergrad" ? "post_undergrad" : "undergrad_enrolled",
                  })
                }
                options={[
                  { value: "undergrad", label: "학부" },
                  { value: "post_undergrad", label: "대학원 등" },
                ]}
              />
            </Field>

            {spec.enrollment_status === "post_undergrad" ? (
              <SelectField
                label="과정 구분"
                value={spec.degree_level ?? "masters"}
                onChange={(v) => setSpec({ ...spec, degree_level: v as DegreeLevel })}
                options={[
                  { value: "masters", label: "석사" },
                  { value: "doctoral", label: "박사" },
                  { value: "integrated_ms_phd", label: "석박사통합" },
                ]}
              />
            ) : (
              <>
                <Field label="학부 재학 구분">
                  <PillToggle
                    value={spec.enrollment_status}
                    onChange={(v) => {
                      const nextStatus = v as EnrollmentStatus;
                      // 편입생은 1학년으로 들어오는 경우가 거의 없어서, 편입 선택 중
                      // 학년이 1학년으로 남아있으면 2학년으로 올려줌
                      const nextGrade =
                        nextStatus === "undergrad_transfer" && spec.grade === "1" ? "2" : spec.grade;
                      setSpec({ ...spec, enrollment_status: nextStatus, grade: nextGrade });
                    }}
                    options={[
                      { value: "undergrad_enrolled", label: "재학" },
                      { value: "undergrad_leave", label: "휴학" },
                      { value: "undergrad_transfer", label: "편입" },
                    ]}
                  />
                </Field>

                <div>
                  <SelectField
                    label="학년"
                    value={spec.grade}
                    onChange={(v) => setSpec({ ...spec, grade: v })}
                    options={(spec.enrollment_status === "undergrad_transfer"
                      ? ["2", "3", "4"]
                      : ["1", "2", "3", "4"]
                    ).map((g) => ({ value: g, label: `${g}학년` }))}
                  />
                  {spec.enrollment_status === "undergrad_enrolled" && spec.grade === "1" && (
                    <p className="mt-1.5 text-xs font-semibold text-blue-500">
                      ✓ 신입생으로 인식돼요 — 신입생 전용 장학금도 함께 찾아드려요
                    </p>
                  )}
                </div>
              </>
            )}

            <Field label={`직전 학기 평점 (${gpaScale} 만점 기준)`}>
              <input
                type="number"
                required
                step={0.01}
                min={0}
                max={gpaScale}
                value={spec.semester_gpa}
                onChange={(e) => setSpec({ ...spec, semester_gpa: e.target.value })}
                className={inputClass}
              />
            </Field>

            <Field label={`전체 재학기간 누적 평점 (${gpaScale} 만점 기준)`}>
              <input
                type="number"
                required
                step={0.01}
                min={0}
                max={gpaScale}
                value={spec.cumulative_gpa}
                onChange={(e) => setSpec({ ...spec, cumulative_gpa: e.target.value })}
                className={inputClass}
              />
            </Field>

            <button
              type="submit"
              className="mt-2 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99]"
            >
              다음
            </button>
          </form>
        )}

        {step === 2 && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(3);
            }}
            className="mt-6 flex flex-col gap-5"
          >
            <Field label="나이">
              <input
                type="number"
                required
                min={0}
                value={spec.age}
                onChange={(e) => setSpec({ ...spec, age: e.target.value })}
                className={inputClass}
              />
            </Field>

            <Field label="성별">
              <PillToggle
                value={spec.gender}
                onChange={(v) => setSpec({ ...spec, gender: v as UserSpec["gender"] })}
                options={[
                  { value: "male", label: "남성" },
                  { value: "female", label: "여성" },
                ]}
              />
            </Field>

            <SelectField
              label="광역자치단체"
              value={spec.sido}
              onChange={(v) => {
                const nextSido = SIDO_LIST.find((s) => s.name === v)!;
                setSpec({ ...spec, sido: nextSido.name, district: nextSido.districts[0] ?? "" });
              }}
              options={SIDO_LIST.map((s) => ({ value: s.name, label: s.name }))}
            />

            {currentDistricts.length > 0 && (
              <SelectField
                label="기초자치단체"
                value={spec.district}
                onChange={(v) => setSpec({ ...spec, district: v })}
                options={currentDistricts.map((d) => ({ value: d, label: d }))}
              />
            )}

            <Field label="병역">
              <PillToggle
                value={spec.military_status}
                onChange={(v) =>
                  setSpec({ ...spec, military_status: v as UserSpec["military_status"] })
                }
                options={[
                  { value: "not_served", label: "미필" },
                  { value: "completed", label: "군필" },
                  { value: "exempted", label: "면제" },
                ]}
              />
            </Field>

            <Field label="소득분위 (1~10)">
              <input
                type="number"
                required
                min={1}
                max={10}
                value={spec.income_bracket}
                onChange={(e) => setSpec({ ...spec, income_bracket: e.target.value })}
                className={inputClass}
              />
            </Field>

            <ToggleChip
              checked={spec.is_foreigner}
              onChange={(v) => setSpec({ ...spec, is_foreigner: v })}
              label="외국인(유학생)"
            />

            <div className="mt-2 flex gap-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full rounded-2xl border border-gray-200 py-4 text-[15px] font-semibold text-gray-600 transition hover:bg-gray-50"
              >
                이전
              </button>
              <button
                type="submit"
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99]"
              >
                다음
              </button>
            </div>
          </form>
        )}

        {step === 3 && (
          <form onSubmit={handleFinalSubmit} className="mt-6 flex flex-col gap-5">
            <CollapsibleToggle
              checked={optionalInfo.languageTestEnabled}
              onChange={(v) => setOptionalInfo({ ...optionalInfo, languageTestEnabled: v })}
              label="어학점수"
            >
              <SelectField
                label="종류"
                value={optionalInfo.languageTestType}
                onChange={(v) => setOptionalInfo({ ...optionalInfo, languageTestType: v })}
                options={LANGUAGE_TESTS.map((t) => ({ value: t.value, label: t.label }))}
              />
              <Field
                label={`점수${
                  LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max != null
                    ? ` (만점 ${LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max})`
                    : ""
                }`}
              >
                <input
                  type="number"
                  min={0}
                  max={LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max ?? undefined}
                  value={optionalInfo.languageTestScore}
                  onChange={(e) => setOptionalInfo({ ...optionalInfo, languageTestScore: e.target.value })}
                  className={inputClass}
                />
              </Field>
            </CollapsibleToggle>

            <CollapsibleToggle
              checked={spec.has_disability}
              onChange={(v) => setSpec({ ...spec, has_disability: v })}
              label="장애인"
            >
              <SelectField
                label="유형"
                value={optionalInfo.disabilityType}
                onChange={(v) => setOptionalInfo({ ...optionalInfo, disabilityType: v })}
                options={DISABILITY_TYPES}
              />
            </CollapsibleToggle>

            <CollapsibleToggle
              checked={optionalInfo.specialStatusEnabled}
              onChange={(v) =>
                setOptionalInfo({
                  ...optionalInfo,
                  specialStatusEnabled: v,
                  specialStatus: v ? optionalInfo.specialStatus : [],
                })
              }
              label="특수상황"
            >
              <MultiPillSelect
                values={optionalInfo.specialStatus}
                onChange={(v) => setOptionalInfo({ ...optionalInfo, specialStatus: v })}
                options={SPECIAL_STATUS_OPTIONS}
              />
            </CollapsibleToggle>

            {error && (
              <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">{error}</p>
            )}

            <div className="mt-2 flex gap-2">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="w-full rounded-2xl border border-gray-200 py-4 text-[15px] font-semibold text-gray-600 transition hover:bg-gray-50"
              >
                이전
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
              >
                {submitting ? "저장 중..." : "내 장학금 찾기"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
