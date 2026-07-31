# frontend/

Next.js (App Router) + React + TypeScript + Tailwind CSS. 회원가입/이메일인증/로그인부터 스펙 입력 → 추천 → 상세, 마이페이지까지 실제 백엔드 API에 붙어서 동작함. 디자인은 Toss 스타일(블루 포인트 컬러, 라운드 카드, 필 토글)로 되어 있음.

## 코드 구조

```
src/
├── app/
│   ├── layout.tsx      # 루트 레이아웃 — 모든 페이지를 감싸는 껍데기, 폰트 설정 + <html>/<body>
│   ├── page.tsx         # "/" 라우트 — 로그인. POST /auth/login → 토큰 저장 → 스펙 있으면 /home, 없으면 /spec
│   ├── globals.css      # Tailwind 진입점 + 전역 스타일
│   ├── signup/
│   │   └── page.tsx     # "/signup" — 회원가입 폼 → 이메일 인증 코드 입력 (내부 2단계), 완료되면 "/"로 이동
│   ├── spec/
│   │   └── page.tsx     # "/spec" — 최초 스펙 입력 2단계 위저드. POST /users/me/spec 성공 시 /home으로 이동
│   ├── home/
│   │   └── page.tsx     # "/home" — 로그인 유저의 추천 목록(GET /scholarships/recommendations). 정렬/카테고리 필터/페이지네이션 + 마이페이지·로그아웃 버튼
│   ├── mypage/
│   │   └── page.tsx     # "/mypage" — 저장된 스펙 조회(GET)·수정(PUT). 단일 폼(위저드 아님)
│   └── scholarship/[id]/
│       └── page.tsx     # 상세 페이지 — 자격조건 체크리스트, 비슷한 장학금 추천, 신청 링크
├── components/
│   └── form-ui.tsx      # Field/SelectField/PillToggle/ToggleChip/TopBar — /spec, /mypage가 공유하는 필드 UI
└── lib/
    ├── auth.ts           # 토큰 저장(localStorage) + authFetch(Authorization 헤더 자동 첨부, 401이면 로그인으로 리다이렉트)
    ├── spec.ts            # UserSpec/SpecForm 타입, specFormToUserSpec/userSpecToSpecForm 변환
    ├── scholarship.ts     # Scholarship 타입, 정렬/분류/유사추천 헬퍼
    ├── regions.ts         # 광역/기초자치단체 목록(SIDO_LIST) + 지역 표기 축약·역변환 헬퍼
    └── universities.ts    # 대학별 단과대 목록 + 학점 만점 기준(gpaScale)
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

## 로그인 후 플로우는 어디에

`/` → `/spec`(최초 1회) → `/home` → 필요하면 `/mypage`.

- 토큰은 `localStorage`에 저장(`lib/auth.ts`) — 아직 진짜 세션/쿠키가 아니라 access token 30분 만료되면 그냥 다시 로그인해야 함(리프레시 자동 재시도 없음, 단순함 우선).
- `authFetch()`가 모든 인증 필요 요청에 `Authorization: Bearer <token>`을 붙이고, 401 받으면 토큰 지우고 `/`로 보냄 — 각 페이지가 개별적으로 401 처리 안 해도 됨.
- `/home`은 페이지 진입할 때마다 `GET /users/me/spec-status`를 먼저 확인함 — 스펙이 없으면(예: DB에서 직접 지운 경우 등) `/spec`으로 돌려보냄.
- `/mypage`는 `GET /users/me/spec`으로 현재 값을 불러와 폼에 채우고, 저장은 `PUT`. `region`은 짧은 시/도 단위로만 저장돼 있어서(구/군 정보 없음) 되돌릴 때 시/도까지만 정확히 복원되고 구/군은 그 시/도의 첫 값으로 기본 설정됨 — 애초에 매칭에 구/군 단위까지는 안 쓰여서 문제없음.

## 남은 것 (2026-07-31 기준)

- 리프레시 토큰으로 조용히 재로그인하는 로직 없음 — access token 만료되면 다음 `authFetch` 호출에서 401 → 강제 로그인 화면 이동.
- 회원가입 시 이메일 인증 코드 발송은 백엔드가 Resend를 통해 보내는데, Railway `RESEND_API_KEY`가 아직 실제 값으로 안 채워져 있으면 회원가입 자체가 이메일 발송 단계(502)에서 막힘 — `backend/README.md` "이메일 발송" 참고.
- 브라우저로 직접 클릭해보며 하는 E2E 테스트는 아직 안 함(이 환경엔 브라우저 자동화 도구가 없음) — `next build`/`tsc`/`eslint` 통과, 그리고 Node로 백엔드 API 실제 호출 순서(로그인→스펙저장→추천→수정)까지는 검증했지만, 실제 브라우저에서 폼 입력/클릭까지 확인한 건 아님.
