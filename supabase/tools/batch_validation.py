# -*- coding: utf-8 -*-
"""새 장학금 배치 SQL을 생성하기 전에 돌리는 하드 게이트.

gen_batchN.py 패턴(batch2/batch3에서 쓰던 dict 리스트 + COLUMNS assert 방식)에 이어붙여
쓰는 검증 함수. description_gap_check.py의 규칙(A: 플레이스홀더 값, B/C: 자격조건·금액·인원·
기간 키워드 vs NULL, 포괄 제한문구 catch-all)을 각 row에 대해 돌려서, 걸리는 게 있으면
**SQL을 아예 생성하지 못하게 예외를 던짐**(기존 컬럼-개수 assert와 동일한 강도).

배경: "문화예술인재학부장학금" 사고(2026-08-07) — description엔 전공 제한이 다 적혀
있었는데 major 컬럼을 NULL로 둔 채로 배치에 실려서, 매칭 로직의 "비어있으면 통과" 원칙 때문에
전 국민에게 노출됐던 사고. 이 사고가 재발하지 않도록 배치 생성 단계에서 원천 차단.

사용법 (gen_batchN.py 안에서):
    from batch_validation import validate_rows
    ...
    validate_rows(ROWS)  # COLUMNS assert 하기 전에 호출
    print(generate(ROWS))

오탐(진짜 조건이 없는데 단어만 걸린 경우)이면, 그 row dict에 `_reviewed_gaps`를 추가하고
왜 오탐인지 이유를 반드시 같이 적을 것:
    {
        "name": "...",
        ...
        "_reviewed_gaps": {"major"},  # "학과 무관하게 지원 가능"이라 오탐 — 실제 제한 없음
    }
"_reviewed_gaps"는 COLUMNS에 없는 메타 키라 render_row()에는 안 들어감(row.get(c) for c
in COLUMNS만 읽으므로 안전).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from description_gap_check import (  # noqa: E402
    find_gaps,
    find_generic_restriction_flag,
    find_placeholder_values,
)


class BatchValidationError(Exception):
    pass


def validate_rows(rows: list[dict]) -> None:
    """문제가 하나라도 있으면 BatchValidationError를 던짐(즉시 중단). 문제 없으면 조용히 통과."""
    errors: list[str] = []

    for row in rows:
        label = row.get("name", "(이름 없음)")

        placeholder_hits = find_placeholder_values(row)
        if placeholder_hits:
            for col, val in placeholder_hits.items():
                errors.append(
                    f"[플레이스홀더] {label!r}: 컬럼 `{col}`에 실제 값 대신 "
                    f"{val!r}가 그대로 들어있음 — 원문 재확인해서 채우거나 NULL로 비워둘 것."
                )

        gaps = find_gaps(row)
        if gaps:
            errors.append(
                f"[미반영 조건 의심] {label!r}: description엔 있는 것 같은데 다음 필드가 "
                f"비어있음 — {', '.join(gaps)}. 실제로 조건이 없으면 row dict에 "
                f'`"_reviewed_gaps": {{{", ".join(repr(g) for g in gaps)}}}`를 이유와 함께 추가할 것.'
            )

        if find_generic_restriction_flag(row):
            errors.append(
                f"[포괄 제한문구] {label!r}: description에 강한 배제 문구(~외 지원불가/~만 해당/"
                f"~에 한함 등)가 있는데 구조화된 자격조건이 전부 비어있음 — 어느 필드에 대한 "
                f"제한인지 원문을 다시 봐서 채울 것."
            )

    if errors:
        message = f"\n\n배치 검증 실패 — {len(errors)}건. SQL을 생성하지 않음.\n\n" + "\n".join(
            f"- {e}" for e in errors
        )
        raise BatchValidationError(message)
