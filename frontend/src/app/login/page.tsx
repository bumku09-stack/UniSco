"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  AuthError,
  AuthLogo,
  authInputClass,
  authPrimaryButtonClass,
  AuthShell,
  KakaoLoginButton,
} from "@/components/auth-ui";
import { kakaoAuthorizeUrl, postJson, setTokens } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const result = await postJson("/auth/login", { username, password }, "로그인에 실패했어요.");
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    const data = result.data as { access_token: string; refresh_token: string; spec_completed: boolean };
    setTokens(data.access_token, data.refresh_token);
    // 로그인 응답에 spec_completed가 같이 오기 때문에(백엔드에서 로그인 시점에 조회해서
    // 실어보냄) /users/me/spec-status를 또 부를 필요 없음 — 요청 한 번 줄임.
    router.push(data.spec_completed ? "/home" : "/spec");
  }

  return (
    <AuthShell>
      <AuthLogo href="/" />

      <h1 className="text-2xl font-bold leading-snug text-gray-900">로그인</h1>
      <p className="mt-2 text-sm text-gray-500">저장해둔 스펙으로 바로 매칭 결과를 볼 수 있어요</p>

      <form onSubmit={handleSubmit} className="mt-10 flex flex-col gap-3">
        <input
          type="text"
          required
          placeholder="아이디"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={authInputClass}
        />
        <input
          type="password"
          required
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={authInputClass}
        />

        {error && <AuthError>{error}</AuthError>}

        <button type="submit" disabled={loading} className={authPrimaryButtonClass}>
          {loading ? "로그인 중..." : "로그인"}
        </button>
      </form>

      <KakaoLoginButton onClick={() => (window.location.href = kakaoAuthorizeUrl())} />

      <p className="mt-4 text-center text-xs text-gray-400">
        <Link href="/forgot-password" className="font-semibold text-blue-500">
          비밀번호를 잊으셨나요?
        </Link>
      </p>

      <p className="mt-2 text-center text-xs text-gray-400">
        아직 계정이 없으신가요?{" "}
        <Link href="/signup" className="font-semibold text-blue-500">
          회원가입
        </Link>
        {" · "}
        <Link href="/" className="font-semibold text-blue-500">
          로그인 없이 둘러보기
        </Link>
      </p>
    </AuthShell>
  );
}
