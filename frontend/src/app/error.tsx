"use client";

import { useEffect } from "react";
import { TopBar } from "@/components/form-ui";

// 라우트 트리 어딘가에서 렌더링 중 예외가 터지면 Next.js가 이 컴포넌트로 대체함(리렌더링
// 대상은 이 파일이 속한 세그먼트 이하 전체) — 이게 없으면 빈 기본 에러 화면만 뜨고 복구
// 수단도 없었음. reset()은 에러 경계를 다시 렌더링 시도함(원인이 일시적이었으면 복구됨).
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col bg-neu-bg">
      <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-lg">
        <TopBar />
        <div className="mt-16 flex flex-col items-center gap-3 text-center">
          <p className="text-sm font-bold text-gray-900">문제가 발생했어요</p>
          <p className="text-sm text-gray-500">
            잠시 후 다시 시도해주세요. 계속되면 페이지를 새로고침해보세요.
          </p>
          <button
            type="button"
            onClick={reset}
            className="mt-3 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-bold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed"
          >
            다시 시도
          </button>
        </div>
      </div>
    </div>
  );
}
