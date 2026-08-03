const ACCESS_TOKEN_KEY = "unisco_access_token";
const REFRESH_TOKEN_KEY = "unisco_refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
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

// 로그인 필요한 API 호출용 fetch 래퍼 — Authorization 헤더를 자동으로 붙이고,
// 토큰이 없거나 만료/무효(401)면 로그인 화면으로 보냄. 리프레시 토큰으로 조용히
// 재시도하는 로직은 없음 — access token 30분 만료면 그냥 재로그인하게 함(단순함 우선).
export async function authFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getAccessToken();
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers ?? {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (res.status === 401) {
    clearTokens();
    window.location.href = "/";
  }
  return res;
}
