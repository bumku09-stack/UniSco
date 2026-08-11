"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { ScholarshipResults } from "@/components/ScholarshipResults";
import { authFetch, clearTokens, isLoggedIn } from "@/lib/auth";
import { getGuestResults } from "@/lib/guest";
import { getCachedRecommendations, setCachedRecommendations } from "@/lib/recommendations-cache";
import { Scholarship } from "@/lib/scholarship";

// 게스트 결과가 sessionStorage에만 있어서(2026-08-11 확인된 허점) 탭을 닫거나 새로고침하면
// 경고 없이 그냥 사라졌음 — 한 번 닫으면 같은 세션 안에서는 다시 안 뜨게 이 키로 기억함.
const GUEST_WARNING_DISMISSED_KEY = "unisco_guest_warning_dismissed";

export default function HomePage() {
  const router = useRouter();
  // sessionStorage는 서버(SSR)에서 항상 null이라, 초기 state를 캐시값으로 바로 잡으면
  // 서버는 "로딩 중" 화면을, 캐시가 있는 클라이언트는 바로 결과 화면을 렌더링해서
  // hydration mismatch가 났었음(2026-08-04) — 그래서 초기값은 항상 서버와 동일하게
  // null/true로 시작하고, 캐시 확인은 아래 useEffect(클라이언트에서만 실행됨) 안으로 옮김.
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // 로그인 없이 게스트 모드로 들어온 건지 — 마찬가지로 서버/클라이언트 첫 렌더 모두 false로
  // 시작하고 useEffect 안에서만 판단함(같은 hydration 이유).
  const [guestMode, setGuestMode] = useState(false);
  const [showGuestWarning, setShowGuestWarning] = useState(false);

  useEffect(() => {
    // 전체를 async IIFE 하나로 감쌈 — effect 본문에 setState를 직접 두면
    // react-hooks/set-state-in-effect가 걸려서(게스트/로그인 두 분기 다 마찬가지) 이 안으로
    // 옮김. async 함수는 첫 await 전까지 동기적으로 실행되므로 타이밍은 바뀌지 않음.
    (async () => {
      if (!isLoggedIn()) {
        // 로그인 없이 /spec에서 기본 정보만 입력하고 POST /match로 받은 결과가 있으면 그걸
        // 보여줌(2026-08-10 게스트 플로우 추가) — 그것도 없으면 뭘 보여줄 게 없으니 랜딩으로.
        const guestResults = getGuestResults();
        if (guestResults === null) {
          router.replace("/");
          return;
        }
        setGuestMode(true);
        setResults(guestResults);
        setLoading(false);
        if (!sessionStorage.getItem(GUEST_WARNING_DISMISSED_KEY)) {
          setShowGuestWarning(true);
        }
        return;
      }

      const cached = getCachedRecommendations();
      if (cached !== null) {
        setResults(cached);
        setLoading(false);
      }
      // hadCache를 state가 아니라 이 변수로 판단하는 건 의도적임 — 마운트 시점의 캐시
      // 유무만 한 번 확인하면 되고, 나중에 setResults 하는 것 때문에 이펙트가 다시 도는
      // 걸 막기 위함.
      const hadCache = cached !== null;

      const statusRes = await authFetch("/users/me/spec-status");
      if (!statusRes.ok) {
        if (!hadCache) {
          setError("정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
          setLoading(false);
        }
        return;
      }
      const status = await statusRes.json();
      if (!status.spec_completed) {
        router.replace("/spec");
        return;
      }

      const recRes = await authFetch("/scholarships/recommendations");
      if (!recRes.ok) {
        // 캐시된 이전 결과가 이미 화면에 떠 있으면 그거 그대로 두고 조용히 넘어감 —
        // 캐시가 없을 때만(최초 진입) 에러를 실제로 보여줌.
        if (!hadCache) {
          setError("매칭에 실패했습니다. 백엔드 서버가 켜져 있는지 확인해주세요.");
          setLoading(false);
        }
        return;
      }
      const data: Scholarship[] = await recRes.json();
      setResults(data);
      setCachedRecommendations(data);
      setLoading(false);
    })();
  }, [router]);

  function handleLogout() {
    clearTokens();
    router.push("/");
  }

  function dismissGuestWarning() {
    sessionStorage.setItem(GUEST_WARNING_DISMISSED_KEY, "1");
    setShowGuestWarning(false);
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <TopBar
          right={
            loading ? undefined : guestMode ? (
              <Link href="/login" className="text-sm font-semibold text-gray-400">
                로그인
              </Link>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/saved" className="text-sm font-semibold text-blue-500">
                  찜한 장학금
                </Link>
                <Link href="/mypage" className="text-sm font-semibold text-blue-500">
                  마이페이지
                </Link>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="text-sm font-semibold text-gray-400"
                >
                  로그아웃
                </button>
              </div>
            )
          }
        />

        {loading && <p className="mt-8 text-center text-sm text-gray-400">매칭 중...</p>}

        {error && (
          <p className="mt-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
            {error}
          </p>
        )}

        {guestMode && !loading && !error && (
          <div className="mt-4 rounded-2xl bg-blue-50 px-4 py-4">
            <p className="text-sm font-bold text-blue-700">더 정확한 매칭을 원하시나요?</p>
            <p className="mt-1 text-xs leading-relaxed text-blue-600">
              상세 정보를 입력해주시면 결과가 더 정확해지고, 
              저장을 통해 언제든 불러오실 수 있습니다.
            </p>
            <Link
              href="/signup"
              className="mt-3 block w-full rounded-xl bg-blue-500 py-2.5 text-center text-sm font-bold text-white transition hover:bg-blue-600 active:scale-[0.99]"
            >
              회원가입하고 상세 정보 입력하기
            </Link>
          </div>
        )}

        {!loading && !error && results !== null && <ScholarshipResults results={results} />}
      </div>

      {showGuestWarning && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 px-6 pb-8 sm:items-center"
          onClick={dismissGuestWarning}
        >
          <div
            className="w-full max-w-sm rounded-2xl bg-white p-5 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-sm font-bold text-gray-900">⚠️ 이 결과, 저장 안 돼있어요</p>
            <p className="mt-1.5 text-xs leading-relaxed text-gray-500">
              지금 보시는 건 임시 결과라 새로고침하거나 창을 닫으면 사라져요. 계속 보관하고
              싶으면 회원가입해주세요 — 입력하신 정보 그대로 이어져요.
            </p>
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={dismissGuestWarning}
                className="w-full rounded-xl border border-gray-200 py-2.5 text-xs font-bold text-gray-600"
              >
                알겠어요
              </button>
              <Link
                href="/signup"
                className="w-full rounded-xl bg-blue-500 py-2.5 text-center text-xs font-bold text-white"
              >
                회원가입하기
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
