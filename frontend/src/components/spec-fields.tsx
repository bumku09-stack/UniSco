import type { Dispatch, SetStateAction } from "react";
import {
  CollapsibleToggle,
  Field,
  inputClass,
  MultiPillSelect,
  PillToggle,
  SelectField,
  ToggleChip,
} from "@/components/form-ui";
import { SIDO_LIST } from "@/lib/regions";
import {
  ADMISSION_TRACK_OPTIONS,
  AdmissionTrack,
  applySpecialStatusExclusivity,
  DegreeLevel,
  DISABILITY_TYPES,
  EnrollmentStatus,
  gradeOptions,
  INCOME_BRACKET_OPTIONS,
  LANGUAGE_TESTS,
  OptionalInfo,
  SpecForm,
  SPECIAL_STATUS_OPTIONS,
} from "@/lib/spec";
import { UNIVERSITIES } from "@/lib/universities";

// /spec(온보딩 마법사)과 /mypage(수정 화면)가 같은 필드 세트를 편집하므로(README
// "/spec과 /mypage는 필드를 항상 같이 맞출 것" 참고), 그 편집 UI 자체를 여기 한 곳에
// 모아두고 두 페이지가 공유함 — 필드가 추가/변경될 때 한 쪽만 고치고 잊어버리는 걸 방지.

export function deriveSpecFields(spec: SpecForm) {
  const currentUniversity = UNIVERSITIES.find((u) => u.name === spec.university) ?? UNIVERSITIES[0];
  const currentColleges = currentUniversity.colleges;
  const currentDepartments = currentColleges.find((c) => c.name === spec.college)?.departments ?? [];
  const currentDistricts = SIDO_LIST.find((s) => s.name === spec.sido)?.districts ?? [];
  return {
    currentUniversity,
    gpaScale: currentUniversity.gpaScale,
    currentColleges,
    currentDepartments,
    currentDistricts,
  };
}

type SpecDerived = ReturnType<typeof deriveSpecFields>;
type SetSpec = Dispatch<SetStateAction<SpecForm>>;
type SetOptionalInfo = Dispatch<SetStateAction<OptionalInfo>>;

export function SchoolFields({
  spec,
  setSpec,
  derived,
  showFreshmanHint = false,
}: {
  spec: SpecForm;
  setSpec: SetSpec;
  derived: SpecDerived;
  showFreshmanHint?: boolean;
}) {
  const { gpaScale, currentColleges, currentDepartments } = derived;

  return (
    <>
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

      <SelectField
        label="입학전형"
        value={spec.admission_track}
        onChange={(v) => setSpec({ ...spec, admission_track: v as AdmissionTrack })}
        options={ADMISSION_TRACK_OPTIONS}
      />

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

          <div>
            <SelectField
              label="학년"
              value={spec.grade}
              onChange={(v) => setSpec({ ...spec, grade: v })}
              options={gradeOptions(spec.department, spec.enrollment_status)}
            />
            {showFreshmanHint &&
              spec.enrollment_status === "undergrad_enrolled" &&
              spec.grade === "1" && (
                <p className="mt-1.5 text-xs font-semibold text-blue-500">
                  ✓ 신입생으로 인식돼요 — 신입생 전용 장학금도 함께 찾아드려요
                </p>
              )}
          </div>
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
    </>
  );
}

export function CommonFields({
  spec,
  setSpec,
  derived,
  optionalInfo,
  setOptionalInfo,
}: {
  spec: SpecForm;
  setSpec: SetSpec;
  derived: SpecDerived;
  optionalInfo: OptionalInfo;
  setOptionalInfo: SetOptionalInfo;
}) {
  const { currentDistricts } = derived;
  const currentParentDistricts =
    SIDO_LIST.find((s) => s.name === optionalInfo.parentSido)?.districts ?? [];

  return (
    <>
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
    </>
  );
}

export function OptionalFields({
  spec,
  setSpec,
  optionalInfo,
  setOptionalInfo,
}: {
  spec: SpecForm;
  setSpec: SetSpec;
  optionalInfo: OptionalInfo;
  setOptionalInfo: SetOptionalInfo;
}) {
  return (
    <>
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
        checked={optionalInfo.creditsEnabled}
        onChange={(v) => setOptionalInfo({ ...optionalInfo, creditsEnabled: v })}
        label="직전학기 이수학점"
      >
        <Field label="이수학점">
          <input
            type="number"
            min={0}
            value={optionalInfo.creditsLastSemester}
            onChange={(e) => setOptionalInfo({ ...optionalInfo, creditsLastSemester: e.target.value })}
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
    </>
  );
}
