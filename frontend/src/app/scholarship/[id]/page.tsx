"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { TopBar } from "@/components/form-ui";
import { apiUrl, authFetch, isLoggedIn } from "@/lib/auth";
import {
  CATEGORY_L2_LABEL,
  eligibilityList,
  formatAmount,
  isAutoSelected,
  isListingOnlyUrl,
  Scholarship,
  unverifiableConditionParts,
} from "@/lib/scholarship";
import { UNIVERSITIES } from "@/lib/universities";

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

// 지원금액 요약칸(StatBox)용 — amount_detail에 "A급: 등록금 전액" 처럼 서로 다른 갈래(트랙)가
// 2개 이상 나열돼 있으면 길이와 상관없이 이 좁은 칸엔 다 안 보여주고 짧은 안내 문구로 대신함
// (2026-08-14, 사용자 확정 — 글자 수 기준이 아니라 "갈래가 몇 개냐"가 기준). "본교 등록금
// 전액 + 자매대학 실납부금 50% 이내"처럼 +로 이어진 건 하나의 트랙이 받는 혜택 묶음이라
// 갈래가 아님 — 헷갈리지 말 것. 실제 판별 방법: `\n`으로 나눈 각 줄이 "라벨: 값" 형태로
// 콜론(:)을 포함하는지 셈(각 갈래는 항상 "A급:", "교류학생:" 처럼 콜론으로 값을 표시하고,
// 반환조건·환수조건 같은 단일 트랙의 부가 설명 문장에는 콜론이 없음 — 이 차이로 구분됨).
// 콜론 포함 줄이 2개 이상이면 갈래가 2개 이상인 것으로 판단. 전체 내용은 아래 "금액" 섹션에
// 그대로 다 나오므로 정보 손실은 없음.
function summarizeAmountForStatBox(amount: number | null, amountDetail: string | null): string {
  const formatted = formatAmount(amount);
  if (formatted) return formatted;
  if (!amountDetail) return "정보 없음";
  const branchLineCount = amountDetail
    .split("\n")
    .filter((line) => line.includes(":") || line.includes("：")).length;
  // 콜론으로 갈래가 안 나뉘어도, "빨/주/노/초/파/남/보 단계별 차등, 15만~85만원(학년별 기준
  // 다름)"처럼 범위(~)로 뭉뚱그리면서 "차등/다름/단계별로 다르다"는 걸 명시한 경우도 사실상
  // 여러 조건이 섞인 것 — 같은 취급(2026-08-14, 레인보우장학금 사례로 확정).
  const isVagueRangeWithVariance =
    amountDetail.includes("~") && /차등|다름|단계|구간별/.test(amountDetail);
  if (branchLineCount >= 2 || isVagueRangeWithVariance) return "조건별로 달라요\n아래 '금액' 참조";
  // 유지조건("평점평균 3.70 이상 유지 시 4년간 지속")은 데이터 자체(amount_detail)엔 그대로
  // 남겨서 아래 "금액" 섹션 본문엔 나오게 하되, 이 위쪽 요약 카드에서만 빼고 짧게 보여줌
  // (2026-08-14, 사용자 확정 — "지원금액" 카드는 요약용이라 유지조건까지 다 넣으면 빽빽해짐).
  // 조건("평점평균 X 이상 유지 시")뿐 아니라 그 조건에 딸린 결과절("N년간 지속")까지 같이
  // 지워야 "등록금 전액 + 도서비 200만원 4년간 지속"처럼 붕 뜬 문구가 안 남음(사용자 재지적).
  let summary = amountDetail.replace(
    /[,.]?\s*평점평균\s*[\d.]+\s*이상\s*유지(\s*시)?(\s*\d*년간\s*지속)?/g,
    ""
  );
  // "(특별한 사유 없는 한)"처럼 기본금액에 붙은 단서 괄호나, "~없으면 70%만 지급"처럼 별도
  // 줄로 붙은 예외/감액 조건도 같은 취급 — 데이터(amount_detail)엔 그대로 두고 이 요약
  // 카드에서만 뺌(2026-08-14, 체육특기자장학금 사례로 확정. 위 유지조건 스트리핑과 동일한
  // 원칙: "기본 지급액" 자체가 아니라 그걸 깎는/조건 붙이는 부가 설명은 여기선 생략).
  summary = summary
    .replace(/\([^()]*없는\s*한\)/g, "")
    .replace(/\(입학금\s*제외\)/g, "") // 2026-08-14, 사용자 확정 — 이 세부 단서도 요약카드에선 생략
    .split("\n")
    .filter((line) => !/없으면/.test(line))
    .join("\n");
  return summary
    .replace(/\(\s*\)/g, "") // 조건을 지우고 남은 빈 괄호
    .replace(/\s{2,}/g, " ")
    .replace(/[,.]\s*$/g, "") // 끝에 남은 쉼표/마침표
    .trim();
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
      <p className={`mt-1 whitespace-pre-line text-sm font-bold leading-tight ${valueColor}`}>
        {value}
      </p>
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
  const [viewerGpaScale, setViewerGpaScale] = useState<number | undefined>(undefined);

  // 본문은 GET /scholarships/{id} 하나로 바로 받아서 빠르게 그림 — 예전엔 전체 목록(수백
  // 건)을 받아서 그중 하나를 골라 쓰는 방식이라 상세페이지 열 때마다 느렸음. "이런 장학금은
  // 어때요" 추천 섹션만 전체 목록이 필요해서, 본문 렌더링을 막지 않게 따로(병렬로) 받아옴.
  useEffect(() => {
    fetch(apiUrl(`/scholarships/${id}`))
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

  // 자격조건의 학점(min_gpa)은 4.5만점 기준으로 저장돼 있는데(예: KAIST는 4.3만점), 로그인해서
  // 대학을 등록해둔 학생한테는 본인 대학 만점 기준으로 환산해서 보여줌(2026-08-14). 스펙 없는
  // 게스트는 그냥 4.5만점 그대로 보임 — similar 추천과 동일한 로그인 게이팅 패턴.
  useEffect(() => {
    if (!isLoggedIn()) return;
    authFetch("/users/me/spec")
      .then((res) => (res.ok ? res.json() : null))
      .then((spec: { university?: string } | null) => {
        if (!spec?.university) return;
        const scale = UNIVERSITIES.find((u) => u.name === spec.university)?.gpaScale;
        if (scale != null) setViewerGpaScale(scale);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto w-full max-w-md flex-1 px-6 pb-32 pt-6 sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
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
          <p className="mt-8 text-center text-sm text-gray-400">장학금을 찾을 수 없어요.</p>
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
                value={summarizeAmountForStatBox(scholarship.amount, scholarship.amount_detail)}
                tone="blue"
              />
              <StatBox
                label="신청기간"
                value={
                  scholarship.application_period
                    ?.split("\n")[0]
                    .replace(/^[가-힣A-Za-z0-9()]{1,10}\s*[:：]\s*/, "") ?? "정보 없음"
                }
                tone="gray"
              />
              <StatBox label="선발인원" value={scholarship.headcount ?? "정보 없음"} tone="gray" />
            </div>

            {/* 금액/기간/신청방식 — 예전엔 description을 문장 그대로 쭉 나열해서 읽기
                힘들었음(2026-08-11 지적). 2026-08-14부터 이 세 항목을 구조화된 칸
                (amount_detail/application_period/application_method)으로 나눠서 보여줌.
                값이 없으면 "정보 없음"으로 표시 — 위 StatBox랑 동일한 원칙(칸 개수가
                장학금마다 들쭉날쭉하지 않게). */}
            <div className="mt-7 border-b border-gray-100 pb-7">
              <SectionHeading>금액</SectionHeading>
              <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-gray-700">
                {scholarship.amount_detail ?? formatAmount(scholarship.amount) ?? "정보 없음"}
              </p>
            </div>

            <div className="mt-7 border-b border-gray-100 pb-7">
              <SectionHeading>신청방식</SectionHeading>
              <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-gray-700">
                {scholarship.application_method ?? "정보 없음"}
              </p>
            </div>

            <div className="mt-7 border-b border-gray-100 pb-7">
              <SectionHeading>기간</SectionHeading>
              <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-gray-700">
                {/* application_period가 없을 때 application_method를 대신 보여주면 바로 위
                    "신청방식" 섹션과 문장이 그대로 중복돼 보임(2026-08-15 리뷰에서 발견) —
                    금액/신청방식과 동일하게 "정보 없음"으로 통일. */}
                {scholarship.application_period ?? "정보 없음"}
              </p>
            </div>

            {/* 자격조건 — 시스템이 실제로 걸러낸 조건(파란 점), 원문엔 있지만 아직 필터에는
                못 쓰는 조건(이수학점·입학성적, 노란 점 — 학생이 직접 확인해야 함), 그리고
                구조화된 칸 어디에도 안 들어가는 나머지 조건 설명(description, 노란 점)을
                한 목록 안에서 점 색깔로 구분해서 보여줌(2026-08-11 사용자 아이디어, 2026-08-14
                description을 여기로 통합). */}
            <div className="mt-7">
              <SectionHeading>자격조건</SectionHeading>
              <p className="mt-1 text-xs text-gray-400">
                <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-blue-400" />
                시스템이 확인한 조건 · <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-amber-400" />
                직접 확인 필요한 조건
              </p>
              <ul className="mt-3 flex flex-col gap-2.5">
                {eligibilityList(scholarship, viewerGpaScale).map((item, i) => (
                  <li key={`e-${i}`} className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
                    {item}
                  </li>
                ))}
                {scholarship.min_credits && scholarship.min_credits_last_semester == null && (
                  <li className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                    <span>
                      <span className="font-semibold text-gray-500">이수학점</span> ·{" "}
                      {scholarship.min_credits}
                    </span>
                  </li>
                )}
                {scholarship.admission_score_condition && (
                  <li className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                    <span>
                      <span className="font-semibold text-gray-500">입학성적</span> ·{" "}
                      {scholarship.admission_score_condition}
                    </span>
                  </li>
                )}
                {unverifiableConditionParts(scholarship).map((item, i) => (
                  <li key={`u-${i}`} className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                    {item}
                  </li>
                ))}
                {scholarship.description &&
                  splitSentences(scholarship.description).map((sentence, i) => (
                    <li key={`d-${i}`} className="flex items-start gap-2.5 text-sm leading-relaxed text-gray-700">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                      {sentence}
                    </li>
                  ))}
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

      {/* 스크롤해도 항상 보이는 신청 버튼 — 자동선발 장학금은 버튼(링크)은 그대로 두고
          (혹시 판정이 틀려도 신청 기능 자체는 안 사라지게) 위에 안내 문구만 얹음. */}
      {scholarship?.application_url && (
        <div className="sticky bottom-0 border-t border-gray-100 bg-white/95 px-6 py-4 backdrop-blur">
          <div className="mx-auto w-full max-w-md sm:max-w-xl md:max-w-2xl lg:max-w-3xl">
            {isAutoSelected(scholarship) && (
              <p className="mb-2 text-center text-xs text-gray-400">
                별도 신청 없이 조건에 맞으면 학교에서 자동으로 선발해요 — 아래 버튼은 학교
                안내 페이지로 연결돼요
              </p>
            )}
            {!isAutoSelected(scholarship) && isListingOnlyUrl(scholarship.application_url) && (
              <p className="mb-2 text-center text-xs text-gray-400">
                이 링크는 학교의 장학금 안내 목록 페이지예요 — 실제 신청 방법은 학교(학생과
                등)에 문의해 확인해주세요
              </p>
            )}
            <a
              href={scholarship.application_url}
              target="_blank"
              rel="noreferrer noopener"
              className="block w-full rounded-2xl bg-blue-500 py-4 text-center text-[15px] font-bold text-white transition hover:bg-blue-600 active:scale-[0.99]"
            >
              {isAutoSelected(scholarship) || isListingOnlyUrl(scholarship.application_url)
                ? "학교 안내 확인하기"
                : "신청하러 가기"}
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
