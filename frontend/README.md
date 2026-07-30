# frontend/

Next.js (App Router) + React + TypeScript + Tailwind CSS. `create-next-app`으로 스캐폴딩 후 로그인 화면 + 2단계 스펙 입력 위저드 + 매칭 결과 화면까지 구현됨. 디자인은 Toss 스타일(블루 포인트 컬러, 라운드 카드, 필 토글)로 되어 있음.

## 코드 구조

```
src/
├── app/
│   ├── layout.tsx      # 루트 레이아웃 — 모든 페이지를 감싸는 껍데기, 폰트 설정 + <html>/<body>
│   ├── page.tsx         # "/" 라우트 — 로그인 화면 (실제 인증 연동 전, 제출하면 /spec으로 이동)
│   ├── globals.css      # Tailwind 진입점 + 전역 스타일
│   └── spec/
│       └── page.tsx     # "/spec" 라우트 — 2단계 스펙 입력 위저드 + 매칭 결과 리스트(15개씩 페이지네이션)
└── lib/
    ├── regions.ts        # 광역/기초자치단체 목록(SIDO_LIST) + 지역 표기 축약 헬퍼
    └── universities.ts   # 대학별 단과대 목록 + 학점 만점 기준(gpaScale)
```

### Next.js App Router 동작 방식 (처음이라면)

- **파일시스템 기반 라우팅**: `src/app/` 아래 폴더 하나가 URL 경로 하나가 되고, 그 안의 `page.tsx`가 해당 경로에서 렌더링됨. 예: `src/app/results/page.tsx`를 만들면 `/results` 페이지가 됨. 따로 라우터 설정 파일을 관리할 필요 없음.
- **`layout.tsx`**: 여러 페이지에서 공유하는 UI 껍데기 (내비게이션 바, 폰트, `<html>` 태그 등). 페이지 이동해도 다시 렌더링 안 되고 유지됨.
- **컴포넌트**: React 컴포넌트는 그냥 JSX(TypeScript/JS 안에 HTML처럼 생긴 문법)를 반환하는 함수임 — 실제로 어떻게 생겼는지는 `page.tsx` 보면 됨. 프로젝트 커지면 거대한 `page.tsx` 하나 대신 작은 컴포넌트로 쪼개서 짜면 됨.
- 스타일링은 Tailwind CSS — 별도 CSS 파일 대신 JSX의 `className`에 유틸리티 클래스를 바로 씀 (예: `className="flex items-center gap-4"`).

## 로컬 셋업

```bash
npm install                    # 스캐폴딩할 때 이미 한 번 실행됨
cp .env.example .env.local
npm run dev                    # http://localhost:3000
```

`.env.local`의 `NEXT_PUBLIC_API_URL`은 백엔드를 가리켜야 함 (로컬에서는 `http://localhost:8000`) — `NEXT_PUBLIC_` 접두사가 붙은 건 브라우저 코드에 노출되는데, 프론트가 호출할 API 주소는 노출돼야 하니 딱 맞음.

## 실제 UI는 어디에

`app/page.tsx`(로그인) → `app/spec/page.tsx`(스펙 위저드). 핵심 플로우: 1단계(대학/단과대/재학상태/학년·과정/학점) → 2단계(나이/성별/지역/병역/소득분위/장애·외국인 여부) 입력 후 `POST /match` → 매칭된 장학금을 카드 리스트로, 15개 넘으면 하단 숫자 페이지네이션으로 표시. 스펙 값은 로그인이 아직 없어서 `localStorage`에 저장해뒀다가 다음 방문 때 불러옴(실제 인증 붙으면 서버 저장으로 교체 예정).

## 남은 것 (2026-07-30 기준)

- 실제 로그인 연동 안 됨 — 인증 방식(Supabase Auth 등)은 동업자와 논의 중, 지금은 UI만 있고 제출하면 그냥 `/spec`으로 넘어감.
- 장학금 상세 페이지 없음 — 카드 클릭해서 들어가는 상세 화면은 아직 미구현.
