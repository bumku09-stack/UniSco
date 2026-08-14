-- 대전 청년 월세지원사업(id=4) 원문(daejeonyouthportal.kr) 재대조 반영
UPDATE scholarship
SET
    amount_detail = '월 최대 20만원씩 최대 12개월 지원(생애 1회). 월세가 20만원 미만이면 실제 납부액만 지급 (총 최대 240만원)',
    application_method = '대전청년포털(daejeonyouthportal.kr) 온라인 신청만 가능. 청년 본인 신청만 가능(부모 등 대리신청 불가)',
    application_period = '신청기간 : 2026-08-31(월) 09:00 ~ 2026-09-10(목) 18:00
선정발표 : 2026-10-30(금) 17:00 예정',
    headcount = '1,000명',
    max_age = 40,
    description = '임차보증금 1억원 이하, 월세 60만원 이하 또는 전월세 환산액 80만원 이하인 주택 임차인. 세대주이면서 무주택자. 건강보험료 고지금액이 기준 중위소득 120% 이하. 소득 기준 점수(60점)+임차료 기준 점수(40점)로 선정.'
WHERE id = 4;
