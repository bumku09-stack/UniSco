# -*- coding: utf-8 -*-
"""2026-08-12: application_url이 기관 "메인 홈페이지"만 가리키고 있던 132건(상세페이지
"신청하러 가기" 버튼을 누르면 실제 신청/공고 페이지가 아니라 홈페이지로만 이동하던 문제)을
병렬 조사 에이전트 6개로 원문 재확인해서 실제 신청/공고 페이지 URL로 교체.

원본 조사 결과: fix_application_url_2026-08-12_data.json (132건, 각 항목마다
confidence(high/medium/low)와 근거 note 포함). new_url == old_url인 6건은 조사 결과
"이미 정확하거나(원래부터 전용 신청 시스템/상시접수창구)" 또는 "더 구체적인 페이지가
존재하지 않음(로그인 필요/지정기부·비공개 방식)"으로 확인된 것 — 실제로는 값이 안 바뀜.

사용법:
    python fix_application_url_2026-08-12.py           # dry-run만
    python fix_application_url_2026-08-12.py --apply    # 실제 반영
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg2


def load_database_url() -> str:
    env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"DATABASE_URL not found in {env_path}")


def load_fixes() -> list[dict]:
    data_path = Path(__file__).resolve().parent / "fix_application_url_2026-08-12_data.json"
    return json.loads(data_path.read_text(encoding="utf-8"))


def main() -> None:
    apply = "--apply" in sys.argv
    fixes = load_fixes()
    conn = psycopg2.connect(load_database_url())
    cur = conn.cursor()

    ids = [f["id"] for f in fixes]
    cur.execute(
        "SELECT id, name, application_url FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    before_rows = {r[0]: r for r in cur.fetchall()}

    missing = set(ids) - set(before_rows)
    if missing:
        print(f"경고: DB에서 못 찾은 id 있음: {missing}")

    mismatched_before: list[str] = []
    for fix in fixes:
        row = before_rows.get(fix["id"])
        if row is not None and row[2] != fix["old_url"]:
            mismatched_before.append(
                f"id={fix['id']} `{row[1]}`: 조사 당시 old_url({fix['old_url']!r})과 지금 DB 값"
                f"({row[2]!r})이 다름 — 그 사이 다른 수정이 있었을 수 있음, 확인 필요."
            )

    for fix in fixes:
        cur.execute(
            "UPDATE scholarship SET application_url = %s WHERE id = %s",
            (fix["new_url"], fix["id"]),
        )

    cur.execute(
        "SELECT id, name, application_url FROM scholarship WHERE id = ANY(%s) ORDER BY id",
        (ids,),
    )
    after_rows = {r[0]: r for r in cur.fetchall()}

    report_lines: list[str] = []
    if mismatched_before:
        report_lines.append("## 경고: 조사 시점과 DB 현재 값이 다른 항목")
        report_lines.extend(f"- {m}" for m in mismatched_before)
        report_lines.append("")

    by_confidence: dict[str, list[dict]] = {"high": [], "medium": [], "low": []}
    for fix in fixes:
        by_confidence[fix["confidence"]].append(fix)

    for conf in ("high", "medium", "low"):
        group = by_confidence[conf]
        report_lines.append(f"## {conf} confidence — {len(group)}건")
        for fix in group:
            fid = fix["id"]
            before = before_rows.get(fid)
            after = after_rows.get(fid)
            if before is None or after is None:
                continue
            changed = "변경" if before[2] != after[2] else "동일(유지)"
            report_lines.append(f"\n### id={fid} {before[1]} ({changed})")
            report_lines.append(f"  before: {before[2]!r}")
            report_lines.append(f"  after:  {after[2]!r}")
            report_lines.append(f"  note: {fix['note']}")
        report_lines.append("")

    report = "\n".join(report_lines)
    out_path = Path(__file__).resolve().parents[1] / "audit_reports" / "fix_application_url_2026-08-12_diff.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    if apply:
        conn.commit()
        print(f"반영 완료(commit). {len(fixes)}건 처리. diff: {out_path}")
    else:
        conn.rollback()
        print(f"dry-run만 수행(rollback, 실제 반영 안 됨). {len(fixes)}건 확인. diff: {out_path}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
