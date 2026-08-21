-- 회원가입 인증 흐름 재설계(2026-08-21) — 인증 코드 확인 전까지는 User 테이블에 아무것도
-- 안 만들고 여기 임시로만 보관함. 예전엔 가입 버튼 누르는 순간 바로 User를 만들어서, 오타/
-- 존재하지 않는 이메일로 시도한 계정이 인증 안 된 채로 아이디/이메일을 영구히 점유하는
-- 문제가 있었음(그래서 그날 먼저 시간 기반 자동삭제(ghost_accounts.py)를 만들었었는데,
-- 이 테이블 분리가 그 문제를 애초에 발생하지 않게 만드는 더 근본적인 해결책이라 같이 둠 —
-- ghost_accounts.py는 이제 대부분 상황에서 지울 게 없는 안전망으로만 남음).
--
-- username/email에 유니크 제약을 일부러 안 걸었음 — 아직 확정된 계정이 아니라서 여러 개
-- 겹쳐도 무해함(실제 유니크 검사는 User 테이블에서, 그리고 인증 성공 순간 다시 한번 함 —
-- backend/app/api/auth.py의 verify_code 참고).

CREATE TABLE pendingsignup (
    id SERIAL NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    code VARCHAR NOT NULL,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    attempts INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_pendingsignup_username ON pendingsignup (username);
CREATE INDEX ix_pendingsignup_email ON pendingsignup (email);
ALTER TABLE pendingsignup ENABLE ROW LEVEL SECURITY;
