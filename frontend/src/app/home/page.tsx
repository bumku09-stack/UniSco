"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { authFetch, clearTokens, isLoggedIn } from "@/lib/auth";
import { getCachedRecommendations, setCachedRecommendations } from "@/lib/recommendations-cache";
import {
  CATEGORY_L1_LABEL,
  CATEGORY_L2_BY_L1,
  CATEGORY_L2_LABEL,
  CategoryL1,
  eligibilitySummary,
  formatAmount,
  Scholarship,
  sortScholarships,
  SortBy,
} from "@/lib/scholarship";

const PAGE_SIZE = 15;

function Pagination({
  page,
  totalPages,
  onChange,
}: {
  page: number;
  totalPages: number;
  onChange: (p: number) => void;
}) {
  return (
    <div className="mt-6 flex flex-wrap items-center justify-center gap-1.5">
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
        <button
          key={p}
          type="button"
          onClick={() => onChange(p)}
          className={`flex h-9 w-9 items-center justify-center rounded-xl text-sm font-semibold transition ${
            p === page ? "bg-blue-500 text-white" : "text-gray-500 hover:bg-gray-100"
          }`}
        >
          {p}
        </button>
      ))}
    </div>
  );
}

function ScholarshipCard({ s }: { s: Scholarship }) {
  return (
    <li className="rounded-2xl border border-gray-100 bg-white p-5 shadow-[0_2px_10px_rgba(15,23,42,0.05)]">
      <Link href={`/scholarship/${s.id}`} className="block">
        {s.category_l2 && (
          <span className="mb-1.5 inline-block rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-600">
            {CATEGORY_L2_LABEL[s.category_l2] ?? s.category_l2}
          </span>
        )}
        <h2 className="font-bold text-gray-900">{s.name}</h2>
        {s.provider && <p className="mt-0.5 text-sm text-gray-400">{s.provider}</p>}

        {formatAmount(s.amount) && (
          <p className="mt-3 text-lg font-bold text-blue-600">{formatAmount(s.amount)}</p>
        )}
        {s.description && (
          <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-gray-600">{s.description}</p>
        )}
        {s.application_period && (
          <p className="mt-3 text-xs font-semibold text-gray-500">신청기간 · {s.application_period}</p>
        )}
        <p className="mt-2 text-xs text-gray-400">{eligibilitySummary(s)}</p>
      </Link>

      <Link
        href={`/scholarship/${s.id}`}
        className="mt-4 block w-full rounded-xl border border-blue-500 py-3 text-center text-sm font-bold text-blue-600 transition hover:bg-blue-50 active:scale-[0.99]"
      >
        자세히 보기
      </Link>
    </li>
  );
}

export default function HomePage() {
  const router = useRouter();
  // sessionStorage는 서버(SSR)에서 항상 null이라, 초기 state를 캐시값으로 바로 잡으면
  // 서버는 "로딩 중" 화면을, 캐시가 있는 클라이언트는 바로 결과 화면을 렌더링해서
  // hydration mismatch가 났었음(2026-08-04) — 그래서 초기값은 항상 서버와 동일하게
  // null/true로 시작하고, 캐시 확인은 아래 useEffect(클라이언트에서만 실행됨) 안으로 옮김.
  const [results, setResults] = useState<Scholarship[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortBy>("relevance");
  const [categoryL1, setCategoryL1] = useState<CategoryL1 | "all">("all");
  const [categoryL2, setCategoryL2] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/");
      return;
    }

    (async () => {
      // 캐시가 있으면 마운트 직후(첫 페인트 전에 가깝게) 바로 반영해서 로딩 스피너가
      // 거의 안 보이게 함 — 없을 때만 실제 loading=true 화면이 유지됨. async 함수는
      // 첫 await 전까지 동기적으로 실행되므로 타이밍은 이전과 동일함 — effect 본문에
      // 직접 두면 react-hooks/set-state-in-effect가 걸려서 여기(async 클로저 안)로 옮김.
      const cached = getCachedRecommendations();
      if (cached !== null) {
        setResults(cached);
        setLoading(false);
      }
      // hadCache를 state가 아니라 이 변수로 판단하는 건 의도적임 — 마운트 시점의 캐시
      // 유무만 한 번 확인하면 되고, 나중에 setResults 하는 것 때문에 이펙트가 다시 도는
      // 걸 막기 위함.
      const hadCache = cached !== null;

      const statusRes = await authFetch("/users/me/spec-status");
      if (!statusRes.ok) {
        if (!hadCache) {
          setError("정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
          setLoading(false);
        }
        return;
      }
      const status = await statusRes.json();
      if (!status.spec_completed) {
        router.replace("/spec");
        return;
      }

      const recRes = await authFetch("/scholarships/recommendations");
      if (!recRes.ok) {
        // 캐시된 이전 결과가 이미 화면에 떠 있으면 그거 그대로 두고 조용히 넘어감 —
        // 캐시가 없을 때만(최초 진입) 에러를 실제로 보여줌.
        if (!hadCache) {
          setError("매칭에 실패했습니다. 백엔드 서버가 켜져 있는지 확인해주세요.");
          setLoading(false);
        }
        return;
      }
      const data: Scholarship[] = await recRes.json();
      setResults(data);
      setCachedRecommendations(data);
      setLoading(false);
    })();
  }, [router]);

  function handleLogout() {
    clearTokens();
    router.push("/");
  }

  const categoryFiltered = (results ?? []).filter((s) => {
    if (categoryL1 === "all") return true;
    if (s.category_l1 !== categoryL1) return false;
    if (categoryL2 && s.category_l2 !== categoryL2) return false;
    return true;
  });
  const filteredSorted = sortScholarships(categoryFiltered, sortBy);
  const totalAmount = filteredSorted.reduce((sum, s) => sum + (s.amount ?? 0), 0);

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <TopBar
          right={
            <div className="flex items-center gap-3">
              <Link href="/mypage" className="text-sm font-semibold text-blue-500">
                마이페이지
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="text-sm font-semibold text-gray-400"
              >
                로그아웃
              </button>
            </div>
          }
        />

        {loading && <p className="mt-8 text-center text-sm text-gray-400">매칭 중...</p>}

        {error && (
          <p className="mt-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-500">
            {error}
          </p>
        )}

        {!loading && !error && results !== null && (
          <div>
            <h2 className="mt-6 text-lg font-bold text-gray-900">내 맞춤 장학금</h2>
            <p className="mt-1 text-xs text-gray-400">
              조건을 자세하게 입력할수록 더 적합도 높은 장학금을 추천해드려요
            </p>

            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="rounded-2xl bg-blue-50 px-4 py-3">
                <p className="text-xs font-semibold text-blue-500">매칭 건수</p>
                <p className="mt-0.5 text-lg font-bold text-blue-600">{filteredSorted.length}건</p>
              </div>
              <div className="rounded-2xl bg-blue-50 px-4 py-3">
                <p className="text-xs font-semibold text-blue-500">매칭 금액 합계</p>
                <p className="mt-0.5 text-lg font-bold text-blue-600">
                  {formatAmount(totalAmount) ?? "0원"}
                </p>
              </div>
            </div>

            <div className="mt-5 flex gap-1.5 overflow-x-auto pb-1">
              {(["all", "school_internal", "school_external", "support_fund"] as const).map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => {
                    setCategoryL1(c);
                    setCategoryL2(null);
                    setPage(1);
                  }}
                  className={`shrink-0 rounded-full border px-3.5 py-2 text-xs font-semibold transition ${
                    categoryL1 === c
                      ? "border-blue-500 bg-blue-500 text-white"
                      : "border-gray-200 bg-white text-gray-500"
                  }`}
                >
                  {c === "all" ? "전체" : CATEGORY_L1_LABEL[c]}
                </button>
              ))}
            </div>

            {categoryL1 !== "all" && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {CATEGORY_L2_BY_L1[categoryL1].map((l2) => (
                  <button
                    key={l2}
                    type="button"
                    onClick={() => {
                      setCategoryL2(categoryL2 === l2 ? null : l2);
                      setPage(1);
                    }}
                    className={`shrink-0 rounded-full border px-3 py-1.5 text-[11px] font-semibold transition ${
                      categoryL2 === l2
                        ? "border-blue-500 bg-blue-50 text-blue-600"
                        : "border-gray-200 bg-white text-gray-400"
                    }`}
                  >
                    {CATEGORY_L2_LABEL[l2] ?? l2}
                  </button>
                ))}
              </div>
            )}

            <div className="mt-3 flex gap-2">
              {(
                [
                  { value: "relevance", label: "매칭적합도순" },
                  { value: "amount", label: "금액순" },
                  { value: "deadline", label: "마감일순" },
                ] as const
              ).map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setSortBy(opt.value)}
                  className={`flex-1 rounded-xl border py-2 text-xs font-semibold transition ${
                    sortBy === opt.value
                      ? "border-blue-500 bg-blue-50 text-blue-600"
                      : "border-gray-200 bg-white text-gray-500"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {filteredSorted.length === 0 ? (
              <p className="mt-8 text-center text-sm text-gray-400">조건에 맞는 장학금이 없습니다.</p>
            ) : (
              <>
                <ul className="mt-4 flex flex-col gap-3">
                  {filteredSorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map((s) => (
                    <ScholarshipCard key={s.id} s={s} />
                  ))}
                </ul>
                {filteredSorted.length > PAGE_SIZE && (
                  <Pagination
                    page={page}
                    totalPages={Math.ceil(filteredSorted.length / PAGE_SIZE)}
                    onChange={setPage}
                  />
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
