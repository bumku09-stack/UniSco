"""오케스트레이션: collect_links → 원문 확보(HTML/첨부파일) → dedup → extract(LLM, 2회) →
verify → build_pr.

대학 단위로 처리함(설계안 5장 "한 번 실행 = 대학 1~2곳 분량"). 실행:

    python -m harness.run                       # 로테이션에서 자동으로 다음 대학 선택
    python -m harness.run --university 한밭대학교  # 특정 대학만
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from harness import build_pr, collect_links, config, db, dedup, extract, http, sites, verify
from harness.models import CollectionResult, Listing, VerifiedScholarship

REPO_ROOT = Path(__file__).resolve().parents[1]
ROTATION_STATE_PATH = REPO_ROOT / "harness" / "state" / "rotation.json"

_ATTACHMENT_EXTS = {".hwp", ".hwpx", ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def _log(msg: str) -> None:
    print(f"[harness] {msg}", flush=True)


def fetch_source_text(listing: Listing) -> str | None:
    """게시글 상세페이지 또는 첨부파일에서 원문 텍스트를 뽑음.

    URL 확장자로 첨부파일(HWP/HWPX/이미지)인지 HTML 상세페이지인지 구분함 — 첨부파일이면
    기존 supabase/tools/extract_text.py를 그대로 재사용함(신규 구현 안 함). HTML이면 bs4로
    태그만 벗겨낸 텍스트를 씀. 어느 쪽이든 실패하면 None을 반환하고 이 항목만 건너뛰며 로그를
    남김 — 파이프라인 전체를 죽이지 않음.

    주의: extract_text.py의 이미지 OCR은 TESSERACT_EXE/TESSDATA_DIR이 데이터 입력을 맡은
    친구분 Windows 컴퓨터 경로로 하드코딩돼 있어서, Linux인 GitHub Actions 러너에서는 이미지
    첨부파일만 실패함(HWP/HWPX는 문제없음) — extract_text.py 자체는 건드리지 않고 이 함수가
    그 실패를 흡수해서 해당 항목만 스킵/로그로 남김.
    """
    ext = Path(urlparse(listing.url).path).suffix.lower()

    if ext in _ATTACHMENT_EXTS:
        sys.path.insert(0, str(REPO_ROOT / "supabase" / "tools"))
        import extract_text  # type: ignore  # supabase/tools/extract_text.py, 그대로 재사용

        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(http.get(listing.url).content)
                tmp_path = Path(tmp.name)
            try:
                return extract_text.extract(tmp_path)
            finally:
                tmp_path.unlink(missing_ok=True)
        except Exception as e:  # noqa: BLE001 — 원문 확보 실패는 이 항목 하나만 건너뛰는 사유
            _log(f"첨부파일 원문 추출 실패({listing.url}): {e}")
            return None

    try:
        soup = BeautifulSoup(http.get_text(listing.url), "lxml")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:  # noqa: BLE001
        _log(f"상세페이지 원문 확보 실패({listing.url}): {e}")
        return None


def _load_rotation_index() -> int:
    if ROTATION_STATE_PATH.exists():
        data = json.loads(ROTATION_STATE_PATH.read_text(encoding="utf-8"))
        return data.get("next_index", 0)
    return 0


def _save_rotation_index(index: int) -> None:
    """상태 파일을 쓰고 **현재 체크아웃된 브랜치(main)에 바로 커밋·푸시**함 — 장학금 데이터와
    달리 이건 "다음엔 어디부터"라는 부기 정보일 뿐이라 PR 리뷰 게이트를 거칠 이유가 없음.
    이 함수는 build_pr.py가 harness/* 브랜치를 만들기 전에(run_for_university보다 먼저)
    호출되므로, 여기서 커밋해두지 않으면 이후 `git checkout -b`로 변경사항이 딸려가 버려서
    main엔 영영 반영되지 않고 유실됨."""
    ROTATION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 끝에 개행 포함 — 없으면 값이 그대로여도(예: index 0 -> 0) 매번 포맷만 다른 diff가 생겨서
    # 나이트런마다 의미 없는 커밋이 쌓임(2026-08-05, 첫 실행에서 실제로 발생해서 발견).
    ROTATION_STATE_PATH.write_text(json.dumps({"next_index": index}) + "\n", encoding="utf-8")
    rel_path = str(ROTATION_STATE_PATH.relative_to(REPO_ROOT))
    subprocess.run(["git", "add", rel_path], cwd=REPO_ROOT, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if diff.returncode != 0:  # 변경사항 있을 때만 커밋(없으면 빈 커밋 에러 남)
        subprocess.run(
            ["git", "commit", "-m", f"[harness] rotation state -> {index}"], cwd=REPO_ROOT, check=True
        )
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT, check=True)


def _pick_universities(explicit: list[str] | None) -> list[str]:
    """--university가 명시되면 그걸 그대로 쓰고, 아니면 sites.py 등록 순서대로 로테이션.

    로테이션 상태는 harness/state/rotation.json에 저장됨 — 스케줄된 실행이 실제 스콜라십
    데이터(PR)와 달리 리뷰 게이트 없이 그냥 진행 지점만 기록하는 부기용 파일이라, main에
    바로 커밋해도 안전하다고 판단함(run.py 실행 스크립트가 직접 커밋, build_pr.py와 무관).
    """
    if explicit:
        return explicit
    all_universities = sites.universities_in_order()
    if not all_universities:
        return []
    start = _load_rotation_index() % len(all_universities)
    n = config.UNIVERSITIES_PER_NIGHTLY_RUN
    picked = [all_universities[(start + i) % len(all_universities)] for i in range(min(n, len(all_universities)))]
    _save_rotation_index((start + n) % len(all_universities))
    return picked


def run_for_university(university: str) -> None:
    boards = sites.boards_for(university)
    if not boards:
        _log(f"{university}: sites.py에 등록된 게시판이 없음 — 스킵")
        return

    # 수집·추출(Anthropic API 비용 발생 구간)을 시작하기 전에, 오늘 이 대학으로 이미 열려있는
    # PR이 있는지 먼저 확인함 — 같은 날 재실행(예: 이전 실행이 도중에 실패해서 다시 돌리는
    # 경우) 때 이미 끝난 작업을 또 돌려서 토큰을 이중으로 쓰는 걸 막기 위함(2026-08-10).
    try:
        existing_pr = build_pr.find_existing_open_pr(university)
    except Exception as e:  # noqa: BLE001 — 확인 자체가 실패해도(네트워크 등) 원래 하려던 작업은 계속 진행
        _log(f"{university}: 기존 PR 확인 실패(무시하고 계속) — {e}")
        existing_pr = None
    if existing_pr:
        _log(f"{university}: 오늘자 PR이 이미 열려있어 스킵 — {existing_pr}")
        return

    _log(f"[collect] {university} — 게시판 {len(boards)}개 순회 시작")
    collection_results: list[CollectionResult] = collect_links.collect_all(boards)
    for r in collection_results:
        status = "ok" if r.ok else "MISMATCH/FAIL"
        _log(f"[collect] {r.board_name}: {r.actual_count}건 수집 (게시판 표시 {r.expected_count}) — {status}")

    all_listings = [listing for r in collection_results for listing in r.listings]
    if not all_listings:
        _log(f"{university}: 수집된 링크 없음 — 종료")
        return

    _log("[dedup] 기존 DB와 대조 중")
    existing = db.fetch_existing_scholarships()
    new_listings, skipped = dedup.filter_new(all_listings, existing)
    _log(f"[dedup] 신규 {len(new_listings)}건 / 스킵(기존 중복 추정) {len(skipped)}건")

    verified_list: list[VerifiedScholarship] = []
    for listing in new_listings:
        source_text = fetch_source_text(listing)
        if not source_text or not source_text.strip():
            _log(f"[extract] 원문 확보 실패로 스킵: {listing.url}")
            continue

        _log(f"[extract] {(listing.title[:40] or listing.url)}")
        # 숫자 핵심 필드 대조용 2중 추출 — 매번 동일 함수를 상태 없이 두 번 호출함
        # (설계안 "동일 함수를 파라미터만 바꿔 2회 독립 호출할 수 있게 구성").
        try:
            primary = extract.extract_scholarship(source_text, listing.url)
            secondary = extract.extract_scholarship(source_text, listing.url)
            verified = verify.verify_scholarship(primary, source_text, listing.title, secondary)
        except Exception as e:  # noqa: BLE001
            # 항목 하나가 API 에러(레이트리밋 등, extract.py가 자체 재시도 후에도 실패한 경우)로
            # 죽어도 배치 전체를 죽이면 이미 이 항목들보다 앞서 처리된 나머지 항목에 쓴 토큰이
            # 통째로 날아감 — 이 항목만 로그 남기고 건너뜀(2026-08-10).
            _log(f"[extract] 추출 실패로 스킵({listing.url}): {e}")
            continue
        verified_list.append(verified)

    flagged = sum(1 for v in verified_list if v.has_flags)
    _log(f"[verify] 총 {len(verified_list)}건 중 플래그 있는 항목 {flagged}건")

    pr_url = build_pr.build_and_open_pr(university, verified_list, collection_results, len(skipped))
    if pr_url:
        _log(f"[build_pr] PR 오픈: {pr_url}")
    else:
        _log("[build_pr] 신규 항목 없어 PR 안 만듦")


def main() -> None:
    parser = argparse.ArgumentParser(description="장학금 자동 수집·분류 하네스")
    parser.add_argument(
        "--university",
        action="append",
        dest="universities",
        help="처리할 대학 이름(여러 번 지정 가능). 생략하면 로테이션에서 자동 선택.",
    )
    args = parser.parse_args()

    universities = _pick_universities(args.universities)
    if not universities:
        _log("처리할 대학이 없음 — harness/sites.py의 SITES 레지스트리를 먼저 채울 것.")
        return

    failures: list[str] = []
    for university in universities:
        try:
            run_for_university(university)
        except Exception as e:  # noqa: BLE001
            # 한 대학에서 git/PR 단계가 실패해도(build_pr.build_and_open_pr가 재전파) 같은
            # 나이트런에 묶인 다른 대학까지 통째로 스킵되면 안 됨 — 나머지는 계속 진행하고,
            # 실패한 대학만 모아뒀다가 마지막에 명시적으로 실패로 표시함(2026-08-10).
            _log(f"{university}: 처리 중 실패 — {e}")
            failures.append(university)

    if failures:
        _log(f"실패한 대학: {', '.join(failures)} — 워크플로 로그에서 산출물 복구 후 재실행할 것")
        sys.exit(1)


if __name__ == "__main__":
    main()
