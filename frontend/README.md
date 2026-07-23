# frontend/

Next.js (App Router) + React + TypeScript + Tailwind CSS. `create-next-app`으로 스캐폴딩함, 아직은 대부분 기본 템플릿 그대로 — 스펙 입력 폼과 결과 리스트가 여기 만들어질 예정.

## 코드 구조

```
src/app/
├── layout.tsx      # 루트 레이아웃 — 모든 페이지를 감싸는 껍데기, 지금은 폰트 설정 + <html>/<body>만
├── page.tsx        # "/" 라우트 — 지금은 create-next-app 기본 플레이스홀더 페이지
└── globals.css      # Tailwind 진입점 + 전역 스타일
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

아직 안 만듦. 브리프 기준 핵심 플로우는: 한 번 입력하는 스펙 폼(학년, 전공, 소득분위, 지역 등) → 백엔드 매칭 엔드포인트로 `POST` → 맞춤형 장학금 리스트 렌더링. 루트 [README.md](../README.md) "다음 단계" 참고.
