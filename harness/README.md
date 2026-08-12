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
├── state/rotation.json            # 다음 나이트런이 어느 대학부터 처리할지 기억하는 상태 파일
└── prompts/extraction_spec.md      # LLM 시스템 프롬프트 재료 — 필드 정의/enum, extract.py가 읽어서 씀
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

새 대학 하나를 추가하려면:

1. 그 대학의 장학공지 게시판(대학 공통 + 필요하면 학과별)을 브라우저로 직접 열어서 확인:
   - 목록 URL이 페이지 번호를 어떻게 받는지 (`?page=2` 같은 쿼리 파라미터가 보통)
   - "전체 N건" 또는 "N/M 페이지" 같은 총 개수 표시 문구 → 정규식으로 만들 수 있는지
   - 공고 링크를 고르는 CSS 셀렉터
   - JS 렌더링이 필요한지(페이지 소스 보기에 목록이 안 보이면 필요한 것)
2. `harness/sites.py`의 `SITES` 리스트에 `BoardConfig(...)` 하나 추가 (파일 안 예시 주석 참고).
3. `python -m harness.run --university <그 대학>`으로 로컬에서 한 번 돌려서 `collect_links`
   단계 로그의 개수 대조가 맞는지 확인.

## 알려진 한계

- **이미지 첨부파일 OCR은 GitHub Actions(Linux)에서 실패함.** 기존
  `supabase/tools/extract_text.py`의 Tesseract 경로가 데이터 입력을 맡은 친구분 Windows
  컴퓨터 경로로 하드코딩돼 있음 — 이 파일은 재사용 대상이라 건드리지 않았고, `run.py`가 그
  실패를 잡아서 해당 항목만 로그 남기고 건너뜀. HWP/HWPX 첨부파일은 문제없음.
- **dedup 시점의 "이름"은 게시글 제목**임 (설계안 3단계가 LLM 추출 이전이라 아직 정식
  명칭이 없음) — 장학금 정식 명칭과 게시글 제목이 많이 다르면 놓칠 수 있음. 애매하면 그냥
  통과시켜서 LLM 추출까지 가게 두는 쪽으로 설계함(과다매칭이 과소매칭보다 낫다는 기존 원칙과
  같은 방향).
- **PDF 추출은 아직 없음** — `extract_text.py`가 HWP/HWPX/이미지만 지원함. PDF 첨부파일이 있는
  게시판을 온보딩하게 되면 그때 `extract_text.py`에 PDF 지원을 추가할 것(하네스 쪽 코드 변경
  없이 `run.py`의 `_ATTACHMENT_EXTS`에 `.pdf`만 추가하면 됨).
