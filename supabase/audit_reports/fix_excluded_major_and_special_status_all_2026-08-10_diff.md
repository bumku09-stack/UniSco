
## id=257 특별장학금(신입생)
  excluded_major: None -> '한의예과,군사학과'

## id=1134 계통대학교장학금
  excluded_major: None -> '신학과'

## id=1019 다문화가정학생장학금(영암군)
  required_special_status_all: [] -> ['multicultural_family']
  required_special_status: ['multicultural_family', 'basic_livelihood_recipient', 'near_poor'] -> ['basic_livelihood_recipient', 'near_poor']

## id=1052 북한이탈주민 장학생(인천)
  required_special_status_all: [] -> ['north_korean_defector']
  required_special_status: ['north_korean_defector'] -> ['basic_livelihood_recipient', 'near_poor', 'single_parent_family']
  requires_disability: None -> True