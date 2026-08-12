# frontend/

Next.js (App Router) + React + TypeScript + Tailwind CSS. 회원가입/이메일인증/로그인부터 스펙 입력 → 추천 → 상세, 마이페이지까지 실제 백엔드 API에 붙어서 동작함. 디자인은 Toss 스타일(블루 포인트 컬러, 라운드 카드, 필 토글)로 되어 있음.

## 코드 구조

```
src/
├── app/
│   ├── layout.tsx      # 루트 레이아웃 — 모든 페이지를 감싸는 껍데기, 폰트 설정 + <html>/<body>
│   ├── error.tsx        # 라우트 세그먼트 렌더링 중 예외 발생 시 대체 화면("다시 시도" 버튼) — 2026-08-13 추가, 이전엔 Next.js 기본 에러 화면만 떴음
│   ├── global-error.tsx # 루트 layout.tsx 자체가 실패하는 극단적 경우용(자체 <html>/<body> 필요) — 2026-08-13 추가
│   ├── not-found.tsx    # 존재하지 않는 경로 진입 시 대체 화면 — 2026-08-13 추가
│   ├── page.tsx         # "/" 라우트 — 랜딩/선택 화면(2026-08-10 개편, 예전엔 로그인 폼이었음). "지금 바로 둘러보기" → /spec(게스트), "로그인" → /login
│   ├── globals.css      # Tailwind 진입점 + 전역 스타일
│   ├── login/
│   │   └── page.tsx     # "/login" — 로그인 폼(예전 "/" 내용 그대로 이동). POST /auth/login → 토큰 저장 → 스펙 있으면 /home, 없으면 /spec
│   ├── signup/
│   │   └── page.tsx     # "/signup" — 회원가입 폼 → 이메일 인증 코드 입력 (내부 2단계), 완료되면 "/login"으로 이동
│   ├── forgot-password/
│   │   └── page.tsx     # "/forgot-password" — 이메일로 재설정 코드 받기 → 새 비밀번호 설정 (내부 2단계)
│   ├── spec/
│   │   └── page.tsx     # "/spec" — 듀얼 모드(2026-08-10). 비로그인=게스트 2단계(학교+공통 정보) → POST /match, 로그인=기존 3단계 → POST /users/me/spec. 아래 "게스트 플로우" 참고
│   ├── home/
│   │   └── page.tsx     # "/home" — 듀얼 모드. 로그인=GET /scholarships/recommendations, 게스트=세션에 저장된 POST /match 결과. 목록 UI 자체는 components/ScholarshipResults.tsx 공유
│   ├── mypage/
│   │   └── page.tsx     # "/mypage" — 저장된 스펙 조회(GET)·수정(PUT), 회원탈퇴(DELETE). 단일 폼(위저드 아님). 로그인 전용(게스트 모드 없음)
│   ├── saved/
│   │   └── page.tsx     # "/saved" — 찜한 장학금 목록(GET /users/me/saved-scholarships). 로그인 전용
│   └── scholarship/[id]/
│       └── page.tsx     # 상세 페이지 — 자격조건 체크리스트, 비슷한 장학금 추천(로그인 전용, 게스트는 스킵), 찜하기(로그인 전용), 신청 링크. 본문 자체는 게스트도 열람 가능
├── components/
│   ├── form-ui.tsx           # Field/SelectField/PillToggle/ToggleChip/CollapsibleToggle/MultiPillSelect/TopBar — 기본 입력 UI 조각
│   ├── spec-fields.tsx       # SchoolFields/CommonFields/OptionalFields — /spec, /mypage가 그대로 공유하는 필드 묶음(2026-08-04 추출, 아래 참고)
│   └── ScholarshipResults.tsx # 통계·분류필터·정렬·카드·페이지네이션 — /home이 로그인/게스트 두 모드에서 공유(2026-08-10 추출)
└── lib/
    ├── auth.ts           # 토큰 저장(localStorage) + authFetch(401이면 refresh 토큰으로 조용히 재시도, 그것도 실패하면 로그아웃) + postJson(로그인 전 페이지용) + apiUrl(NEXT_PUBLIC_API_URL 미설정 시 방어, 2026-08-13 추가 — 모든 API 호출이 이걸 거침)
    ├── guest.ts           # 게스트 스펙·매칭 결과 sessionStorage 저장소(2026-08-10 추가) — 서버에 원본이 없는 유일한 사본
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

`/login` → `/spec`(최초 1회, 3단계) → `/home` → 필요하면 `/mypage`.

- 토큰은 `localStorage`에 저장(`lib/auth.ts`). `authFetch()`가 모든 인증 필요 요청에 `Authorization: Bearer <token>`을 붙이고, access token(30분) 만료로 401이 오면 refresh token으로 한 번 조용히 재발급받아 원 요청을 재시도함(2026-08-07 추가) — 그것도 실패하면(refresh token도 만료/없음) 그때만 토큰 지우고 `/`로 보냄. 처음부터 토큰이 없었던 요청(게스트)은 이 로그아웃 처리를 안 함 — 아래 "게스트 플로우" 참고.
- `/home`은 페이지 진입할 때마다 `GET /users/me/spec-status`를 먼저 확인함 — 스펙이 없으면(예: DB에서 직접 지운 경우 등) `/spec`으로 돌려보냄.
- `/mypage`는 `GET /users/me/spec`으로 현재 값을 불러와 폼에 채우고, 저장은 `PUT`. `region`은 짧은 시/도 단위로만 저장돼 있어서(구/군 정보 없음) 되돌릴 때 시/도까지만 정확히 복원되고 구/군은 그 시/도의 첫 값으로 기본 설정됨 — 애초에 매칭에 구/군 단위까지는 안 쓰여서 문제없음.

## 게스트 플로우 — 로그인 없이 둘러보기 (2026-08-10 추가)

"일단 가볍게 써보고 싶은 사람"을 위해 계정 없이도 매칭 결과를 볼 수 있게 함. 새 라우트를
따로 안 만들고 기존 `/spec`·`/home`을 로그인 여부에 따라 다르게 동작하는 듀얼 모드로 만듦.

- `/`(랜딩) → "지금 바로 장학금 둘러보기" → `/spec`. 비로그인 상태라 자동으로 **게스트 모드**
  (2단계만: 학교 정보 + 공통 정보 — 기존 위저드의 1·2단계와 동일한 컴포넌트를 그대로 씀, 3단계
  선택 정보는 아예 안 보여줌).
- 2단계 제출 시 `POST /users/me/spec`(로그인 필요) 대신 `POST /match`(로그인 불필요, 아무것도
  저장 안 하고 그 자리에서 채점만)로 보냄. 응답 결과와 입력했던 스펙을 `lib/guest.ts`로
  `sessionStorage`에 저장하고 `/home`으로 이동.
- `/home`은 비로그인이면 `sessionStorage`에 저장된 게스트 결과를 보여줌(서버에서 다시 안
  받아옴 — 게스트는 애초에 서버에 저장된 게 없음). 결과 화면엔 "더 정확한 매칭을 원하시나요?"
  배너로 `/signup` 전환을 유도함.
- 회원가입 완료 후 `/login`으로 로그인하면(로그인 응답의 `spec_completed=false`라서) `/spec`으로
  자동 이동하는데, 이때 `/spec`은 로그인 상태라 3단계 모드로 동작하면서 `lib/guest.ts`에 남아있는
  게스트 스펙을 찾아서 1·2단계를 미리 채우고 **3단계(선택 정보)부터 이어서** 보여줌 — 이미 입력한
  학교·공통 정보를 다시 안 치게 함. 3단계까지 실제로 저장(`POST /users/me/spec`)되면 게스트
  데이터는 지움(`clearGuestData()`).
- 상세페이지(`/scholarship/[id]`)는 본문(`GET /scholarships/{id}`)은 원래도 로그인 불필요라
  게스트도 그대로 열람 가능. 다만 "이런 장학금은 어때요?"(`GET /scholarships/{id}/similar`)는
  로그인 필요(저장된 스펙 기준으로 고르는 API라 게스트는 기준이 없음) — 게스트면 아예 이
  요청을 안 보냄(`isLoggedIn()` 가드).
- `authFetch()`는 처음부터 토큰이 없었던 요청이 401을 맞아도 로그아웃 리다이렉트를 안 함(위
  "로그인 후 플로우" 참고) — 게스트가 보는 페이지가 배경에서 인증 필요한 API를 불렀다가
  튕겨나가는 일이 없게 하는 안전장치. 그래도 애초에 게스트 페이지에서 인증 필요한 API는
  안 부르는 쪽이 기본(위 상세페이지 예시처럼).

## /spec과 /mypage는 필드를 항상 같이 맞출 것 (2026-08-02 추가, 2026-08-04 컴포넌트 공유로 갱신)

`/spec`(최초 입력 위저드)과 `/mypage`(수정 폼)는 같은 스펙을 다루는 서로 다른 화면임. 처음엔 두 페이지 각자에 거의 동일한 필드 JSX를 그대로 복붙해 넣었었는데(university/college/department 캐스케이딩 select, 학년/GPA, 나이·성별·지역·병역·소득분위·외국인, 어학점수·장애·특수상황 — 세 그룹), 필드가 하나 늘어날 때마다 두 파일을 동시에 고쳐야 하고 실수로 한쪽만 고치기 쉬웠음.

그래서 그 세 그룹을 `components/spec-fields.tsx`의 `SchoolFields`/`CommonFields`/`OptionalFields`(+ 파생값 계산용 `deriveSpecFields`)로 뽑아냈고, 이제 `/spec`과 `/mypage`는 둘 다 이 세 컴포넌트를 그대로 렌더링만 함. **필드를 추가/변경할 땐 `spec-fields.tsx` 한 곳만 고치면 두 페이지 모두에 반영됨** — `lib/spec.ts`의 `SpecForm`/`OptionalInfo` 타입에 필드를 추가하는 것만 별도로 필요.

두 페이지가 다른 부분(위저드 단계 구분, 신입생 안내 문구 `showFreshmanHint`, `/mypage`의 draft 자동저장·복원 배너 등)은 각 `page.tsx`에 그대로 남아있음 — 공유되는 건 순수 필드 편집 UI뿐임.

## 남은 것 (2026-08-13 기준)

- 브라우저로 직접 클릭해보며 하는 E2E 테스트는 여전히 없음(이 환경엔 브라우저 자동화 도구가 없음) — `next build`/`tsc`/`eslint` 통과까지는 매번 확인하지만, 실제 브라우저에서 폼 입력/클릭까지 확인한 기능이 아직 많음 — 새 화면 추가할 때마다 실제 브라우저로 한 번씩 눌러보고 확인 권장.
- **JWT를 `localStorage`에 평문 저장 중** — 배포 전 점검(2026-08-13)에서 나온 가장 큰 보안 갭. 정석 해결책은 백엔드가 `httpOnly` 쿠키로 토큰을 내려주는 방식으로 전환하는 것인데, 프론트(Vercel)와 백엔드(Railway)가 서로 다른 도메인이라 `SameSite=None` 크로스사이트 쿠키가 필요하고, Safari 등 일부 브라우저의 서드파티 쿠키 차단 정책에 걸려 로그인이 깨질 위험이 있음 — 백엔드(`backend/app/api/auth.py`, `backend/app/api/deps.py`) 변경까지 같이 필요한 작업이라 이번엔 손 안 대고 남겨둠. 진행하려면 같은 도메인으로 묶는 Vercel rewrite/프록시 구성까지 같이 설계할 것.
- 게스트 회원가입 전환 시 로그인까지는 여전히 수동임(자동 로그인 없음) — `/signup` 인증 완료 후 `/login`으로 보내고 직접 로그인해야 `/spec`에 게스트 데이터가 이어짐. 전환 단계를 더 줄이고 싶으면 인증 성공 시 자동 로그인을 추가하는 걸 고려할 것(지금은 로그인/회원가입 로직을 분리해두려고 일부러 그대로 둠).
- 실사용자 UX 리서치(5~6명)에서 나온 피드백 기반 개선이 진행형 — 매칭 정확도 이슈(마감일·전공 조건 등)가 우선순위. 루트 `README.md`의 "개발 방향 / 예정" 참고.

## 배포 전 프론트 하드닝 (2026-08-13)

첫 실사용자 배포를 앞두고 프론트 코드를 감사해서 나온 블로커 5개를 고침 — 상세 내역은 커밋 메시지 참고, 요약만 남김:

- 에러 바운더리 부재 → `error.tsx`/`global-error.tsx`/`not-found.tsx` 신설
- `home`/`saved`/`mypage` 진입 시 네트워크 자체가 끊기면(서버 다운 등) `authFetch`가 reject하는데 try/catch가 없어서 로딩 스피너가 무한정 안 멈췄음 → 세 곳 다 try/catch 추가
- `<html lang="en">`(전체가 한국어 서비스인데) → `lang="ko"`
- `NEXT_PUBLIC_API_URL` 미설정 시 방어 없이 `undefined/...` 요청이 조용히 나가던 것 → `lib/auth.ts`의 `apiUrl()`로 통일, 없으면 즉시 에러
- 모든 페이지가 `max-w-md`(448px) 고정 폭이라 PC 화면에서 좌우 여백만 큰 좁은 카드로 보이던 것 → 브레이크포인트별 폭 확장(`sm/md/lg`), 장학금 카드 목록(`home`/`saved`)은 `md` 이상에서 2열 그리드로 전환

남은 블로커는 위 "JWT를 localStorage에 평문 저장 중" 항목 하나뿐.
