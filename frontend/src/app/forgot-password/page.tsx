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
  PasswordMatchHint,
  PasswordStrengthMeter,
} from "@/components/auth-ui";
import { passwordRequirementError, postJson } from "@/lib/auth";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [step, setStep] = useState<"request" | "reset">("request");

  const [identifier, setIdentifier] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  // signup/page.tsx와 동일(2026-08-21) — "비밀번호 재설정" 버튼을 눌러보기 전엔
  // resetBlockReason을 안 보여줌.
  const [attemptedReset, setAttemptedReset] = useState(false);

  // 회원가입 페이지와 동일하게(2026-08-21) — 비밀번호 규칙/일치 여부를 다 채우기 전엔
  // 제출 버튼 자체를 눌러지지 않게 함.
  const newPasswordOk = passwordRequirementError(newPassword) === null;
  const newPasswordMatches = newPassword.length > 0 && newPassword === newPasswordConfirm;
  const canReset = newPasswordOk && newPasswordMatches;

  // 버튼이 왜 안 눌리는지 이유를 항상 옆에 보여줌(2026-08-21 추가, signup/page.tsx와 동일 패턴).
  const resetBlockReason = !newPasswordOk
    ? "비밀번호가 영문+숫자+특수문자를 포함한 8자 이상이어야 해요"
    : !newPasswordMatches
      ? "비밀번호 확인이 비밀번호랑 일치해야 해요"
      : null;

  async function handleRequest(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const result = await postJson(
      "/auth/forgot-password",
      { identifier },
      "코드 발송에 실패했어요."
    );
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setNotice("재설정 코드를 이메일로 보냈어요. 5분 안에 입력해주세요.");
    setStep("reset");
  }

  async function handleReset(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setAttemptedReset(true);

    if (!canReset) {
      return; // resetBlockReason이 이제 화면에 뜸(아래 JSX 참고)
    }

    setLoading(true);
    const result = await postJson(
      "/auth/reset-password",
      { identifier, code, new_password: newPassword },
      "비밀번호 재설정에 실패했어요."
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
    const result = await postJson(
      "/auth/forgot-password",
      { identifier },
      "재발송에 실패했어요."
    );
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setNotice("재설정 코드를 다시 보냈어요.");
  }

  return (
    <AuthShell>
      <AuthLogo />

      {step === "request" ? (
        <>
          <h1 className="text-2xl font-bold leading-snug text-gray-900">비밀번호 찾기</h1>
          <p className="mt-2 text-sm text-gray-500">
            가입할 때 쓴 아이디나 이메일을 입력하면 재설정 코드를 보내드려요
          </p>

          <form onSubmit={handleRequest} className="mt-10 flex flex-col gap-3">
            <input
              type="text"
              required
              placeholder="아이디 또는 이메일"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className={authInputClass}
            />

            {error && <AuthError>{error}</AuthError>}

            <button type="submit" disabled={loading} className={authPrimaryButtonClass}>
              {loading ? "처리 중..." : "재설정 코드 받기"}
            </button>
          </form>
        </>
      ) : (
        <>
          <h1 className="text-2xl font-bold leading-snug text-gray-900">비밀번호 재설정</h1>
          <p className="mt-2 text-sm text-gray-500">
            이메일로 받은 6자리 코드와 새 비밀번호를 입력해주세요
          </p>

          <form onSubmit={handleReset} className="mt-10 flex flex-col gap-3">
            <input
              type="text"
              required
              inputMode="numeric"
              minLength={6}
              maxLength={6}
              placeholder="재설정 코드 6자리"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              className={`${authInputClass} tracking-[0.3em]`}
            />
            <input
              type="password"
              required
              minLength={8}
              placeholder="새 비밀번호 (영문+숫자+특수문자, 8자 이상)"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className={authInputClass}
            />
            <PasswordStrengthMeter password={newPassword} />
            <input
              type="password"
              required
              minLength={8}
              placeholder="새 비밀번호 확인"
              value={newPasswordConfirm}
              onChange={(e) => setNewPasswordConfirm(e.target.value)}
              className={`${authInputClass} ${
                newPasswordConfirm.length === 0
                  ? ""
                  : newPasswordConfirm === newPassword
                    ? "ring-2 ring-green-500"
                    : "ring-2 ring-red-400"
              }`}
            />
            <PasswordMatchHint password={newPassword} confirm={newPasswordConfirm} />

            {notice && !error && <AuthNotice>{notice}</AuthNotice>}
            {error && <AuthError>{error}</AuthError>}

            <button type="submit" disabled={loading} className={authPrimaryButtonClass}>
              {loading ? "확인 중..." : "비밀번호 재설정"}
            </button>
            {attemptedReset && !error && resetBlockReason && (
              <p className="px-1 text-center text-xs text-gray-400">{resetBlockReason}</p>
            )}
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
        <Link href="/login" className="font-semibold text-blue-500">
          로그인으로 돌아가기
        </Link>
      </p>
    </AuthShell>
  );
}
