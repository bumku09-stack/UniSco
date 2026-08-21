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
  KakaoLoginButton,
  PasswordMatchHint,
  PasswordStrengthMeter,
} from "@/components/auth-ui";
import { checkUsernameAvailable, kakaoAuthorizeUrl, passwordRequirementError, postJson } from "@/lib/auth";

type UsernameCheckStatus = "idle" | "checking" | "available" | "taken" | "error";

export default function SignupPage() {
  const router = useRouter();
  const [step, setStep] = useState<"signup" | "verify">("signup");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");

  // 아이디 중복확인(2026-08-21 추가) — "확인한 값"을 따로 저장해서, 확인 버튼 누른 뒤에
  // 아이디를 다시 고치면 checkedUsername !== username이 되어 자동으로 재확인을 요구함.
  const [usernameCheckStatus, setUsernameCheckStatus] = useState<UsernameCheckStatus>("idle");
  const [checkedUsername, setCheckedUsername] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function handleCheckUsername() {
    if (username.length < 3) {
      setUsernameCheckStatus("error");
      setError("아이디는 3자 이상이어야 해요.");
      return;
    }
    setError(null);
    setUsernameCheckStatus("checking");
    const available = await checkUsernameAvailable(username);
    setCheckedUsername(username);
    if (available === null) {
      setUsernameCheckStatus("error");
    } else {
      setUsernameCheckStatus(available ? "available" : "taken");
    }
  }

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (usernameCheckStatus !== "available" || checkedUsername !== username) {
      setError("아이디 중복확인을 먼저 해주세요.");
      return;
    }

    const requirementError = passwordRequirementError(password);
    if (requirementError) {
      setError(requirementError);
      return;
    }
    if (password !== passwordConfirm) {
      setError("비밀번호가 서로 일치하지 않아요.");
      return;
    }

    setLoading(true);
    const result = await postJson("/auth/signup", { username, password, email }, "회원가입에 실패했어요.");
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
      "인증에 실패했어요."
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
    const result = await postJson("/auth/resend-code", { identifier: username }, "재발송에 실패했어요.");
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
            <div className="flex gap-2">
              <input
                type="text"
                required
                minLength={3}
                maxLength={32}
                placeholder="아이디"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={authInputClass}
              />
              <button
                type="button"
                onClick={handleCheckUsername}
                disabled={usernameCheckStatus === "checking" || username.length < 3}
                className="shrink-0 rounded-2xl border border-gray-200 px-4 text-sm font-semibold text-gray-600 transition hover:bg-gray-50 disabled:opacity-50"
              >
                {usernameCheckStatus === "checking" ? "확인 중..." : "중복확인"}
              </button>
            </div>
            {checkedUsername === username && usernameCheckStatus === "available" && (
              <p className="-mt-1 px-1 text-xs font-semibold text-green-600">
                사용 가능한 아이디예요
              </p>
            )}
            {checkedUsername === username && usernameCheckStatus === "taken" && (
              <p className="-mt-1 px-1 text-xs font-semibold text-red-500">
                이미 사용 중인 아이디예요
              </p>
            )}
            {checkedUsername === username && usernameCheckStatus === "error" && (
              <p className="-mt-1 px-1 text-xs font-semibold text-gray-400">
                확인에 실패했어요. 다시 시도해주세요.
              </p>
            )}
            <input
              type="password"
              required
              minLength={8}
              placeholder="비밀번호 (영문+숫자+특수문자, 8자 이상)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={authInputClass}
            />
            <PasswordStrengthMeter password={password} />
            <input
              type="password"
              required
              minLength={8}
              placeholder="비밀번호 확인"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              className={`${authInputClass} ${
                passwordConfirm.length === 0
                  ? ""
                  : passwordConfirm === password
                    ? "ring-2 ring-green-500"
                    : "ring-2 ring-red-400"
              }`}
            />
            <PasswordMatchHint password={password} confirm={passwordConfirm} />
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

          <KakaoLoginButton onClick={() => (window.location.href = kakaoAuthorizeUrl())} />
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
