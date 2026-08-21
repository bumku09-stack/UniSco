-- 장애 유형을 특수상황처럼 복수선택 가능하게 변경 — 단일 enum 컬럼을 special_status와
-- 동일한 TEXT[] 컬럼으로 교체. 기존 값(있다면)은 배열로 감싸서 보존.
ALTER TABLE savedspec ADD COLUMN disability_type_new TEXT[] NOT NULL DEFAULT '{}';
UPDATE savedspec SET disability_type_new = ARRAY[disability_type::text] WHERE disability_type IS NOT NULL;
ALTER TABLE savedspec DROP COLUMN disability_type;
ALTER TABLE savedspec RENAME COLUMN disability_type_new TO disability_type;
