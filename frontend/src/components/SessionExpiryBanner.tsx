"use client";

import { useEffect, useState } from "react";
import { getAccessTokenExpiry } from "@/lib/auth";

const WARNING_WINDOW_MS = 5 * 60 * 1000; // 만료 5분 전부터 경고 표시
const CHECK_INTERVAL_MS = 15 * 1000;

// access token(30분 만료)이 예고 없이 끊겨서 마이페이지에서 작업 중이던 내용이 그냥
// 날아가던 문제 때문에 추가함. 만료 5분 전부터 남은 시간을 보여줌 — 실제로 만료돼서
// 401이 뜨면(authFetch 참고) 로그인 화면으로 넘어가는데, 마이페이지는 그 전에 폼 내용을
// 임시 저장해뒀다가 재로그인 후 복원해줌(mypage/page.tsx의 draft 로직 참고).
export function SessionExpiryBanner() {
  const [minutesLeft, setMinutesLeft] = useState<number | null>(null);

  useEffect(() => {
    function check() {
      const expiry = getAccessTokenExpiry();
      if (expiry === null) {
        setMinutesLeft(null);
        return;
      }
      const msLeft = expiry - Date.now();
      setMinutesLeft(msLeft > 0 && msLeft <= WARNING_WINDOW_MS ? Math.ceil(msLeft / 60000) : null);
    }
    check();
    const interval = setInterval(check, CHECK_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  if (minutesLeft === null) return null;

  return (
    <p className="mt-4 rounded-2xl bg-amber-50 px-4 py-3 text-sm font-medium text-amber-700">
      약 {minutesLeft}분 후 로그인이 만료돼요. 작성 중인 내용이 있으면 지금 저장해주세요.
    </p>
  );
}
