
## id=21 진학우수(일반대학원)
  min_gpa_basis: None -> 'cumulative'

## id=22 진학격려(일반대학원)
  min_gpa_basis: None -> 'cumulative'

## id=14 대전·충청 장학금(신입생)
  major: '인문계: 국어·영어 3등급 이내 / 자연계: 수학·영어 3등급 이내' -> None
  admission_score_condition: '전공란 조건 참고' -> '인문계: 국어·영어 3등급 이내 / 자연계: 수학·영어 3등급 이내'

## id=59 학생활동 장학금(재학생)
  required_special_status: [] -> ['student_council_officer']

## id=74 2026년 화성시인재육성재단 소상공인 장학금
  required_special_status: [] -> ['parent_occupation_condition']

## id=77 2026학년도 의암 손병희 우수논문 장학생
  required_enrollment_status: 'undergrad_enrolled' -> None

## id=94 2026년 푸른등대 삼성기부장학금(대학생)
  required_special_status: [] -> ['religious_or_career_intent_condition']

## id=95 2026년 푸른등대 삼성기부장학금(대학원생)
  major: None -> '인문사회계열'

## id=110 학생자치단체 간부장학금(회장/비상대책위원장)
  required_special_status: [] -> ['student_council_officer']

## id=111 학생자치단체 간부장학금(부회장/부비상대책위원장)
  required_special_status: [] -> ['student_council_officer']

## id=112 학생자치단체 간부장학금(임원진/학과대표)
  required_special_status: [] -> ['student_council_officer']

## id=114 김영한글로벌리더 장학금
  required_enrollment_status: 'undergrad_enrolled' -> None

## id=122 미산등산장학금(7회 이상)
  required_enrollment_status: 'undergrad_enrolled' -> None

## id=123 미산등산장학금(3~6회)
  required_enrollment_status: 'undergrad_enrolled' -> None

## id=151 일반유학장학금(국립대학부외)
  language_test_type: None -> 'TOPIK'
  language_test_min_score: None -> 3.0
  min_gpa: None -> 3.0

## id=152 일반유학장학금(국제학부)
  language_test_type: None -> 'IELTS'
  language_test_min_score: None -> 6.0
  min_gpa: None -> 3.0

## id=217 진리장학금
  headcount: None -> '3명'

## id=218 자유장학금
  headcount: None -> '6명'

## id=226 튜터장학금
  min_grade: None -> 3
  max_grade: None -> 4

## id=228 글로벌인재장학금(한남대)
  min_grade: None -> 1
  max_grade: None -> 1
  headcount: None -> '1명'

## id=231 농어촌학생장학금(한남대)
  headcount: None -> '1명'

## id=232 기초생활수급자·차상위계층장학금(한남대, 신입생)
  headcount: None -> '1명'

## id=234 외국인장학금(한남대)
  min_grade: 1 -> None
  max_grade: 1 -> None

## id=238 환경미화원자녀장학금
  min_grade: None -> 1
  max_grade: None -> 1

## id=239 동문자녀장학금(한남대)
  min_grade: None -> 1
  max_grade: None -> 1

## id=254 전북 향토인재 장학생
  application_deadline: None -> datetime.date(2026, 4, 12)

## id=294 융합인재장학금(대전대)
  headcount: None -> '70명 이내'
  admission_score_condition: '총 70명 이내' -> None

## id=297 대한민국 인재상
  application_deadline: None -> datetime.date(2026, 8, 19)

## id=316 차세대의료인장학금(일현육성)
  min_grade: None -> 3
  max_grade: None -> 6

## id=641 의생명과학분야대학원장학생
  required_degree_level: 'masters' -> None
  required_enrollment_status: None -> 'post_undergrad'

## id=642 해외의생명과학분야대학원장학생
  required_degree_level: 'masters' -> None
  required_enrollment_status: None -> 'post_undergrad'

## id=644 보건의료정책분야대학원장학생
  required_degree_level: 'masters' -> None
  required_enrollment_status: None -> 'post_undergrad'
  application_url: 'https://www.asanfoundaton.or.kr' -> 'https://www.asanfoundation.or.kr'

## id=646 관정재단 대학원장학생
  required_degree_level: 'masters' -> None
  required_enrollment_status: None -> 'post_undergrad'

## id=358 민유선교수기념장학금
  major: None -> '신학'

## id=532 대학생학자금대출이자지원(아산)
  max_age: 30 -> 29

## id=651 수림재단 신규장학생
  major: None -> '물리학과,화학과,생물학과,수학과,의예과'

## id=653 보훈장학금(대학원장학)
  required_special_status: [] -> ['national_merit']

## id=654 보훈장학금(대학장학)
  required_special_status: [] -> ['national_merit']

## id=672 숲과나눔 인재양성 프로그램(글로벌리더십)
  foreigner_eligibility: None -> 'foreigner_only'

## id=683 양양양수발전소주변지역장학금(주민자녀)
  eligible_region: '양양군' -> '양양군,인제군'

## id=942 일반대학생장학금(마루)
  min_credits: None -> '12학점'

## id=945 농어촌목회자자녀및신학생
  application_deadline: None -> datetime.date(2026, 4, 9)

## id=947 자매애청년장학금
  application_deadline: None -> datetime.date(2026, 4, 9)

## id=954 성적우수장학생(안동시)
  application_deadline: None -> datetime.date(2026, 4, 3)

## id=956 특별장학생(안동시)
  application_deadline: None -> datetime.date(2026, 4, 3)

## id=957 특기장학생(안동시)
  application_deadline: None -> datetime.date(2026, 4, 3)

## id=958 다자녀장학생(안동시)
  application_deadline: None -> datetime.date(2026, 4, 3)

## id=955 진학장학생(안동시)
  admission_score_condition: None -> '수능 4개영역 백분위 평균 80점 이상 또는 내신 3개학기 평균 80점 이상'
  application_deadline: None -> datetime.date(2026, 4, 3)

## id=962 성적우수장학생(음성군)
  min_credits: None -> '15학점'
  admission_score_condition: None -> '(신입생) 수능 4개영역 중 3개영역 이상 3등급 이내 또는 고2~3-1 전과목 석차등급평균 3등급 이내'

## id=985 진학장학금(용인시)
  admission_score_condition: None -> '수능성적입학생(한국사+국어+수학+영어+탐구(2) 등급합 12이내)/내신성적입학생(상위10% 이내)'

## id=986 우수장학금(용인시, 대학생)
  min_credits: None -> '12학점'

## id=1028 우선선발 장학생(이공계/전문대, 백운장학회)
  major: '이공계열' -> None

## id=1067 성적우수장학금(일반대학교, 김해시)
  min_credits: None -> '12학점'

## id=1069 기업체근로자자녀장학금(김해시)
  min_grade: 3 -> None

## id=1072 성적우수장학생(공주시)
  min_credits: None -> '12학점'

## id=1076 다자녀가정장학생(공주시)
  min_credits: None -> '12학점'

## id=1082 수능성적우수자특별장학생(거창군)
  required_special_status: [] -> ['suneung_score_condition']

## id=1087 거창군지역출신대학생등록금지원
  min_credits: None -> '12학점'

## id=1089 특별장학생(익산사랑)
  min_credits: None -> '12학점'

## id=1096 학업우수장학생(과천시)
  min_credits: None -> '15학점'

## id=1105 특지장학생(임광, 충북인재평생교육진흥원)
  required_enrollment_status: 'undergrad_enrolled' -> None

## id=1116 성적우수장학금(구미시)
  min_grade: 3 -> 2

## id=1117 기회균등장학금(구미시)
  min_grade: None -> 2

## id=1140 생활장학금(울산연구원)
  required_special_status: ['multicultural_family'] -> ['basic_livelihood_recipient', 'near_poor', 'multicultural_family']