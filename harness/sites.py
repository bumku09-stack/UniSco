"""대학·게시판별 크롤 설정 레지스트리.

`frontend/src/lib/universities.ts`엔 단과대/학과 조직도는 있지만 실제 장학공지 게시판
URL·페이지네이션 구조·HTML 셀렉터는 이 프로젝트 어디에도 기록돼 있지 않아서, 검증 안 된
셀렉터를 미리 채워 넣지 않고 대학을 하나씩 실제로 열어서 확인한 것만 여기 추가하는 방식으로
운영함(설계안 "한 번 실행 = 대학 1~2곳 분량"과도 맞음 — 점진적 온보딩 전제).

collect_links.py는 이 BoardConfig만 보고 동작하므로, 새 대학 온보딩은 이 파일만 고치면 되고
collect_links.py의 순회/대조 로직은 건드릴 필요 없음.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BoardConfig:
    """게시판 하나(대학 공통 또는 특정 학과)의 크롤 설정.

    total_count_pattern과 total_pages_pattern 중 최소 하나는 있어야 함 — 게시판이 "총 N건"만
    보여주면 total_count_pattern + items_per_page로 페이지 수를 계산하고, "N/M 페이지"처럼
    총 페이지를 직접 보여주면 total_pages_pattern을 씀.
    """

    university: str
    board_name: str  # 예: "교내장학공지" — 사람이 알아보기 위한 라벨
    department: str | None  # None이면 대학 공통 게시판
    list_url_template: str  # {page} 플레이스홀더 포함 (예: ".../board.do?page={page}")
    link_selector: str  # 목록 페이지에서 공고 상세 링크를 고르는 CSS 셀렉터
    total_count_pattern: str | None = None  # 예: r"전체\s*(\d+)\s*건"
    total_pages_pattern: str | None = None  # 예: r"(\d+)\s*/\s*(\d+)\s*페이지" (그룹2가 총 페이지)
    items_per_page: int = 15  # total_count_pattern으로 계산할 때만 쓰임
    first_page_index: int = 1
    requires_js: bool = False  # True면 Playwright로 렌더링 후 파싱 (설계안 3.1절 5번)
    link_base_url: str = ""  # link_selector가 상대경로를 반환할 때 urljoin으로 절대경로화


# 아래는 실제로 그 사이트를 열어서 확인한 뒤 채운 항목들임 — 각 항목 주석에 검증 방법과
# 날짜를 남겨서, 사이트 구조가 바뀌었을 때 "언제 기준으로 맞았던 설정인지" 알 수 있게 함.

SITES: list[BoardConfig] = [
    # 2026-08-05 검증: curl로 원문 HTML을 직접 받아 "Total : 31 / Today : 0" 문구와
    # td.title a 링크 구조, GotoPage=N 페이지네이션을 확인함. harness/collect_links.py로
    # 실제 수집까지 돌려서 수집 31건 == 게시판 표시 31건 일치 확인(1~4페이지, 10건/페이지).
    # 학생과가 장학·학자금 업무를 겸해서 이 게시판에 정원 공지·학사 공지와 장학 공지가 섞여
    # 있음 — extract.py의 LLM 추출 단계가 장학금이 아닌 공지는 대부분 필드를 비워서
    # 반환할 것이므로(원문에 해당 근거가 없어서), verify.py에서 자연스럽게 "빈 값 많음"으로
    # 걸러지긴 하지만 완전한 사전 필터는 아님 — 이후 리뷰 마크다운에서 사람이 최종 판단.
    BoardConfig(
        university="충남대학교",
        board_name="학생과 공지사항(장학·학자금 포함)",
        department=None,
        list_url_template=(
            "https://plus.cnu.ac.kr/_prog/_board/"
            "?code=support_030401&site_dvs_cd=hub&menu_dvs_cd=030401&GotoPage={page}"
        ),
        link_selector="td.title a",
        total_count_pattern=r"Total\s*:\s*(\d+)",
        items_per_page=10,
        requires_js=False,
        link_base_url="https://plus.cnu.ac.kr/_prog/_board/",
    ),
]

# 채우는 방법(다음 대학 온보딩 시 참고) — 아래는 형태만 보여주는 예시, 실제로 검증 안 됐으니
# 그대로 쓰지 말 것:
#
# BoardConfig(
#     university="한밭대학교",
#     board_name="교내장학공지",
#     department=None,
#     list_url_template="https://www.hanbat.ac.kr/kor/8320/subview.do?page={page}",
#     link_selector="table.board-list td.title a",
#     total_count_pattern=r"전체\s*(\d+)\s*건",
#     items_per_page=15,
#     requires_js=False,
#     link_base_url="https://www.hanbat.ac.kr",
# ),


def universities_in_order() -> list[str]:
    """SITES에 등록된 순서대로 대학 이름 목록(중복 제거) — run.py의 로테이션 기준."""
    seen: list[str] = []
    for site in SITES:
        if site.university not in seen:
            seen.append(site.university)
    return seen


def boards_for(university: str) -> list[BoardConfig]:
    return [s for s in SITES if s.university == university]
