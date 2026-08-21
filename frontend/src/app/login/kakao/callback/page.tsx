"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { AuthError, AuthLogo, authSecondaryButtonClass, AuthShell } from "@/components/auth-ui";
import { consumeKakaoState, kakaoRedirectUri, postJson, setTokens } from "@/lib/auth";

// 카카오가 인가 후 여기로 ?code=...를 붙여서 되돌려보냄(카카오 디벨로퍼스에 등록해둔
// Redirect URI가 정확히 이 경로여야 함, lib/auth.ts의 kakaoAuthorizeUrl() 참고). 이 코드를
// 그대로 백엔드로 넘겨서 실제 로그인/가입 처리는 전부 백엔드(POST /auth/kakao)가 함 — 프론트는
// 응답받은 토큰만 저장하고 로그인 페이지와 동일하게 라우팅.
function KakaoCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // home/page.tsx·spec/page.tsx와 동일한 이유로 async IIFE 하나로 감쌈(effect 본문에
    // setState를 직접 두면 react-hooks/set-state-in-effect가 걸림) — code가 없는 경우의
    // setError도 같이 이 안으로 넣음.
    (async () => {
      const code = searchParams.get("code");
      if (!code) {
        setError("카카오 로그인이 취소됐거나 코드가 전달되지 않았어요.");
        return;
      }
      // CSRF 방지(lib/auth.ts의 kakaoAuthorizeUrl/consumeKakaoState 참고) — 이 브라우저가
      // 실제로 로그인을 시작한 게 맞는지 확인. 실패하면 code를 백엔드로 넘기지 않고 여기서 멈춤.
      if (!consumeKakaoState(searchParams.get("state"))) {
        setError("로그인 요청을 확인할 수 없어요. 다시 시도해주세요.");
        return;
      }
      const result = await postJson(
        "/auth/kakao",
        { code, redirect_uri: kakaoRedirectUri() },
        "카카오 로그인에 실패했어요."
      );
      if (!result.ok) {
        setError(result.error);
        return;
      }
      const data = result.data as { access_token: string; refresh_token: string; spec_completed: boolean };
      setTokens(data.access_token, data.refresh_token);
      router.push(data.spec_completed ? "/home" : "/spec");
    })();
  }, [searchParams, router]);

  return (
    <AuthShell>
      <AuthLogo />

      {error ? (
        <div className="flex flex-col gap-3">
          <AuthError>{error}</AuthError>
          <Link href="/login" className={`${authSecondaryButtonClass} block text-center`}>
            로그인으로 돌아가기
          </Link>
        </div>
      ) : (
        <p className="text-center text-sm text-gray-400">카카오 로그인 처리 중...</p>
      )}
    </AuthShell>
  );
}

export default function KakaoCallbackPage() {
  return (
    <Suspense fallback={null}>
      <KakaoCallbackInner />
    </Suspense>
  );
}
