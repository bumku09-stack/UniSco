-- 어학점수를 시험 하나(language_test_type/language_test_score)에서 여러 개(JSONB 배열)로
-- 변경 — 기존 값(있다면)은 1개짜리 배열로 감싸서 보존.
ALTER TABLE savedspec ADD COLUMN language_tests JSONB NOT NULL DEFAULT '[]';
UPDATE savedspec
SET language_tests = jsonb_build_array(
  jsonb_build_object('type', language_test_type, 'score', language_test_score)
)
WHERE language_test_type IS NOT NULL AND language_test_score IS NOT NULL;
ALTER TABLE savedspec DROP COLUMN language_test_type;
ALTER TABLE savedspec DROP COLUMN language_test_score;
