-- id=1042, 1125, 679, 680에 오늘(2026-08-21) 잘못 채워넣은 min_credits_last_semester를
-- 되돌림. 호성이 2026-08-18 fix_backfill_min_credits_last_semester_2026-08-18.py에서 이미
-- 세워둔 원칙과 어긋났던 실수였음: "min_credits_last_semester"는 정확히 "직전학기(방금 끝난
-- 학기) 이수학점"을 뜻하는 필드인데, 원문에 "직전학기"/"매학기"/"학기별" 같은 명시적인
-- 시간 표현이 없이 그냥 숫자만 있으면(예: "12학점 이상") 그게 매 학기 기준인지 누적 총
-- 학점 기준인지 원문만으로 확정할 수 없음 — 이 프로젝트가 예전에 이런 식으로 넘겨짚다가
-- 틀린 적이 있어서(id=996류는 "학기별"이 명시돼 있어 안전, id=1042/1125류는 그 말이 없어
-- 호성이 의도적으로 제외해둔 것) 호성은 이 4건을 전부 빈칸(NULL)으로 남겨뒀었음.
--
-- id=1042, 1125: "OO학점 이상(신입생 면제)" — 시간 표현 자체가 없음.
-- id=679, 680: "해당학기 12학점 이상" — "해당학기"는 "직전학기"와 정확히 같은 말이 아님
--   (지금 신청/등록하는 학기로도 읽힐 수 있음) — 호성도 이 2건은 원문 첨부파일 추출 실패로
--   "확인 불가"로 남겨뒀었음.
--
-- 빈칸으로 두면 매칭 로직의 기존 leniency(모르는 조건은 통과시킴)에 의해 자동으로
-- 과다조건(노란색 표시)으로 처리되어 안전함 — matching_gaps.md류 원칙과 동일.
UPDATE scholarship SET min_credits_last_semester = NULL WHERE id = 1042;
UPDATE scholarship SET min_credits_last_semester = NULL WHERE id = 1125;
UPDATE scholarship SET min_credits_last_semester = NULL WHERE id = 679;
UPDATE scholarship SET min_credits_last_semester = NULL WHERE id = 680;
