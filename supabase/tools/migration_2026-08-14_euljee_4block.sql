-- 을지대학교 18건 4블록(금액/기간/신청방식) 분리

UPDATE scholarship SET
  amount_detail = '학과(전공) 재학생 인원 규모(10~24명/~29명/~50명/~99명/~120명/121~159명/160~190명)별로 순위(1등 최우수~8등 성적우등)에 따라 등록금 전액~1/7까지 차등 지급(인원이 많을수록 선발 인원·등수 구간 확대).',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '직전학기 성적 산정 시 인정성적 기준 적용(P/NP 포함).',
  min_credits_last_semester = 12
WHERE id = 302;

UPDATE scholarship SET
  amount_detail = '50만원 지급',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '직전학기 대비 평점평균(GPA) 1.0 이상 향상된 재학생 대상.'
WHERE id = 303;

UPDATE scholarship SET
  amount_detail = '기초생활수급자·차상위계층: 등록금 전액
소득분위 1~2구간 또는 8구간 이내 다자녀가구: 등록금 1/2
소득분위 3~5구간: 150만원',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '당해학기 국가장학금 신청자 중 소득구간 및 성적 기준 충족자 대상.'
WHERE id = 304;

UPDATE scholarship SET
  amount_detail = '교직원(비전임교원·강사 제외) 직계자녀 또는 노원을지대학교병원·의정부을지대학교병원(의료법인)·학교법인 재직자의 자녀: 등록금 1/2
본교 졸업생의 자녀: 1인당 100만원
가족(형제·자매·남매) 2인 이상 재학 중(휴학자 제외): 1인당 50만원',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = NULL
WHERE id = 305;

UPDATE scholarship SET
  amount_detail = '등록금 전액 지급(대학수업료 등 면제증명서 증빙 시)',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '국가보훈처 지정 보훈대상자 및 그 직계자녀(보훈관련 법령에 의함) 대상.'
WHERE id = 306;

UPDATE scholarship SET
  amount_detail = '등록금 전액 지급(교육지원대상자 증명서·북한이탈주민등록확인서 증빙 시)',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '북한이탈주민(본인 또는 그 자녀 포함, 북한이탈주민법 기준 준수) 대상.'
WHERE id = 307;

UPDATE scholarship SET
  amount_detail = '중증: 등록금 2/3
경증: 등록금 1/2',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '장애인등록증으로 증빙되는 장애 학생 본인 대상.'
WHERE id = 308;

UPDATE scholarship SET
  amount_detail = '100만원 지급',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '중증장애인의 자녀인 재학생 대상(가족관계증명서, 장애인등록증(부모) 증빙).'
WHERE id = 309;

UPDATE scholarship SET
  amount_detail = '평점평균 4.0 이상: 등록금 최소 50% 지원(토픽 성적별 차등, 예: 토픽 6급 80% 감면~)
3.0 이상: 최소 30% 지원(토픽 성적별 차등)
2.0 이상~3.0 미만: 등록금 1/5(20%) 지원
(세종학당 중급2 이수자는 토픽4급, 중급1 이수자는 토픽3급에 준하여 인정, 법무부 사회통합프로그램 이수자도 인정)',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '순수 외국인으로 입학했거나 순수 외국인(외국인유학생)인 재학생 대상, 한국어능력시험(TOPIK) 서류 증빙.'
WHERE id = 310;

UPDATE scholarship SET
  amount_detail = '100만원 지급',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '다문화가정의 자녀인 재학생 대상(부모 중 한 사람 이상이 외국인 또는 귀화자, 가족관계증명서·국적확인서류 증빙).'
WHERE id = 311;

UPDATE scholarship SET
  amount_detail = '총학생회장·부총학생회장: 등록금 전액
단과대 학생회장(학생연합협의회장): 등록금 3/4
학과 학생회장·총학생회 부장: 등록금 2/3
총학생회 차장: 등록금 1/3
홍보대사 "바탕": 개인실적반영 최대 150만원',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '학생자치기구 간부 대상.'
WHERE id = 312;

UPDATE scholarship SET
  amount_detail = '학과/학년/반별 반대표: 40만원
캠퍼스별 사생대표: 30만원
학보사 편집장(3개 캠퍼스 통합 1명): 등록금 2/3
학보사 기자(각 캠퍼스별)·홍보대사 "뉴미디어": 개인실적반영 최대 150만원',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = '학생자치기구 및 특별기구 등에서 학교·학과를 위해 활동하는 자 대상.'
WHERE id = 313;

UPDATE scholarship SET
  amount_detail = '학생봉사단 "빛길" 활동자: 개인실적반영 최대 150만원
재학 중 누적봉사시간 300시간 이상(봉사활동 확인서 증빙): 100만원',
  application_period = '2026년 공고 미확인, 직전 회차: 2025-11-10(월) 자정 마감',
  application_method = 'EIS 온라인 신청(특별장학금 통합신청)',
  description = NULL
WHERE id = 314;

UPDATE scholarship SET
  amount_detail = '100만원 지급',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '재학 중 공인 어학성적 우수자(TOEIC 950, TOEFL 110, TEPS 500, HSK 6급, JLPT 1급 이상) 대상.'
WHERE id = 317;

UPDATE scholarship SET
  amount_detail = '정량+정성 평가 후 최대 50만원 지급',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '재학생의 대학 및 재단 홍보활동(SNS 게시물 등록 및 오프라인 활동 등) 우수자 대상(뉴미디어·바탕 홍보대사 활동자 제외).'
WHERE id = 318;

UPDATE scholarship SET
  amount_detail = '영역당 30만원 지급',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '을지대 HUMAN 핵심역량 인증제(Humanistic(인문)/Universal(글로벌)/Multidisciplinary(창의융합)/Altruistic(봉사헌신)/Networking(소통협업) 5개 영역) 중 우수 인증을 받은 재학생 대상.'
WHERE id = 319;

UPDATE scholarship SET
  amount_detail = '지급액은 사안에 따라 상이(사안별 심사 후 지급)',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청(사안별 심사)',
  description = '재학 중 학교 발전에 크게 공헌하거나 명예를 빛낸 공로가 인정된 자(장관·지자체장급 또는 이에 준하는 수상실적자, 국제규모 각종대회 수상자, 교외 선행/봉사/표창 수상자 등), 재해·긴급한 경제적 어려움 등 지원이 필요하다고 판단되는 자, 그 밖에 총장이 특별한 사유를 인정하는 자.'
WHERE id = 320;

UPDATE scholarship SET
  amount_detail = '최소 100~최대 300 마일리지 신청 가능, 1마일리지당 1,500원 환산(최대 45만원)',
  application_period = '2026-1학기: 2026-05-12~05-20(2026-2학기 미공고)',
  application_method = 'EIS 온라인 신청',
  description = '대학에서 지정한 비교과 프로그램에 참여하고 마일리지 장학금을 신청한 재학생 대상.'
WHERE id = 321;
