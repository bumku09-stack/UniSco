"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { CommonFields, OptionalFields, SchoolFields, deriveSpecFields } from "@/components/spec-fields";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { SIDO_LIST } from "@/lib/regions";
import { initialOptionalInfo, OptionalInfo, specFormToUserSpec, SpecForm, UserSpec } from "@/lib/spec";
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
  income_bracket: "unknown",
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

  const derived = deriveSpecFields(spec);

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
            <SchoolFields spec={spec} setSpec={setSpec} derived={derived} showFreshmanHint />

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
            <CommonFields spec={spec} setSpec={setSpec} derived={derived} />

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
            <OptionalFields
              spec={spec}
              setSpec={setSpec}
              optionalInfo={optionalInfo}
              setOptionalInfo={setOptionalInfo}
            />

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
