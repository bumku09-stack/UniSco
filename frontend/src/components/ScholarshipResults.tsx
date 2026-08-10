"use client";

import Link from "next/link";
import { useState } from "react";
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

export function ScholarshipResults({ results }: { results: Scholarship[] }) {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortBy>("relevance");
  const [categoryL1, setCategoryL1] = useState<CategoryL1 | "all">("all");
  const [categoryL2, setCategoryL2] = useState<string | null>(null);

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
  );
}
