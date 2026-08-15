# harness/

장학금 자동 수집·분류 하네스 — 설계는 [DESIGN.md](./DESIGN.md) 참고. 이 폴더는 `backend/`,
`frontend/`와 별개로 GitHub Actions에서 독립 실행되는 파이프라인이고, 앱 코드나 운영 DB
쓰기 권한과는 분리돼 있음 — 최종 산출물은 항상 **PR**이고, 실제 DB 반영은 지금처럼 사람이
`supabase/tools/run_sql.py`를 직접 실행함.

## 코드 구조

```
harness/
├── config.py           # 튜닝 가능한 값 전부 (인용 임계값, 2중추출 대상, 페이싱, 모델명...)
├── models.py             # 파이프라인 단계 사이를 오가는 dataclass (Listing, ExtractedScholarship, VerifiedScholarship...)
├── db.py                  # DATABASE_URL 읽기 전용 접근 — dedup용 (name, provider) 조회만, 쓰기 없음
├── sites.py                # 대학·게시판별 크롤 설정(BoardConfig) 레지스트리 — 지금은 비어있음, 아래 "다음 할 일" 참고
├── collect_links.py        # [1] 목록 수집 — LLM 미개입, 총 개수 파싱 → 페이지 순회 → 개수 대조
├── dedup.py                  # [3] 중복 스킵 — rapidfuzz 이름+기관 유사도, LLM 미개입
├── extract.py                 # [4] LLM 구조화 추출 — Anthropic tool-use 1건 호출, 상태 없음
├── verify.py                   # [5] 자동 검증 — 인용 대조 + 2중추출 대조, LLM 자기검증 아님
├── build_pr.py                  # [6][7] SQL 초안 + 리뷰 마크다운 생성, 브랜치 커밋, PR 오픈
├── run.py                        # 오케스트레이션 — python -m harness.run
├── onboard.py                     # 온보딩 에이전트 — 새 대학 게시판 조사, BoardConfig 초안 PR 생성. 아래 "온보딩 에이전트" 참고
├── budget.py                       # API 사용량 예산 추적 — 아래 "토큰 예산" 참고
├── state/rotation.json            # 다음 나이트런이 어느 대학부터 처리할지 기억하는 상태 파일
└── prompts/
    ├── extraction_spec.md          # LLM 시스템 프롬프트 재료 — 필드 정의/enum, extract.py가 읽어서 씀
    └── onboarding_spec.md          # 온보딩 에이전트 시스템 프롬프트 — onboard.py가 그대로 주입해서 씀
```

## 로컬 실행

```bash
pip install -r harness/requirements.txt
playwright install chromium

export ANTHROPIC_API_KEY=...
export DATABASE_URL=...   # 없으면 backend/.env에서 자동으로 읽음(run_sql.py와 동일한 폴백)
export GITHUB_TOKEN=...   # PR을 실제로 열려면 필요. 없으면 브랜치 push까지만 되고 에러 남

python -m harness.run --university 한밭대학교
```

`sites.py`의 `SITES`가 비어있는 대학은 "게시판이 없음 — 스킵"만 찍히고 아무 일도 안 일어남
(아래 "다음 할 일" 참고).

## 원칙 두 가지가 코드 어디에 있는지

1. **"다 봤는지" 판단은 코드가 한다** — `collect_links.py`의 `collect_board_links()`. 정규식으로
   파싱한 총 개수/총 페이지 수만큼 기계적으로 순회하고, 끝나면 `수집된 링크 수 == 파싱된 총
   개수`를 그냥 등호로 비교함. LLM에게 "다 모았어?"라고 묻는 코드는 이 파일 어디에도 없음.
2. **인용 강제 + 기계적 대조** — `extract.py`가 필드마다 `field_value`+`source_quote`를 tool-use
   스키마로 강제하고, `verify.py`의 `quote_exists_in_source()`가 그 인용문이 원문에 실제로
   있는지 문자열로 대조함. LLM에게 "이 값 맞아?"라고 다시 확인받는 코드는 없음 — 정규화 후
   완전포함 검사, 그래도 없으면 `rapidfuzz.partial_ratio`로 임계값 이상인지만 봄.

## 현재 상태 (2026-08-12 기준)

`sites.py`에 대전권 7개 대학 + KAIST, 총 8개교가 등록돼 있고, GitHub Actions
(`.github/workflows/harness_nightly.yml`)가 매일 새벽 2시(KST)에 로테이션 순서대로
1~2곳씩 자동으로 돌려서 초안 PR을 엶(머지는 여전히 사람이 직접, 이 워크플로는 DB에
아무것도 안 씀). 지금까지 이렇게 열린 PR들이 실제로 머지돼서 데이터가 들어갔음 —
설계는 끝났고 지금은 "운영 중" 단계.

## 다음 할 일 — 커버리지 확장 + 튜닝

남은 건 새 대학 온보딩(대전권에 아직 안 들어간 학교들, 지자체·재단 등 학교 소속과 무관한
외부 장학금 발굴 채널)과, 아직 실측 벤치마크 없이 초기 판단값으로 박아둔 설정값들
(`config.py` "7.4 모델 선택" 주석 참고 — 추출 모델 선택, 2중 추출 대상 필드 개수,
`EXTRACTION_CONCURRENCY`)을 실제 공고문 샘플로 검증하는 것. 이미지 첨부파일 OCR
(아래 "알려진 한계")과 PDF 미지원도 남아있음.

새 대학 하나를 추가하려면(수동):

1. 그 대학의 장학공지 게시판(대학 공통 + 필요하면 학과별)을 브라우저로 직접 열어서 확인:
   - 목록 URL이 페이지 번호를 어떻게 받는지 (`?page=2` 같은 쿼리 파라미터가 보통)
   - "전체 N건" 또는 "N/M 페이지" 같은 총 개수 표시 문구 → 정규식으로 만들 수 있는지
   - 공고 링크를 고르는 CSS 셀렉터
   - JS 렌더링이 필요한지(페이지 소스 보기에 목록이 안 보이면 필요한 것)
2. `harness/sites.py`의 `SITES` 리스트에 `BoardConfig(...)` 하나 추가 (파일 안 예시 주석 참고).
3. `python -m harness.run --university <그 대학>`으로 로컬에서 한 번 돌려서 `collect_links`
   단계 로그의 개수 대조가 맞는지 확인.

또는 아래 "온보딩 에이전트"로 위 1~2번(브라우저로 직접 확인하고 `BoardConfig`를 채우는 부분)을
자동화할 수 있음 — 3번(실제 나이트런으로 검증)은 여전히 사람이 함.

## 온보딩 에이전트 (2026-08-14 추가, 아직 실전 투입 전)

`harness/onboard.py` — 대학 이름과 게시판(또는 대학 메인) URL 하나를 주면, 그 사이트를
직접 조사해서 `BoardConfig` 초안을 PR로 올리는 에이전트. 위 "새 대학 온보딩" 1~2번(브라우저로
직접 열어서 페이지네이션 파라미터·총건수 문구·셀렉터 확인하고 `BoardConfig`를 채우는 작업)을
대신함. 시스템 프롬프트는 [`prompts/onboarding_spec.md`](./prompts/onboarding_spec.md) —
`extraction_spec.md`와 마찬가지로 사람이 읽는 설명이 아니라 에이전트에게 그대로 주입되는
지시문이므로, 조사 절차나 출력 스키마를 바꾸고 싶으면 그 문서 자체를 고칠 것.

```bash
python -m harness.onboard --university 한밭대학교 --seed-url https://www.hanbat.ac.kr/... [--target-hint 장학금]
```

기존 데이터 추출 파이프라인과 같은 두 원칙을 그대로 따름 — 다만 대상이 "장학금 공고문"이
아니라 "게시판을 크롤링하기 위한 설정값"이라는 점만 다름:

1. **"다 조사했는지" 판단을 에이전트에게 전적으로 맡기지 않음** — `onboarding_spec.md`가
   정해진 7단계(총건수 문구 찾기 → 셀렉터 찾기 → 페이지네이션 확인 → ... → 드라이런)를
   순서대로 강제하고, 다 못 끝낸 항목은 `unresolved_issues`로 명시하게 함. 에이전트가 낸
   `overall_confidence`도 신뢰하지 않고 `onboard.py`의 `_enforce_confidence_rule()`이
   confidence 필드들을 보고 기계적으로 다시 계산해서 덮어씀.
2. **모든 값에 원문 근거를 강제** — 총건수 문구·셀렉터 매칭 예시·JS 렌더링 필요 여부 판단
   근거를 전부 원문 그대로 첨부하게 하고, `render_review_markdown()`이 PR 리뷰에 그대로
   노출함.

**프롬프트 캐싱**(2026-08-14) — 도구 호출로 계속 자라나는 에이전틱 대화라 캐싱을 안 하면
매 턴 이전 도구 결과(특히 `fetch_raw_html`/`fetch_rendered_html`, 15,000자까지) 전체가
그대로 재과금됨. 두 단계로 처리함:
- system 프롬프트는 대학이 바뀌어도 거의 동일해서(참고용 `existing_configs_sample`도
  여기로 옮김) 1시간 TTL로 캐싱 — 한 세션에서 대학 여러 곳을 연달아 온보딩할 때 공유됨.
- `messages`(도구 결과가 쌓이는 부분)는 "움직이는" 브레이크포인트 하나로 처리 — 매 턴
  직전 마커를 지우고 새 턴 끝으로 옮김(`_mark_cache_breakpoint`/`_strip_cache_control`).
  캐싱은 프리픽스 매칭이라 오래된 마커를 계속 남겨둘 필요가 없어서, 대화가 `ONBOARD_MAX_TURNS`
  (기본 20턴)까지 길어져도 요청당 브레이크포인트는 항상 2개(system 1 + 이동 마커 1)로
  고정 — API 상한(4개)에 여유 있게 안전함.

추가로 **에이전트 제안을 코드가 다시 실행해서 재검증**함(`_mechanical_reverify()`) — 제안된
설정으로 실제 1~3페이지를 다시 요청해서 총건수 파싱·페이지네이션(2페이지에서 새 링크가
실제로 나오는지)·(onclick 방식이면) 상세페이지 URL 응답까지 확인하고, 하나라도 안 맞으면
`overall_confidence`를 `needs_manual_setup`으로 강제 전환함 — 에이전트 혼자만의 판단으로
`sites.py`에 반영되는 경로는 없음. 산출물(`harness/onboarding_review_*.md` +
`harness/onboarding_draft_*.py`)도 `harness/onboard-*` 브랜치로 별도 PR을 여는 것까지만 하고,
`sites.py`는 항상 사람이 검토 후 직접 고침 — 기존 데이터 PR과 동일한 "PR로 올라옴 → 사람이
리뷰 → 머지"게이트 위에 얹혀 있고, 자동으로 우회하는 경로가 없음.

**2026-08-15 — 실제 대학 3곳(을지대·대전대·한국침례신학대)으로 첫 실전 테스트, 전부
`needs_manual_setup`.** 원인이 셋 다 동일함 — 모든 서브페이지에 전체 사이트 메뉴
(depth1~depth3)를 인라인 HTML로 통째로 박아넣는 구식 대학 CMS라, 도구 결과 가시 구간
(15,000자, `_MAX_TOOL_RESULT_CHARS`)이 메뉴 코드만으로 소진돼 실제 게시판 목록·페이지네이션
·총건수 문구에 아예 도달을 못 함. 다만 에이전트가 억지로 추측해서 낮은 신뢰도 값을 내지
않고 정직하게 조사 실패로 보고했고, 기계적 재검증(`_mechanical_reverify`)도 빈 필드를
정확히 잡아냄 — "에이전트 자기판단을 그대로 안 믿는다"는 설계 원칙 자체는 의도대로
작동함. 실용적으로는 이런 초대형 GNB형 구식 사이트엔 아직 약함 — `--seed-url`에 대학
메인이 아니라 사람이 미리 찾아둔 정확한 게시판 URL을 직접 주면 더 잘 될 가능성이 높음
(아직 검증 안 함). 신형 프레임워크(전자정부프레임워크 계열 등) 사이트로도 아직 테스트
안 해봄.

## 토큰 예산 (`harness/budget.py`, 2026-08-15 추가)

토큰은 무제한이 아니라서, 배치가 예상보다 커지거나 뭔가 잘못돼서 같은 항목을 계속
재시도하는 등 비정상적으로 많이 도는 상황에서 비용이 그대로 새는 걸 막는 안전장치.
`extract.py`(나이트런, `MAX_TOKENS_PER_EXTRACTION_RUN` 기본 200만 토큰)와 `onboard.py`
(대학 1곳 조사, `MAX_TOKENS_PER_ONBOARD_RUN` 기본 50만 토큰)가 각자 자기 프로세스 안에서
API 응답의 `usage`를 누적해서 세고, 상한을 넘기면 그 시점부터 새 API 호출을 막음 — 이미
진행 중이던 항목이 상한을 살짝 넘기는 것까진 허용(정교한 예산 관리가 아니라 "이상 상황
감지용 상한"). `extract.py` 쪽은 예외를 그냥 던지는 걸로 충분함 — `run.py`의
`_extract_one`이 이미 항목 하나당 API 에러를 통째로 잡아서 로그 남기고 스킵하는
try/except를 갖고 있어서(2026-08-10, 배치 전체가 안 죽게 하려고 추가), 이 예외도 같은
경로로 자연스럽게 흡수됨. `onboard.py` 쪽은 애초에 실패해도 예외를 안 던지는 설계라
(`run_onboarding_agent`이 항상 `(제안 또는 None, 로그)`를 돌려줌), 예산 초과도 max_turns
소진과 동일하게 조용히 조사 중단으로 처리함. 둘 다 `HARNESS_MAX_TOKENS_PER_EXTRACTION_RUN`
/ `HARNESS_MAX_TOKENS_PER_ONBOARD_RUN` 환경변수로 조정 가능.

## 알려진 한계

- **이미지 첨부파일 OCR — 2026-08-15 GitHub Actions(Linux)에서도 되게 고침.** 기존
  `supabase/tools/extract_text.py`의 `TESSERACT_EXE`/`TESSDATA_DIR`가 데이터 입력을 맡은
  친구분 Windows 컴퓨터 경로로 하드코딩돼 있던 걸, 그 기본값은 그대로 두고 env var로
  오버라이드만 가능하게 열었음(그 친구분 로컬 워크플로는 그대로 안 건드림). CI는 apt로
  `tesseract-ocr`/`tesseract-ocr-kor`를 설치하고 `TESSERACT_EXE=tesseract`,
  `TESSDATA_DIR=""`를 넘겨서 씀 — `run.py`는 여전히 실패를 잡아서 해당 항목만 스킵하는
  방어 로직을 유지(다른 원인의 OCR 실패까지 파이프라인 전체를 죽이면 안 되므로).
- **dedup 시점의 "이름"은 게시글 제목**임 (설계안 3단계가 LLM 추출 이전이라 아직 정식
  명칭이 없음) — 장학금 정식 명칭과 게시글 제목이 많이 다르면 놓칠 수 있음. 애매하면 그냥
  통과시켜서 LLM 추출까지 가게 두는 쪽으로 설계함(과다매칭이 과소매칭보다 낫다는 기존 원칙과
  같은 방향).
- **PDF 추출은 아직 없음** — `extract_text.py`가 HWP/HWPX/이미지만 지원함. PDF 첨부파일이 있는
  게시판을 온보딩하게 되면 그때 `extract_text.py`에 PDF 지원을 추가할 것(하네스 쪽 코드 변경
  없이 `run.py`의 `_ATTACHMENT_EXTS`에 `.pdf`만 추가하면 됨).
