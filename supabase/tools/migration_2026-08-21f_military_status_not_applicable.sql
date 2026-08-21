-- 병역 선택지에 "해당사항 없음" 추가(SpecialStatus의 NOT_APPLICABLE과 같은 패턴).
ALTER TYPE militarystatus ADD VALUE 'not_applicable';
