"""하네스 전역 설정값.

설계안(`scholarship-harness-design.md`) 7장 "열린 질문"에서 나중에 튜닝하기로 한 값들을
전부 여기 상수로 모아둠 — 코드 곳곳에 흩어져 있으면 다음에 조정할 때 어디를 고쳐야 할지
찾아야 하는데, 여기 하나만 보면 되게 함. 환경변수로 오버라이드 가능한 것들은 그렇게 해둠
(GitHub Actions에서 재배포 없이 워크플로 파일만 고쳐서 바꿀 수 있게).
"""
from __future__ import annotations

import os

# ── 7.1 인용 대조 임계값 ────────────────────────────────────────────────
# 원문과 완전히 동일한 문자열만 인정하지 않고, 공백·문장부호 차이 정도는 허용하는 옵션.
# 정규화(공백 collapse, 일부 문장부호 제거) 후에도 안 맞으면 rapidfuzz의 partial_ratio로
# "원문 어딘가에 이 인용문과 이만큼 비슷한 부분이 있는지"를 0~100 점수로 재확인함.
# 너무 낮추면 실제로 지어낸 값도 "확인됨"으로 통과시킬 위험이 커지므로 보수적으로 시작.
QUOTE_FUZZY_MATCH_ENABLED = True
QUOTE_FUZZY_MIN_RATIO = int(os.environ.get("HARNESS_QUOTE_FUZZY_MIN_RATIO", "92"))  # 0~100

# ── 7.2 2중 추출 적용 범위 ──────────────────────────────────────────────
# "숫자 핵심 필드"만 두 번 독립 추출해서 대조함 — 텍스트 필드까지 전부 대조하면 리뷰 큐가
# 너무 커짐(비용 자체는 공고문 1건당 텍스트가 짧아 크지 않음, 설계안 7.2절 참고).
# 여기 나열된 필드 이름은 harness/models.py의 ExtractedScholarship 필드명과 정확히 일치해야 함.
DUAL_EXTRACT_FIELDS: frozenset[str] = frozenset(
    {
        "amount",
        "min_age",
        "max_age",
        "max_income_bracket",
        "min_gpa",
        "language_test_min_score",
        "min_grade",
        "max_grade",
        "application_deadline",
    }
)
# 부동소수점 필드(min_gpa, language_test_min_score) 비교 시 표현 오차 허용치.
DUAL_EXTRACT_FLOAT_TOLERANCE = 1e-6

# ── 7.3 페이싱 ──────────────────────────────────────────────────────────
# 나이트런 1회당 처리할 대학 수. sites.py의 SITES 순서대로 이만큼씩 돌아가며 처리하고,
# state/rotation.json에 다음 시작 지점을 기록함(harness/run.py 참고).
UNIVERSITIES_PER_NIGHTLY_RUN = int(os.environ.get("HARNESS_UNIVERSITIES_PER_RUN", "2"))

# 대학 하나를 실행당 처리할 "신규(기존 DB에 없는)" 게시글 수 상한. 처음 온보딩하는 대학은
# 게시판 역사 전체(수백~수천 건)가 전부 "신규"로 잡혀서 상한이 없으면 한 번에 다 처리하려다
# 몇 시간씩 걸리고, 결과 리뷰 마크다운도 PR 본문 글자수 제한(GitHub 약 65536자)을 넘겨서
# PR 오픈 자체가 422로 실패함(2026-08-11, 한밭대 온보딩 첫 실행에서 실제 발생 — 179페이지·
# 1786건이 한 번에 몰려서 5시간 넘게 걸리다 마지막에 PR 생성만 실패). 목록은 게시판이
# 최신순으로 보여주므로 앞에서부터 이 개수만 잘라 처리 — 나머지는 여전히 DB에 없는 채로
# 남아있으니 다음 나이트런이 이어서 처리함(하네스가 상태를 안 가져도 자연스럽게 여러 밤에
# 걸쳐 나뉘어 처리되는 구조).
MAX_NEW_ITEMS_PER_RUN = int(os.environ.get("HARNESS_MAX_NEW_ITEMS_PER_RUN", "40"))

# ── 7.4 모델 선택 ───────────────────────────────────────────────────────
# 추출 정확도·비용 트레이드오프는 실제 공고문 샘플로 벤치마크 필요(설계안 7.4절, 아직 미완료)
# — 그 전까지는 최신 Sonnet으로 시작. 워크플로 파일 수정 없이 이 환경변수만 바꿔서 실험 가능.
EXTRACTION_MODEL = os.environ.get("HARNESS_EXTRACTION_MODEL", "claude-sonnet-5")
EXTRACTION_MAX_TOKENS = 4096
# 2중 추출의 대조용 호출(DUAL_EXTRACT_FIELDS 9개만 뽑음)은 primary처럼 전체 판단을 책임지는
# 게 아니라 숫자만 맞는지 교차 확인하는 용도라 더 싸고 빠른 모델로도 충분함(2026-08-11) —
# 여기서 값이 달라 보이면 그냥 needs_review로 플래그만 될 뿐 데이터가 틀리게 나가진 않으므로,
# Haiku가 가끔 Sonnet과 다르게 봐도 안전한 방향(더 보수적인 리뷰 큐)으로만 작용함.
DUAL_EXTRACT_MODEL = os.environ.get("HARNESS_DUAL_EXTRACT_MODEL", "claude-haiku-4-5-20251001")
# 추출(Anthropic API 호출)을 항목 여러 개 동시에 돌림 — 항목마다 서로 상태를 공유하지 않는
# 독립 호출이라(설계안 "상태 없음" 원칙) 병렬화해도 결과가 달라지지 않음. 목록 수집/원문
# 확보 쪽 지연(REQUEST_DELAY_SECONDS)은 대학 사이트로 가는 요청이라 그대로 순차 유지하고,
# 이건 Anthropic API로 가는 요청이라 별개로 동시 처리함(2026-08-11, 나이트런 소요시간 단축).
EXTRACTION_CONCURRENCY = int(os.environ.get("HARNESS_EXTRACTION_CONCURRENCY", "4"))

# ── 7.5 목록 수집 실패 처리 ─────────────────────────────────────────────
# 총 개수 파싱 자체가 안 되거나(게시판 구조가 특이한 학교), 페이지 순회 후에도 수집된 링크 수가
# 파싱된 총 개수와 안 맞으면 이만큼 통째로 재시도. 그래도 안 맞으면 그 게시판은 스킵하고
# CollectionResult.ok=False로 플래그만 남김 — 사람이 수동으로 봐야 함(설계안 7.5절, 코드가
# "다 봤는지"를 판단하되 판단이 안 서면 침묵하지 않고 실패를 명시적으로 드러내는 것이 핵심).
LINK_COLLECTION_MAX_RETRIES = 2

# ── 이름+기관 중복 판정 임계값 (설계안 6장 표 "LLM으로 중복 판정" 대신 채택한 방식) ──
DEDUP_SIMILARITY_THRESHOLD = int(os.environ.get("HARNESS_DEDUP_THRESHOLD", "90"))  # 0~100

# ── 7.6 같은 호스트로의 요청 간격 ───────────────────────────────────────
# 목록 페이지 순회(collect_links.py)와 상세페이지/첨부파일 확보(run.py)가 같은 대학 사이트로
# 짧은 시간에 요청을 몰아서 보내면, 대학 쪽 방화벽(WAF)이 봇 트래픽으로 판단해 그 IP를
# 일시적으로 막을 수 있음(2026-08-10 — 31건을 몇 초 만에 연달아 요청한 첫 실행 직후,
# 재실행이 GitHub Actions 러너에서만 계속 connect timeout으로 실패. 같은 시각 사람이 직접
# 접속하면 1초 안에 정상 응답해서, 사이트 자체가 아니라 요청 패턴이 원인으로 추정됨).
# 요청 사이에 짧게 쉬어서 이런 버스트 패턴 자체를 피함.
REQUEST_DELAY_SECONDS = float(os.environ.get("HARNESS_REQUEST_DELAY_SECONDS", "0.7"))

# ── 기타 ────────────────────────────────────────────────────────────────
GITHUB_REPO = os.environ.get("HARNESS_GITHUB_REPO", "hoseongdev/UniSco")
PR_BASE_BRANCH = "main"
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_USER_AGENT = "UniSco-Harness/1.0 (+https://github.com/hoseongdev/UniSco)"
