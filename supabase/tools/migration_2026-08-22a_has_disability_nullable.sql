-- 장애인을 필수에서 선택 입력으로 변경(병역과 동일한 패턴) — 안 건드리면 null(모름)로 남아야
-- 하므로 NOT NULL 제약을 없앰.
ALTER TABLE savedspec ALTER COLUMN has_disability DROP NOT NULL;
