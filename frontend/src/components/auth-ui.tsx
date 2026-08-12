// 로그인/회원가입/비밀번호 찾기 세 페이지가 레이아웃·입력창·버튼·알림 메시지 스타일을
// 거의 그대로 복붙하고 있던 걸 모아둠(2026-08-11 리팩터링). form-ui.tsx의 inputClass와는
// 별개임 — 그쪽은 라벨이 붙는 스펙 입력 폼용(placeholder 색 없음), 여긴 라벨 없이
// placeholder만으로 안내하는 인증 폼용이라 스타일이 미세하게 다름(py-4 vs py-3.5,
// placeholder:text-gray-400 유무) — 실수로 통일하지 말 것, 의도된 차이임.

import Link from "next/link";

export const authInputClass =
  "w-full rounded-2xl bg-gray-100 px-4 py-4 text-[15px] text-gray-900 placeholder:text-gray-400 outline-none transition focus:bg-blue-50 focus:ring-2 focus:ring-blue-500";

export const authPrimaryButtonClass =
  "mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50";

export const authSecondaryButtonClass =
  "w-full rounded-2xl border border-gray-200 py-4 text-[15px] font-semibold text-gray-600 transition hover:bg-gray-50 disabled:opacity-50";

export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        {children}
      </div>
    </div>
  );
}

// href를 주면 클릭 시 이동하는 로고(로그인 화면에서 랜딩으로), 안 주면 그냥 정적 헤더
// (회원가입·비밀번호 찾기 — 이미 그 흐름 중이라 로고 클릭으로 이탈시킬 이유가 없음, 기존
// 동작 그대로 유지).
export function AuthLogo({ href }: { href?: string }) {
  const content = (
    <>
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white">
        U
      </div>
      <span className="text-lg font-bold text-gray-900">UniSco</span>
    </>
  );
  if (href) {
    return (
      <Link href={href} className="mb-10 flex items-center gap-2">
        {content}
      </Link>
    );
  }
  return <div className="mb-10 flex items-center gap-2">{content}</div>;
}

export function AuthNotice({ children }: { children: React.ReactNode }) {
  return (
    <p className="rounded-2xl bg-blue-50 px-4 py-3 text-sm font-medium text-blue-600">{children}</p>
  );
}

export function AuthError({ children }: { children: React.ReactNode }) {
  return (
    <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">{children}</p>
  );
}
