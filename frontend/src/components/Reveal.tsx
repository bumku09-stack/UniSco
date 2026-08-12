"use client";

import { useEffect, useRef, useState } from "react";

// 스크롤로 뷰포트에 들어오면 한 번만 서서히 나타남 — IntersectionObserver가 감지하는 즉시
// unobserve해서, 위아래로 스크롤을 왔다갔다 해도 다시 사라졌다 나타나지 않음(랜딩 페이지
// 전용, 결과 리스트 등 반복 렌더링되는 곳엔 안 씀).
export function Reveal({
  children,
  className = "",
  delayMs = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delayMs?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
      className={`transition-all duration-700 ease-out ${
        visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      } ${className}`}
    >
      {children}
    </div>
  );
}
