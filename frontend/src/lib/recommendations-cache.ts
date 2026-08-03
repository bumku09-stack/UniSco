import { Scholarship } from "@/lib/scholarship";

// /home이 페이지 이동할 때마다 "매칭 중..." 로딩을 보여주던 문제 때문에 추가함 —
// 마지막으로 받은 추천 결과를 세션 동안만(sessionStorage, 탭 닫으면 사라짐) 기억해뒀다가
// 재방문 시 즉시 보여주고, 새로고침은 화면 뒤에서 조용히 함(스피너 없이). 스펙을 실제로
// 수정했을 때만(마이페이지 저장 성공 시) 캐시를 지워서 다음 방문에 진짜로 새로 계산되게 함.
const CACHE_KEY = "unisco_recommendations_cache";

export function getCachedRecommendations(): Scholarship[] | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(CACHE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Scholarship[];
  } catch {
    return null;
  }
}

export function setCachedRecommendations(data: Scholarship[]): void {
  sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
}

export function clearCachedRecommendations(): void {
  sessionStorage.removeItem(CACHE_KEY);
}
