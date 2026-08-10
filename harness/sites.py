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
    # 제목 링크의 href가 "#"/"#view"/"javascript:" 같은 자리표시자고 실제 게시글 ID가 다른
    # 속성에만 있는 사이트용(2026-08-11, 한밭대·배재대는 onclick="fn_xxx('ID')" 형태, 대전대는
    # data-id="ID" 형태 — 셋 다 같은 부류 문제라 하나의 메커니즘으로 처리). id_source_attr +
    # view_url_template은 반드시 같이 설정. id_pattern은 선택 — 있으면 그 속성값에서 정규식
    # 캡처그룹 1개로 ID를 뽑고(예: onclick="fn_search_detail('B0001')"면
    # r"fn_search_detail\('([^']+)'\)"), 없으면 속성값 자체를 ID로 씀(예: data-id="553608").
    # view_url_template은 {id} 플레이스홀더 포함 URL(예: ".../view.do?nttId={id}").
    # collect_links.py의 _extract_links() 참고.
    id_source_attr: str | None = None
    id_pattern: str | None = None
    view_url_template: str | None = None


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
    # 2026-08-11 검증: 한밭대는 학과별 장학공지가 아니라 "학사 및 장학정보" 일반 게시판
    # (전자정부프레임워크 스킨)에 학사공지와 장학공지가 섞여서 올라옴 — CNU와 동일 패턴이라
    # verify.py의 "빈 값 많음" 필터링에 그대로 맡김. robots.txt 확인 결과 이 경로(/bbs/)는
    # 크롤 허용(Disallow에 안 걸림). 이 게시판의 제목 링크는 href가 "#view" 자리표시자고
    # 실제 게시글 ID는 onclick="javascript: fn_search_detail('B0001...'); ..."에만 있어서
    # id_source_attr/id_pattern/view_url_template 조합으로 처리함(collect_links.py 참고) —
    # href만 보는 기존 방식으로는 전부 같은 URL로 뭉개짐. curl로 원문 HTML 직접 받아 확인:
    # - td.subject a 셀렉터로 페이지당 실제 게시글(공지 고정건 중복 제외) 10건 확인
    # - pageIndex=1과 pageIndex=2 요청 결과 게시글 ID가 서로 겹치지 않음(진짜 페이지네이션)
    # - 페이지네이션 위젯의 "마지막페이지"(aria-label="last") 링크가 pageIndex=179 —
    #   총 게시물 수 표시는 없지만 총 페이지 수는 이 링크로 명시적으로 알 수 있어서
    #   total_pages_pattern으로 씀(원칙 1 — 전 페이지를 코드가 끝까지 순회하는 건 동일).
    BoardConfig(
        university="한밭대학교",
        board_name="학사 및 장학정보(일반공지)",
        department=None,
        list_url_template=(
            "https://www.hanbat.ac.kr/bbs/BBSMSTR_000000000042/list.do?mno=sub05_01&pageIndex={page}"
        ),
        link_selector="td.subject a",
        total_pages_pattern=r'aria-label="last"[^>]*pageIndex=(\d+)',
        items_per_page=10,
        requires_js=False,
        id_source_attr="onclick",
        id_pattern=r"fn_search_detail\('([^']+)'\)",
        view_url_template="https://www.hanbat.ac.kr/bbs/BBSMSTR_000000000042/view.do?nttId={id}",
    ),
    # 2026-08-11 검증(배재대학교 온보딩 에이전트가 조사, 이 세션에서 반영): 배재대는
    # "장학공지" 전용 게시판이 따로 있음. robots.txt 확인 결과 이 경로(/kor/article/)는
    # Allow: / 에 포함돼 크롤 허용. 제목 링크가 href="#"에 onclick="article.view('SEQ'); ..."
    # 구조라(한밭대와 동일한 종류의 문제) id_source_attr/id_pattern/view_url_template로 처리함.
    # 원문 HTML 확인: "총 게시물<em>1109</em>건" 문구(정규식 매칭 확인), 페이지당 p.subject a
    # 10건, 1109/10=111페이지와 페이지네이션 위젯 일치. 실제 게시글 URL
    # (https://www.pcu.ac.kr/kor/article/scholarship/{seq}) curl로 200 응답 확인함.
    # 페이지네이션 파라미터는 ?page=가 아니라 ?pageIndex=임 — Article.js의
    # searchForm.pageIndex 필드명으로 확인, ?page=2로 시도했다가 1페이지와 완전히 동일한
    # 결과가 나와서(파라미터 자체가 무시됨) 잘못 짚었던 걸 ?pageIndex=2로 재확인해 바로잡음
    # (겹치는 글 0건으로 진짜 페이지네이션 확인).
    BoardConfig(
        university="배재대학교",
        board_name="장학공지",
        department=None,
        list_url_template="https://www.pcu.ac.kr/kor/article/scholarship?pageIndex={page}",
        link_selector="p.subject a",
        total_count_pattern=r"총\s*게시물<em>(\d+)</em>건",
        items_per_page=10,
        requires_js=False,
        id_source_attr="onclick",
        id_pattern=r"article\.view\('([^']+)'\)",
        view_url_template="https://www.pcu.ac.kr/kor/article/scholarship/{id}",
    ),
    # 2026-08-11 조사(대전대학교 온보딩 에이전트) — 등록 안 함. "장학"/"장학제도" 게시판
    # (mi=3957&bbsId=1853) 자체는 기술적으로 크롤 가능한 것까지 다 확인했음(href="javascript:"
    # + data-id="553041" 형태라 id_source_attr="data-id"로 풀림, "전체 154건"/"1/16페이지"
    # 확인, currPage=1/2 결과 겹치는 글 없음 확인 — 침례신학대 케이스와 달리 기술적 장벽은
    # 없었음). 하지만 대전대 robots.txt가 `Disallow: /*/na/ntt/`로 이 게시판이 속한 경로
    # 전체를 명시적으로 크롤 금지하고 있어서(침례신학대의 `Disallow: /*Board.do`와 같은
    # 성격 — 특정 경로를 콕 집어 막은 것), 기술적으로 우회 가능하다는 이유로 등록하지 않음.
    #
    # 2026-08-11 조사(을지대학교 온보딩 에이전트 + 직접 확인) — 등록 안 함. "공지사항-장학"
    # 게시판(menuno=4005) 자체는 실제로 살아있는 정상 게시판(102페이지, 최신 글 2026-08-10)
    # 이지만 두 가지 문제가 겹침: (1) 제목 링크가 href='###'+onclick="submitForm(this,'view',N)"
    # 구조라 한밭대/배재대와 같은 부류지만, (2) 사이트 자체가 WAF로 막혀 있어서 curl에 일반
    # 브라우저 User-Agent를 안 붙이면 robots.txt조차 400 Bad Request로 거부함 — 하네스는
    # config.REQUEST_USER_AGENT로 스스로를 "UniSco-Harness/1.0"이라고 밝히는 게 원칙이라
    # (config.py 참고), 이 WAF를 통과하려고 브라우저인 척 User-Agent를 위장하는 건 하지
    # 않음. (1)은 이제 풀 수 있는 문제지만 (2) 때문에 어차피 등록 안 함.
    #
    # 2026-08-11 검증(목원대학교 온보딩 에이전트가 조사, 이 세션에서 반영): 목원대 홈
    # (mokwon.ac.kr) 상단메뉴 → 알림마당 하위에 sub06/0601(일반공지), 0602(학사공지),
    # 0603(장학공지)가 각각 별도 게시판으로 존재함을 확인. 0603.html의 <title>목록 > 장학공지
    # > 알림마당 > 목원대학교</title>로 장학 전용 게시판임을 재확인. curl로 원문 HTML을 직접
    # 받아 "총 <strong>1952</strong>건" 문구(총건수)와 td.title a 링크 구조, ?mode=L&GotoPage=N
    # 페이지네이션(마지막 페이지 131)을 확인함. 1페이지에서 td.title a 링크 15개 수집 →
    # items_per_page=15와 일치. 2페이지도 curl로 받아 1페이지와 겹치는 no= 값이 0개임을
    # 확인(같은 페이지 반복 아님, GotoPage 파라미터가 실제로 동작). 마지막 131페이지를 curl로
    # 받아 링크 2개 확인 → 130*15+2=1952로 총건수와 정확히 일치. 이 사이트는 SSR HTML에
    # 목록이 그대로 내려오므로(JS 렌더링 불필요) requires_js=False. robots.txt는 /search/,
    # /convert/만 막아서 이 경로는 크롤 허용.
    BoardConfig(
        university="목원대학교",
        board_name="장학공지",
        department=None,
        list_url_template=(
            "https://www.mokwon.ac.kr/kr/html/sub06/0603.html?mode=L&GotoPage={page}"
        ),
        link_selector="td.title a",
        total_count_pattern=r"총\s*<strong>(\d+)</strong>\s*건",
        items_per_page=15,
        requires_js=False,
        link_base_url="https://www.mokwon.ac.kr/kr/html/sub06/0603.html",
    ),
    # 2026-08-11 검증(우송대학교 온보딩 에이전트가 조사, 이 세션에서 반영): 우송대학교 메인
    # 포털(www.wsu.ac.kr)은 curl로 루트나 board/read.jsp를 열어도 SSO(sso.wsu.ac.kr)로 302
    # 리다이렉트된 뒤 "failureCause=unauthorized&status=failure"로 떨어져서 로그인 없이는
    # 아예 못 읽음 — 그래서 학생복지처 장학팀이 올리는 학교 공식 공지사항 게시판은 이번엔
    # 대상에서 제외. 대신 힌트로 준 wsjanghak.wsu.ac.kr("우송장학" = 우송장학회, 대학 부설
    # 장학재단)은 SSO 없이 열림. 그 홈에서 메뉴 링크를 직접 훑어 code=wsjanghak0401이
    # "공지사항"(장학생 선발 공고류)이고 나머지(wsjanghak0301/0302/0402)는 갤러리·연수소감문·
    # 커뮤니티라 장학공지가 아님을 확인함. curl로 원문 HTML을 받아 "Total :
    # <font color="blue">5</font> 건" 문구를 확인(정규식은 태그를 건너뛰게 작성),
    # table.table-hover(데스크톱 표, hidden-sm hidden-xs로 모바일 <ul>과 안 겹침) 안의
    # span.title a 5개가 정확히 Total 5건과 일치함도 확인. board/index.jsp?...&page= 파라미터명은
    # wsjanghak0401 자체가 5건짜리 단일 페이지라 안 드러나서, 같은 플랫폼(board/index.jsp)을 쓰는
    # global.wsu.ac.kr의 다건(Total:125) 게시판에서 페이지네이션 링크가 실제로 `?page=2&code=...`
    # 형태로 나오는 걸 확인한 뒤 그 파라미터명을 여기 그대로 적용함. 마지막으로 wsjanghak0401에
    # &page=2를 직접 넣어 요청하면 게시글 0건(빈 목록)이 나오는 것도 확인해서 — 페이지 파라미터가
    # 실제로 존중되고 1페이지가 그냥 반복되는 게 아님, 즉 "총 5건 · 1페이지"가 진짜라는 걸
    # 재확인. 우송장학회 자체 공고라 매년 1건씩만 올라오는 소규모 게시판(연 1회 "OOOO학년도
    # 우송장학회 장학생 선발 공고")이라 학교 전체 장학공지 대비 커버리지는 좁음 — 학생복지처
    # 장학팀의 공식 공지 게시판은 SSO 뒤에 있어 지금은 크롤 불가라는 점을 리뷰어가 참고할 것.
    # robots.txt는 문서 확장자(xls/hwp 등)만 막아서 이 경로는 크롤 허용.
    BoardConfig(
        university="우송대학교",
        board_name="우송장학회 공지사항",
        department=None,
        list_url_template=(
            "https://wsjanghak.wsu.ac.kr/board/index.jsp?code=wsjanghak0401&page={page}"
        ),
        link_selector="table.table-hover span.title a",
        total_count_pattern=r"Total\s*:\s*<font[^>]*>(\d+)</font>",
        items_per_page=10,
        requires_js=False,
        link_base_url="https://wsjanghak.wsu.ac.kr/board/",
    ),
    # 2026-08-11 검증(한남대학교 온보딩 에이전트가 조사, 이 세션에서 반영): 기존(비자동) 장학
    # 데이터가 참조하던 http://janghak.hannam.ac.kr/(장학팀 전용 서브도메인)를 curl로 열어
    # 메인 페이지의 "장학공지 전체보기" 링크를 따라가서 https://janghak.hannam.ac.kr/sub4/menu_1.html
    # 이 실제 장학공지 게시판임을 확인함. 원문 HTML(euc-kr, iconv로 확인)에 "총
    # <strong>1,631건</strong>의 게시물이 있습니다"와 "페이지 <strong>1</strong>/135"이 있고,
    # table.simple-type 안 td.txt-l a가 목록 링크임을 확인(페이지1: 24개 링크 — "공지" 라벨
    # 12개 + 번호 매겨진 일반글 12개, 실제 화면 행 수와 일치). ?pPageNo={page}&pRowCount=12 로
    # 페이지2를 불러와 pPostNo가 페이지1과 전혀 겹치지 않는 걸 확인했고, 페이지 표시도 "2/135"로
    # 바뀜. 3,4,5,6,10,50,100,134,135페이지도 열어 링크 수를 셈: "공지" 라벨 글은 페이지1(12개)·
    # 페이지2(2개)에만 나오고 이후론 0개, 번호 매겨진 일반글은 3~134페이지 각 12개·135페이지
    # (마지막) 9개 — 합산하면 14(공지) + 1617(일반) = 1631로 게시판이 표시하는 총 1,631건과
    # 정확히 일치함(전 페이지 순회해도 중복/누락 없음 확인). total_count_pattern 대신
    # total_pages_pattern을 쓴 이유: "1,631"처럼 천단위 콤마가 들어간 문구라 collect_links.py의
    # int(m.group(1))이 그대로 깨짐(콤마 포함 문자열은 int() 변환 불가) — "135"는 콤마 없이
    # 안전하게 파싱됨. 게다가 페이지1·2에 "공지" 라벨 글이 12/page 기준보다 더 얹혀 나오는
    # 구조라 total_count_pattern+items_per_page(=12)로 역산하면 ceil(1631/12)=136페이지가 되어
    # 실제 페이지 수(135)와 어긋남 — 사이트가 직접 보여주는 "135"를 그대로 쓰는 쪽이 맞음.
    # robots.txt 없음(404) — 크롤 제한 명시 안 돼 있어 기본적으로 허용.
    BoardConfig(
        university="한남대학교",
        board_name="장학팀 장학공지",
        department=None,
        list_url_template=(
            "https://janghak.hannam.ac.kr/sub4/menu_1.html?pPageNo={page}&pRowCount=12"
        ),
        link_selector="table.simple-type td.txt-l a",
        total_pages_pattern=r"페이지\s*<strong[^>]*>\d+</strong>/(\d+)",
        items_per_page=12,
        requires_js=False,
        link_base_url="https://janghak.hannam.ac.kr",
    ),
    # 2026-08-11 검증(KAIST 온보딩 에이전트가 조사, 이 세션에서 반영): KAIST는 다른 대학과
    # 달리 학과가 ~40개로 흩어져 있어 "학교 공통 게시판 1곳"으로 끝나지 않음. 아래는 부분
    # 커버리지임 — 조사한 범위와 판단 근거를 남김:
    #
    # 1) 학교 공통 후보 — www.kaist.ac.kr "학사공지"(kr/html/footer/0802.html, /_prog/bbs
    #    프레임워크, curl로 원문 확인). 페이지네이션(GotoPage=N, 마지막 39페이지)과
    #    "총 <strong>573</strong>건" 총건수 문구까지 구조적으로는 CNU와 동일하게 멀쩡히
    #    검증됨. 하지만 이 게시판이 실제로 장학 공지를 담는지 그 사이트 자체 검색
    #    기능(sval=장학/교내장학/특별장학/성적장학 등)으로 확인해보니, 573건 전체 역사를
    #    통틀어 "장학" 매치가 1건(그나마 2016년 국가장학금 안내글)뿐이고 나머지 검색어는
    #    전부 0건 — 등록금 납부·학번확인·수강신청 같은 학사 행정 공지 전용 게시판이라
    #    장학 신호가 사실상 없음. CNU 학생과 게시판처럼 "장학 공지가 섞여 있는" 케이스가
    #    아니라서 여기 등록하지 않음(구조는 멀쩡해도 이 프로젝트 목적엔 안 맞는 게시판).
    #    edu/03110501~04.html("장학안내")은 정책·지급기준 설명 정적 페이지일 뿐 게시판이
    #    아님(페이지네이션·총건수 문구 없음) — 확인 후 제외.
    #    → 학교 공통 장학 게시판은 못 찾음. 후속 조사 필요(학생처/장학복지팀이 별도
    #    시스템(포털 로그인 뒤)을 쓸 가능성 있음 — 이번 조사에서는 못 들어가 봄).
    #
    # 2) 학과 페이지 3곳 확인(chem/mse/nuclear):
    #    - chem.kaist.ac.kr/scholarship: curl로 원문 확인, 페이지네이션·총건수 문구 없이
    #      학과 자체 장학금 4종(우수논문상 등)을 dl 목록으로 하드코딩한 정적 페이지.
    #      한밭대 사례처럼 게시판이 아니라서 제외.
    #    - nuclear.kaist.ac.kr/informaiton/scholarship.php: curl로 원문 확인, 마찬가지로
    #      장학금별 선발시기·인원·대상·지급액을 표로 정리한 정적 페이지(날짜 없음,
    #      페이지네이션 없음). 제외. (참고: 이 학과의 진짜 게시판은 /board/notice.php인데
    #      이번 조사 범위 밖이라 미확인 — 후속 조사 후보.)
    #    - mse.kaist.ac.kr: 전용 "/scholarship" 경로는 없고 홈페이지에 "Scholarship" 정적
    #      서브페이지(mid=page_LDvo64, 미확인)와 별도로 학과 공지 게시판
    #      "mse_notice"(XpressEngine, mid=mse_notice)가 있음 — 아래 등록.
    #
    # → 결론: 이번 커밋은 KAIST 신소재공학과(MSE) 학과 공지 게시판 1곳만 등록. 학교 공통
    #   장학 게시판과 나머지 ~39개 학과는 전부 미커버 — 학과별 전수 조사는 후속 작업으로
    #   남겨둠.
    #
    # mse_notice 검증 내역: curl로 원문 HTML 확인. XpressEngine 게시판이라 "총 N건" 문구는
    # 없고 대신 페이지 이동 위젯에 `<input type="text" name="page" class="itx" />/ 4`
    # 형태로 총 페이지 수가 박혀 있어 그걸로 total_pages_pattern을 만듦(마지막 페이지가
    # 실제로 4임을 4페이지를 직접 열어 번호 1~6 게시글로 끝나는 것까지 확인). td.title a로
    # 뽑히는 링크 수가 페이지별 <td class="title"> 개수·고유 document_srl 개수와 정확히
    # 일치함(1페이지 22개, 2페이지 29개 — 모두 절대경로라 link_base_url 불필요). 상단
    # "공지"로 고정된 글 9개가 모든 페이지에 중복 노출되는데, collect_links.py가 URL 기준
    # 중복 제거를 이미 하므로 문제 없음. 실제 최근 글 목록에 "Merck International Graduate
    # Fellowship", "[삼성디스플레이] KAIST-EPSD 장학생 모집" 등 2026년 장학 공고가 다수
    # 섞여 있어 장학 신호가 충분히 확인됨. robots.txt 없음(404) — 크롤 제한 명시 안 돼 있어
    # 기본적으로 허용.
    BoardConfig(
        university="KAIST",
        board_name="신소재공학과 공지사항(장학 공고 포함)",
        department="신소재공학과",
        list_url_template="https://mse.kaist.ac.kr/index.php?mid=mse_notice&page={page}",
        link_selector="td.title a",
        total_pages_pattern=r'name="page" class="itx"\s*/>\s*/\s*(\d+)',
        requires_js=False,
        link_base_url="",
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
