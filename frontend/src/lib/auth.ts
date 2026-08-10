const ACCESS_TOKEN_KEY = "unisco_access_token";
const REFRESH_TOKEN_KEY = "unisco_refresh_token";

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
}

export function isLoggedIn(): boolean {
  return getAccessToken() !== null;
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
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
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
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
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
  const url = `${process.env.NEXT_PUBLIC_API_URL}${path}`;
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
