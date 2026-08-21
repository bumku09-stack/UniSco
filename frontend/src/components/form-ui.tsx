// 스펙 입력 위저드(/spec)랑 마이페이지(/mypage) 둘 다 같은 필드 UI를 쓰기 때문에
// 여기 하나로 모아둠 — 스타일(Toss 느낌: 라운드, 옅은 회색 배경, 파란 포인트) 통일 목적.

import Link from "next/link";

// 뉴모피즘: 인풋은 항상 "움푹 들어간" 상태(shadow-neu-inset)로 시작 — 버튼류(튀어나옴)와
// 시각적으로 바로 구분되게. 포커스 시 inset은 유지한 채 얇은 블루 글로우만 덧붙임
// (shadow-neu-focus). 배경은 부모와 거의 같은 neu-surface — 대비가 아니라 그림자로만 구분.
export const inputClass =
  "w-full rounded-2xl bg-neu-surface px-4 py-3.5 text-[15px] text-gray-900 outline-none transition shadow-neu-inset focus:shadow-neu-focus";

export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-gray-700">{label}</span>
      {children}
    </label>
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
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 rounded-2xl bg-neu-surface py-3.5 text-sm font-semibold transition active:shadow-neu-pressed ${
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
  return (
    <div className="flex flex-col gap-3">
      <ToggleChip checked={checked} onChange={onChange} label={label} />
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
  options: { value: string; label: string }[];
}) {
  function toggle(v: string) {
    onChange(values.includes(v) ? values.filter((x) => x !== v) : [...values, v]);
  }
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => toggle(opt.value)}
          className={`rounded-full bg-neu-surface px-4 py-2 text-sm font-semibold transition ${
            values.includes(opt.value)
              ? "shadow-neu-pressed text-blue-600"
              : "text-gray-500 shadow-neu-raised-sm hover:shadow-neu-raised"
          }`}
        >
          {opt.label}
        </button>
      ))}
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
