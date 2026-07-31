"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { setTokens } from "@/lib/auth";

const inputClass =
  "w-full rounded-2xl bg-gray-100 px-4 py-4 text-[15px] text-gray-900 placeholder:text-gray-400 outline-none transition focus:bg-blue-50 focus:ring-2 focus:ring-blue-500";

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
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? "로그인에 실패했습니다.");
        return;
      }
      setTokens(data.access_token, data.refresh_token);

      const statusRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me/spec-status`, {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      const status = await statusRes.json();
      router.push(status.spec_completed ? "/home" : "/spec");
    } catch {
      setError("로그인에 실패했습니다. 잠시 후 다시 시도해주세요.");
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

        <h1 className="text-2xl font-bold leading-snug text-gray-900">
          장학금, 이제는 놓치지 말자
          <br />
          UniSco
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          대전 지역 대학생을 위한 맞춤형 장학금 매칭 서비스
        </p>

        <form onSubmit={handleSubmit} className="mt-10 flex flex-col gap-3">
          <input
            type="text"
            required
            placeholder="아이디"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className={inputClass}
          />
          <input
            type="password"
            required
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />

          {error && (
            <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-gray-400">
          아직 계정이 없으신가요?{" "}
          <Link href="/signup" className="font-semibold text-blue-500">
            회원가입
          </Link>
        </p>
      </div>
    </div>
  );
}
