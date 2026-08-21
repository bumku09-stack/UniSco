-- id=679/680(고리원자력본부장학) "해당학기 12학점 이상" — 매칭.py 리뷰 중 "완료된 직전학기
-- 기준인지, 신청 중인 학기 기준인지" 애매하다고 보류했던 항목. 사용자 확인(2026-08-21):
-- 직전학기 기준으로 잡고 그대로 구조화하기로 결정.
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 679;  -- "해당학기 12학점 이상" (일반장학생)
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 680;  -- "해당학기 12학점 이상" (특별장학생)
