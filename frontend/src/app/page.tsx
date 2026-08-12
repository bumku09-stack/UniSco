"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";
import { Reveal } from "@/components/Reveal";
import { isLoggedIn } from "@/lib/auth";

// 2026-08-10 개편 — 예전엔 이 경로가 로그인 폼이었음(지금은 /login으로 옮김). 로그인부터
// 강제하지 않고, 계정 없이 학교·공통 정보만으로도 바로 매칭 결과를 볼 수 있게(/spec이
// 비로그인 상태면 게스트 2단계 모드로 동작함, 결과는 POST /match) 진입점을 여기로 바꿈 —
// 결과 화면에서 "회원가입하면 더 정확해져요" 유도 배너로 전환을 유도함(home/page.tsx 참고).
//
// 2026-08-13 — 첫 화면이 CTA 버튼 하나뿐이라 밋밋하다는 피드백으로 스크롤 유도형 소개
// 섹션을 추가함(차별점/통계/이용방법). 색감·비주얼 디테일은 의도적으로 기존 팔레트
// 그대로 씀 — 구조·카피만 이번 스코프, 톤앤매너는 다음 라운드에서 별도로 다룰 것.

const FEATURES = [
  {
    title: "가입 없이 바로 확인",
    body: "학교와 기본 정보만 입력하면 계정 없이도 바로 매칭 결과를 볼 수 있어요. 마음에 들면 그때 가입해도 늦지 않아요.",
  },
  {
    title: "대전 지역에 집중",
    body: "전국을 다 다루는 정부 포털과 달리, 대전권 대학생에게 실제로 해당되는 장학금만 정밀하게 걸러드려요.",
  },
  {
    title: "조건 기반 정밀 매칭",
    body: "학점·소득분위·거주지역·전공 같은 자격조건을 규칙 기반으로 하나하나 대조해서, 안 맞는 장학금은 애초에 안 보여드려요.",
  },
  {
    title: "계속 업데이트되는 데이터",
    body: "자동 수집 파이프라인이 매일 새벽 신규 장학금을 찾아내고, 사람이 검수해서 반영해요.",
  },
] as const;

const STATS = [
  { value: "660+", label: "등록된 장학금·지원금" },
  { value: "8+", label: "대전권 지원 대학(KAIST 포함)" },
  { value: "0원", label: "가입 없이도 결과 확인" },
] as const;

const STEPS = [
  { step: "1", title: "학교 정보 입력", body: "학교, 단과대, 학과만 알려주세요." },
  { step: "2", title: "몇 가지 조건 확인", body: "학년·학점·거주지역 같은 공통 조건이에요." },
  { step: "3", title: "맞춤 결과 확인", body: "조건에 맞는 장학금만 정리해서 보여드려요." },
] as const;

function ScrollCue({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="아래로 스크롤"
      className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce text-gray-300 transition hover:text-gray-400"
    >
      <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth={2}>
        <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}

export default function LandingPage() {
  const router = useRouter();
  const introRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 이미 로그인된 사용자가 여기로 오면(즐겨찾기 등) 굳이 선택 화면을 다시 보여줄 필요 없이
    // 바로 홈으로 — /home이 알아서 spec_completed 여부에 따라 /spec으로도 보냄.
    if (isLoggedIn()) router.replace("/home");
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 py-16">
        <div className="mx-auto flex w-full max-w-md flex-col sm:max-w-lg md:max-w-xl">
          <div className="mb-10 flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white">
              U
            </div>
            <span className="text-lg font-bold text-gray-900">UniSco</span>
          </div>

          <h1 className="text-2xl font-bold leading-snug text-gray-900 sm:text-3xl">
            장학금, 이제는 놓치지 말자
            <br />
            UniSco
          </h1>
          <p className="mt-2 text-sm text-gray-500 sm:text-base">
            대전 지역 대학생을 위한 맞춤형 장학금 매칭 서비스
          </p>

          <Link
            href="/spec"
            className="mt-10 block w-full rounded-2xl bg-blue-500 py-4 text-center text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99]"
          >
            지금 바로 장학금 둘러보기
          </Link>
          <p className="mt-2 text-center text-xs text-gray-400">
            가입 없이 학교·기본 정보만 입력하면 바로 결과를 볼 수 있어요
          </p>

          <p className="mt-6 text-center text-xs text-gray-400">
            이미 계정이 있으신가요?{" "}
            <Link href="/login" className="font-semibold text-blue-500">
              로그인
            </Link>
            {" 또는 "}
            <Link href="/signup" className="font-semibold text-blue-500">
              회원가입
            </Link>
          </p>
        </div>

        <ScrollCue onClick={() => introRef.current?.scrollIntoView({ behavior: "smooth" })} />
      </section>

      <div ref={introRef}>
        <Reveal className="mx-auto w-full max-w-md px-6 py-20 sm:max-w-2xl md:max-w-4xl lg:max-w-6xl lg:px-10">
          <h2 className="text-center text-2xl font-bold text-gray-900 sm:text-3xl">
            온통청년 대신 UniSco를 쓰는 이유
          </h2>
          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f, i) => (
              <Reveal key={f.title} delayMs={i * 100}>
                <div className="h-full rounded-2xl border border-gray-100 bg-white p-6 shadow-[0_2px_10px_rgba(15,23,42,0.05)]">
                  <p className="font-bold text-gray-900">{f.title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-gray-500">{f.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </Reveal>

        <Reveal className="bg-blue-50 py-16">
          <div className="mx-auto grid w-full max-w-md grid-cols-1 gap-8 px-6 text-center sm:max-w-2xl sm:grid-cols-3 md:max-w-4xl lg:max-w-6xl lg:px-10">
            {STATS.map((s, i) => (
              <Reveal key={s.label} delayMs={i * 100}>
                <p className="text-3xl font-bold text-blue-600">{s.value}</p>
                <p className="mt-1 text-sm font-medium text-blue-500">{s.label}</p>
              </Reveal>
            ))}
          </div>
        </Reveal>

        <Reveal className="mx-auto w-full max-w-md px-6 py-20 sm:max-w-2xl md:max-w-4xl lg:max-w-6xl lg:px-10">
          <h2 className="text-center text-2xl font-bold text-gray-900 sm:text-3xl">이용 방법</h2>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {STEPS.map((s, i) => (
              <Reveal key={s.step} delayMs={i * 100}>
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-500 text-sm font-bold text-white">
                  {s.step}
                </div>
                <p className="mt-3 font-bold text-gray-900">{s.title}</p>
                <p className="mt-1 text-sm text-gray-500">{s.body}</p>
              </Reveal>
            ))}
          </div>
        </Reveal>

        <Reveal className="border-t border-gray-100 px-6 py-20 text-center">
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">지금 바로 시작해보세요</h2>
          <p className="mt-2 text-sm text-gray-500">가입 없이도 1분이면 결과를 확인할 수 있어요</p>
          <Link
            href="/spec"
            className="mx-auto mt-6 block w-full max-w-xs rounded-2xl bg-blue-500 py-4 text-center text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99]"
          >
            장학금 둘러보기
          </Link>
        </Reveal>
      </div>
    </div>
  );
}
