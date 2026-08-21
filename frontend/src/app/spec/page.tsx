"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { OptionalFields, PersonalFields, SchoolFields, deriveSpecFields } from "@/components/spec-fields";
import { apiUrl, authFetch, clearTokens, isLoggedIn } from "@/lib/auth";
import { clearGuestData, getGuestSpec, saveGuestResults, saveGuestSpec } from "@/lib/guest";
import {
  initialOptionalInfo,
  initialSpec,
  OptionalInfo,
  specFormToUserSpec,
  SpecForm,
  UserSpec,
} from "@/lib/spec";

const STEP_LABELS = ["인적사항", "학교정보", "선택사항"];

// 2026-08-21 추가 — 얇은 진행 바 대신 번호 원 + 라벨을 눌러서 원하는 단계로 바로 이동할 수
// 있는 스텝 인디케이터로 교체. 사용자 요청으로 이미 지나온 단계뿐 아니라 앞 단계로도 자유롭게
// 건너뛸 수 있게 함 — 대신 각 단계의 실제 "다음"/제출 버튼은 그대로 그 단계 <form>에 남아있어서
// (여기서 새로 안 건드림) 정상적으로 "다음"을 눌러 넘어갈 때는 필수 입력값 검증이 그대로
// 걸림. 원을 눌러 건너뛴 뒤 앞 단계를 안 채우고 마지막에서 바로 제출하면 그 단계 필수값
// 검증은 건너뛰게 되는데, 이건 사용자가 자유 이동을 선택하면서 감수하기로 한 트레이드오프.
function StepIndicator({
  step,
  totalSteps,
  onStepClick,
}: {
  step: number;
  totalSteps: number;
  onStepClick: (n: number) => void;
}) {
  return (
    <div className="flex items-start">
      {STEP_LABELS.slice(0, totalSteps).map((label, i) => {
        const n = i + 1;
        const isActive = n === step;
        const isPast = n < step;
        return (
          <div key={n} className="contents">
            <button
              type="button"
              onClick={() => onStepClick(n)}
              className="flex flex-col items-center gap-1.5"
            >
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold transition ${
                  isActive
                    ? "bg-blue-500 text-white shadow-neu-raised-sm"
                    : isPast
                      ? "bg-neu-surface text-blue-500 shadow-neu-pressed"
                      : "bg-neu-surface text-gray-400 shadow-neu-raised-sm"
                }`}
              >
                {n}
              </span>
              <span
                className={`whitespace-nowrap text-xs font-semibold ${
                  isActive ? "text-blue-600" : isPast ? "text-blue-400" : "text-gray-400"
                }`}
              >
                {label}
              </span>
            </button>
            {n < totalSteps && <div className="mt-4 h-px flex-1 bg-gray-200" />}
          </div>
        );
      })}
    </div>
  );
}

// 2026-08-10 개편 — 로그인 없이도 접근 가능하게 함("가볍게 둘러보기" 플로우). 로그인 여부는
// isLoggedIn()이 localStorage를 읽어서 판단하는데, 서버 렌더링 시점엔 localStorage 자체가
// 없어서 render 본문에서 직접 부르면 SSR이 죽음 — 그래서 항상 "loading"으로 시작해서
// useEffect(클라이언트 전용) 안에서만 실제로 판단함(홈 화면의 hydration-mismatch 회피
// 패턴과 동일한 이유).
//   - 로그인 안 됨(게스트): 3단계(인적정보 + 학교정보 + 선택 정보, 2026-08-21 재구성 —
//     아래 PersonalFields/SchoolFields/OptionalFields 참고) 전부 받고 POST /match로
//     즉석 매칭 → 결과+입력값을 세션에 저장하고 /home으로.
//   - 로그인 됨: 3단계 + POST /users/me/spec. 방금 게스트로 입력해둔 값이 세션에 있으면
//     (회원가입 직후 전환 케이스) 그걸로 폼을 미리 채우고 3단계부터 이어서 입력하게 함 —
//     1·2단계를 다시 안 치게.
// 2026-08-18 — UX 배포용으로 게스트도 3단계(선택 정보)까지 받도록 임시로 풀었음(원래는 게스트
// 2단계에서 바로 매칭 끝, 3단계는 회원가입 후에만 — 아래 원본 설명):
//   - 로그인 안 됨(게스트, 원래): 1·2단계만 받고 POST /match로 즉석
//     매칭 → 결과+입력값을 세션에 저장하고 /home으로. 3단계(선택 정보)는 아예 안 보여줌 —
//     회원가입 후에 마저 입력하도록 유도(/home의 안내 배너 참고).
// 되돌리려면: 아래 "2026-08-18" 표시된 주석 처리 코드들(totalSteps, handleGuestFinish,
// step 2/3 JSX, home/page.tsx의 안내 배너 2곳)을 원상복구.
type Mode = "loading" | "guest" | "authed";

export default function SpecWizard() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("loading");
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [spec, setSpec] = useState<SpecForm>(initialSpec);
  const [optionalInfo, setOptionalInfo] = useState<OptionalInfo>(initialOptionalInfo);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step1Attempted, setStep1Attempted] = useState(false);

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
  // 2026-08-18 — UX 배포용으로 게스트도 3단계(선택 정보)까지 받도록 임시로 품 (원래는 게스트
  // 2단계/로그인 3단계로 갈렸었음, 아래 원본 줄 주석 참고 — 되돌릴 땐 이 줄만 원복하면 됨).
  const totalSteps = 3;
  // const totalSteps = mode === "guest" ? 2 : 3;

  // 로그인은 됐는데 스펙을 아직 한 번도 저장 안 한 계정(카카오 로그인 직후 등)은 /home으로
  // 못 가고(스펙 없으면 /home이 다시 여기로 돌려보냄) /spec에 갇히는데, 그동안 로그아웃할
  // 방법이 아예 없었음(2026-08-13 사용자 실제 신고로 발견) — TopBar 오른쪽에 로그아웃 추가.
  // 게스트 모드는 로그인 세션 자체가 없어서 안 보여줌.
  function handleLogout() {
    clearTokens();
    router.push("/");
  }

  // 2026-08-18 — UX 배포용으로 게스트도 실제 입력한 optionalInfo(선택 정보)를 그대로 넘기게
  // 바꿈. 원래는 게스트가 3단계 UI 자체를 안 봐서 initialOptionalInfo(빈 값)로 고정 발송했음
  // (아래 주석 처리된 원본 버전 참고 — 되돌릴 땐 이 함수만 원복하면 됨).
  async function handleGuestFinish(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: UserSpec = specFormToUserSpec(spec, optionalInfo);
      const res = await fetch(apiUrl("/match"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`status ${res.status}`);
      const results = await res.json();
      saveGuestSpec(spec, optionalInfo);
      saveGuestResults(results);
      router.push("/home");
    } catch {
      setError("매칭에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  }
  // async function handleGuestFinish(e: React.FormEvent) {
  //   e.preventDefault();
  //   setSubmitting(true);
  //   setError(null);
  //   try {
  //     const body: UserSpec = specFormToUserSpec(spec, initialOptionalInfo);
  //     const res = await fetch(apiUrl("/match"), {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify(body),
  //     });
  //     if (!res.ok) throw new Error(`status ${res.status}`);
  //     const results = await res.json();
  //     saveGuestSpec(spec, initialOptionalInfo);
  //     saveGuestResults(results);
  //     router.push("/home");
  //   } catch {
  //     setError("매칭에 실패했어요. 잠시 후 다시 시도해주세요.");
  //   } finally {
  //     setSubmitting(false);
  //   }
  // }

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
      setError("스펙 저장에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setSubmitting(false);
    }
  }

  if (mode === "loading") {
    return (
      <div className="min-h-screen bg-neu-bg">
        <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
          <TopBar />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neu-bg pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
        <TopBar
          right={
            mode === "authed" ? (
              <button
                type="button"
                onClick={handleLogout}
                className="text-sm font-semibold text-gray-400"
              >
                로그아웃
              </button>
            ) : undefined
          }
        />

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">
          {step === 1 && "먼저 인적사항을 알려주세요"}
          {step === 2 && "어느 학교에 다니시나요?"}
          {step === 3 && "해당하는 항목이 있으면 알려주세요"}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {step === 1 && "이름·거주지역 같은 기본 정보로 딱 맞는 장학금부터 찾아드릴게요"}
          {step === 2 && "학교 정보에 맞는 장학금까지 좁혀드릴게요"}
          {step === 3 && "선택 항목이라 없으면 그냥 넘어가도 돼요"}
        </p>

        <div className="mt-5">
          <StepIndicator
            step={step}
            totalSteps={totalSteps}
            onStepClick={(n) => setStep(n as 1 | 2 | 3)}
          />
        </div>

        {step === 1 && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!spec.address) {
                setStep1Attempted(true);
                return;
              }
              setStep1Attempted(false);
              setStep(2);
            }}
            className="mt-6 flex flex-col gap-5"
          >
            <PersonalFields
              spec={spec}
              setSpec={setSpec}
              optionalInfo={optionalInfo}
              setOptionalInfo={setOptionalInfo}
              showErrors={step1Attempted}
            />

            <button
              type="submit"
              className="mt-2 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed"
            >
              다음
            </button>
          </form>
        )}

        {step === 2 && (mode === "guest" || mode === "authed") && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(3);
            }}
            className="mt-6 flex flex-col gap-5"
          >
            <SchoolFields
              spec={spec}
              setSpec={setSpec}
              derived={derived}
              optionalInfo={optionalInfo}
              setOptionalInfo={setOptionalInfo}
              showFreshmanHint
            />

            <div className="mt-2 flex gap-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full rounded-2xl bg-neu-surface py-4 text-[15px] font-semibold text-gray-600 shadow-neu-raised transition hover:shadow-neu-raised-lg active:shadow-neu-pressed"
              >
                이전
              </button>
              <button
                type="submit"
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed"
              >
                다음
              </button>
            </div>
          </form>
        )}

        {/* 2026-08-18 — UX 배포용으로 새로 추가된 게스트 3단계. authed 버전과 필드는 같지만
            제출 핸들러(handleGuestFinish, 저장 없이 즉석 매칭)와 버튼 문구가 달라서 별도
            블록으로 둠. 되돌릴 땐 이 블록만 지우고 위 "2026-08-18" 주석 두 곳도 원복. */}
        {step === 3 && mode === "guest" && (
          <form onSubmit={handleGuestFinish} className="mt-6 flex flex-col gap-5">
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
                className="w-full rounded-2xl bg-neu-surface py-4 text-[15px] font-semibold text-gray-600 shadow-neu-raised transition hover:shadow-neu-raised-lg active:shadow-neu-pressed"
              >
                이전
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50"
              >
                {submitting ? "찾는 중..." : "장학금 찾아보기"}
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
                className="w-full rounded-2xl bg-neu-surface py-4 text-[15px] font-semibold text-gray-600 shadow-neu-raised transition hover:shadow-neu-raised-lg active:shadow-neu-pressed"
              >
                이전
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50"
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
