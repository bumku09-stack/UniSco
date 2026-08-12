"use client";

// error.tsx는 루트 layout.tsx 자체가 실패하면 못 잡음(레이아웃 바깥에서 렌더링되니까) —
// 그 경우에만 Next.js가 이걸 대신 씀. 루트 layout이 통째로 날아간 상황이라 <html>/<body>를
// 직접 그려야 함(평소엔 layout.tsx가 담당하던 부분). 의존성을 최소로 유지함 — 이 파일이
// 뜨는 상황 자체가 나머지 앱 트리(폰트, 공용 컴포넌트 등)가 신뢰 안 되는 상태일 수 있어서.
export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="ko">
      <body className="flex min-h-screen flex-col items-center justify-center gap-3 bg-white px-6 text-center">
        <p className="text-sm font-bold text-gray-900">문제가 발생했어요</p>
        <p className="text-sm text-gray-500">잠시 후 다시 시도해주세요.</p>
        <button
          type="button"
          onClick={reset}
          className="mt-2 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-bold text-white"
        >
          다시 시도
        </button>
      </body>
    </html>
  );
}
