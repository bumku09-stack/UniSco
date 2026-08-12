-- 2026-08-11: 비밀번호 재설정 기능. emailverification과 구조 동일한 별도 테이블 —
-- 이메일 인증(가입 완료용)과 비밀번호 재설정(이미 가입된 계정 보안 동작)을 섞지 않으려고
-- 분리함. backend/app/models/user.py의 PasswordReset, app/api/auth.py의
-- forgot-password/reset-password 참고.
--
-- 실행 방법: python run_sql.py migration_2026-08-11b_password_reset.sql

CREATE TABLE passwordreset (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "user" (id),
    code VARCHAR NOT NULL,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_used BOOLEAN NOT NULL,
    attempts INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_passwordreset_user_id ON passwordreset (user_id);
ALTER TABLE passwordreset ENABLE ROW LEVEL SECURITY;
