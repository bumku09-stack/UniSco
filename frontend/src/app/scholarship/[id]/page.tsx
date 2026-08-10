"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { CATEGORY_L2_LABEL, eligibilityList, formatAmount, Scholarship } from "@/lib/scholarship";

function SectionHeading({ children }: { children: React.ReactNode }) {
  return <h2 className="text-[15px] font-bold text-gray-900">{children}</h2>;
}

// description이 문장 하나로 다 이어붙어 있어서(줄바꿈 없음) 읽기 힘들다는 지적(2026-08-11) —
// 마침표+공백을 문장 경계로 보고 줄 단위로 쪼개서 보여줌. "3.0 이상"처럼 소수점 뒤에 공백이
// 없는 숫자는 마침표 뒤에 공백이 없어서 안 쪼개짐(의도한 동작).
function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+(?=\S)/)
    .map((s) => s.trim())
    .filter(Boolean);
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
  const [similar, setSimilar] = useState<Scholarship[]>([]);

  // 본문은 GET /scholarships/{id} 하나로 바로 받아서 빠르게 그림 — 예전엔 전체 목록(수백
  // 건)을 받아서 그중 하나를 골라 쓰는 방식이라 상세페이지 열 때마다 느렸음. "이런 장학금은
  // 어때요" 추천 섹션만 전체 목록이 필요해서, 본문 렌더링을 막지 않게 따로(병렬로) 받아옴.
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/scholarships/${id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then(setScholarship)
      .catch(() => setScholarship(null));
  }, [id]);

  // 추천은 "내 조건에 맞는 장학금" 안에서만 서버가 골라줌(같은 중분류>대분류>워딩 유사도
  // 순, core/matching.py의 find_similar 참고) — A→B로 넘어온 경우 exclude_id로 B의
  // 추천에 A가 다시 뜨는 핑퐁을 막음. 이 API는 로그인(저장된 스펙) 필요라 게스트는 애초에
  // 호출 안 함(2026-08-10부터 상세페이지도 로그인 없이 열람 가능해져서, 안 그러면 이 요청이
  // 401을 맞고 authFetch가 로그인 화면으로 튕겨버림 — lib/auth.ts의 authFetch 참고).
  useEffect(() => {
    if (!scholarship || !isLoggedIn()) return;
    const query = from ? `?exclude_id=${from}` : "";
    authFetch(`/scholarships/${scholarship.id}/similar${query}`)
      .then((res) => (res.ok ? res.json() : []))
      .then(setSimilar)
      .catch(() => setSimilar([]));
  }, [scholarship, from]);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto w-full max-w-md flex-1 px-6 pb-32 pt-6">
        <TopBar
          right={
            <Link href="/home" className="text-sm font-semibold text-gray-400">
              ← 목록으로
            </Link>
          }
        />

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

            {/* 금액 / 신청기간 / 선발인원 — 어떤 장학금이든 항상 이 3개를 같은 순서로 보여줌
                (값이 없으면 "정보 없음"으로 표시 — 장학금마다 보이는 칸 개수가 들쭉날쭉하지
                않도록 통일). */}
            <div className="mt-5 flex gap-2">
              <StatBox
                label="지원금액"
                value={formatAmount(scholarship.amount) ?? "정보 없음"}
                tone="blue"
              />
              <StatBox
                label="신청기간"
                value={scholarship.application_period ?? "정보 없음"}
                tone="gray"
              />
              <StatBox label="선발인원" value={scholarship.headcount ?? "정보 없음"} tone="gray" />
            </div>

            {/* 장학금 소개 — 문장 단위로 줄을 나눠서 표시(2026-08-11, 한 문단으로 다 이어붙어
                있어서 읽기 힘들다는 지적 반영) */}
            {scholarship.description && (
              <div className="mt-7 border-b border-gray-100 pb-7">
                <SectionHeading>장학금 소개</SectionHeading>
                <div className="mt-3 flex flex-col gap-2">
                  {splitSentences(scholarship.description).map((sentence, i) => (
                    <p key={i} className="whitespace-pre-line text-sm leading-relaxed text-gray-700">
                      {sentence}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* 지원조건 — 시스템이 실제로 걸러낸 조건과, 원문엔 있지만 아직 필터에는 못 쓰는
                조건(이수학점·입학성적)을 한 목록으로 통일해서 보여줌. 예전엔 "자격조건"/
                "참고조건" 두 섹션으로 나뉘어 있어서 "참고조건"이 덜 중요한 정보처럼 보였는데,
                둘 다 학생 입장에선 똑같이 지켜야 할 지원조건이라 하나로 합침(2026-08-11). */}
            <div className="mt-7">
              <SectionHeading>지원조건</SectionHeading>
              <ul className="mt-3 flex flex-col gap-2.5">
                {eligibilityList(scholarship).map((item, i) => (
                  <li key={`e-${i}`} className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    {item}
                  </li>
                ))}
                {scholarship.min_credits && (
                  <li className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    <span>
                      <span className="font-semibold text-gray-500">이수학점</span> ·{" "}
                      {scholarship.min_credits}
                    </span>
                  </li>
                )}
                {scholarship.admission_score_condition && (
                  <li className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    <span>
                      <span className="font-semibold text-gray-500">입학성적</span> ·{" "}
                      {scholarship.admission_score_condition}
                    </span>
                  </li>
                )}
              </ul>
            </div>

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
              className="block w-full rounded-2xl bg-blue-500 py-4 text-center text-[15px] font-bold text-white transition hover:bg-blue-600 active:scale-[0.99]"
            >
              신청하러 가기
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
