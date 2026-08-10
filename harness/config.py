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

# ── 7.4 모델 선택 ───────────────────────────────────────────────────────
# 추출 정확도·비용 트레이드오프는 실제 공고문 샘플로 벤치마크 필요(설계안 7.4절, 아직 미완료)
# — 그 전까지는 최신 Sonnet으로 시작. 워크플로 파일 수정 없이 이 환경변수만 바꿔서 실험 가능.
EXTRACTION_MODEL = os.environ.get("HARNESS_EXTRACTION_MODEL", "claude-sonnet-5")
EXTRACTION_MAX_TOKENS = 4096

# ── 7.5 목록 수집 실패 처리 ─────────────────────────────────────────────
# 총 개수 파싱 자체가 안 되거나(게시판 구조가 특이한 학교), 페이지 순회 후에도 수집된 링크 수가
# 파싱된 총 개수와 안 맞으면 이만큼 통째로 재시도. 그래도 안 맞으면 그 게시판은 스킵하고
# CollectionResult.ok=False로 플래그만 남김 — 사람이 수동으로 봐야 함(설계안 7.5절, 코드가
# "다 봤는지"를 판단하되 판단이 안 서면 침묵하지 않고 실패를 명시적으로 드러내는 것이 핵심).
LINK_COLLECTION_MAX_RETRIES = 2

# ── 이름+기관 중복 판정 임계값 (설계안 6장 표 "LLM으로 중복 판정" 대신 채택한 방식) ──
DEDUP_SIMILARITY_THRESHOLD = int(os.environ.get("HARNESS_DEDUP_THRESHOLD", "90"))  # 0~100

# ── 기타 ────────────────────────────────────────────────────────────────
GITHUB_REPO = os.environ.get("HARNESS_GITHUB_REPO", "hoseongdev/UniSco")
PR_BASE_BRANCH = "main"
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_USER_AGENT = "UniSco-Harness/1.0 (+https://github.com/hoseongdev/UniSco)"
