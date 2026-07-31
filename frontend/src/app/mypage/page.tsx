"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Field, inputClass, PillToggle, SelectField, ToggleChip, TopBar } from "@/components/form-ui";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { SIDO_LIST } from "@/lib/regions";
import {
  DegreeLevel,
  EnrollmentStatus,
  specFormToUserSpec,
  SpecForm,
  userSpecToSpecForm,
  UserSpec,
} from "@/lib/spec";
import { UNIVERSITIES } from "@/lib/universities";

export default function MyPage() {
  const router = useRouter();
  const [spec, setSpec] = useState<SpecForm | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/");
      return;
    }

    (async () => {
      const res = await authFetch("/users/me/spec");
      if (res.status === 404) {
        router.replace("/spec");
        return;
      }
      if (!res.ok) {
        setError("스펙을 불러오지 못했습니다.");
        setLoading(false);
        return;
      }
      const data: UserSpec = await res.json();
      setSpec(userSpecToSpecForm(data));
      setLoading(false);
    })();
  }, [router]);

  if (loading || spec === null) {
    return (
      <div className="min-h-screen bg-white">
        <div className="mx-auto w-full max-w-md px-6 py-6">
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

  const currentUniversity = UNIVERSITIES.find((u) => u.name === spec.university) ?? UNIVERSITIES[0];
  const gpaScale = currentUniversity.gpaScale;
  const currentColleges = currentUniversity.colleges;
  const currentDistricts = SIDO_LIST.find((s) => s.name === spec.sido)?.districts ?? [];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!spec) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const body: UserSpec = specFormToUserSpec(spec);
      const res = await authFetch("/users/me/spec", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail ?? `status ${res.status}`);
      }
      setSaved(true);
    } catch {
      setError("스펙 수정에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <TopBar right={<Link href="/home" className="text-sm font-semibold text-gray-400">← 홈으로</Link>} />

        <h1 className="mt-6 text-xl font-bold leading-snug text-gray-900">마이페이지</h1>
        <p className="mt-1 text-sm text-gray-500">스펙을 수정하면 추천 목록도 새로 계산돼요</p>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <SelectField
            label="소속 대학"
            value={spec.university}
            onChange={(v) => {
              const next = UNIVERSITIES.find((u) => u.name === v)!;
              setSpec({ ...spec, university: next.name, college: next.colleges[0] ?? "" });
            }}
            options={UNIVERSITIES.map((u) => ({ value: u.name, label: u.name }))}
          />

          {currentColleges.length > 0 && (
            <SelectField
              label="단과대"
              value={spec.college}
              onChange={(v) => setSpec({ ...spec, college: v })}
              options={currentColleges.map((c) => ({ value: c, label: c }))}
            />
          )}

          <Field label="재학 상태">
            <PillToggle
              value={spec.enrollment_status === "post_undergrad" ? "post_undergrad" : "undergrad"}
              onChange={(v) =>
                setSpec({
                  ...spec,
                  enrollment_status: v === "post_undergrad" ? "post_undergrad" : "undergrad_enrolled",
                })
              }
              options={[
                { value: "undergrad", label: "학부" },
                { value: "post_undergrad", label: "대학원 등" },
              ]}
            />
          </Field>

          {spec.enrollment_status === "post_undergrad" ? (
            <SelectField
              label="과정 구분"
              value={spec.degree_level ?? "masters"}
              onChange={(v) => setSpec({ ...spec, degree_level: v as DegreeLevel })}
              options={[
                { value: "masters", label: "석사" },
                { value: "doctoral", label: "박사" },
                { value: "integrated_ms_phd", label: "석박사통합" },
              ]}
            />
          ) : (
            <>
              <Field label="학부 재학 구분">
                <PillToggle
                  value={spec.enrollment_status}
                  onChange={(v) => {
                    const nextStatus = v as EnrollmentStatus;
                    const nextGrade =
                      nextStatus === "undergrad_transfer" && spec.grade === "1" ? "2" : spec.grade;
                    setSpec({ ...spec, enrollment_status: nextStatus, grade: nextGrade });
                  }}
                  options={[
                    { value: "undergrad_enrolled", label: "재학" },
                    { value: "undergrad_leave", label: "휴학" },
                    { value: "undergrad_transfer", label: "편입" },
                  ]}
                />
              </Field>

              <SelectField
                label="학년"
                value={spec.grade}
                onChange={(v) => setSpec({ ...spec, grade: v })}
                options={(spec.enrollment_status === "undergrad_transfer"
                  ? ["2", "3", "4"]
                  : ["1", "2", "3", "4"]
                ).map((g) => ({ value: g, label: `${g}학년` }))}
              />
            </>
          )}

          <Field label={`학점 (${gpaScale} 만점 기준)`}>
            <input
              type="number"
              required
              step={0.01}
              min={0}
              max={gpaScale}
              value={spec.gpa}
              onChange={(e) => setSpec({ ...spec, gpa: e.target.value })}
              className={inputClass}
            />
          </Field>

          <Field label="나이">
            <input
              type="number"
              required
              min={0}
              value={spec.age}
              onChange={(e) => setSpec({ ...spec, age: e.target.value })}
              className={inputClass}
            />
          </Field>

          <Field label="성별">
            <PillToggle
              value={spec.gender}
              onChange={(v) => setSpec({ ...spec, gender: v as "male" | "female" })}
              options={[
                { value: "male", label: "남성" },
                { value: "female", label: "여성" },
              ]}
            />
          </Field>

          <SelectField
            label="광역자치단체"
            value={spec.sido}
            onChange={(v) => {
              const nextSido = SIDO_LIST.find((s) => s.name === v)!;
              setSpec({ ...spec, sido: nextSido.name, district: nextSido.districts[0] ?? "" });
            }}
            options={SIDO_LIST.map((s) => ({ value: s.name, label: s.name }))}
          />

          {currentDistricts.length > 0 && (
            <SelectField
              label="기초자치단체"
              value={spec.district}
              onChange={(v) => setSpec({ ...spec, district: v })}
              options={currentDistricts.map((d) => ({ value: d, label: d }))}
            />
          )}

          <Field label="병역">
            <PillToggle
              value={spec.military_status}
              onChange={(v) =>
                setSpec({ ...spec, military_status: v as "completed" | "exempted" | "not_served" })
              }
              options={[
                { value: "not_served", label: "미필" },
                { value: "completed", label: "군필" },
                { value: "exempted", label: "면제" },
              ]}
            />
          </Field>

          <Field label="소득분위 (1~10)">
            <input
              type="number"
              required
              min={1}
              max={10}
              value={spec.income_bracket}
              onChange={(e) => setSpec({ ...spec, income_bracket: e.target.value })}
              className={inputClass}
            />
          </Field>

          <div className="flex flex-col gap-2">
            <ToggleChip
              checked={spec.has_disability}
              onChange={(v) => setSpec({ ...spec, has_disability: v })}
              label="장애인"
            />
            <ToggleChip
              checked={spec.is_foreigner}
              onChange={(v) => setSpec({ ...spec, is_foreigner: v })}
              label="외국인(유학생)"
            />
          </div>

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
            className="mt-2 w-full rounded-2xl bg-blue-500 py-4 text-[15px] font-semibold text-white transition hover:bg-blue-600 active:scale-[0.99] disabled:opacity-50"
          >
            {saving ? "저장 중..." : "저장하기"}
          </button>
        </form>
      </div>
    </div>
  );
}
