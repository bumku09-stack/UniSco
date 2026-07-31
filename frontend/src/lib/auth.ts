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
