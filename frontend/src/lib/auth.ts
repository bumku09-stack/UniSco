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

// 카카오 인가(로그인 동의) 화면으로 보낼 URL. redirect_uri는 카카오 디벨로퍼스에 등록해둔
// 값과 정확히 일치해야 하며, 그 URI로 카카오가 ?code=...를 붙여서 되돌려보내면
// app/login/kakao/callback/page.tsx가 받아서 POST /auth/kakao로 넘김.
export function kakaoAuthorizeUrl(): string {
  const clientId = process.env.NEXT_PUBLIC_KAKAO_CLIENT_ID;
  const params = new URLSearchParams({
    client_id: clientId ?? "",
    redirect_uri: kakaoRedirectUri(),
    response_type: "code",
  });
  return `https://kauth.kakao.com/oauth/authorize?${params.toString()}`;
}

// JWT의 payload(가운데 조각)만 디코드해서 만료 시각을 읽음 — 서명 검증은 안 함(그건
// 백엔드가 매 요청마다 함), 순전히 "몇 분 남았는지" 화면에 보여주기 위한 용도라 그걸로 충분함.
function decodeJwtExpiry(token: string): number | null {
  try {
    const payload = token.split(".")[1];
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
    const json = JSON.parse(atob(padded));
    return typeof json.exp === "number" ? json.exp * 1000 : null; // ms 단위로 변환
  } catch {
    return null;
  }
}

/** access token 만료 시각(ms epoch). 토큰이 없거나 파싱 실패하면 null. */
export function getAccessTokenExpiry(): number | null {
  const token = getAccessToken();
  return token ? decodeJwtExpiry(token) : null;
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
