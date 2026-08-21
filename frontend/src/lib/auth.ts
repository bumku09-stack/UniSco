import { clearCachedRecommendations } from "@/lib/recommendations-cache";

const ACCESS_TOKEN_KEY = "unisco_access_token";
const REFRESH_TOKEN_KEY = "unisco_refresh_token";

// NEXT_PUBLIC_API_URL이 배포 환경(Vercel)에 빠지면 이 전엔 그냥 "undefined/auth/login" 같은
// URL로 조용히 요청이 나가서 원인 파악이 어려웠음(2026-08-13 발견) — 여기서 한 번에 막고
// 콘솔에 원인이 바로 보이는 에러를 던짐. 모든 API 호출이 이 함수를 거치게 해서 누락되는
// 곳이 없게 함.
export function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_URL;
  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL이 설정되지 않았습니다. 배포 환경변수를 확인해주세요.");
  }
  return `${base}${path}`;
}

// mypage/page.tsx가 "작성하다 만 내용" 임시저장에 씀 — 여기서 export하는 이유는 clearTokens가
// 이것도 같이 지워야 해서(유저 구분 없이 sessionStorage에 저장되는 건 전부 로그아웃/탈퇴 시
// 같이 지워야 다음 사람한테 안 새어나감, 위 recommendations-cache와 같은 이유).
export const MYPAGE_DRAFT_KEY = "unisco_mypage_draft";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  // recommendations-cache는 유저 구분 없이 sessionStorage에 저장돼서, 이걸 안 지우면
  // 로그아웃/회원탈퇴 후 같은 브라우저로 다른 계정에 들어왔을 때 이전 사람의 매칭 결과가
  // 잠깐 화면에 떴다가 새로고침되는 문제가 있었음(2026-08-11 발견 — 공용 PC에서는 특히
  // 문제). clearTokens를 호출하는 모든 곳(로그아웃, 회원탈퇴)이 자동으로 같이 지워지게
  // 여기서 처리 — 호출부마다 따로 챙기게 하면 나중에 또 빠뜨리기 쉬움.
  clearCachedRecommendations();
  sessionStorage.removeItem(MYPAGE_DRAFT_KEY);
}

export function isLoggedIn(): boolean {
  return getAccessToken() !== null;
}

// 배포 도메인이 여러 개(예: unisco-pi.vercel.app, 커스텀 도메인)일 수 있어서 고정 문자열
// 대신 항상 현재 접속한 origin 기준으로 계산함 — 카카오 인가 요청과 백엔드 토큰 교환 둘 다
// 이 함수로 계산한 같은 값을 써야 함(app/login/kakao/callback/page.tsx가 POST /auth/kakao
// 보낼 때 이 값을 redirect_uri로 같이 실어보냄, backend/app/models/auth.py의
// KakaoLoginRequest.redirect_uri 참고 — 백엔드는 고정 설정값을 안 씀).
export function kakaoRedirectUri(): string {
  return `${window.location.origin}/login/kakao/callback`;
}

const KAKAO_STATE_STORAGE_KEY = "kakao_oauth_state";

// 카카오 인가(로그인 동의) 화면으로 보낼 URL. redirect_uri는 카카오 디벨로퍼스에 등록해둔
// 값과 정확히 일치해야 하며, 그 URI로 카카오가 ?code=...를 붙여서 되돌려보내면
// app/login/kakao/callback/page.tsx가 받아서 POST /auth/kakao로 넘김.
//
// state는 CSRF 방지용(2026-08-21 추가) — 로그인을 시작한 이 브라우저가 실제로 콜백을
// 받는 그 브라우저가 맞는지 확인하는 1회용 값. 여기서 랜덤하게 만들어 카카오한테 그대로
// 보내는 동시에, 이 브라우저 안(sessionStorage)에만 저장해둠 — 서버로는 안 보냄. 공격자가
// 자기 계정용으로 미리 받아둔 code를 피해자한테 링크로 심어 콜백 페이지를 직접 열게 만드는
// 로그인 CSRF를 막기 위함(consumeKakaoState 참고).
export function kakaoAuthorizeUrl(): string {
  const clientId = process.env.NEXT_PUBLIC_KAKAO_CLIENT_ID;
  const state = crypto.randomUUID();
  sessionStorage.setItem(KAKAO_STATE_STORAGE_KEY, state);
  const params = new URLSearchParams({
    client_id: clientId ?? "",
    redirect_uri: kakaoRedirectUri(),
    response_type: "code",
    state,
  });
  return `https://kauth.kakao.com/oauth/authorize?${params.toString()}`;
}

// 콜백 단계(app/login/kakao/callback/page.tsx)에서, 카카오가 돌려준 state가 로그인 시작 시
// 이 브라우저가 저장해둔 값과 같은지 확인함. 1회용이라 결과와 무관하게 바로 지움 — 같은
// 콜백 URL을 새로고침/재방문해도 두 번째부터는 항상 실패하게(replay 방지).
export function consumeKakaoState(returnedState: string | null): boolean {
  const saved = sessionStorage.getItem(KAKAO_STATE_STORAGE_KEY);
  sessionStorage.removeItem(KAKAO_STATE_STORAGE_KEY);
  return saved !== null && returnedState === saved;
}

// 비밀번호 규칙(2026-08-21 추가) — 백엔드 models/auth.py의 _validate_password_complexity와
// 같은 규칙(영문+숫자+특수문자 필수, 8자 이상)을 프론트에서도 미리 검사해서, 서버까지 갔다가
// 에러 받는 대신 제출 전에 바로 안내함. 통과하면 null, 아니면 안내 문구를 돌려줌.
export function passwordRequirementError(password: string): string | null {
  if (password.length < 8) return "비밀번호는 8자 이상이어야 해요.";
  const hasLetter = /[A-Za-z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  if (!hasLetter || !hasDigit || !hasSpecial) {
    return "비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 해요.";
  }
  return null;
}

export type PasswordStrengthLevel = "empty" | "weak" | "medium" | "strong" | "very-strong";

export interface PasswordStrength {
  score: number; // 0~5, 만족한 체크 항목 개수
  level: PasswordStrengthLevel;
  label: string;
}

// 규칙 기반 강도 계산(2026-08-21 추가) — 실제 필수 통과 조건(영문+숫자+특수문자+8자)보다
// 더 세분화된 체크리스트 5개를 두고, 몇 개를 만족하는지 개수만 세는 방식. 타이핑할 때마다
// (매 keystroke) 즉시 다시 계산해도 부담 없을 만큼 가벼움 — zxcvbn 같은 사전 기반 라이브러리는
// 안 씀(이 프로젝트 규모엔 과함, lib/auth.ts에 룰만 추가하는 게 더 단순함).
export function passwordStrength(password: string): PasswordStrength {
  if (password.length === 0) return { score: 0, level: "empty", label: "" };

  const checks = [
    password.length >= 8,
    password.length >= 12,
    /[A-Za-z]/.test(password),
    /\d/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ];
  const score = checks.filter(Boolean).length;

  if (score <= 2) return { score, level: "weak", label: "약함" };
  if (score === 3) return { score, level: "medium", label: "보통" };
  if (score === 4) return { score, level: "strong", label: "강함" };
  return { score, level: "very-strong", label: "매우 강함" };
}

// 아이디 중복확인(2026-08-21 추가) — GET /auth/check-username 호출. true/false/null 중
// null은 "네트워크 오류 등으로 확인 자체가 실패함"을 뜻함(사용 가능/불가능과는 다른 상태라
// 호출부가 따로 안내 문구를 보여줘야 함). 최종 방어선인 signup()의 409 에러는 여전히
// 살아있으니(레이스 컨디션 대비), 이 함수는 어디까지나 제출 전 사전 안내용.
export async function checkUsernameAvailable(username: string): Promise<boolean | null> {
  try {
    const res = await fetch(apiUrl(`/auth/check-username?username=${encodeURIComponent(username)}`));
    if (!res.ok) return null;
    const data = await res.json();
    return data.available === true;
  } catch {
    return null;
  }
}

// 로그인 전(회원가입/로그인/이메일인증/재발송) 호출용 — 토큰이 아직 없어서 authFetch를 못 씀.
// "JSON POST → 실패하면 detail 메시지, 네트워크 자체가 끊기면 폴백 메시지"가 로그인·회원가입
// 페이지 곳곳에서 그대로 반복되길래 하나로 뽑음.
export async function postJson(
  path: string,
  body: Record<string, string>,
  networkErrorFallback: string
): Promise<{ ok: true; data: Record<string, unknown> } | { ok: false; error: string }> {
  try {
    const res = await fetch(apiUrl(path), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, error: data.detail ?? networkErrorFallback };
    return { ok: true, data };
  } catch {
    return { ok: false, error: `${networkErrorFallback} 잠시 후 다시 시도해주세요.` };
  }
}

function authHeaders(token: string | null, extra?: HeadersInit): HeadersInit {
  return { ...(extra ?? {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

// 동시에 여러 authFetch가 401을 맞아도 refresh 요청은 한 번만 나가게 함 — 진행 중인
// refresh가 있으면 새로 시작하지 않고 그 결과를 같이 기다림.
let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refreshToken = getRefreshToken();
      if (!refreshToken) return false;
      try {
        const res = await fetch(apiUrl("/auth/refresh"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        setTokens(data.access_token, data.refresh_token);
        return true;
      } catch {
        return false;
      }
    })();
  }
  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

// 로그인 필요한 API 호출용 fetch 래퍼 — Authorization 헤더를 자동으로 붙임. access token이
// 만료돼 401이 오면 refresh token으로 한 번 조용히 갱신을 시도하고 원래 요청을 재시도함
// (2026-08-07 추가 — 예전엔 access token 30분 만료되면 그냥 강제 로그아웃이었음, refresh
// 엔드포인트는 백엔드에 있었는데 프론트가 안 쓰고 있었음). refresh 자체도 실패하면(refresh
// token 없음/만료/네트워크 오류) 그때만 로그아웃 처리.
//
// 처음부터 토큰이 아예 없었으면(게스트) 로그아웃 처리를 안 하고 401을 그대로 돌려줌 —
// 2026-08-10부터 로그인 없이 접근 가능한 페이지(예: 상세페이지)가 배경에서 인증 필요한
// API(예: 비슷한 장학금 추천)를 호출했다가 401 맞을 수 있는데, 그때마다 게스트를 로그인
// 화면으로 강제 이동시키면 안 됨 — "로그인된 적 없는데 로그아웃"은 애초에 성립 안 하는
// 상태라, 이런 요청은 그냥 실패로 두고 호출한 쪽이 조용히 처리하게 함.
export async function authFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const url = apiUrl(path);
  const tokenAtRequestTime = getAccessToken();
  const res = await fetch(url, { ...options, headers: authHeaders(tokenAtRequestTime, options.headers) });
  if (res.status !== 401) return res;
  if (tokenAtRequestTime === null) return res;

  if (await refreshAccessToken()) {
    return fetch(url, { ...options, headers: authHeaders(getAccessToken(), options.headers) });
  }

  clearTokens();
  window.location.href = "/";
  return res;
}
