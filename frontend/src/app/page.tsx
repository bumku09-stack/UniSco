type Scholarship = {
  id: number;
  name: string;
  provider: string | null;
  description: string | null;
  amount: number | null;
  application_url: string | null;
  min_age: number | null;
  max_age: number | null;
  required_gender: "male" | "female" | null;
  eligible_region: string | null;
  required_military_status: "completed" | "exempted" | "not_served" | null;
  max_income_bracket: number | null;
  min_gpa: number | null;
  requires_disability: boolean | null;
  foreigner_eligibility: "korean_only" | "foreigner_only" | null;
};

async function getScholarships(): Promise<Scholarship[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scholarships`);
  if (!res.ok) {
    throw new Error(`Failed to fetch scholarships: ${res.status}`);
  }
  return res.json();
}

function formatAmount(amount: number | null) {
  if (amount == null) return null;
  return `${amount.toLocaleString("ko-KR")}원`;
}

const MILITARY_LABEL: Record<string, string> = {
  completed: "군필",
  exempted: "면제",
  not_served: "미필",
};

function eligibilitySummary(s: Scholarship): string {
  const parts: string[] = [];
  if (s.eligible_region) parts.push(s.eligible_region);
  if (s.min_age != null || s.max_age != null) {
    parts.push(`${s.min_age ?? ""}~${s.max_age ?? ""}세`);
  }
  if (s.max_income_bracket != null) parts.push(`소득분위 ${s.max_income_bracket} 이하`);
  if (s.min_gpa != null) parts.push(`학점 ${s.min_gpa} 이상`);
  if (s.required_military_status) parts.push(MILITARY_LABEL[s.required_military_status]);
  if (s.required_gender) parts.push(s.required_gender === "male" ? "남성" : "여성");
  if (s.requires_disability) parts.push("장애인 한정");
  if (s.foreigner_eligibility) {
    parts.push(s.foreigner_eligibility === "foreigner_only" ? "외국인 한정" : "내국인 한정");
  }
  return parts.length > 0 ? parts.join(" · ") : "제한 없음";
}

export default async function Home() {
  let scholarships: Scholarship[] = [];
  let error: string | null = null;
  try {
    scholarships = await getScholarships();
  } catch {
    error = "장학금 목록을 불러오지 못했습니다. 백엔드 서버가 켜져 있는지 확인해주세요.";
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto w-full max-w-md px-4 py-6">
        <h1 className="text-xl font-bold text-zinc-900">UniSco 장학금 목록</h1>
        <p className="mt-1 text-sm text-zinc-500">대전 지역 대학생 대상</p>

        {error && <p className="mt-8 text-sm text-red-600">{error}</p>}

        {!error && scholarships.length === 0 && (
          <p className="mt-8 text-sm text-zinc-500">아직 등록된 장학금이 없습니다.</p>
        )}

        <ul className="mt-6 flex flex-col gap-3">
          {scholarships.map((s) => (
            <li key={s.id} className="rounded-xl border border-zinc-200 p-4">
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-semibold text-zinc-900">{s.name}</h2>
                {formatAmount(s.amount) && (
                  <span className="shrink-0 text-sm font-medium text-zinc-900">
                    {formatAmount(s.amount)}
                  </span>
                )}
              </div>
              {s.provider && <p className="mt-0.5 text-sm text-zinc-500">{s.provider}</p>}
              {s.description && <p className="mt-2 text-sm text-zinc-600">{s.description}</p>}
              <p className="mt-2 text-xs text-zinc-400">{eligibilitySummary(s)}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
