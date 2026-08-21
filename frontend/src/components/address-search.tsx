"use client";

import { useState } from "react";
import { Field, inputClass } from "@/components/form-ui";
import { resolveSidoFromDaumAddress } from "@/lib/regions";

// 2026-08-21 추가 — 거주지역을 시/도·시/군/구 드롭다운 대신 실제 주소 검색(다음 우편번호
// 서비스)으로 받기 위한 컴포넌트. 검색 결과는 매칭 로직이 이해하는 기존 모양(SIDO_LIST의
// 정식 명칭 sido + 구/군 원문 district)으로 변환해서 돌려주므로, 이 컴포넌트를 쓰는 쪽
// (spec-fields.tsx)이나 matching.py는 전혀 안 바뀜 — resolveSidoFromDaumAddress() 참고.

type DaumPostcodeData = {
  sido: string;
  sigungu: string;
  roadAddress: string;
  jibunAddress: string;
};

declare global {
  interface Window {
    daum?: {
      Postcode: new (options: {
        oncomplete: (data: DaumPostcodeData) => void;
      }) => { open: () => void };
    };
  }
}

const DAUM_POSTCODE_SRC = "https://t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js";

// 스크립트는 페이지에서 처음 검색 버튼을 누를 때만 로드하고(안 쓰면 안 받아옴), 여러 번
// 눌러도 한 번만 추가되게 모듈 스코프에 프로미스를 캐시해둠.
let daumScriptPromise: Promise<void> | null = null;

function loadDaumPostcodeScript(): Promise<void> {
  if (typeof window !== "undefined" && window.daum?.Postcode) return Promise.resolve();
  if (!daumScriptPromise) {
    daumScriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = DAUM_POSTCODE_SRC;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("주소 검색 스크립트를 불러오지 못했습니다."));
      document.head.appendChild(script);
    });
  }
  return daumScriptPromise;
}

export function AddressSearchField({
  label,
  sido,
  district,
  address,
  onChange,
  required,
  error,
}: {
  label: string;
  sido: string;
  district: string;
  address: string;
  onChange: (next: { sido: string; district: string; address: string }) => void;
  required?: boolean;
  error?: string;
}) {
  const [loadError, setLoadError] = useState(false);

  async function handleSearch() {
    setLoadError(false);
    try {
      await loadDaumPostcodeScript();
    } catch {
      setLoadError(true);
      return;
    }
    if (!window.daum?.Postcode) {
      setLoadError(true);
      return;
    }
    new window.daum.Postcode({
      oncomplete: (data) => {
        onChange({
          sido: resolveSidoFromDaumAddress(data.sido),
          district: data.sigungu,
          address: data.roadAddress || data.jibunAddress,
        });
      },
    }).open();
  }

  return (
    <Field label={label}>
      <div className="flex gap-2">
        <input
          type="text"
          readOnly
          required={required}
          value={address}
          placeholder="주소 검색을 눌러주세요"
          onClick={handleSearch}
          className={`${inputClass} cursor-pointer ${error ? "shadow-neu-focus ring-2 ring-red-400" : ""}`}
        />
        <button
          type="button"
          onClick={handleSearch}
          className="shrink-0 rounded-2xl bg-neu-surface px-4 text-sm font-semibold text-gray-600 shadow-neu-raised transition hover:shadow-neu-raised-lg active:shadow-neu-pressed"
        >
          주소 검색
        </button>
      </div>
      {address && (
        <p className="px-1 text-xs text-gray-400">
          {sido} {district}(으)로 인식했어요
        </p>
      )}
      {loadError && (
        <p className="px-1 text-xs font-semibold text-red-500">
          주소 검색을 불러오지 못했어요. 인터넷 연결을 확인하고 다시 시도해주세요.
        </p>
      )}
      {!loadError && error && <p className="px-1 text-xs font-semibold text-red-500">{error}</p>}
    </Field>
  );
}
