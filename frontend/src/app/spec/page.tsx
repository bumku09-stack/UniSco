"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { SIDO_LIST } from "@/lib/regions";
import { SPEC_STORAGE_KEY, SpecForm, EnrollmentStatus, DegreeLevel, UserSpec } from "@/lib/spec";
import { UNIVERSITIES } from "@/lib/universities";

const DEFAULT_SIDO = SIDO_LIST.find((s) => s.name === "대전광역시")!;
const DEFAULT_UNIVERSITY = UNIVERSITIES[0];

const initialSpec: SpecForm = {
  university: DEFAULT_UNIVERSITY.name,
  college: DEFAULT_UNIVERSITY.colleges[0] ?? "",
  gpa: "4.0",
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

const inputClass =
  "w-full rounded-2xl bg-gray-100 px-4 py-3.5 text-[15px] text-gray-900 outline-none transition focus:bg-blue-50 focus:ring-2 focus:ring-blue-500";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-gray-700">{label}</span>
      {children}
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <Field label={label}>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`${inputClass} appearance-none pr-10`}
        >
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <svg
          className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
          viewBox="0 0 20 20"
          fill="none"
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </Field>
  );
}

function PillToggle({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 rounded-2xl border py-3.5 text-sm font-semibold transition ${
            value === opt.value
              ? "border-blue-500 bg-blue-50 text-blue-600"
              : "border-gray-200 bg-white text-gray-500"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

function ToggleChip({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex items-center justify-between rounded-2xl border px-4 py-3.5 text-sm font-semibold transition ${
        checked ? "border-blue-500 bg-blue-50 text-blue-600" : "border-gray-200 bg-white text-gray-600"
      }`}
    >
      <span>{label}</span>
      <span
        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] transition ${
          checked ? "border-blue-500 bg-blue-500 text-white" : "border-gray-300 text-transparent"
        }`}
      >
        ✓
      </span>
    </button>
  );
}

function ProgressBar({ step }: { step: 1 | 2 }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
      <div
        className="h-full rounded-full bg-blue-500 transition-all duration-300"
        style={{ width: step === 1 ? "50%" : "100%" }}
      />
    </div>
  );
}

export default function SpecWizard() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);

  // 로그인이 아직 없어서, 브라우저에 저장해뒀다가 다음 방문 때 불러옴 (실제 로그인 붙으면 서버 저장으로 교체 예정)
  useEffect(() => {
    const saved = localStorage.getItem(SPEC_STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSpec({
          ...initialSpec,
          ...parsed,
          age: String(parsed.age ?? initialSpec.age),
          gpa: String(parsed.gpa ?? initialSpec.gpa),
          income_bracket: String(parsed.income_bracket ?? initialSpec.income_bracket),
          sido: parsed.sido ?? initialSpec.sido,
          district: parsed.district ?? initialSpec.district,
          college: parsed.college ?? initialSpec.college,
          enrollment_status: parsed.enrollment_status ?? initialSpec.enrollment_status,
          grade: String(parsed.grade ?? initialSpec.grade),
          degree_level: parsed.degree_level ?? initialSpec.degree_level,
        });
      } catch {
        // 저장된 값이 깨졌으면 그냥 기본값 씀
      }
    }
  }, []);

  const currentUniversity = UNIVERSITIES.find((u) => u.name === spec.university) ?? UNIVERSITIES[0];
  const gpaScale = currentUniversity.gpaScale;
  const currentColleges = currentUniversity.colleges;
  const currentDistricts = SIDO_LIST.find((s) => s.name === spec.sido)?.districts ?? [];

  function handleFinalSubmit(e: React.FormEvent) {
    e.preventDefault();
    localStorage.setItem(SPEC_STORAGE_KEY, JSON.stringify(spec));
    router.push("/matches");
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500 text-sm font-bold text-white">
            U
          </div>
          <span className="text-base font-bold text-gray-900">UniSco</span>
        </div>

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">
          {step === 1 ? "어느 학교에 다니시나요?" : "몇 가지만 더 알려주세요"}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {step === 1
            ? "학교 정보에 맞는 장학금부터 찾아드릴게요"
            : "공통 조건까지 확인하면 매칭이 끝나요"}
        </p>

        <div className="mt-5 flex items-center gap-3">
          <ProgressBar step={step} />
          <span className="shrink-0 text-xs font-semibold text-gray-400">{step} / 2</span>
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
                setSpec({ ...spec, university: next.name, college: next.colleges[0] ?? "" });
              }}
              options={UNIVERSITIES.map((u) => ({ value: u.name, label: u.name }))}
            />

            {currentColleges.length > 0 && (
              <SelectField
                label="단과대"
                value={spec.college}
                onChange={(v) => setSpec({ ...spec, college: v })}
                options={currentColleges.map((c) => ({ value: c, label: c }))}
              />
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

            <Field label={`학점 (${gpaScale} 만점 기준)`}>
              <input
                type="number"
                required
                step={0.01}
                min={0}
                max={gpaScale}
                value={spec.gpa}
                onChange={(e) => setSpec({ ...spec, gpa: e.target.value })}
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
          <form onSubmit={handleFinalSubmit} className="mt-6 flex flex-col gap-5">
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

            <div className="flex flex-col gap-2">
              <ToggleChip
                checked={spec.has_disability}
                onChange={(v) => setSpec({ ...spec, has_disability: v })}
                label="장애인"
              />
              <ToggleChip
                checked={spec.is_foreigner}
                onChange={(v) => setSpec({ ...spec, is_foreigner: v })}
                label="외국인(유학생)"
              />
            </div>

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
                내 장학금 찾기
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
