"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  AuthError,
  AuthLogo,
  authInputClass,
  authPrimaryButtonClass,
  AuthNotice,
  authSecondaryButtonClass,
  AuthShell,
} from "@/components/auth-ui";
import { postJson } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [step, setStep] = useState<"signup" | "verify">("signup");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const result = await postJson("/auth/signup", { username, password, email }, "회원가입에 실패했습니다.");
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setNotice("인증 코드를 이메일로 보냈어요. 5분 안에 입력해주세요.");
    setStep("verify");
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const result = await postJson(
      "/auth/verify-code",
      { identifier: username, code },
      "인증에 실패했습니다."
    );
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    router.push("/login");
  }

  async function handleResend() {
    setLoading(true);
    setError(null);
    setNotice(null);
    const result = await postJson("/auth/resend-code", { identifier: username }, "재발송에 실패했습니다.");
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setNotice("인증 코드를 다시 보냈어요.");
  }

  return (
    <AuthShell>
      <AuthLogo />

      {step === "signup" ? (
        <>
          <h1 className="text-2xl font-bold leading-snug text-gray-900">회원가입</h1>
          <p className="mt-2 text-sm text-gray-500">
            이메일만 있으면 바로 시작할 수 있어요
          </p>

          <form onSubmit={handleSignup} className="mt-10 flex flex-col gap-3">
            <input
              type="text"
              required
              minLength={3}
              placeholder="아이디"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={authInputClass}
            />
            <input
              type="password"
              required
              minLength={8}
              placeholder="비밀번호 (8자 이상)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={authInputClass}
            />
            <input
              type="email"
              required
              placeholder="이메일 (인증용)"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={authInputClass}
            />

            {error && <AuthError>{error}</AuthError>}

            <button type="submit" disabled={loading} className={authPrimaryButtonClass}>
              {loading ? "처리 중..." : "다음"}
            </button>
          </form>
        </>
      ) : (
        <>
          <h1 className="text-2xl font-bold leading-snug text-gray-900">이메일 인증</h1>
          <p className="mt-2 text-sm text-gray-500">{email}로 받은 6자리 코드를 입력해주세요</p>

          <form onSubmit={handleVerify} className="mt-10 flex flex-col gap-3">
            <input
              type="text"
              required
              inputMode="numeric"
              minLength={6}
              maxLength={6}
              placeholder="인증 코드 6자리"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              className={`${authInputClass} tracking-[0.3em]`}
            />

            {notice && !error && <AuthNotice>{notice}</AuthNotice>}
            {error && <AuthError>{error}</AuthError>}

            <button type="submit" disabled={loading} className={authPrimaryButtonClass}>
              {loading ? "확인 중..." : "인증 완료"}
            </button>
            <button
              type="button"
              onClick={handleResend}
              disabled={loading}
              className={authSecondaryButtonClass}
            >
              코드 재발송
            </button>
          </form>
        </>
      )}

      <p className="mt-6 text-center text-xs text-gray-400">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="font-semibold text-blue-500">
          로그인
        </Link>
      </p>
    </AuthShell>
  );
}
