"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { ScholarshipResults } from "@/components/ScholarshipResults";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { Scholarship } from "@/lib/scholarship";

// 찜한 장학금만 모아보는 화면. 게스트는 찜 자체가 불가능한 기능이라(로그인 필요) 여기
// 들어오면 바로 로그인 화면으로 보냄 — home처럼 게스트 모드를 따로 지원하지 않음.
export default function SavedPage() {
  const router = useRouter();
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }
    (async () => {
      // authFetch가 network 자체 실패(서버 다운 등)에는 reject하므로, try/catch 없이 두면
      // "불러오는 중..." 스피너가 안 멈췄음 — home/page.tsx와 동일한 이유(2026-08-13).
      try {
        const res = await authFetch("/users/me/saved-scholarships");
        if (!res.ok) {
          setError("찜 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
          return;
        }
        setResults(await res.json());
      } catch {
        setError("서버에 연결하지 못했습니다. 잠시 후 다시 시도해주세요.");
      }
    })();
  }, [router]);

  function handleSaveChange(id: number, saved: boolean) {
    // 이 화면 자체가 "찜한 것만" 모아보는 목록이라, 찜 취소하면 바로 화면에서도 빠짐
    // (ScholarshipResults의 onSaveChange 참고 — home에서는 이 콜백을 안 넘겨서 그쪽은
    // 그대로 남아있음).
    if (saved) return;
    setResults((prev) => (prev ? prev.filter((s) => s.id !== id) : prev));
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl lg:px-10">
        <TopBar right={<Link href="/home" className="text-sm font-semibold text-gray-400">← 홈으로</Link>} />

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">찜한 장학금</h1>

        {error && (
          <p className="mt-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
            {error}
          </p>
        )}

        {!error && results === null && (
          <p className="mt-8 text-center text-sm text-gray-400">불러오는 중...</p>
        )}

        {!error && results !== null && results.length === 0 && (
          <div className="mt-10 flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-gray-400">아직 찜한 장학금이 없어요</p>
            <Link
              href="/home"
              className="rounded-xl border border-blue-500 px-4 py-2 text-sm font-semibold text-blue-600"
            >
              추천 장학금 보러 가기
            </Link>
          </div>
        )}

        {!error && results !== null && results.length > 0 && (
          <ScholarshipResults results={results} onSaveChange={handleSaveChange} />
        )}
      </div>
    </div>
  );
}
