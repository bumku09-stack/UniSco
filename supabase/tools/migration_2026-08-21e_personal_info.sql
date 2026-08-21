-- /spec 1단계 "인적정보" 재구성(이름/생년월일 신규 + 주소 검색으로 받은 전체 주소 저장)
-- 전부 nullable — 기존에 저장된 스펙엔 없는 값이라 필수로 두면 안 됨.
ALTER TABLE savedspec ADD COLUMN display_name VARCHAR;
ALTER TABLE savedspec ADD COLUMN birth_date DATE;
ALTER TABLE savedspec ADD COLUMN address VARCHAR;
ALTER TABLE savedspec ADD COLUMN parent_address VARCHAR;
