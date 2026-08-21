// 스펙 입력 위저드(/spec)랑 마이페이지(/mypage) 둘 다 같은 필드 UI를 쓰기 때문에
// 여기 하나로 모아둠 — 스타일(Toss 느낌: 라운드, 옅은 회색 배경, 파란 포인트) 통일 목적.

import Link from "next/link";

// 뉴모피즘: 인풋은 항상 "움푹 들어간" 상태(shadow-neu-inset)로 시작 — 버튼류(튀어나옴)와
// 시각적으로 바로 구분되게. 포커스 시 inset은 유지한 채 얇은 블루 글로우만 덧붙임
// (shadow-neu-focus). 배경은 부모와 거의 같은 neu-surface — 대비가 아니라 그림자로만 구분.
export const inputClass =
  "w-full rounded-2xl bg-neu-surface px-4 py-3.5 text-[15px] text-gray-900 outline-none transition shadow-neu-inset focus:shadow-neu-focus";

// number 인풋의 브라우저 기본 증감 화살표(스피너)를 숨김 — GPA처럼 소수점 값을 직접 타이핑해서
// 넣는 칸에서는 0.01 단위로 눌러 올리는 화살표가 실용성이 없고 자리만 차지한다는 지적(2026-08-22)
// 으로 추가. inputClass와 같이 이어붙여 씀(예: `${inputClass} ${noSpinnerClass}`).
export const noSpinnerClass =
  "[appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none";

export function Field({ label, children }: { label: React.ReactNode; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-gray-700">{label}</span>
      {children}
    </label>
  );
}

// 라벨 없이 셀렉트 하나만 필요할 때(예: 생년월일의 연/월/일처럼 여러 개를 한 줄에 묶어서
// 쓰고, 그 묶음 전체를 감싸는 라벨은 바깥 Field가 따로 담당하는 경우) 쓰는 버전 — SelectField는
// 항상 Field로 감싸서 라벨을 만들기 때문에, 라벨이 중첩되는 걸 피하려고 분리함.
export function PlainSelect({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${inputClass} appearance-none pr-10`}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <svg
        className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
        viewBox="0 0 20 20"
        fill="none"
      >
        <path
          d="M5 7.5L10 12.5L15 7.5"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}

export function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <Field label={label}>
      <PlainSelect value={value} onChange={onChange} options={options} />
    </Field>
  );
}

export function PillToggle({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  // flex-wrap 추가(2026-08-21) — 병역 선택지가 5개로 늘어나면서 좁은 화면에서 한 줄에 다
  // 욱여넣으면 글자가 두 줄로 깨지고 버튼이 지나치게 좁아짐(예: "학군단(ROTC)"). 옵션이
  // 2~4개라 원래도 한 줄에 다 들어가던 기존 화면들(성별, 재학상태 등)은 줄바꿈이 아예
  // 일어나지 않으니 영향 없음 — min-w만큼 자리가 안 나올 때만 다음 줄로 넘어감.
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`min-w-[84px] flex-1 rounded-2xl bg-neu-surface py-3.5 text-sm font-semibold transition active:shadow-neu-pressed ${
            value === opt.value
              ? "shadow-neu-pressed text-blue-600"
              : "text-gray-500 shadow-neu-raised hover:shadow-neu-raised-lg"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export function ToggleChip({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex items-center justify-between rounded-2xl bg-neu-surface px-4 py-3.5 text-sm font-semibold transition ${
        checked ? "shadow-neu-pressed text-blue-600" : "text-gray-600 shadow-neu-raised hover:shadow-neu-raised-lg"
      }`}
    >
      <span>{label}</span>
      <span
        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] transition ${
          checked ? "bg-blue-500 text-white shadow-neu-raised-sm" : "bg-neu-surface text-transparent shadow-neu-inset"
        }`}
      >
        ✓
      </span>
    </button>
  );
}

export function CollapsibleToggle({
  checked,
  onChange,
  label,
  children,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  children?: React.ReactNode;
}) {
  // 2026-08-21 — ToggleChip(체크 표시)을 그대로 재사용했었는데, "누르면 켜짐/꺼짐"인 순수
  // 토글(외국인 등)이랑 "누르면 안에 입력 폼이 펼쳐짐"인 이 컴포넌트가 똑같이 생겨서 학생
  // 입장에서 구분이 안 된다는 디자인 논의 결과 — 화살표(SelectField 등에서 이미 쓰던 것과
  // 같은 아이콘)로 바꿔서 "펼쳐지는 항목"이라는 걸 눈으로 바로 알 수 있게 함. 펼쳐지면
  // 화살표가 180도 돌아서 위를 가리킴(아코디언 관례).
  return (
    <div className="flex flex-col gap-3">
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`flex items-center justify-between rounded-2xl bg-neu-surface px-4 py-3.5 text-sm font-semibold transition ${
          checked ? "shadow-neu-pressed text-blue-600" : "text-gray-600 shadow-neu-raised hover:shadow-neu-raised-lg"
        }`}
      >
        <span>{label}</span>
        <svg
          viewBox="0 0 20 20"
          fill="none"
          className={`h-4 w-4 shrink-0 transition-transform duration-200 ${
            checked ? "rotate-180 text-blue-500" : "text-gray-400"
          }`}
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      {checked && children && (
        <div className="flex flex-col gap-3 rounded-2xl bg-neu-surface p-4 shadow-neu-inset">{children}</div>
      )}
    </div>
  );
}

export function MultiPillSelect({
  values,
  onChange,
  options,
}: {
  values: string[];
  onChange: (v: string[]) => void;
  // highlight: "해당사항 없음"처럼 목록에 묻히면 안 되는 항목에 강조색을 줌(2026-08-22 사용자 요청)
  options: { value: string; label: string; highlight?: boolean }[];
}) {
  function toggle(v: string) {
    onChange(values.includes(v) ? values.filter((x) => x !== v) : [...values, v]);
  }
  const highlighted = options.find((o) => o.highlight);
  const rest = options.filter((o) => !o.highlight);
  const highlightSelected = !!highlighted && values.includes(highlighted.value);
  return (
    <div className="flex flex-col gap-3">
      {highlighted && (
        <>
          <button
            type="button"
            onClick={() => toggle(highlighted.value)}
            className={`w-full rounded-xl px-4 py-2.5 text-center text-sm font-semibold transition ${
              highlightSelected
                ? "bg-neu-surface text-blue-600 shadow-neu-pressed"
                : "bg-neu-surface text-stone-500 shadow-neu-raised-sm hover:shadow-neu-raised"
            }`}
          >
            {highlighted.label}
          </button>
          <div className="flex items-center gap-3 text-xs font-medium text-gray-400">
            <span className="h-px flex-1 bg-gray-200" />
            또는 해당하는 항목 선택
            <span className="h-px flex-1 bg-gray-200" />
          </div>
        </>
      )}
      <div className="flex flex-wrap gap-2">
        {rest.map((opt) => {
          const isSelected = values.includes(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => toggle(opt.value)}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                isSelected
                  ? "bg-neu-surface text-blue-600 shadow-neu-pressed"
                  : "bg-neu-surface text-gray-500 shadow-neu-raised-sm hover:shadow-neu-raised"
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function TopBar({ right }: { right?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <Link href="/home" className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500 text-sm font-bold text-white shadow-neu-raised-sm">
          U
        </div>
        <span className="text-base font-bold text-gray-900">UniSco</span>
      </Link>
      {right}
    </div>
  );
}
