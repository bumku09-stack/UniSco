-- 병역을 필수에서 선택 입력으로 변경 — 이미 골라둔 걸 다시 눌러서 선택 해제하면(모름) null로
-- 저장돼야 하므로 NOT NULL 제약을 없앰.
ALTER TABLE savedspec ALTER COLUMN military_status DROP NOT NULL;
