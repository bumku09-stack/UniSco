# eligibility_alt_groups로 OR 조건 구조화 — 2026-08-15

matching_gaps.md의 두 "코드 변경 없이 데이터 작업만" 항목 반영. 스크립트:
`supabase/tools/fix_or_conditions_alt_groups_2026-08-15.py`

## A. 여러 어학시험 중 하나만 맞으면 되는 조건 (6건)

`LanguageTestType`이 TOEIC/TOEFL/IELTS/TOPIK 4종만 지원(TEPS/HSK/JLPT/TOEIC Speaking은
학생이 선택할 옵션 자체가 없음) — 원문에 이 4종 밖의 시험이 같이 걸려있으면 그 갈래만
제외. 6건 전부 기존엔 `language_test_type`이 NULL(무필터, 전원 노출)이었어서, 일부 갈래만
구조화돼도 순수 개선(전보다 나빠지는 케이스 없음).

| id | 이름 | 구조화된 조건 | 제외된 갈래(미지원 시험) |
|---|---|---|---|
| 52 | 외국어성적우수 장학금(재학생) | TOEIC 900 또는 TOEFL 102 | 없음 |
| 31 | 외국인(대학원) 등록금전액 | TOPIK 5급 또는 TOEFL 95 또는 IELTS 6.5 또는 TOEIC 800 | TEPS 386 |
| 32 | 외국인(대학원) 등록금일부 B급 | TOPIK 4급 또는 TOEFL 71 또는 IELTS 5.5 또는 TOEIC 700 | TEPS 327 |
| 343 | 외국어능력우수장학금(침례신학대) | TOEFL 90 또는 TOEIC 850 | TOEIC Speaking 중상급(질적 등급이라 표현 불가) |
| 197 | 영어능력우수장학금 | TOEIC 900 또는 TOEFL 100 | 없음 |
| 317 | 어학성적우수장학금(을지대학교) | TOEIC 950 또는 TOEFL 110 | TEPS 500, HSK 6급, JLPT 1급 |

## B. 학위과정 "석사 또는 박사" 둘 다 대상인데 단일값이라 배제되던 조건 (7건)

| id | 이름 | 기존 값 | 새 값 |
|---|---|---|---|
| 79 | 2026학년도 3.1장학생(박사과정) | doctoral만 | doctoral 또는 integrated_ms_phd (원문 "석박사통합과정도 준함") |
| 649 | 동아시아연구장학생 | masters만 | masters 또는 doctoral (원문 "...또는 박사과정 재학자") |
| 653 | 보훈장학금(대학원장학) | masters만 | masters 또는 doctoral (원문 "대학원 석/박사과정 재학") |
| 671 | 숲과나눔 인재양성(석·박사과정) | masters만 | masters 또는 doctoral |
| 672 | 숲과나눔 인재양성(글로벌리더십) | masters만 | masters 또는 doctoral |
| 673 | 숲과나눔 인재양성(공익활동가) | masters만 | masters 또는 doctoral |
| 674 | 숲과나눔 인재양성(생물다양성 분야) | masters만 | masters 또는 doctoral |

전부 원문에 석박사통합 언급이 없어서(순수 "석·박사"만) integrated_ms_phd는 추가 안 함 —
근거 없이 추정하지 않는다는 원칙 그대로 적용.

## C. 곁다리로 발견한 별개 버그 1건 — id=678 미래산업 인재 대학원 장학생

원문 "석/박사/석박사통합과정" = 3종 전부 대상인데 `required_degree_level=masters`로
좁혀놓아서 박사·석박사통합 학생이 부당하게 걸러지고 있었음. 3종 전부 대상이면 그냥
"제한 없음"(NULL)이 정확한 값이라 alt_groups 안 쓰고 직접 NULL로 수정.

**남은 문제(이번 스코프 밖, 안 건드림)**: 이 레코드는 `required_enrollment_status`도
NULL이라 학부생한테도 필터링 없이 노출되고 있음 — 대학원 한정 장학금인데. 별도 작업 필요.

## 검증

`core/matching.py`의 `alt_groups_match()`를 실제 함수 호출로 테스트(가짜 학생 스펙 5종 ×
id=52 케이스, 3종 × 학위과정 케이스) — 전부 기대한 대로 통과/탈락 확인 후 반영.

## 최종 결과

14건 대상, 14건 변경 완료(`--apply`로 반영).
