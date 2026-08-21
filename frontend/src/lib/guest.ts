import { Scholarship } from "@/lib/scholarship";
import { initialOptionalInfo, initialSpec, OptionalInfo, SpecForm } from "@/lib/spec";

// 로그인 없이 "가볍게 둘러보기"용 상태 저장소 (2026-08-10 추가). recommendations-cache.ts와
// 달리 이건 서버에 원본이 있는 데이터의 "캐시"가 아니라 — 게스트는 애초에 서버에 아무것도
// 저장 안 하므로 sessionStorage 자체가 유일한 사본임. 두 가지를 따로 들고 있음:
//   1. 게스트가 입력한 스펙(spec) — /spec이 비로그인 상태로 접근됐을 때 채워짐. 이후 회원가입
//      전환 시 다시 안 치도록 /spec이 이 값으로 폼을 미리 채우는 데 씀(3단계부터 이어서).
//   2. 게스트 매칭 결과(results) — POST /match 응답. /home이 로그인 없이 이 값을 보여줌.
// 회원가입을 마치고 실제 계정 스펙(POST /users/me/spec)이 저장되면 둘 다 지움(clearGuestData).
const GUEST_SPEC_KEY = "unisco_guest_spec";
const GUEST_RESULTS_KEY = "unisco_guest_results";

export function saveGuestSpec(spec: SpecForm, optionalInfo: OptionalInfo): void {
  sessionStorage.setItem(GUEST_SPEC_KEY, JSON.stringify({ spec, optionalInfo }));
}

export function getGuestSpec(): { spec: SpecForm; optionalInfo: OptionalInfo } | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(GUEST_SPEC_KEY);
  if (!raw) return null;
  try {
    // 폼 필드 구조가 바뀌면(필드 추가/이름 변경 등) 세션에 저장된 예전 JSON엔 새 필드가 아예
    // 없을 수 있음 — 그대로 쓰면 없는 키를 참조하는 컴포넌트가 undefined에서 터짐(2026-08-21,
    // MultiPillSelect의 values.includes(...) 크래시로 발견). 항상 최신 기본값 위에 저장된
    // 값을 덮어써서, 새로 생긴 필드는 기본값으로라도 채워지게 함.
    const parsed = JSON.parse(raw) as { spec: Partial<SpecForm>; optionalInfo: Partial<OptionalInfo> };
    return {
      spec: { ...initialSpec, ...parsed.spec },
      optionalInfo: { ...initialOptionalInfo, ...parsed.optionalInfo },
    };
  } catch {
    return null;
  }
}

export function saveGuestResults(results: Scholarship[]): void {
  sessionStorage.setItem(GUEST_RESULTS_KEY, JSON.stringify(results));
}

export function getGuestResults(): Scholarship[] | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(GUEST_RESULTS_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Scholarship[];
  } catch {
    return null;
  }
}

export function clearGuestData(): void {
  sessionStorage.removeItem(GUEST_SPEC_KEY);
  sessionStorage.removeItem(GUEST_RESULTS_KEY);
}
