"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  CollapsibleToggle,
  Field,
  inputClass,
  MultiPillSelect,
  PillToggle,
  SelectField,
  ToggleChip,
  TopBar,
} from "@/components/form-ui";
import { SessionExpiryBanner } from "@/components/SessionExpiryBanner";
import { authFetch, isLoggedIn } from "@/lib/auth";
import { clearCachedRecommendations } from "@/lib/recommendations-cache";
import { SIDO_LIST } from "@/lib/regions";
import {
  applySpecialStatusExclusivity,
  DegreeLevel,
  DISABILITY_TYPES,
  EnrollmentStatus,
  gradeOptions,
  INCOME_BRACKET_OPTIONS,
  initialOptionalInfo,
  LANGUAGE_TESTS,
  OptionalInfo,
  specFormToUserSpec,
  SpecForm,
  SPECIAL_STATUS_OPTIONS,
  userSpecToOptionalInfo,
  userSpecToSpecForm,
  UserSpec,
} from "@/lib/spec";
import { UNIVERSITIES } from "@/lib/universities";

// 세션(access token 30분) 만료로 강제 로그아웃되면 작성 중이던 내용이 그냥 날아가던 문제
// 때문에 추가함 — 편집할 때마다 여기에 임시 저장해두고, 재로그인 후 돌아오면 복원할지 물어봄.
const DRAFT_KEY = "unisco_mypage_draft";

export default function MyPage() {
  const router = useRouter();
  const [spec, setSpec] = useState<SpecForm | null>(null);
  const [optionalInfo, setOptionalInfo] = useState<OptionalInfo>(initialOptionalInfo);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [draft, setDraft] = useState<{ spec: SpecForm; optionalInfo: OptionalInfo } | null>(null);
  const isInitialLoad = useRef(true);

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
      setOptionalInfo(userSpecToOptionalInfo(data));
      setLoading(false);

      const draftRaw = sessionStorage.getItem(DRAFT_KEY);
      if (draftRaw) {
        try {
          setDraft(JSON.parse(draftRaw));
        } catch {
          sessionStorage.removeItem(DRAFT_KEY);
        }
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
  const currentDepartments =
    currentColleges.find((c) => c.name === spec.college)?.departments ?? [];
  const currentDistricts = SIDO_LIST.find((s) => s.name === spec.sido)?.districts ?? [];
  const currentParentDistricts =
    SIDO_LIST.find((s) => s.name === optionalInfo.parentSido)?.districts ?? [];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!spec) return;
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
      setError("스펙 수정에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-white pb-16">
      <div className="mx-auto w-full max-w-md px-6 py-6">
        <TopBar right={<Link href="/home" className="text-sm font-semibold text-gray-400">← 홈으로</Link>} />
        <SessionExpiryBanner />

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
                className="rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-bold text-white"
              >
                불러오기
              </button>
              <button
                type="button"
                onClick={discardDraft}
                className="rounded-lg border border-amber-300 px-3 py-1.5 text-xs font-bold text-amber-700"
              >
                무시하기
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <SelectField
            label="소속 대학"
            value={spec.university}
            onChange={(v) => {
              const next = UNIVERSITIES.find((u) => u.name === v)!;
              const nextDepartment = next.colleges[0]?.departments[0] ?? "";
              setSpec({
                ...spec,
                university: next.name,
                college: next.colleges[0]?.name ?? "",
                department: nextDepartment,
                grade: gradeOptions(nextDepartment, spec.enrollment_status)[0]?.value ?? spec.grade,
              });
            }}
            options={UNIVERSITIES.map((u) => ({ value: u.name, label: u.name }))}
          />

          {currentColleges.length > 0 && (
            <SelectField
              label="단과대"
              value={spec.college}
              onChange={(v) => {
                const nextCollege = currentColleges.find((c) => c.name === v)!;
                const nextDepartment = nextCollege.departments[0] ?? "";
                setSpec({
                  ...spec,
                  college: v,
                  department: nextDepartment,
                  grade: gradeOptions(nextDepartment, spec.enrollment_status)[0]?.value ?? spec.grade,
                });
              }}
              options={currentColleges.map((c) => ({ value: c.name, label: c.name }))}
            />
          )}

          {currentDepartments.length > 0 ? (
            <SelectField
              label="학과"
              value={spec.department}
              onChange={(v) =>
                setSpec({
                  ...spec,
                  department: v,
                  grade: gradeOptions(v, spec.enrollment_status)[0]?.value ?? spec.grade,
                })
              }
              options={currentDepartments.map((d) => ({ value: d, label: d }))}
            />
          ) : (
            <Field label="학과 (선택)">
              <input
                type="text"
                value={spec.department}
                onChange={(e) => setSpec({ ...spec, department: e.target.value })}
                placeholder="예: 컴퓨터공학과"
                className={inputClass}
              />
            </Field>
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
                    const nextOptions = gradeOptions(spec.department, nextStatus);
                    const nextGrade = nextOptions.some((o) => o.value === spec.grade)
                      ? spec.grade
                      : nextOptions[0]?.value ?? spec.grade;
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
                options={gradeOptions(spec.department, spec.enrollment_status)}
              />
            </>
          )}

          <Field label={`직전 학기 평점 (${gpaScale} 만점 기준)`}>
            <input
              type="number"
              required
              step={0.01}
              min={0}
              max={gpaScale}
              value={spec.semester_gpa}
              onChange={(e) => setSpec({ ...spec, semester_gpa: e.target.value })}
              className={inputClass}
            />
          </Field>

          <Field label={`전체 재학기간 누적 평점 (${gpaScale} 만점 기준)`}>
            <input
              type="number"
              required
              step={0.01}
              min={0}
              max={gpaScale}
              value={spec.cumulative_gpa}
              onChange={(e) => setSpec({ ...spec, cumulative_gpa: e.target.value })}
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

          <Field label="부모님 거주지역">
            <p className="mb-2 text-xs text-gray-500">
              지역 장학금 중엔 본인이 아니라 부모님 주소지 기준으로도 자격이 되는 경우가 있어요.
            </p>
            <PillToggle
              value={optionalInfo.parentRegionEnabled ? "different" : "same"}
              onChange={(v) => setOptionalInfo({ ...optionalInfo, parentRegionEnabled: v === "different" })}
              options={[
                { value: "same", label: "본인과 동일" },
                { value: "different", label: "다름" },
              ]}
            />
          </Field>

          {optionalInfo.parentRegionEnabled && (
            <>
              <SelectField
                label="부모님 광역자치단체"
                value={optionalInfo.parentSido}
                onChange={(v) => {
                  const nextSido = SIDO_LIST.find((s) => s.name === v)!;
                  setOptionalInfo({
                    ...optionalInfo,
                    parentSido: nextSido.name,
                    parentDistrict: nextSido.districts[0] ?? "",
                  });
                }}
                options={SIDO_LIST.map((s) => ({ value: s.name, label: s.name }))}
              />
              {currentParentDistricts.length > 0 && (
                <SelectField
                  label="부모님 기초자치단체"
                  value={optionalInfo.parentDistrict}
                  onChange={(v) => setOptionalInfo({ ...optionalInfo, parentDistrict: v })}
                  options={currentParentDistricts.map((d) => ({ value: d, label: d }))}
                />
              )}
            </>
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

          <SelectField
            label="소득분위"
            value={spec.income_bracket}
            onChange={(v) => setSpec({ ...spec, income_bracket: v })}
            options={INCOME_BRACKET_OPTIONS}
          />

          <ToggleChip
            checked={spec.is_foreigner}
            onChange={(v) => setSpec({ ...spec, is_foreigner: v })}
            label="외국인(유학생)"
          />

          <CollapsibleToggle
            checked={optionalInfo.languageTestEnabled}
            onChange={(v) => setOptionalInfo({ ...optionalInfo, languageTestEnabled: v })}
            label="어학점수"
          >
            <SelectField
              label="종류"
              value={optionalInfo.languageTestType}
              onChange={(v) => setOptionalInfo({ ...optionalInfo, languageTestType: v })}
              options={LANGUAGE_TESTS.map((t) => ({ value: t.value, label: t.label }))}
            />
            <Field
              label={`점수${
                LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max != null
                  ? ` (만점 ${LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max})`
                  : ""
              }`}
            >
              <input
                type="number"
                min={0}
                max={LANGUAGE_TESTS.find((t) => t.value === optionalInfo.languageTestType)?.max ?? undefined}
                value={optionalInfo.languageTestScore}
                onChange={(e) => setOptionalInfo({ ...optionalInfo, languageTestScore: e.target.value })}
                className={inputClass}
              />
            </Field>
          </CollapsibleToggle>

          <CollapsibleToggle
            checked={spec.has_disability}
            onChange={(v) => setSpec({ ...spec, has_disability: v })}
            label="장애인"
          >
            <SelectField
              label="유형"
              value={optionalInfo.disabilityType}
              onChange={(v) => setOptionalInfo({ ...optionalInfo, disabilityType: v })}
              options={DISABILITY_TYPES}
            />
          </CollapsibleToggle>

          <CollapsibleToggle
            checked={optionalInfo.specialStatusEnabled}
            onChange={(v) =>
              setOptionalInfo({
                ...optionalInfo,
                specialStatusEnabled: v,
                specialStatus: v ? optionalInfo.specialStatus : [],
              })
            }
            label="특수상황"
          >
            <MultiPillSelect
              values={optionalInfo.specialStatus}
              onChange={(v) =>
                setOptionalInfo({
                  ...optionalInfo,
                  specialStatus: applySpecialStatusExclusivity(optionalInfo.specialStatus, v),
                })
              }
              options={SPECIAL_STATUS_OPTIONS}
            />
          </CollapsibleToggle>

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
