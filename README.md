# UniSco

Unisco — 대전 지역 대학생을 위한 맞춤형 장학금·지원금 매칭 서비스.

배경, 스코프, 왜 이렇게 결정했는지는 [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) 참고.

## 배포 주소 (2026-08-15 기준)

- **서비스(프론트)**: https://unisco-pi.vercel.app — Vercel, `main` 브랜치 푸시할 때마다 자동 재배포
- **API(백엔드)**: https://unisco-production.up.railway.app — Railway, `main` 브랜치 푸시할 때마다 자동 재배포
- **DB**: Supabase 프로젝트 `unisco` (Studio 접근은 `supabase/README.md` 참고)
- **데이터 자동 수집**: GitHub Actions가 매일 새벽 2시(KST) `harness/`를 돌려서 신규 장학금 초안 PR을 엶(머지는 사람이 직접). `harness/README.md` 참고.
- **데이터 재검증**: 이미 들어간 데이터의 근거를 다시 확인하는 `harness/reverify.py`도 있음(2026-08-15 추가, 수동 트리거). 최근 실행에서 충남대 배치 72건의 근거 없는 값을 찾아냄 — `harness/README.md`의 "재검증" 참고.

배포 설정(환경변수, Root Directory 등)은 Railway/Vercel 대시보드에만 있고 git엔 안 잡힘 — 새로 참여하는 사람은 각 서비스 대시보드에서 직접 확인해야 함.

## 스택

- **백엔드**: FastAPI (Python 3.13) + SQLModel
- **프론트엔드**: Next.js (App Router) + React + TypeScript + Tailwind CSS
- **데이터베이스**: PostgreSQL (Supabase — 호스팅형, 비개발자용 데이터 입력을 위한 스프레드시트 같은 Studio UI 포함)
- **데이터 수집 하네스**: Anthropic Claude API(추출) + Playwright(크롤링), GitHub Actions에서 나이트런으로 독립 실행 — 앱 코드/운영 DB 쓰기 권한과 분리돼 있고, 산출물은 항상 PR

## 프로젝트 구조

네 부분으로 나뉩니다. 각 폴더에 코드 설명과 셋업 방법이 담긴 README가 따로 있고, 이 파일은 전체 방향만 잡아줍니다.

```
UniSco/
├── backend/    # FastAPI 앱 — 매칭 로직, DB 통신. backend/README.md 참고
├── frontend/   # Next.js 앱 — 스펙 입력 폼 + 결과 UI. frontend/README.md 참고
├── harness/    # 장학금 자동 수집·추출·검증 파이프라인 (GitHub Actions 나이트런). harness/README.md 참고
└── supabase/   # 호스팅형 Postgres DB + Studio (친구용 데이터 입력 화면). supabase/README.md 참고
```

- [backend/README.md](./backend/README.md) — FastAPI 코드 구조, 로컬 셋업, 린트
- [frontend/README.md](./frontend/README.md) — Next.js/React 코드 구조, 로컬 셋업
- [harness/README.md](./harness/README.md) — 자동 수집 파이프라인 구조, 대학 온보딩 방법, 알려진 한계
- [supabase/README.md](./supabase/README.md) — 호스팅 DB가 뭔지, 친구가 Studio로 데이터 입력하는 방법
- [supabase/data_collection_guide.md](./supabase/data_collection_guide.md) — 조사/입력할 때 자주 놓치는 항목 체크리스트, 특수상황 태그 전체 목록
- [supabase/handoff_2026-08-12.md](./supabase/handoff_2026-08-12.md) — 데이터 작업 인수인계: 지금 이어서 할 것, 보류된 것, 정기적으로 돌려야 하는 감사 스크립트 목록

## 빠른 시작

```bash
# 백엔드
cd backend && source venv/bin/activate && uvicorn app.main:app --reload   # http://localhost:8000

# 프론트엔드 (별도 터미널)
cd frontend && npm run dev                                                # http://localhost:3000
```

최초 셋업(venv 생성, `pip install`, `.env` 파일 등)은 각 폴더 README에 있습니다.

## 진행 상황 (2026-08-15 기준)

**v1 기능은 사실상 다 완성돼서 지금은 실사용자 피드백(에타 등으로 소규모 배포, 5~6명 UX 리서치 완료) 기반 개선 단계로 넘어감.**

1. ~~**Supabase 프로젝트 생성 / 데이터 모델 정의**~~ — 완료. `Scholarship`(자격조건 필드 + `category_l1`/`category_l2` 분류), `UserSpec`/`SavedSpec`, `User`, 관련 enum 전부 `backend/app/models/`에 있음.
2. **장학금 데이터 입력** — 계속 진행 중(현재 659건, 대전권 9개 대학 + KAIST 온보딩 — 이 중 7개교는 `harness/sites.py`로 자동 수집, 나머지(대전대·을지대·한국침례신학대)는 수동 크롤링). 사람이 손으로 하던 조사를 `harness/`(Claude API 기반 자동 수집·추출·검증 파이프라인, GitHub Actions 나이트런)가 상당 부분 대체하는 중 — 최종 반영은 여전히 사람이 PR 리뷰 후 머지. 남은 대학 온보딩, 지자체/재단 등 외부 장학금 발굴은 계속 진행. **데이터 정확도 자체도 계속 문제**: 출처 없이 들어간 값이 종종 발견됨(2026-08-15, 근거 없는 CNU 배치 72건을 `harness/reverify.py`로 잡아냄 + 출처 확인이 안 되는 장학금 3건 삭제) — 상세는 `supabase/data_collection_guide.md`, `EXTERNAL_SCHOLARSHIPS_PLAN.md`, `harness/README.md` 참고.
3. ~~**매칭 엔드포인트**~~ — 완료. `GET /scholarships`, `GET /scholarships/recommendations`(로그인 유저), `POST /match`(비로그인 게스트, 즉석 채점만) (`backend/app/api/`). 규칙 기반, ML 없음.
4. ~~**프론트엔드 스펙 입력 폼 + 결과 리스트**~~ — 완료. 로그인 → 3단계 스펙 위저드 → 매칭 결과(카드+페이지네이션, "매칭적합도순" 정렬). 비로그인 게스트도 2단계 간이 위저드로 결과를 볼 수 있음("일단 둘러보기" → 나중에 회원가입 전환). Toss 스타일 UI. `frontend/README.md` 참고.
5. ~~**실제 로그인 연동**~~ — 완료. 회원가입(이메일 인증)/로그인/비밀번호 재설정/회원탈퇴/스펙 저장·수정(마이페이지)까지 프론트-백엔드 전체 연결됨. access token 만료 시 조용한 refresh, 인증 관련 엔드포인트(재발송/비밀번호 찾기) rate limit 적용됨.
6. ~~**장학금 상세 페이지 + 찜하기**~~ — 완료. `/scholarship/[id]` — 자격조건 체크리스트, 비슷한 장학금 추천, 신청 링크, 저장("찜")/`/saved`에서 모아보기. "신청하러 가기" 버튼이 실제로는 학교 안내 목록 페이지로만 연결되는 경우(자동선발형, 또는 그 URL 자체가 신청 폼이 아닌 단순 안내 목록인 경우) 안내 문구를 조건부로 얹음(`isAutoSelected`/`isListingOnlyUrl`, `frontend/src/lib/scholarship.ts`).
7. **마이그레이션 도구화** — 아직 안 함. 스키마가 계속 바뀌는 중이라 지금은 `SQLModel.metadata.create_all()` + 수동 `ALTER TABLE`로 운영, 변경 빈도가 줄어들면 Alembic 등 도입 검토.
8. ~~**배포 전 프론트 하드닝**~~ — 완료(2026-08-13). 에러 바운더리 부재, 네트워크 실패 시 무한로딩(`home`/`saved`/`mypage`), `<html lang="en">` 오류, `NEXT_PUBLIC_API_URL` 미설정 방어 없음, PC 화면 반응형 레이아웃 부재 — 5개 블로커 수정. 상세는 `frontend/README.md`의 "배포 전 프론트 하드닝" 참고. JWT `localStorage` 평문 저장 문제만 백엔드 동반 작업 필요해서 남겨둠(아래 "개발 방향" 참고).

## 개발 방향 / 예정 (2026-08-15 기준)

**지금 우선순위는 새 기능보다 "이미 있는 매칭이 정확한가"에 있음** — 실사용자 소수 테스트에서 나온 두 가지 실제 버그(마감 지난 장학금 계속 노출, 무관한 전공에 특기자 장학금 노출)를 8월 초에 고쳤고, 이런 종류의 매칭 정확도 문제를 계속 찾아 고치는 게 사업화 전 단계의 핵심 작업으로 판단하고 있음. 특이 케이스가 나올 때마다 자격조건 필드를 세분화하는 것도 같은 맥락 — 예: "군필"만으로는 못 걸러지는 병사/장교·부사관 전역 구분 조건(id=652 제대군인대부지원)을 발견하고 `required_discharge_type` 필드를 새로 추가함(2026-08-15, `backend/app/core/matching.py`의 `discharge_type_matches()`).

- **데이터 정확도 반복 개선**: `supabase/tools/audit_description_gaps.py`(설명 텍스트엔 조건이 있는데 구조화 필드가 비어있는 경우 탐지) 같은 감사 스크립트를 계속 정기 실행하면서, 새로운 유형의 "구조화 안 된 조건" 클래스를 발견할 때마다 감지 규칙에 편입 — 완전 자동 분류기보다는 "그물을 계속 넓혀가는" 반자동 방식으로 접근 중. **"값이 그럴듯하다"와 "값이 실제로 출처에 있다"는 다른 문제라는 게 2026-08-15에 재확인됨** — CNU 배치 하나에서만 72건이 근거 없이 들어가 있었고(사람이 형제 레코드 패턴으로 넘겨짚었다가 두 번이나 틀림), 출처 자체가 대전대 게시판이라고 적혀있었는데 실제로 그 게시판 전체(29페이지)를 뒤져도 없는 장학금 3건도 발견해서 삭제함. 패턴 추정 대신 `harness/reverify.py`(원문 인용 강제 + 기계적 대조)로 재검증하는 쪽으로 전환 — 아직 충남대 한 곳만 돌려봄, 나머지 학교도 순차 실행 필요.
- **데이터 입력 가이드 문서 최신화**: `supabase/README.md`/`supabase/data_collection_guide.md`가 실제 스키마·매칭 로직과 오래 어긋나 있던 걸 발견해서 정리함(2026-08-12) — 이 문서들이 협업자/AI 입력 작업의 유일한 기준이라, 코드가 바뀔 때마다 같이 갱신하는 습관이 필요.
- **하네스 커버리지 확장**: `harness/sites.py`에 현재 8개 대학만 등록돼 있음 — 대전권 나머지 대학 온보딩, 지자체/재단 등 학교 소속과 무관한 외부 장학금 발굴 채널 확보가 남음.
- **재검증 커버리지 확장**: `harness/reverify.py`를 충남대 배치 외 다른 대학/배치에도 순차 실행 필요 — 지금은 결과가 얼마나 나올지 예측이 안 돼서 GitHub Actions 워크플로(`harness_reverify.yml`)도 일부러 자동 스케줄 없이 수동 트리거만 열어둔 상태(`harness/README.md`의 "재검증" 참고).
- **하네스 성능/비용 튜닝**: 추출 모델 선택(Sonnet/Haiku 2중 추출), 동시성(4), 나이트런당 처리량(대학 1~2곳, 신규 40건 상한) 전부 초기 판단값이고 실측 벤치마크는 아직 안 함(`harness/config.py` 참고) — 트래픽/비용이 늘면 재검토 대상.
- **마이그레이션 도구 도입**: 스키마 변경 빈도가 줄어들면 `SQLModel.metadata.create_all()` + 수동 `ALTER TABLE` 대신 Alembic 등으로 전환 검토.
- **회귀 방지 자동화 부족**: 브라우저 E2E 테스트가 아직 없음(`frontend/README.md` "남은 것" 참고) — 프론트 변경 시 수동 확인에 의존 중.
- **JWT `localStorage` 저장 → `httpOnly` 쿠키 전환**: 배포 전 점검(2026-08-13)에서 나온 가장 큰 보안 갭. 프론트(Vercel)·백엔드(Railway)가 다른 도메인이라 크로스사이트 쿠키(`SameSite=None`) 필요 — Safari 등 서드파티 쿠키 차단 정책과 충돌 위험이 있어 Vercel rewrite/프록시로 같은 도메인처럼 묶는 설계까지 같이 필요함. 프론트(`frontend/src/lib/auth.ts`)·백엔드(`backend/app/api/auth.py`, `backend/app/api/deps.py`) 동반 작업. 상세는 `frontend/README.md` "남은 것" 참고.
