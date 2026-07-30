"use client";

import { useEffect, useState } from "react";
import { regionShortName, SIDO_LIST } from "@/lib/regions";
import { UNIVERSITIES } from "@/lib/universities";

type Scholarship = {
  id: number;
  name: string;
  provider: string | null;
  description: string | null;
  amount: number | null;
  application_url: string | null;
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
};

type EnrollmentStatus = "undergrad_enrolled" | "undergrad_leave" | "post_undergrad";
type DegreeLevel = "masters" | "doctoral" | "integrated_ms_phd";

type UserSpec = {
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
type SpecForm = Omit<UserSpec, "age" | "gpa" | "income_bracket" | "region" | "grade"> & {
  age: string;
  gpa: string;
  income_bracket: string;
  sido: string;
  district: string;
  grade: string;
};

const STORAGE_KEY = "unisco_spec";

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

function formatAmount(amount: number | null) {
  if (amount == null) return null;
  return `${amount.toLocaleString("ko-KR")}원`;
}

const MILITARY_LABEL: Record<string, string> = {
  completed: "군필",
  exempted: "면제",
  not_served: "미필",
};

function eligibilitySummary(s: Scholarship): string {
  const parts: string[] = [];
  if (s.eligible_region) parts.push(s.eligible_region);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`${s.min_age ?? ""}~${s.max_age ?? ""}세`);
  }
  if (s.max_income_bracket != null) parts.push(`소득분위 ${s.max_income_bracket} 이하`);
  if (s.min_gpa != null) parts.push(`학점 ${s.min_gpa} 이상`);
  if (s.required_military_status) parts.push(MILITARY_LABEL[s.required_military_status]);
  if (s.required_gender) parts.push(s.required_gender === "male" ? "남성" : "여성");
  if (s.requires_disability) parts.push("장애인 한정");
  if (s.foreigner_eligibility) {
    parts.push(s.foreigner_eligibility === "foreigner_only" ? "외국인 한정" : "내국인 한정");
  }
  return parts.length > 0 ? parts.join(" · ") : "제한 없음";
}

const CATEGORY_L2_LABEL: Record<string, string> = {
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

const PAGE_SIZE = 15;

function Pagination({
  page,
  totalPages,
  onChange,
}: {
  page: number;
  totalPages: number;
  onChange: (p: number) => void;
}) {
  return (
    <div className="mt-6 flex flex-wrap items-center justify-center gap-1.5">
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
        <button
          key={p}
          type="button"
          onClick={() => onChange(p)}
          className={`flex h-9 w-9 items-center justify-center rounded-xl text-sm font-semibold transition ${
            p === page ? "bg-blue-500 text-white" : "text-gray-500 hover:bg-gray-100"
          }`}
        >
          {p}
        </button>
      ))}
    </div>
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

function ScholarshipCard({ s }: { s: Scholarship }) {
  return (
    <li className="rounded-2xl border border-gray-100 bg-white p-5 shadow-[0_2px_10px_rgba(15,23,42,0.05)]">
      {s.category_l2 && (
        <span className="mb-2 inline-block rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-600">
          {CATEGORY_L2_LABEL[s.category_l2] ?? s.category_l2}
        </span>
      )}
      <h2 className="font-bold text-gray-900">{s.name}</h2>
      {s.provider && <p className="mt-0.5 text-sm text-gray-400">{s.provider}</p>}
      {formatAmount(s.amount) && (
        <p className="mt-2 text-lg font-bold text-blue-600">{formatAmount(s.amount)}</p>
      )}
      {s.description && <p className="mt-2 text-sm leading-relaxed text-gray-600">{s.description}</p>}
      <p className="mt-3 text-xs text-gray-400">{eligibilitySummary(s)}</p>
    </li>
  );
}

export default function SpecWizard() {
  const [step, setStep] = useState<1 | 2>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  // 로그인이 아직 없어서, 브라우저에 저장해뒀다가 다음 방문 때 불러옴 (실제 로그인 붙으면 서버 저장으로 교체 예정)
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
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

  async function handleFinalSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const payload: UserSpec = {
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
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(spec));
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      setResults(await res.json());
      setPage(1);
    } catch {
      setError("매칭에 실패했습니다. 백엔드 서버가 켜져 있는지 확인해주세요.");
      setResults(null);
    } finally {
      setLoading(false);
    }
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

        {results === null && (
          <>
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
          </>
        )}

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
                value={spec.enrollment_status}
                onChange={(v) => setSpec({ ...spec, enrollment_status: v as EnrollmentStatus })}
                options={[
                  { value: "undergrad_enrolled", label: "학부 재학" },
                  { value: "undergrad_leave", label: "학부 휴학" },
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
              <SelectField
                label="학년"
                value={spec.grade}
                onChange={(v) => setSpec({ ...spec, grade: v })}
                options={[
                  { value: "1", label: "1학년" },
                  { value: "2", label: "2학년" },
                  { value: "3", label: "3학년" },
                  { value: "4", label: "4학년" },
                ]}
              />
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
                disabled={loading}
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
              >
                {loading ? "찾는 중..." : "내 장학금 찾기"}
              </button>
            </div>
          </form>
        )}

        {error && (
          <p className="mt-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
            {error}
          </p>
        )}

        {results !== null && !error && (
          <div className="mt-2">
            <button
              type="button"
              onClick={() => setResults(null)}
              className="mb-4 text-sm font-semibold text-gray-400"
            >
              ← 조건 다시 입력
            </button>

            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">매칭 결과</h2>
              <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-blue-600">
                {results.length}건
              </span>
            </div>

            {results.length === 0 ? (
              <p className="mt-8 text-center text-sm text-gray-400">조건에 맞는 장학금이 없습니다.</p>
            ) : (
              <>
                <ul className="mt-4 flex flex-col gap-3">
                  {results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map((s) => (
                    <ScholarshipCard key={s.id} s={s} />
                  ))}
                </ul>
                {results.length > PAGE_SIZE && (
                  <Pagination
                    page={page}
                    totalPages={Math.ceil(results.length / PAGE_SIZE)}
                    onChange={setPage}
                  />
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
