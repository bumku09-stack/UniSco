-- 2026-08-11: 찜하기(북마크) 기능. 로그인한 유저가 장학금을 저장해두는 새 테이블.
-- 별도 boolean 컬럼 없이 행 존재 여부로 찜 상태를 표현함(찜=행 추가, 취소=행 삭제) —
-- backend/app/models/saved_scholarship.py, app/api/scholarships.py의 save/unsave 참고.
--
-- 실행 방법: python run_sql.py migration_2026-08-11_saved_scholarship.sql

CREATE TABLE savedscholarship (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "user" (id),
    scholarship_id INTEGER NOT NULL REFERENCES scholarship (id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_savedscholarship_user_scholarship
    ON savedscholarship (user_id, scholarship_id);
CREATE INDEX ix_savedscholarship_user_id ON savedscholarship (user_id);
ALTER TABLE savedscholarship ENABLE ROW LEVEL SECURITY;
