import { useState, type Dispatch, type SetStateAction } from "react";
import { AddressSearchField } from "@/components/address-search";
import {
  CollapsibleToggle,
  Field,
  inputClass,
  MultiPillSelect,
  noSpinnerClass,
  PillToggle,
  PlainSelect,
  SelectField,
  ToggleChip,
} from "@/components/form-ui";
import {
  ADMISSION_TRACK_OPTIONS,
  AdmissionTrack,
  applyExclusiveNotApplicable,
  applySpecialStatusExclusivity,
  DegreeLevel,
  DISABILITY_NOT_APPLICABLE,
  DISABILITY_TYPES,
  DISCHARGE_TYPE_OPTIONS,
  DischargeType,
  EnrollmentStatus,
  gradeOptions,
  INCOME_BRACKET_OPTIONS,
  LANGUAGE_TESTS,
  LanguageTestFormEntry,
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
  return {
    currentUniversity,
    gpaScale: currentUniversity.gpaScale,
    currentColleges,
    currentDepartments,
  };
}

type SpecDerived = ReturnType<typeof deriveSpecFields>;
type SetSpec = Dispatch<SetStateAction<SpecForm>>;
type SetOptionalInfo = Dispatch<SetStateAction<OptionalInfo>>;

export function SchoolFields({
  spec,
  setSpec,
  derived,
  optionalInfo,
  setOptionalInfo,
  showFreshmanHint = false,
}: {
  spec: SpecForm;
  setSpec: SetSpec;
  derived: SpecDerived;
  optionalInfo: OptionalInfo;
  setOptionalInfo: SetOptionalInfo;
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

      <div className="grid grid-cols-2 gap-3">
        <Field label="직전 학기 평점">
          <div className="flex items-center rounded-2xl bg-neu-surface px-4 py-3.5 shadow-neu-inset transition focus-within:shadow-neu-focus">
            <input
              type="text"
              inputMode="decimal"
              required
              placeholder={`${gpaScale} 만점`}
              value={spec.semester_gpa}
              onChange={(e) => {
                const v = e.target.value;
                if (v !== "" && !/^\d*\.?\d{0,2}$/.test(v)) return;
                if (v !== "" && Number(v) > gpaScale) return;
                setSpec({ ...spec, semester_gpa: v });
              }}
              style={spec.semester_gpa ? { width: `${spec.semester_gpa.length}ch` } : undefined}
              className={`bg-transparent text-[15px] text-gray-900 outline-none ${
                spec.semester_gpa ? "" : "w-full"
              }`}
            />
            {spec.semester_gpa && (
              <span className="text-[15px] text-gray-900"> / {gpaScale} 만점</span>
            )}
          </div>
        </Field>

        <Field label="누적 평점">
          <div className="flex items-center rounded-2xl bg-neu-surface px-4 py-3.5 shadow-neu-inset transition focus-within:shadow-neu-focus">
            <input
              type="text"
              inputMode="decimal"
              required
              placeholder={`${gpaScale} 만점`}
              value={spec.cumulative_gpa}
              onChange={(e) => {
                const v = e.target.value;
                if (v !== "" && !/^\d*\.?\d{0,2}$/.test(v)) return;
                if (v !== "" && Number(v) > gpaScale) return;
                setSpec({ ...spec, cumulative_gpa: v });
              }}
              style={spec.cumulative_gpa ? { width: `${spec.cumulative_gpa.length}ch` } : undefined}
              className={`bg-transparent text-[15px] text-gray-900 outline-none ${
                spec.cumulative_gpa ? "" : "w-full"
              }`}
            />
            {spec.cumulative_gpa && (
              <span className="text-[15px] text-gray-900"> / {gpaScale} 만점</span>
            )}
          </div>
        </Field>
      </div>

      {/* 2026-08-21 — 선택정보(3단계)에서 이쪽 학적사항으로 이동. GPA 옆에 있는 편이 자연스럽고
          (둘 다 성적 관련 자기입력값), 선택 입력이라 required는 안 붙임(null="모름"이면 이수학점
          조건이 있는 장학금도 안 거름 — core/matching.py의 credits_matches() 참고).
          2026-08-21 추가 — 원래는 다른 선택 항목들처럼 체크해서 펼치는 방식이었는데, 숫자 하나만
          물어보는 항목까지 한 번 더 눌러야 하는 게 불필요한 단계라 GPA처럼 바로 적을 수 있게
          바꿈(디자인 논의 결과 — 하위 항목이 여러 개인 어학점수·장애인은 펼치는 방식 유지). */}
      <Field
        label={
          <>
            직전학기 이수학점{" "}
            <span className="text-xs font-normal text-gray-400">선택사항</span>
          </>
        }
      >
        <div className="flex items-center rounded-2xl bg-neu-surface px-4 py-3.5 shadow-neu-inset transition focus-within:shadow-neu-focus">
          <input
            type="text"
            inputMode="numeric"
            placeholder="18"
            value={optionalInfo.creditsLastSemester}
            onChange={(e) => {
              const v = e.target.value;
              if (v !== "" && !/^\d{0,2}$/.test(v)) return;
              if (v !== "" && Number(v) > 98) return;
              setOptionalInfo({ ...optionalInfo, creditsLastSemester: v });
            }}
            style={optionalInfo.creditsLastSemester ? { width: `${optionalInfo.creditsLastSemester.length}ch` } : undefined}
            className={`bg-transparent text-[15px] text-gray-900 outline-none ${
              optionalInfo.creditsLastSemester ? "" : "w-6"
            }`}
          />
          <span
            className={`ml-1 text-[15px] transition ${
              optionalInfo.creditsLastSemester ? "text-gray-900" : "text-gray-400"
            }`}
          >
            학점
          </span>
        </div>
      </Field>
    </>
  );
}

// 생년월일을 연/월/일 3개 드롭다운으로 받기 위한 옵션들 — 2026-08-21 추가. 100년 전까지
// 넉넉히 잡음(장학금 대상이 대학생/대학원생이라 실사용 범위는 훨씬 좁지만, 굳이 좁혀서
// 예외를 만들 이유가 없음).
const BIRTH_YEAR_OPTIONS = Array.from({ length: 100 }, (_, i) => {
  const year = new Date().getFullYear() - i;
  return { value: String(year), label: `${year}년` };
});
const BIRTH_MONTH_OPTIONS = Array.from({ length: 12 }, (_, i) => {
  const month = String(i + 1).padStart(2, "0");
  return { value: month, label: `${i + 1}월` };
});
function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate(); // month는 1~12, Date(y, m, 0) = m월의 마지막 날
}
function birthDayOptions(year: number, month: number) {
  return Array.from({ length: daysInMonth(year, month) }, (_, i) => {
    const day = String(i + 1).padStart(2, "0");
    return { value: day, label: `${i + 1}일` };
  });
}

// 2026-08-21 재구성 — 기존 CommonFields를 해체해서 이름/생년월일과 함께 1단계 "인적정보"로
// 묶음(외국인 여부만 OptionalFields로 이동, 아래 참고). 거주지역은 드롭다운 대신 주소 검색
// (AddressSearchField)으로 받되, 내부적으로 기존과 동일한 sido(정식 명칭)/district(구·군
// 원문) 모양으로 저장하므로 matching.py는 전혀 안 바뀜.
export function PersonalFields({
  spec,
  setSpec,
  optionalInfo,
  setOptionalInfo,
  showErrors,
}: {
  spec: SpecForm;
  setSpec: SetSpec;
  optionalInfo: OptionalInfo;
  setOptionalInfo: SetOptionalInfo;
  // 2026-08-22 추가 — 사는 지역(AddressSearchField)이 readOnly 인풋이라 브라우저 네이티브
  // required 검증이 안 먹힘(HTML 스펙상 readonly 인풋은 constraint validation 대상에서
  // 아예 빠짐) — 그래서 주소 안 넣고도 "다음"이 그냥 넘어가던 버그(사용자 실제 신고로 발견).
  // 대신 호출하는 쪽(spec/page.tsx, mypage/page.tsx)에서 제출 시도했는데 주소가 비어있으면
  // 이 플래그를 true로 넘겨서 필드 밑에 에러 메시지를 직접 그려줌.
  showErrors?: boolean;
}) {
  // 연/월/일 셀렉트 3개를 spec.birth_date(yyyy-mm-dd 문자열) 하나로 합쳐서 관리 — 아직 하나도
  // 안 고른 값이 있으면(신규 입력) 기본값으로 채워서 셀렉트가 항상 유효한 값을 보여주게 함.
  const [rawYear, rawMonth, rawDay] = spec.birth_date.split("-");
  const birthYear = rawYear || String(new Date().getFullYear() - 20);
  const birthMonth = rawMonth || "01";
  const birthDay = rawDay || "01";

  function updateBirthDate(next: { year?: string; month?: string; day?: string }) {
    const year = next.year ?? birthYear;
    const month = next.month ?? birthMonth;
    // 달이 바뀌어서(예: 31일 → 2월) 지금 고른 날짜가 더는 그 달에 없으면 그 달의 마지막 날로
    // 당겨줌 — 그대로 두면 "2월 31일" 같은 존재하지 않는 날짜가 만들어짐.
    const maxDay = daysInMonth(Number(year), Number(month));
    const day = next.day ?? (Number(birthDay) > maxDay ? String(maxDay).padStart(2, "0") : birthDay);
    setSpec({ ...spec, birth_date: `${year}-${month}-${day}` });
  }

  return (
    <>
      <Field label="이름">
        <input
          type="text"
          required
          maxLength={20}
          placeholder="예: 홍길동"
          value={spec.display_name}
          onChange={(e) => setSpec({ ...spec, display_name: e.target.value })}
          className={inputClass}
        />
      </Field>

      <Field label="생년월일">
        <div className="grid grid-cols-3 gap-2">
          <PlainSelect
            value={birthYear}
            onChange={(v) => updateBirthDate({ year: v })}
            options={BIRTH_YEAR_OPTIONS}
          />
          <PlainSelect
            value={birthMonth}
            onChange={(v) => updateBirthDate({ month: v })}
            options={BIRTH_MONTH_OPTIONS}
          />
          <PlainSelect
            value={birthDay}
            onChange={(v) => updateBirthDate({ day: v })}
            options={birthDayOptions(Number(birthYear), Number(birthMonth))}
          />
        </div>
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

      <AddressSearchField
        label="사는 지역"
        sido={spec.sido}
        district={spec.district}
        address={spec.address}
        onChange={(next) => setSpec({ ...spec, ...next })}
        required
        error={showErrors && !spec.address ? "사는 지역을 입력해주세요" : undefined}
      />

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
        <AddressSearchField
          label="부모님 사는 지역"
          sido={optionalInfo.parentSido}
          district={optionalInfo.parentDistrict}
          address={optionalInfo.parentAddress}
          onChange={(next) =>
            setOptionalInfo({
              ...optionalInfo,
              parentSido: next.sido,
              parentDistrict: next.district,
              parentAddress: next.address,
            })
          }
        />
      )}

      <SelectField
        label="소득분위"
        value={spec.income_bracket}
        onChange={(v) => setSpec({ ...spec, income_bracket: v })}
        options={INCOME_BRACKET_OPTIONS}
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
  // 2026-08-22 추가 — 어학점수를 "저장"하기 전까지 입력 중인 값(초안). 실제 제출되는 값은
  // optionalInfo.languageTests(저장된 목록)뿐이고, 이 초안은 저장을 눌러야 그 목록으로
  // 들어감 — 다른 컴포넌트로 옮기는 값이 아니라 이 화면 안에서만 의미 있는 임시 상태라
  // OptionalInfo가 아니라 로컬 state로 둠(3단계를 벗어났다 오면 초기화되는 것도 의도된
  // 동작 — 저장 안 한 값은 안 남는 게 자연스러움).
  const [languageTestsOpen, setLanguageTestsOpen] = useState(optionalInfo.languageTests.length > 0);
  const [languageTestDraft, setLanguageTestDraft] = useState<LanguageTestFormEntry>({
    type: LANGUAGE_TESTS[0].value,
    score: "",
  });

  return (
    <>
      {/* 2026-08-21 — 기존 CommonFields에 있던 항목을 여기로 이동. 나이/거주지역 등 다른
          인적사항은 1단계(PersonalFields)로 갔는데, 외국인 여부·병역은 "특별사항" 성격이라
          장애인 항목과 비슷하게 선택정보 단계로 옮기는 게 더 자연스러움.
          2026-08-22 — 외국인 항목만 펼치는 방식이 아니라서(고를 하위 항목이 없는 단순
          예/아니오) 다른 항목들 사이에 섞여 있으면 튀어 보인다는 지적으로 맨 위로 옮김
          (스타일은 그대로 — 논의 끝에 모양 변경은 하지 않기로 함). */}
      <ToggleChip
        checked={spec.is_foreigner}
        onChange={(v) => setSpec({ ...spec, is_foreigner: v })}
        label="외국인(유학생)"
      />

      {/* 2026-08-22 — 장애인처럼 누르면 펼쳐지는 방식으로 변경(사용자 요청) — 안의 PillToggle
          구조/크기는 그대로 두고 바깥만 CollapsibleToggle로 감쌈. "펼침" 여부는
          spec.military_status가 null이 아닌지로 판단 — 펼치는 순간 기본값(미필)을 골라주고,
          이미 고른 걸 다시 눌러서 선택 해제하면(아래 PillToggle onChange 참고) null로 돌아가면서
          자연스럽게 다시 접힘. */}
      <CollapsibleToggle
        checked={spec.military_status != null}
        onChange={(v) =>
          setSpec({
            ...spec,
            military_status: v ? "not_served" : null,
            discharge_type: null,
          })
        }
        label="병역"
      >
        {/* 2026-08-21 — 선택 입력으로 바뀌면서, 이미 고른 항목을 다시 누르면 선택이 풀리고
            null(모름)로 돌아가게 함 — 다른 선택 입력들처럼 "고르고 싶지 않으면 안 골라도
            되는" 상태를 표현하기 위함. */}
        <PillToggle
          value={spec.military_status ?? ""}
          onChange={(v) => {
            const next = v === spec.military_status ? null : v;
            setSpec({
              ...spec,
              military_status: next as
                | "completed"
                | "exempted"
                | "not_served"
                | "rotc_candidate"
                | "not_applicable"
                | null,
              // 군필이 아니면 세부구분 자체가 성립 안 하므로 같이 지움(id=652 "10년 이상
              // 장기복무 제대군인 대상"처럼 군필 세부구분이 걸린 장학금 발견 계기, 2026-08-15).
              discharge_type: next === "completed" ? spec.discharge_type : null,
            });
          }}
          options={[
            { value: "not_served", label: "미필" },
            { value: "completed", label: "군필" },
            { value: "exempted", label: "면제" },
            // 2026-08-15 추가 — "학군단(ROTC) 후보생만 대상" 장학금(id=63,212)이 군필/미필/
            // 면제 어디로도 안 걸러져서 추가(군필이면 애초에 ROTC 후보생 신분 자체가 성립 안
            // 하므로 의미상 겹치지 않음). backend/app/models/enums.py의
            // MilitaryStatus.ROTC_CANDIDATE 참고.
            { value: "rotc_candidate", label: "학군단(ROTC)" },
            // 2026-08-21 추가 — 여성 등 위 4종 어디에도 자기 상황이 안 맞는다고 느끼는
            // 사용자를 위한 명시적 선택지(특수상황의 "해당사항 없음"과 같은 패턴). "미필"로
            // 대충 채우게 하지 않고 실제로 구분되는 값으로 저장하되, required_military_status
            // 조건이 있는 장학금은 여전히 정상적으로 걸러짐(이 값은 어떤 required 값과도 안
            // 같으므로) — backend/app/models/enums.py의 MilitaryStatus.NOT_APPLICABLE 참고.
            { value: "not_applicable", label: "해당사항 없음" },
          ]}
        />
        {/* 2026-08-15 추가 — 군필 선택 시에만 이어서 보여주는 세부 구분. "10년 이상 장기복무
            제대군인 대상"(id=652)처럼 병사/장교·부사관 여부가 갈리는 장학금 발견 계기.
            안 고르면 null로 남고(leniency), 이 조건이 걸린 장학금도 안 거름 — 다른 선택
            입력들과 같은 원칙. */}
        {spec.military_status === "completed" && (
          <div className="mt-2">
            <PillToggle
              value={spec.discharge_type ?? ""}
              onChange={(v) => setSpec({ ...spec, discharge_type: v as DischargeType })}
              options={DISCHARGE_TYPE_OPTIONS}
            />
          </div>
        )}
      </CollapsibleToggle>

      {/* 2026-08-22 재구성(사용자 요청) — "입력 중인 한 칸"과 "저장된 목록"을 분리함. 종류+점수를
          고르고 저장을 누르면 그 값이 목록으로 내려가면서 색이 바뀌고(파란 배지), 입력칸은
          다음 시험을 위해 다시 비워짐 — 저장을 안 누르면 그 값은 제출에 안 들어감(저장 버튼
          자체가 "이만큼은 확정했다"는 표시 역할). 저장된 항목은 연필(수정)/×(삭제) 아이콘으로
          다시 손볼 수 있음 — 수정을 누르면 그 값이 다시 입력칸으로 올라오고 목록에서는 빠짐. */}
      <CollapsibleToggle checked={languageTestsOpen} onChange={setLanguageTestsOpen} label="어학점수">
        <div className="flex flex-col gap-3">
          {(() => {
            const draftMax = LANGUAGE_TESTS.find((t) => t.value === languageTestDraft.type)?.max ?? null;
            const draftScoreNum = languageTestDraft.score === "" ? null : Number(languageTestDraft.score);
            // 2026-08-22 추가 — <input max={...}>는 폼을 실제로 제출할 때만 브라우저가
            // 검사해주고, "저장" 버튼 클릭만으로는 그 검증이 안 걸려서 만점을 넘는 값도
            // 그냥 저장돼버리는 문제가 있었음(예: TOEIC 990점 만점에 1000점 입력해도 저장됨).
            // 그래서 여기서 직접 범위를 확인해서 저장 자체를 막음.
            const isOutOfRange =
              draftScoreNum != null && (draftScoreNum < 0 || (draftMax != null && draftScoreNum > draftMax));
            return (
              <>
                <div className="flex gap-2">
                  <div className="flex-[3]">
                    <PlainSelect
                      value={languageTestDraft.type}
                      onChange={(v) => setLanguageTestDraft({ ...languageTestDraft, type: v })}
                      options={LANGUAGE_TESTS.map((t) => ({ value: t.value, label: t.label }))}
                    />
                  </div>
                  <div className="flex-[2]">
                    <input
                      type="number"
                      min={0}
                      max={draftMax ?? undefined}
                      placeholder={draftMax != null ? `점수(만점 ${draftMax})` : "점수"}
                      value={languageTestDraft.score}
                      onChange={(e) => setLanguageTestDraft({ ...languageTestDraft, score: e.target.value })}
                      className={`${inputClass} ${noSpinnerClass} ${isOutOfRange ? "shadow-neu-focus ring-2 ring-red-400" : ""}`}
                    />
                  </div>
                  <button
                    type="button"
                    disabled={draftScoreNum == null || isOutOfRange}
                    onClick={() => {
                      setOptionalInfo({
                        ...optionalInfo,
                        languageTests: [...optionalInfo.languageTests, languageTestDraft],
                      });
                      setLanguageTestDraft({ type: LANGUAGE_TESTS[0].value, score: "" });
                    }}
                    className="shrink-0 rounded-xl bg-blue-500 px-4 text-sm font-semibold text-white shadow-neu-raised-sm transition hover:bg-blue-600 active:shadow-neu-pressed disabled:opacity-40"
                  >
                    저장
                  </button>
                </div>
                {isOutOfRange && (
                  <p className="-mt-1 px-1 text-xs font-semibold text-red-500">
                    {draftMax != null && draftScoreNum != null && draftScoreNum > draftMax
                      ? `만점(${draftMax}점)을 넘었어요`
                      : "0점 이상으로 입력해주세요"}
                  </p>
                )}
              </>
            );
          })()}

          {optionalInfo.languageTests.map((entry, i) => {
            const label = LANGUAGE_TESTS.find((t) => t.value === entry.type)?.label ?? entry.type;
            return (
              <div
                key={i}
                className="flex items-center justify-between rounded-2xl bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700"
              >
                <span>
                  {label} · {entry.score}점
                </span>
                <div className="flex shrink-0 gap-1">
                  <button
                    type="button"
                    aria-label="이 시험 수정"
                    onClick={() => {
                      setLanguageTestDraft(entry);
                      setOptionalInfo({
                        ...optionalInfo,
                        languageTests: optionalInfo.languageTests.filter((_, idx) => idx !== i),
                      });
                    }}
                    className="flex h-7 w-7 items-center justify-center rounded-lg text-blue-400 transition hover:bg-blue-100 hover:text-blue-600"
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    aria-label="이 시험 삭제"
                    onClick={() =>
                      setOptionalInfo({
                        ...optionalInfo,
                        languageTests: optionalInfo.languageTests.filter((_, idx) => idx !== i),
                      })
                    }
                    className="flex h-7 w-7 items-center justify-center rounded-lg text-blue-400 transition hover:bg-red-100 hover:text-red-500"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </CollapsibleToggle>

      {/* 2026-08-22 — 병역과 같은 방식으로 재구성(사용자 요청): 안 건드리면 has_disability가
          null(모름)로 남아 leniency 적용, 패널을 닫으면 골라둔 유형도 같이 지움(특수상황과
          동일 원칙) — 아래 disabilityTypes도 "해당사항 없음"과 상호배타적으로 고를 수 있음. */}
      <CollapsibleToggle
        checked={spec.has_disability === true}
        onChange={(v) => {
          setSpec({ ...spec, has_disability: v ? true : null });
          if (!v) setOptionalInfo({ ...optionalInfo, disabilityTypes: [] });
        }}
        label="장애인"
      >
        {/* 2026-08-21 — 단일 선택(SelectField)에서 특수상황과 같은 복수선택(MultiPillSelect)
            으로 변경(사용자 요청) — 여러 유형이 동시에 해당하는 경우를 표현할 수 있게 함.
            2026-08-22 — "해당사항 없음"을 다른 유형과 상호배타로 추가(특수상황과 동일 패턴,
            applyExclusiveNotApplicable 참고). */}
        <MultiPillSelect
          values={optionalInfo.disabilityTypes}
          onChange={(v) =>
            setOptionalInfo({
              ...optionalInfo,
              disabilityTypes: applyExclusiveNotApplicable(optionalInfo.disabilityTypes, v, DISABILITY_NOT_APPLICABLE),
            })
          }
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
