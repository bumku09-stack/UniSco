"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

const inputClass =
  "w-full rounded-2xl bg-gray-100 px-4 py-4 text-[15px] text-gray-900 placeholder:text-gray-400 outline-none transition focus:bg-blue-50 focus:ring-2 focus:ring-blue-500";

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
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        <div className="mb-10 flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white">
            U
          </div>
          <span className="text-lg font-bold text-gray-900">UniSco</span>
        </div>

        <h1 className="text-2xl font-bold leading-snug text-gray-900">
          안녕하세요!
          <br />
          이메일로 로그인해주세요
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          대전 지역 대학생을 위한 맞춤형 장학금 매칭 서비스
        </p>

        <form onSubmit={handleSubmit} className="mt-10 flex flex-col gap-3">
          <input
            type="email"
            required
            placeholder="이메일"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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

          <button
            type="submit"
            className="mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99]"
          >
            로그인
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-gray-400">
          아직 계정이 없으신가요? 지금은 아무 이메일로나 로그인할 수 있어요.
        </p>
      </div>
    </div>
  );
}
