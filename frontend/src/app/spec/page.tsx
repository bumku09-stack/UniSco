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
  "w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-900 focus:border-zinc-500 focus:outline-none";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-zinc-700">{label}</span>
      {children}
    </label>
  );
}

function ScholarshipCard({ s }: { s: Scholarship }) {
  return (
    <li className="rounded-xl border border-zinc-200 p-4">
      {s.category_l2 && (
        <span className="mb-1.5 inline-block rounded-full bg-zinc-100 px-2 py-0.5 text-[11px] font-medium text-zinc-500">
          {CATEGORY_L2_LABEL[s.category_l2] ?? s.category_l2}
        </span>
      )}
      <div className="flex items-start justify-between gap-2">
        <h2 className="font-semibold text-zinc-900">{s.name}</h2>
        {formatAmount(s.amount) && (
          <span className="shrink-0 text-sm font-medium text-zinc-900">{formatAmount(s.amount)}</span>
        )}
      </div>
      {s.provider && <p className="mt-0.5 text-sm text-zinc-500">{s.provider}</p>}
      {s.description && <p className="mt-2 text-sm text-zinc-600">{s.description}</p>}
      <p className="mt-2 text-xs text-zinc-400">{eligibilitySummary(s)}</p>
    </li>
  );
}

export default function SpecWizard() {
  const [step, setStep] = useState<1 | 2>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch {
      setError("매칭에 실패했습니다. 백엔드 서버가 켜져 있는지 확인해주세요.");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto w-full max-w-md px-4 py-6">
        <h1 className="text-xl font-bold text-zinc-900">UniSco</h1>
        <p className="mt-1 text-sm text-zinc-500">내 조건에 맞는 장학금 찾기</p>

        <p className="mt-4 text-xs font-medium text-zinc-400">
          {step === 1 ? "1 / 2 · 학교 정보" : "2 / 2 · 공통 정보"}
        </p>

        {step === 1 && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(2);
            }}
            className="mt-4 flex flex-col gap-4"
          >
            <Field label="소속 대학">
              <select
                value={spec.university}
                onChange={(e) => {
                  const next = UNIVERSITIES.find((u) => u.name === e.target.value)!;
                  setSpec({ ...spec, university: next.name, college: next.colleges[0] ?? "" });
                }}
                className={inputClass}
              >
                {UNIVERSITIES.map((u) => (
                  <option key={u.name} value={u.name}>
                    {u.name}
                  </option>
                ))}
              </select>
            </Field>

            {currentColleges.length > 0 && (
              <Field label="단과대">
                <select
                  value={spec.college}
                  onChange={(e) => setSpec({ ...spec, college: e.target.value })}
                  className={inputClass}
                >
                  {currentColleges.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </Field>
            )}

            <Field label="재학 상태">
              <select
                value={spec.enrollment_status}
                onChange={(e) =>
                  setSpec({ ...spec, enrollment_status: e.target.value as EnrollmentStatus })
                }
                className={inputClass}
              >
                <option value="undergrad_enrolled">학부 재학</option>
                <option value="undergrad_leave">학부 휴학</option>
                <option value="post_undergrad">학부 이후 과정 (대학원 등)</option>
              </select>
            </Field>

            {spec.enrollment_status === "post_undergrad" ? (
              <Field label="과정 구분">
                <select
                  value={spec.degree_level ?? "masters"}
                  onChange={(e) => setSpec({ ...spec, degree_level: e.target.value as DegreeLevel })}
                  className={inputClass}
                >
                  <option value="masters">석사</option>
                  <option value="doctoral">박사</option>
                  <option value="integrated_ms_phd">석박사통합</option>
                </select>
              </Field>
            ) : (
              <Field label="학년">
                <select
                  value={spec.grade}
                  onChange={(e) => setSpec({ ...spec, grade: e.target.value })}
                  className={inputClass}
                >
                  <option value="1">1학년</option>
                  <option value="2">2학년</option>
                  <option value="3">3학년</option>
                  <option value="4">4학년</option>
                </select>
              </Field>
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
              className="mt-2 rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white"
            >
              다음
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleFinalSubmit} className="mt-4 flex flex-col gap-4">
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
              <select
                value={spec.gender}
                onChange={(e) => setSpec({ ...spec, gender: e.target.value as UserSpec["gender"] })}
                className={inputClass}
              >
                <option value="male">남성</option>
                <option value="female">여성</option>
              </select>
            </Field>

            <Field label="광역자치단체">
              <select
                value={spec.sido}
                onChange={(e) => {
                  const nextSido = SIDO_LIST.find((s) => s.name === e.target.value)!;
                  setSpec({ ...spec, sido: nextSido.name, district: nextSido.districts[0] ?? "" });
                }}
                className={inputClass}
              >
                {SIDO_LIST.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </select>
            </Field>

            {currentDistricts.length > 0 && (
              <Field label="기초자치단체">
                <select
                  value={spec.district}
                  onChange={(e) => setSpec({ ...spec, district: e.target.value })}
                  className={inputClass}
                >
                  {currentDistricts.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </Field>
            )}

            <Field label="병역">
              <select
                value={spec.military_status}
                onChange={(e) =>
                  setSpec({ ...spec, military_status: e.target.value as UserSpec["military_status"] })
                }
                className={inputClass}
              >
                <option value="not_served">미필</option>
                <option value="completed">군필</option>
                <option value="exempted">면제</option>
              </select>
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

            <label className="flex items-center gap-2 text-sm text-zinc-700">
              <input
                type="checkbox"
                checked={spec.has_disability}
                onChange={(e) => setSpec({ ...spec, has_disability: e.target.checked })}
              />
              장애인
            </label>

            <label className="flex items-center gap-2 text-sm text-zinc-700">
              <input
                type="checkbox"
                checked={spec.is_foreigner}
                onChange={(e) => setSpec({ ...spec, is_foreigner: e.target.checked })}
              />
              외국인(유학생)
            </label>

            <div className="mt-2 flex gap-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full rounded-lg border border-zinc-300 px-4 py-2.5 text-sm font-medium text-zinc-700"
              >
                이전
              </button>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50"
              >
                {loading ? "찾는 중..." : "내 장학금 찾기"}
              </button>
            </div>
          </form>
        )}

        {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

        {results !== null && !error && (
          <div className="mt-8">
            <p className="text-sm text-zinc-500">{results.length}건 매칭됨</p>
            {results.length === 0 ? (
              <p className="mt-4 text-sm text-zinc-500">조건에 맞는 장학금이 없습니다.</p>
            ) : (
              <ul className="mt-3 flex flex-col gap-3">
                {results.map((s) => (
                  <ScholarshipCard key={s.id} s={s} />
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
