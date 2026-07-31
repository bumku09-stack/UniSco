"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import {
  CATEGORY_L2_LABEL,
  eligibilityList,
  findSimilar,
  formatAmount,
  Scholarship,
} from "@/lib/scholarship";

function SectionHeading({ children }: { children: React.ReactNode }) {
  return <h2 className="text-[15px] font-bold text-gray-900">{children}</h2>;
}

function StatBox({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "blue" | "gray";
}) {
  const bg = tone === "blue" ? "bg-blue-50" : "bg-gray-50";
  const labelColor = tone === "blue" ? "text-blue-500" : "text-gray-500";
  const valueColor = tone === "blue" ? "text-blue-600" : "text-gray-700";
  return (
    <div className={`flex-1 rounded-2xl ${bg} px-3.5 py-3`}>
      <p className={`text-[11px] font-semibold ${labelColor}`}>{label}</p>
      <p className={`mt-1 text-sm font-bold leading-tight ${valueColor}`}>{value}</p>
    </div>
  );
}

// 백엔드에 GET /scholarships/{id}가 아직 없어서(README상 목록 전체 반환만 있음),
// 전체 목록을 받아 id로 찾음 — 상세페이지 전용 엔드포인트가 생기면 이 부분만 교체하면 됨.
export default function ScholarshipDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ from?: string }>;
}) {
  const { id } = use(params);
  const { from } = use(searchParams);
  const [scholarship, setScholarship] = useState<Scholarship | null | undefined>(undefined);
  const [allScholarships, setAllScholarships] = useState<Scholarship[]>([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/scholarships`)
      .then((res) => res.json())
      .then((all: Scholarship[]) => {
        setAllScholarships(all);
        setScholarship(all.find((s) => String(s.id) === id) ?? null);
      })
      .catch(() => setScholarship(null));
  }, [id]);

  // A→B로 추천을 타고 넘어온 경우, B의 추천 목록에 A가 다시 뜨는 걸 막음
  const similar = scholarship
    ? findSimilar(scholarship, allScholarships, 3, from ? Number(from) : undefined)
    : [];

  const hasReferenceInfo =
    scholarship &&
    (scholarship.major ||
      scholarship.min_credits ||
      scholarship.admission_score_condition ||
      scholarship.headcount);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto w-full max-w-md flex-1 px-6 pb-32 pt-6">
        <Link href="/matches" className="text-sm font-semibold text-gray-400">
          ← 목록으로
        </Link>

        {scholarship === undefined && (
          <p className="mt-8 text-center text-sm text-gray-400">불러오는 중...</p>
        )}

        {scholarship === null && (
          <p className="mt-8 text-center text-sm text-gray-400">장학금을 찾을 수 없습니다.</p>
        )}

        {scholarship && (
          <div className="mt-5">
            {/* 헤더: 분류 태그 + 이름 + 제공기관 */}
            {scholarship.category_l2 && (
              <span className="mb-2 inline-block rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-600">
                {CATEGORY_L2_LABEL[scholarship.category_l2] ?? scholarship.category_l2}
              </span>
            )}
            <h1 className="text-xl font-bold leading-snug text-gray-900">{scholarship.name}</h1>
            {scholarship.provider && (
              <p className="mt-1 text-sm text-gray-500">{scholarship.provider}</p>
            )}

            {/* 금액 / 마감일 / 선발인원 — 한눈에 보이는 요약 카드 (값이 있을 때만 표시) */}
            {(formatAmount(scholarship.amount) ||
              scholarship.application_period ||
              scholarship.headcount) && (
              <div className="mt-5 flex gap-2">
                {formatAmount(scholarship.amount) && (
                  <StatBox label="지원금액" value={formatAmount(scholarship.amount)!} tone="blue" />
                )}
                {scholarship.application_period && (
                  <StatBox label="신청기간" value={scholarship.application_period} tone="gray" />
                )}
                {scholarship.headcount && (
                  <StatBox label="선발인원" value={scholarship.headcount} tone="gray" />
                )}
              </div>
            )}

            {/* 장학금 소개 */}
            {scholarship.description && (
              <div className="mt-7 border-b border-gray-100 pb-7">
                <SectionHeading>장학금 소개</SectionHeading>
                <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-gray-700">
                  {scholarship.description}
                </p>
              </div>
            )}

            {/* 자격조건 — 한 줄 요약 대신 체크리스트 형태로 */}
            <div className={`mt-7 ${hasReferenceInfo ? "border-b border-gray-100 pb-7" : ""}`}>
              <SectionHeading>자격조건</SectionHeading>
              <ul className="mt-3 flex flex-col gap-2.5">
                {eligibilityList(scholarship).map((item, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* 참고 조건 — 매칭 필터엔 아직 안 쓰이는 원문 텍스트 필드 */}
            {hasReferenceInfo && (
              <div className="mt-7">
                <SectionHeading>참고 조건</SectionHeading>
                <p className="mt-1 text-xs text-gray-400">
                  매칭 필터에는 아직 반영되지 않음 — 원문 그대로 표시
                </p>
                <ul className="mt-3 flex flex-col gap-2.5">
                  {scholarship.major && (
                    <li className="text-sm leading-relaxed text-gray-700">
                      <span className="font-semibold text-gray-500">전공</span> · {scholarship.major}
                    </li>
                  )}
                  {scholarship.min_credits && (
                    <li className="text-sm leading-relaxed text-gray-700">
                      <span className="font-semibold text-gray-500">이수학점</span> ·{" "}
                      {scholarship.min_credits}
                    </li>
                  )}
                  {scholarship.admission_score_condition && (
                    <li className="text-sm leading-relaxed text-gray-700">
                      <span className="font-semibold text-gray-500">입학성적</span> ·{" "}
                      {scholarship.admission_score_condition}
                    </li>
                  )}
                </ul>
              </div>
            )}

            {/* 추천 장학금 — 지금 보는 장학금과 같은 분류(중분류>대분류)를 우선으로 최대 3개.
                목록 페이지 카드랑 같은 스타일(흰 배경 + 옅은 테두리)로 맞춰서 통일감 있게. */}
            {similar.length > 0 && (
              <div className="mt-7">
                <SectionHeading>이런 장학금은 어때요?</SectionHeading>
                <ul className="mt-3 flex flex-col gap-2">
                  {similar.map((s) => (
                    <li key={s.id}>
                      <Link
                        href={`/scholarship/${s.id}?from=${id}`}
                        className="block rounded-2xl border border-gray-100 bg-white p-3.5 shadow-[0_2px_10px_rgba(15,23,42,0.05)] transition hover:border-gray-200"
                      >
                        {s.category_l2 && (
                          <span className="mb-1.5 inline-block rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-600">
                            {CATEGORY_L2_LABEL[s.category_l2] ?? s.category_l2}
                          </span>
                        )}
                        <p className="text-sm font-bold leading-snug text-gray-900">{s.name}</p>
                        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                          {s.provider && <span>{s.provider}</span>}
                          {formatAmount(s.amount) && (
                            <span className="font-semibold text-blue-600">
                              {formatAmount(s.amount)}
                            </span>
                          )}
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 스크롤해도 항상 보이는 신청 버튼 */}
      {scholarship?.application_url && (
        <div className="sticky bottom-0 border-t border-gray-100 bg-white/95 px-6 py-4 backdrop-blur">
          <div className="mx-auto w-full max-w-md">
            <a
              href={scholarship.application_url}
              target="_blank"
              rel="noreferrer noopener"
              className="block w-full rounded-2xl bg-orange-500 py-4 text-center text-[15px] font-bold text-white transition hover:bg-orange-600 active:scale-[0.99]"
            >
              신청하러 가기
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
