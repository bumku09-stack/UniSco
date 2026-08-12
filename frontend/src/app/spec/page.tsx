"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { CommonFields, OptionalFields, SchoolFields, deriveSpecFields } from "@/components/spec-fields";
import { apiUrl, authFetch, isLoggedIn } from "@/lib/auth";
import { clearGuestData, getGuestSpec, saveGuestResults, saveGuestSpec } from "@/lib/guest";
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
  admission_track: "general",
};

function ProgressBar({ step, totalSteps }: { step: number; totalSteps: number }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
      <div
        className="h-full rounded-full bg-blue-500 transition-all duration-300"
        style={{ width: `${(step / totalSteps) * 100}%` }}
      />
    </div>
  );
}

// 2026-08-10 개편 — 로그인 없이도 접근 가능하게 함("가볍게 둘러보기" 플로우). 로그인 여부는
// isLoggedIn()이 localStorage를 읽어서 판단하는데, 서버 렌더링 시점엔 localStorage 자체가
// 없어서 render 본문에서 직접 부르면 SSR이 죽음 — 그래서 항상 "loading"으로 시작해서
// useEffect(클라이언트 전용) 안에서만 실제로 판단함(홈 화면의 hydration-mismatch 회피
// 패턴과 동일한 이유).
//   - 로그인 안 됨(게스트): 1·2단계(학교 정보 + 공통 정보)만 받고 POST /match로 즉석 매칭 →
//     결과+입력값을 세션에 저장하고 /home으로. 3단계(선택 정보)는 아예 안 보여줌 — 회원가입
//     후에 마저 입력하도록 유도(/home의 안내 배너 참고).
//   - 로그인 됨: 기존 3단계 그대로 + POST /users/me/spec. 단, 방금 게스트로 입력해둔 값이
//     세션에 있으면(회원가입 직후 전환 케이스) 그걸로 폼을 미리 채우고 3단계부터 이어서
//     입력하게 함 — 1·2단계를 다시 안 치게.
type Mode = "loading" | "guest" | "authed";

export default function SpecWizard() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("loading");
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);
  const [optionalInfo, setOptionalInfo] = useState<OptionalInfo>(initialOptionalInfo);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 함수로 한 번 감쌈 — effect 본문에 setState를 직접 두면 react-hooks/set-state-in-effect가
    // 걸림(home/page.tsx와 동일한 이유, 여긴 await이 없어서 async는 안 씀).
    (() => {
      if (!isLoggedIn()) {
        setMode("guest");
        return;
      }
      setMode("authed");
      const guest = getGuestSpec();
      if (guest) {
        setSpec(guest.spec);
        setOptionalInfo(guest.optionalInfo);
        setStep(3);
      }
    })();
  }, []);

  const derived = deriveSpecFields(spec);
  const totalSteps = mode === "guest" ? 2 : 3;

  async function handleGuestFinish(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: UserSpec = specFormToUserSpec(spec, initialOptionalInfo);
      const res = await fetch(apiUrl("/match"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      const results = await res.json();
      saveGuestSpec(spec, initialOptionalInfo);
      saveGuestResults(results);
      router.push("/home");
    } catch {
      setError("매칭에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  }

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
      // 게스트로 입력했다가 회원가입 전환한 경우 여기서 진짜 계정 스펙이 저장됐으니
      // 세션에 남아있던 게스트 데이터는 정리 — 안 그러면 로그아웃 후 다시 게스트로 돌아왔을
      // 때 낡은 값이 남아있게 됨.
      clearGuestData();
      router.push("/home");
    } catch {
      setError("스펙 저장에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  }

  if (mode === "loading") {
    return (
      <div className="min-h-screen bg-white">
        <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl">
          <TopBar />
        </div>
      </div>
    );
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
          {step === 2 && mode === "guest" && "입력하면 바로 매칭 결과를 볼 수 있어요"}
          {step === 2 && mode === "authed" && "공통 조건까지 확인하면 매칭이 끝나요"}
          {step === 3 && "선택 항목이라 없으면 그냥 넘어가도 돼요"}
        </p>

        <div className="mt-5 flex items-center gap-3">
          <ProgressBar step={step} totalSteps={totalSteps} />
          <span className="shrink-0 text-xs font-semibold text-gray-400">
            {step} / {totalSteps}
          </span>
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

        {step === 2 && mode === "guest" && (
          <form onSubmit={handleGuestFinish} className="mt-6 flex flex-col gap-5">
            <CommonFields
              spec={spec}
              setSpec={setSpec}
              derived={derived}
              optionalInfo={optionalInfo}
              setOptionalInfo={setOptionalInfo}
            />

            {error && (
              <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">{error}</p>
            )}

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
                disabled={submitting}
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
              >
                {submitting ? "찾는 중..." : "장학금 찾아보기"}
              </button>
            </div>
          </form>
        )}

        {step === 2 && mode === "authed" && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(3);
            }}
            className="mt-6 flex flex-col gap-5"
          >
            <CommonFields
              spec={spec}
              setSpec={setSpec}
              derived={derived}
              optionalInfo={optionalInfo}
              setOptionalInfo={setOptionalInfo}
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

        {step === 3 && mode === "authed" && (
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
