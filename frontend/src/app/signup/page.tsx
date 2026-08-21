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

type UsernameCheckStatus = "idle" | "checking" | "available" | "taken" | "tooShort" | "error";

const stripToUsernameChars = (v: string) => v.replace(/[^a-zA-Z0-9_]/g, "");

export default function SignupPage() {
  const router = useRouter();
  const [step, setStep] = useState<"signup" | "verify">("signup");

  const [username, setUsername] = useState("");
  // 한글 IME 조합 중(예: "ㅇ"→"아"→"안" 순서로 완성되는 도중)엔 필터링을 걸지 않음(2026-08-21
  // 추가) — 조합 중에 JS가 값을 강제로 고치면 브라우저의 조합 상태가 깨지면서 커서 위치가
  // 엉키고 이미 입력해둔 영문/숫자까지 같이 지워지는 문제가 있었음("백스페이스 모드"처럼
  // 보이던 원인). 조합이 끝나는 순간(onCompositionEnd)에만 걸러내면 이 문제가 없음.
  const [isComposingUsername, setIsComposingUsername] = useState(false);
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
  // "다음" 버튼을 한 번이라도 눌러보기 전엔 submitBlockReason을 안 보여줌(2026-08-21 추가) —
  // 페이지 열자마자 "아이디 중복확인을 완료해주세요"가 계속 떠있으면 거슬리니, 눌러봤는데
  // 아직 조건이 안 채워졌을 때만 나타나게 함.
  const [attemptedSubmit, setAttemptedSubmit] = useState(false);

  // 제출 버튼 자체를 막는 조건(2026-08-21 추가) — 기존엔 handleSignup 안에서만 검사해서
  // 버튼은 눌리는데 에러 메시지만 뜨는 방식이었음. 여기서는 아예 버튼을 비활성화해서
  // 세 조건(중복확인 완료·비밀번호 규칙·비밀번호 일치)을 다 채우기 전엔 클릭 자체가 안 되게 함.
  const usernameChecked = usernameCheckStatus === "available" && checkedUsername === username;
  const passwordOk = passwordRequirementError(password) === null;
  const passwordMatches = password.length > 0 && password === passwordConfirm;
  const canSubmit = usernameChecked && passwordOk && passwordMatches;

  // 버튼이 왜 안 눌리는지 이유를 항상 옆에 보여줌(2026-08-21 추가) — 그냥 비활성화만 해두면
  // 사용자 입장에서 뭘 더 해야 하는지 알 방법이 없어서, 안 채워진 조건 중 첫 번째를 짚어줌.
  const submitBlockReason = !usernameChecked
    ? "아이디 중복확인을 완료해주세요"
    : !passwordOk
      ? "비밀번호가 영문+숫자+특수문자를 포함한 8자 이상이어야 해요"
      : !passwordMatches
        ? "비밀번호 확인이 비밀번호랑 일치해야 해요"
        : null;

  async function handleCheckUsername() {
    if (username.length < 5) {
      setUsernameCheckStatus("tooShort");
      setCheckedUsername(username);
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
    setAttemptedSubmit(true);

    if (!canSubmit) {
      return; // submitBlockReason이 이제 화면에 뜸(아래 JSX 참고)
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
      <AuthLogo href="/" />

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
                minLength={5}
                maxLength={32}
                placeholder="아이디"
                value={username}
                // 영문/숫자/밑줄 외 문자(한글 포함)는 걸러내되, 한글 IME 조합 중에는 그대로
                // 두고 조합이 끝나는 시점(onCompositionEnd)에만 걸러냄 — 위 주석 참고.
                onCompositionStart={() => setIsComposingUsername(true)}
                onCompositionEnd={(e) => {
                  setIsComposingUsername(false);
                  setUsername(stripToUsernameChars(e.currentTarget.value));
                }}
                onChange={(e) =>
                  setUsername(
                    isComposingUsername ? e.target.value : stripToUsernameChars(e.target.value)
                  )
                }
                className={authInputClass}
              />
              <button
                type="button"
                onClick={handleCheckUsername}
                disabled={usernameCheckStatus === "checking"}
                className="shrink-0 rounded-2xl bg-neu-surface px-4 text-sm font-semibold text-gray-600 shadow-neu-raised transition hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50"
              >
                {usernameCheckStatus === "checking" ? "확인 중..." : "중복확인"}
              </button>
            </div>
            {checkedUsername === username && usernameCheckStatus === "tooShort" && (
              <p className="-mt-1 px-1 text-xs font-semibold text-red-500">
                아이디는 5자 이상이어야 해요
              </p>
            )}
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
            {attemptedSubmit && !error && submitBlockReason && (
              <p className="px-1 text-center text-xs text-gray-400">{submitBlockReason}</p>
            )}
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
