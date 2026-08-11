"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { authFetch, isLoggedIn } from "@/lib/auth";
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

// /home(로그인 유저)과 게스트 결과 화면이 완전히 같은 목록 UI(통계·분류 필터·정렬·카드·
// 페이지네이션)를 쓰기 때문에 여기 하나로 뽑아둠(2026-08-10) — 데이터를 어디서 가져오는지
// (서버 fetch vs 게스트 sessionStorage)는 각 페이지가 알아서 하고, 이 컴포넌트는 이미
// 받아온 results만 받아서 보여주는 데만 집중함.

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

// 찜 하트 아이콘 — 별도 아이콘 라이브러리 없이 인라인 SVG로(이 프로젝트 다른 곳도 동일 패턴).
function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-5 w-5"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={filled ? 0 : 1.8}
    >
      <path d="M12 20.5s-7.5-4.6-10-9.2C.5 8 2 4.5 5.5 4c2-.3 3.8.7 6.5 3.2C14.7 4.7 16.5 3.7 18.5 4c3.5.5 5 4 3.5 7.3-2.5 4.6-10 9.2-10 9.2z" />
    </svg>
  );
}

// 카드 전체가 이미 Link(내용) + Link("자세히 보기") 두 개로 채워져 있어서(둘 다 li의
// 형제, 서로 안에 안 들어감), 하트 버튼도 그 둘의 형제로 li 맨 위에 절대위치로 얹음 —
// 이러면 Link 안에 또 클릭 가능한 요소를 넣는 게 아니라서 stopPropagation 같은 이벤트
// 버블링 처리가 아예 필요 없음(2026-08-11).
function ScholarshipCard({
  s,
  saved,
  onToggleSave,
}: {
  s: Scholarship;
  saved: boolean | null; // null = 로그인 안 함(하트 자체를 안 보여줌)
  onToggleSave: (id: number) => void;
}) {
  return (
    <li className="relative rounded-2xl border border-gray-100 bg-white p-5 shadow-[0_2px_10px_rgba(15,23,42,0.05)]">
      {saved !== null && (
        <button
          type="button"
          onClick={() => onToggleSave(s.id)}
          aria-label={saved ? "찜 취소" : "찜하기"}
          className={`absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full transition ${
            saved ? "text-red-500" : "text-gray-300 hover:text-gray-400"
          }`}
        >
          <HeartIcon filled={saved} />
        </button>
      )}

      <Link href={`/scholarship/${s.id}`} className="block">
        {s.category_l2 && (
          <span className="mb-1.5 inline-block rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-600">
            {CATEGORY_L2_LABEL[s.category_l2] ?? s.category_l2}
          </span>
        )}
        <h2 className="pr-8 font-bold text-gray-900">{s.name}</h2>
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

export function ScholarshipResults({ results }: { results: Scholarship[] }) {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortBy>("relevance");
  const [categoryL1, setCategoryL1] = useState<CategoryL1 | "all">("all");
  const [categoryL2, setCategoryL2] = useState<string | null>(null);
  // null = 로그인 안 함(하트 자체를 숨김). 로그인 상태면 처음엔 빈 Set으로 시작했다가
  // useEffect에서 실제 찜 목록으로 채움 — 게스트/로그인 여부 판단이 localStorage를 읽어야
  // 해서 SSR에선 못 하므로, 여기도 home 화면과 같은 이유로 useEffect 안에서만 판단함
  // (hydration mismatch 회피 패턴, frontend/src/app/home/page.tsx 참고).
  const [savedIds, setSavedIds] = useState<Set<number> | null>(null);

  useEffect(() => {
    if (!isLoggedIn()) return;
    (async () => {
      try {
        const res = await authFetch("/users/me/saved-scholarships");
        if (!res.ok) return;
        const data: Scholarship[] = await res.json();
        setSavedIds(new Set(data.map((s) => s.id)));
      } catch {
        // 실패해도 조용히 넘어감 — 하트가 그냥 전부 안 찜 상태로 보일 뿐, 페이지 자체는 정상 동작.
      }
    })();
  }, []);

  function handleToggleSave(id: number) {
    setSavedIds((prev) => {
      const next = new Set(prev ?? []);
      const wasSaved = next.has(id);
      if (wasSaved) next.delete(id);
      else next.add(id);

      // 낙관적 업데이트 먼저 반영, 실패하면 되돌림 — API 자체는 idempotent라 재시도/중복
      // 클릭에도 안전함(app/api/scholarships.py의 save/unsave 참고).
      authFetch(`/scholarships/${id}/save`, { method: wasSaved ? "DELETE" : "POST" }).then((res) => {
        if (!res.ok) {
          setSavedIds((cur) => {
            const reverted = new Set(cur ?? []);
            if (wasSaved) reverted.add(id);
            else reverted.delete(id);
            return reverted;
          });
        }
      });

      return next;
    });
  }

  const categoryFiltered = results.filter((s) => {
    if (categoryL1 === "all") return true;
    if (s.category_l1 !== categoryL1) return false;
    if (categoryL2 && s.category_l2 !== categoryL2) return false;
    return true;
  });
  const filteredSorted = sortScholarships(categoryFiltered, sortBy);
  const totalAmount = filteredSorted.reduce((sum, s) => sum + (s.amount ?? 0), 0);

  return (
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
          <p className="mt-0.5 text-lg font-bold text-blue-600">{formatAmount(totalAmount) ?? "0원"}</p>
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
              <ScholarshipCard
                key={s.id}
                s={s}
                saved={savedIds === null ? null : savedIds.has(s.id)}
                onToggleSave={handleToggleSave}
              />
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
  );
}
