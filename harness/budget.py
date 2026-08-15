"""API 사용량 예산 추적.

토큰은 무제한이 아니라서, 한 번의 실행(프로세스 하나 = 나이트런 1회 또는 온보딩 에이전트
1회 호출)에서 누적 사용량이 config.py의 상한을 넘기면 그 이후 새 API 호출을 막음. 프로세스
하나 안에서만 의미 있는 카운터라 모듈 전역 싱글턴으로 두면 충분함(harness.run과
harness.onboard는 항상 각자 별도 프로세스로 실행되므로 서로 섞이지 않음) — 다만 run.py의
추출 단계는 ThreadPoolExecutor로 여러 항목을 동시에 처리하므로 스레드 안전은 필요함.
"""
from __future__ import annotations

import threading

from harness import config


class BudgetExceeded(Exception):
    """이번 실행의 토큰 예산을 넘겨서 더 이상 API를 호출하면 안 됨."""


class TokenBudget:
    def __init__(self, limit: int):
        self._limit = limit
        self._used = 0
        self._lock = threading.Lock()

    def check(self) -> None:
        """새 API 호출을 시작하기 '전'에 부름. 이미 예산을 넘겼으면 그 호출 자체를 막음 —
        진행 중이던 항목이 예산을 살짝 넘기는 것까진 사후에만 알 수 있으므로 허용하고,
        요점은 "그 다음부터 새 호출을 시작하지 않는 것"임."""
        with self._lock:
            used = self._used
        if used >= self._limit:
            raise BudgetExceeded(
                f"이번 실행 토큰 예산({self._limit:,}) 초과 — 누적 사용량 {used:,} 토큰. "
                "환경변수로 상한을 조정하려면 config.py의 관련 HARNESS_MAX_TOKENS_* 참고."
            )

    def record(self, usage) -> None:
        """anthropic 응답의 usage를 예산에 반영. cache_read는 훨씬 싸지만(0.1x) 완전
        무료는 아니고, 여기 목적은 정확한 비용 계산이 아니라 "너무 많이 돌았는지" 감지라
        네 필드를 구분 없이 그냥 더함."""
        added = (
            (getattr(usage, "input_tokens", 0) or 0)
            + (getattr(usage, "output_tokens", 0) or 0)
            + (getattr(usage, "cache_creation_input_tokens", 0) or 0)
            + (getattr(usage, "cache_read_input_tokens", 0) or 0)
        )
        with self._lock:
            self._used += added

    @property
    def used(self) -> int:
        with self._lock:
            return self._used


extraction_budget = TokenBudget(config.MAX_TOKENS_PER_EXTRACTION_RUN)
onboard_budget = TokenBudget(config.MAX_TOKENS_PER_ONBOARD_RUN)
