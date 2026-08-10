"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { isLoggedIn } from "@/lib/auth";

// 2026-08-10 개편 — 예전엔 이 경로가 로그인 폼이었음(지금은 /login으로 옮김). 로그인부터
// 강제하지 않고, 계정 없이 학교·공통 정보만으로도 바로 매칭 결과를 볼 수 있게(/spec이
// 비로그인 상태면 게스트 2단계 모드로 동작함, 결과는 POST /match) 진입점을 여기로 바꿈 —
// 결과 화면에서 "회원가입하면 더 정확해져요" 유도 배너로 전환을 유도함(home/page.tsx 참고).
export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    // 이미 로그인된 사용자가 여기로 오면(즐겨찾기 등) 굳이 선택 화면을 다시 보여줄 필요 없이
    // 바로 홈으로 — /home이 알아서 spec_completed 여부에 따라 /spec으로도 보냄.
    if (isLoggedIn()) router.replace("/home");
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        <div className="mb-10 flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white">
            U
          </div>
          <span className="text-lg font-bold text-gray-900">UniSco</span>
        </div>

        <h1 className="text-2xl font-bold leading-snug text-gray-900">
          장학금, 이제는 놓치지 말자
          <br />
          UniSco
        </h1>
        <p className="mt-2 text-sm text-gray-500">
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
        </p>
      </div>
    </div>
  );
}
