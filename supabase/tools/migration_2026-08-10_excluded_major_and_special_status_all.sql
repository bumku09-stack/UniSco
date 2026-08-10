-- 2026-08-10: 전공 "제외" 조건 + 특수상황 "AND(전부 만족)" 조건 지원.
-- matching_gaps.md 참고. 기존 데이터/로직에는 영향 없음(둘 다 기본값이 "제한 없음"이라
-- 기존 661건은 지금까지와 동일하게 동작함).

ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS excluded_major VARCHAR;
-- major와 동일한 컨벤션(콤마로 구분). NULL=제외 학과 없음(기존과 동일).

ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS required_special_status_all TEXT[] NOT NULL DEFAULT '{}';
-- 기존 required_special_status(하나만 맞아도 통과, OR)와 별개로, "이건 전부 다 있어야 함"
-- 목록. 빈 배열=추가 AND 조건 없음(기존과 동일). 예: id=1019(영암군 다문화가정학생장학금)
-- "다문화가정 이면서 (기초수급자 또는 차상위)" -> required_special_status_all=['multicultural_family'],
-- required_special_status=['basic_livelihood_recipient','near_poor'] (기존 OR 목록 그대로).
