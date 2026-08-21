"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { OptionalFields, PersonalFields, SchoolFields, deriveSpecFields } from "@/components/spec-fields";
import { authFetch, clearTokens, isLoggedIn, MYPAGE_DRAFT_KEY as DRAFT_KEY } from "@/lib/auth";
import { clearCachedRecommendations } from "@/lib/recommendations-cache";
import {
  initialOptionalInfo,
  initialSpec,
  OptionalInfo,
  specFormToUserSpec,
  SpecForm,
  userSpecToOptionalInfo,
  userSpecToSpecForm,
  UserSpec,
} from "@/lib/spec";

// 세션(access token 30분) 만료로 강제 로그아웃되면 작성 중이던 내용이 그냥 날아가던 문제
// 때문에 추가함 — 편집할 때마다 여기에 임시 저장해두고, 재로그인 후 돌아오면 복원할지 물어봄.
// 키 자체는 lib/auth.ts에서 export함 — clearTokens()가 로그아웃/탈퇴 시 이것도 같이 지워야
// 해서(2026-08-11, 다른 계정으로 전환됐을 때 이전 사람 임시저장이 새어나가는 문제 발견).

export default function MyPage() {
  const router = useRouter();
  const [spec, setSpec] = useState<SpecForm | null>(null);
  const [optionalInfo, setOptionalInfo] = useState<OptionalInfo>(initialOptionalInfo);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [showAddressError, setShowAddressError] = useState(false);
  const [draft, setDraft] = useState<{ spec: SpecForm; optionalInfo: OptionalInfo } | null>(null);
  const isInitialLoad = useRef(true);

  // 회원탈퇴 — 되돌릴 수 없는 작업이라 비밀번호 재확인을 받음(백엔드
  // DeleteAccountRequest와 동일한 이유). 확인 패널은 기본적으로 접혀있음.
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      // 마이페이지는 게스트 모드가 아예 성립 안 함(계정 없인 저장된 스펙 자체가 없음) —
      // 랜딩(/)이 아니라 로그인 화면으로 바로 보냄.
      router.replace("/login");
      return;
    }

    (async () => {
      // authFetch가 network 자체 실패에는 reject하므로, try/catch 없이 두면 "불러오는 중..."
      // 스피너가 안 멈췄음 — home/saved page와 동일한 이유(2026-08-13).
      try {
        const res = await authFetch("/users/me/spec");
        if (res.status === 404) {
          router.replace("/spec");
          return;
        }
        if (!res.ok) {
          setError("스펙을 불러오지 못했어요.");
          setLoading(false);
          return;
        }
        const data: UserSpec = await res.json();
        setSpec(userSpecToSpecForm(data));
        setOptionalInfo(userSpecToOptionalInfo(data));
        setLoading(false);

        const draftRaw = sessionStorage.getItem(DRAFT_KEY);
        if (draftRaw) {
          try {
            // 폼 필드 구조가 바뀌면 세션에 남아있던 예전 임시저장엔 새 필드가 없을 수 있음 —
            // 항상 최신 기본값 위에 덮어써서 없는 키 참조로 터지는 걸 방지(2026-08-21,
            // guest.ts의 getGuestSpec()과 동일한 이유).
            const parsed = JSON.parse(draftRaw) as {
              spec: Partial<SpecForm>;
              optionalInfo: Partial<OptionalInfo>;
            };
            setDraft({
              spec: { ...initialSpec, ...parsed.spec },
              optionalInfo: { ...initialOptionalInfo, ...parsed.optionalInfo },
            });
          } catch {
            sessionStorage.removeItem(DRAFT_KEY);
          }
        }
      } catch {
        setError("서버에 연결하지 못했어요. 잠시 후 다시 시도해주세요.");
        setLoading(false);
      }
    })();
  }, [router]);

  // 서버에서 막 불러온 첫 렌더링은 "편집"이 아니라서 저장 안 함(안 그러면 편집을 전혀
  // 안 해도 방금 불러온 값이 바로 draft로 저장돼서 다음 방문 때마다 복원 여부를 묻게 됨).
  useEffect(() => {
    if (spec === null) return;
    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      return;
    }
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify({ spec, optionalInfo }));
  }, [spec, optionalInfo]);

  function restoreDraft() {
    if (!draft) return;
    setSpec(draft.spec);
    setOptionalInfo(draft.optionalInfo);
    setDraft(null);
  }

  function discardDraft() {
    sessionStorage.removeItem(DRAFT_KEY);
    setDraft(null);
  }

  async function handleDeleteAccount(e: React.FormEvent) {
    e.preventDefault();
    setDeleting(true);
    setDeleteError(null);
    try {
      const res = await authFetch("/users/me", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: deletePassword }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail ?? `status ${res.status}`);
      }
      sessionStorage.removeItem(DRAFT_KEY);
      clearTokens();
      router.push("/");
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "회원탈퇴에 실패했어요.");
    } finally {
      setDeleting(false);
    }
  }

  if (loading || spec === null) {
    return (
      <div className="min-h-screen bg-neu-bg">
        <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
          <TopBar />
          {!error && <p className="mt-8 text-center text-sm text-gray-400">불러오는 중...</p>}
          {error && (
            <p className="mt-8 rounded-2xl bg-red-50 px-4 py-3 text-center text-sm font-medium text-red-500">
              {error}
            </p>
          )}
        </div>
      </div>
    );
  }

  const derived = deriveSpecFields(spec);
  // setSpec은 SpecForm | null용이라(위 로딩 상태 때문) 위 early return으로 spec은 이미
  // non-null로 좁혀졌어도 setter 자체의 타입은 안 좁혀짐 — 공유 필드 컴포넌트(spec-fields.tsx)가
  // 기대하는 Dispatch<SetStateAction<SpecForm>> 형태로 여기서만 좁혀서 넘겨줌.
  const setNonNullSpec: Dispatch<SetStateAction<SpecForm>> = (updater) =>
    setSpec((prev) => (typeof updater === "function" ? (updater as (p: SpecForm) => SpecForm)(prev!) : updater));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!spec) return;
    if (!spec.address) {
      setShowAddressError(true);
      return;
    }
    setShowAddressError(false);
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const body: UserSpec = specFormToUserSpec(spec, optionalInfo);
      const res = await authFetch("/users/me/spec", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail ?? `status ${res.status}`);
      }
      // 스펙이 실제로 바뀌었으니 /home의 캐시된 추천 결과는 이제 낡은 값 — 다음 방문 때
      // 다시 계산하도록 지움(clearCachedRecommendations 참고).
      clearCachedRecommendations();
      sessionStorage.removeItem(DRAFT_KEY);
      setSaved(true);
    } catch {
      setError("스펙 수정에 실패했어요. 잠시 후 다시 시도해주세요.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-neu-bg pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
        <TopBar right={<Link href="/home" className="text-sm font-semibold text-gray-400">← 홈으로</Link>} />

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">마이페이지</h1>
        <p className="mt-1 text-sm text-gray-500">스펙을 수정하면 추천 목록도 새로 계산돼요</p>

        {draft && (
          <div className="mt-4 flex items-center justify-between gap-3 rounded-2xl bg-amber-50 px-4 py-3">
            <p className="text-sm font-medium text-amber-700">
              이전에 작성하다 만 내용이 있어요. 불러올까요?
            </p>
            <div className="flex shrink-0 gap-2">
              <button
                type="button"
                onClick={restoreDraft}
                className="rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-bold text-white shadow-neu-raised-sm transition active:shadow-neu-pressed"
              >
                불러오기
              </button>
              <button
                type="button"
                onClick={discardDraft}
                className="rounded-lg bg-neu-surface px-3 py-1.5 text-xs font-bold text-amber-700 shadow-neu-raised-sm transition active:shadow-neu-pressed"
              >
                무시하기
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <PersonalFields
            spec={spec}
            setSpec={setNonNullSpec}
            optionalInfo={optionalInfo}
            setOptionalInfo={setOptionalInfo}
            showErrors={showAddressError}
          />
          <SchoolFields
            spec={spec}
            setSpec={setNonNullSpec}
            derived={derived}
            optionalInfo={optionalInfo}
            setOptionalInfo={setOptionalInfo}
          />
          <OptionalFields
            spec={spec}
            setSpec={setNonNullSpec}
            optionalInfo={optionalInfo}
            setOptionalInfo={setOptionalInfo}
          />

          {saved && !error && (
            <p className="rounded-2xl bg-blue-50 px-4 py-3 text-sm font-medium text-blue-600">
              저장했어요. 홈으로 돌아가면 추천이 새로 반영돼요.
            </p>
          )}
          {error && (
            <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">{error}</p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="mt-2 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white shadow-neu-raised transition hover:bg-blue-600 hover:shadow-neu-raised-lg active:shadow-neu-pressed disabled:opacity-50"
          >
            {saving ? "저장 중..." : "저장하기"}
          </button>
        </form>

        <div className="mt-10 border-t border-gray-100 pt-6">
          {!showDeleteConfirm ? (
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="text-xs font-semibold text-gray-400 underline decoration-gray-300 underline-offset-2"
            >
              회원탈퇴
            </button>
          ) : (
            <div className="rounded-2xl bg-red-50 p-4">
              <p className="text-sm font-bold text-red-600">정말 탈퇴하시겠어요?</p>
              <p className="mt-1 text-xs leading-relaxed text-red-500">
                저장된 스펙, 찜 목록을 포함한 모든 정보가 삭제돼요. 삭제하면 되돌릴 수 없어요.
              </p>
              <form onSubmit={handleDeleteAccount} className="mt-3 flex flex-col gap-2">
                <input
                  type="password"
                  required
                  placeholder="비밀번호 확인"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  className="w-full rounded-xl bg-neu-surface px-3.5 py-3 text-sm text-gray-900 placeholder:text-gray-400 outline-none shadow-neu-inset transition focus:shadow-[inset_4px_4px_8px_rgba(0,0,0,0.15),inset_-4px_-4px_8px_rgba(210,225,255,0.6),0_0_0_3px_rgba(239,68,68,0.35)]"
                />
                {deleteError && <p className="text-xs font-medium text-red-600">{deleteError}</p>}
                <div className="mt-1 flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeletePassword("");
                      setDeleteError(null);
                    }}
                    className="w-full rounded-xl bg-neu-surface py-2.5 text-xs font-bold text-gray-600 shadow-neu-raised-sm transition active:shadow-neu-pressed"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    disabled={deleting}
                    className="w-full rounded-xl bg-red-500 py-2.5 text-xs font-bold text-white shadow-neu-raised-sm transition active:shadow-neu-pressed disabled:opacity-50"
                  >
                    {deleting ? "처리 중..." : "탈퇴하기"}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
