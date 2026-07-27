"use client";

import { useEffect, useState } from "react";

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
};

type UserSpec = {
  university: string;
  gpa: number;
  age: number;
  gender: "male" | "female";
  region: string;
  military_status: "completed" | "exempted" | "not_served";
  income_bracket: number;
  has_disability: boolean;
  is_foreigner: boolean;
};

// 대학마다 학점 만점 기준이 달라서, 학교 선택하면 자동으로 표시해줌 (따로 "몇 점 만점?" 안 물어봄)
const UNIVERSITIES: { name: string; gpaScale: number }[] = [
  { name: "충남대학교", gpaScale: 4.5 },
  { name: "KAIST", gpaScale: 4.3 },
  { name: "기타", gpaScale: 4.5 },
];

const STORAGE_KEY = "unisco_spec";

const initialSpec: UserSpec = {
  university: UNIVERSITIES[0].name,
  gpa: 4.0,
  age: 20,
  gender: "male",
  region: "",
  military_status: "not_served",
  income_bracket: 1,
  has_disability: false,
  is_foreigner: false,
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
  const [spec, setSpec] = useState<UserSpec>(initialSpec);
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 로그인이 아직 없어서, 브라우저에 저장해뒀다가 다음 방문 때 불러옴 (실제 로그인 붙으면 서버 저장으로 교체 예정)
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setSpec(JSON.parse(saved));
      } catch {
        // 저장된 값이 깨졌으면 그냥 기본값 씀
      }
    }
  }, []);

  const gpaScale = UNIVERSITIES.find((u) => u.name === spec.university)?.gpaScale ?? 4.5;

  async function handleFinalSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(spec));
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(spec),
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
                onChange={(e) => setSpec({ ...spec, university: e.target.value })}
                className={inputClass}
              >
                {UNIVERSITIES.map((u) => (
                  <option key={u.name} value={u.name}>
                    {u.name}
                  </option>
                ))}
              </select>
            </Field>

            <Field label={`학점 (${gpaScale} 만점 기준)`}>
              <input
                type="number"
                required
                step={0.01}
                min={0}
                max={gpaScale}
                value={spec.gpa}
                onChange={(e) => setSpec({ ...spec, gpa: Number(e.target.value) })}
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
                onChange={(e) => setSpec({ ...spec, age: Number(e.target.value) })}
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

            <Field label="지역">
              <input
                type="text"
                required
                placeholder="예: 대전"
                value={spec.region}
                onChange={(e) => setSpec({ ...spec, region: e.target.value })}
                className={inputClass}
              />
            </Field>

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
                onChange={(e) => setSpec({ ...spec, income_bracket: Number(e.target.value) })}
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
