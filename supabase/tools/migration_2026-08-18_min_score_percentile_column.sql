-- 2026-08-18 min_score_percentile 컬럼 신설 (백분위 성적 조건을 GPA와 별개 축으로 매칭)
ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS min_score_percentile FLOAT;
