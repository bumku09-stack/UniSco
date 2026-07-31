"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const inputClass =
  "w-full rounded-2xl bg-gray-100 px-4 py-4 text-[15px] text-gray-900 placeholder:text-gray-400 outline-none transition focus:bg-blue-50 focus:ring-2 focus:ring-blue-500";

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
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? "회원가입에 실패했습니다.");
        return;
      }
      setNotice("인증 코드를 이메일로 보냈어요. 5분 안에 입력해주세요.");
      setStep("verify");
    } catch {
      setError("회원가입에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: username, code }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? "인증에 실패했습니다.");
        return;
      }
      router.push("/");
    } catch {
      setError("인증에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/resend-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: username }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? "재발송에 실패했습니다.");
        return;
      }
      setNotice("인증 코드를 다시 보냈어요.");
    } catch {
      setError("재발송에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        <div className="mb-10 flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white">
            U
          </div>
          <span className="text-lg font-bold text-gray-900">UniSco</span>
        </div>

        {step === "signup" ? (
          <>
            <h1 className="text-2xl font-bold leading-snug text-gray-900">회원가입</h1>
            <p className="mt-2 text-sm text-gray-500">
              아이디·비밀번호·이메일만 있으면 바로 시작할 수 있어요
            </p>

            <form onSubmit={handleSignup} className="mt-10 flex flex-col gap-3">
              <input
                type="text"
                required
                minLength={3}
                placeholder="아이디"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={inputClass}
              />
              <input
                type="password"
                required
                minLength={8}
                placeholder="비밀번호 (8자 이상)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
              />
              <input
                type="email"
                required
                placeholder="이메일 (인증용)"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputClass}
              />

              {error && (
                <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
              >
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
                className={`${inputClass} tracking-[0.3em]`}
              />

              {notice && !error && (
                <p className="rounded-2xl bg-blue-50 px-4 py-3 text-sm font-medium text-blue-600">
                  {notice}
                </p>
              )}
              {error && (
                <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
              >
                {loading ? "확인 중..." : "인증 완료"}
              </button>
              <button
                type="button"
                onClick={handleResend}
                disabled={loading}
                className="w-full rounded-2xl border border-gray-200 py-4 text-[15px] font-semibold text-gray-600 transition hover:bg-gray-50 disabled:opacity-50"
              >
                코드 재발송
              </button>
            </form>
          </>
        )}

        <p className="mt-6 text-center text-xs text-gray-400">
          이미 계정이 있으신가요?{" "}
          <Link href="/" className="font-semibold text-blue-500">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
