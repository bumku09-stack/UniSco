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
