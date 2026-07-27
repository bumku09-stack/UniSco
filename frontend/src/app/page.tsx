"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

const inputClass =
  "w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-900 focus:border-zinc-500 focus:outline-none";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // TODO: 실제 로그인 연동 전. 인증 방식(Supabase Auth / 소셜로그인 등) 정해지면 여기 붙임.
  // 지금은 UI만 있고, 제출하면 그냥 다음 단계(스펙 입력)로 넘어감.
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push("/spec");
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto flex w-full max-w-md flex-col justify-center px-4 py-16">
        <h1 className="text-xl font-bold text-zinc-900">UniSco</h1>
        <p className="mt-1 text-sm text-zinc-500">대전 지역 대학생을 위한 맞춤형 장학금 매칭</p>

        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-700">이메일</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-700">비밀번호</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
            />
          </label>

          <button
            type="submit"
            className="mt-2 rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white"
          >
            로그인
          </button>
        </form>
      </div>
    </div>
  );
}
