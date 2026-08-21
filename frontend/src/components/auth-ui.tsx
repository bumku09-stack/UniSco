// 로그인/회원가입/비밀번호 찾기 세 페이지가 레이아웃·입력창·버튼·알림 메시지 스타일을
// 거의 그대로 복붙하고 있던 걸 모아둠(2026-08-11 리팩터링). form-ui.tsx의 inputClass와는
// 별개임 — 그쪽은 라벨이 붙는 스펙 입력 폼용(placeholder 색 없음), 여긴 라벨 없이
// placeholder만으로 안내하는 인증 폼용이라 스타일이 미세하게 다름(py-4 vs py-3.5,
// placeholder:text-gray-400 유무) — 실수로 통일하지 말 것, 의도된 차이임.

import Link from "next/link";
import { passwordStrength } from "@/lib/auth";

export const authInputClass =
  "w-full rounded-2xl bg-neu-surface px-4 py-4 text-[15px] text-gray-900 placeholder:text-gray-400 outline-none transition shadow-neu-inset focus:shadow-neu-focus";

// 눌린 버튼(active)은 튀어나온 그림자 → 움푹 들어간 그림자로 전환해서 실제 눌림 피드백을
// 줌 — 기존 active:scale-[0.99](살짝 축소)는 뉴모피즘 그림자 전환만으로도 눌림이 충분히
// 표현되고 둘을 같이 쓰면 과해서 뺌. 브랜드 블루(bg-blue-500)는 그대로 유지(원칙 3).
export const authPrimaryButtonClass =
  "mt-4 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition shadow-neu-raised hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50";

export const authSecondaryButtonClass =
  "w-full rounded-2xl bg-neu-surface py-4 text-[15px] font-semibold text-gray-600 transition shadow-neu-raised hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50";

export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-neu-bg">
      <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16 sm:max-w-lg md:max-w-xl">
        {children}
      </div>
    </div>
  );
}

// href를 주면 클릭 시 이동하는 로고. 로그인·회원가입은 랜딩으로 링크(2026-08-19 — 회원가입도
// 로고 클릭으로 나갈 수 있어야 한다는 지적으로 추가, 이전엔 로그인만 있었음). 비밀번호
// 찾기·카카오 콜백은 href 없이 정적 헤더로 남김 — 재설정 코드 입력 중간에 실수로 나가는
// 걸 막기 위한 의도적 차이(코드 재발송 없이는 이어서 못 함).
export function AuthLogo({ href }: { href?: string }) {
  const content = (
    <>
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 text-base font-bold text-white shadow-neu-raised-sm">
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

// 5칸짜리 막대바(각 칸 = passwordStrength 체크리스트 5개 중 몇 개 만족했는지) + 색깔 +
// 라벨(약함/보통/강함/매우 강함). 빈 문자열이면 아무것도 안 그림(입력 전엔 표시할 이유 없음).
const STRENGTH_BAR_COLOR: Record<string, string> = {
  weak: "bg-red-400",
  medium: "bg-amber-400",
  strong: "bg-lime-500",
  "very-strong": "bg-green-500",
};

const STRENGTH_LABEL_COLOR: Record<string, string> = {
  weak: "text-red-500",
  medium: "text-amber-500",
  strong: "text-lime-600",
  "very-strong": "text-green-600",
};

export function PasswordStrengthMeter({ password }: { password: string }) {
  const strength = passwordStrength(password);
  if (strength.level === "empty") return null;

  const barColor = STRENGTH_BAR_COLOR[strength.level];
  const labelColor = STRENGTH_LABEL_COLOR[strength.level];

  return (
    <div className="-mt-1 flex items-center gap-2 px-1">
      <div className="flex flex-1 gap-1">
        {Array.from({ length: 5 }, (_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-colors ${
              i < strength.score ? barColor : "bg-gray-200"
            }`}
          />
        ))}
      </div>
      <span className={`text-xs font-semibold ${labelColor}`}>{strength.label}</span>
    </div>
  );
}

// 비밀번호 확인 칸에 타이핑할 때마다(매 keystroke) 원본 비밀번호와 즉시 비교해서 보여줌
// (2026-08-21 추가) — 확인 칸이 비어있으면 아직 아무것도 안 쳤다는 뜻이라 표시 안 함.
export function PasswordMatchHint({ password, confirm }: { password: string; confirm: string }) {
  if (confirm.length === 0) return null;

  const matches = password === confirm;
  return (
    <p
      className={`-mt-1 px-1 text-xs font-semibold ${matches ? "text-green-600" : "text-red-500"}`}
    >
      {matches ? "비밀번호가 일치해요" : "비밀번호가 일치하지 않아요"}
    </p>
  );
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

// 카카오 공식 로그인 버튼 가이드 색상(#FEE500 배경 + #191919 텍스트) — 브랜드 가이드라인상
// 이 조합은 임의로 바꾸면 안 됨. onClick에서 window.location.href를 직접 바꾸는 이유 —
// kakaoAuthorizeUrl()이 window.location.origin을 읽어야 해서 서버 렌더링 시점엔 못 부름
// (lib/auth.ts 참고); 클릭 핸들러 안에서만 부르면 이미 클라이언트에서 실행 중이라 안전함.
export function KakaoLoginButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="mt-3 flex w-full items-center justify-center gap-2 rounded-2xl bg-[#FEE500] py-4 text-[15px] font-semibold text-[#191919] shadow-neu-raised transition hover:shadow-neu-raised-lg hover:brightness-95 active:shadow-neu-pressed"
    >
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor">
        <path d="M12 3C6.48 3 2 6.48 2 10.8c0 2.76 1.85 5.19 4.63 6.58-.2.75-.73 2.73-.84 3.15-.13.53.19.52.4.38.17-.11 2.66-1.81 3.74-2.55.68.1 1.38.15 2.07.15 5.52 0 10-3.48 10-7.71C22 6.48 17.52 3 12 3z" />
      </svg>
      카카오로 로그인
    </button>
  );
}
