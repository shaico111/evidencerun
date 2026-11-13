# Source comparison: Ask Ubuntu vs Server Fault (Stack Exchange dump, Internet Archive ~2024-04)

All rates are **automated** (rules in scripts/temporal.py) unless stated. They are NOT human-verified. Frame = Stage-A filter (config.json), computed over the FULL dumps (not a sample). Stack Overflow was not run (the two sites already give a large frame; no insufficiency).

## Funnel (full dump)
| site | step | count |
|---|---|---:|
| askubuntu | all_posts_rows | 945,111 |
| askubuntu | questions | 414,451 |
| askubuntu | questions_with_AcceptedAnswerId | 136,162 |
| askubuntu | accepted_id_resolves_to_answer_of_same_question | 136,151 |
| askubuntu | and_troubleshooting_lexical_filter | 97,375 |
| askubuntu | and_question_body_>=20_words | 96,593 |
| askubuntu |   of which: no PostHistory rows at all | 0 |
| askubuntu |   of which: PostHistory lacks Initial Body (type 2) | 0 |
| askubuntu | and_>=1_pre_first_answer_comment_or_body_edit  == STAGE-A FRAME | 53,158 |
| serverfault | all_posts_rows | 844,092 |
| serverfault | questions | 325,169 |
| serverfault | questions_with_AcceptedAnswerId | 153,269 |
| serverfault | accepted_id_resolves_to_answer_of_same_question | 153,246 |
| serverfault | and_troubleshooting_lexical_filter | 106,153 |
| serverfault | and_question_body_>=20_words | 105,853 |
| serverfault |   of which: no PostHistory rows at all | 0 |
| serverfault |   of which: PostHistory lacks Initial Body (type 2) | 4 |
| serverfault | and_>=1_pre_first_answer_comment_or_body_edit  == STAGE-A FRAME | 42,424 |

### askubuntu (Stage-A frame = 53,158)

| metric (automated) | simple-random audit sample n=100 | seeded pool n=2000 |
|---|---|---|
| ≥2 states | 42/100 = 42.0% (95% CI 32.8-51.8%) | 785/2000 = 39.2% (95% CI 37.1-41.4%) |
| ≥3 states | 16/100 = 16.0% (95% CI 10.1-24.4%) | 310/2000 = 15.5% (95% CI 14.0-17.2%) |
| accepted answer auto-self-contained | 84/100 = 84.0% (95% CI 75.6-89.9%) | 1757/2000 = 87.8% (95% CI 86.3-89.2%) |
| ≥2 states AND self-contained AND no leakage flag | 31/100 = 31.0% (95% CI 22.8-40.6%) | 588/2000 = 29.4% (95% CI 27.4-31.4%) |
| ≥3 states AND self-contained AND no leakage flag | 12/100 = 12.0% (95% CI 7.0-19.8%) | 218/2000 = 10.9% (95% CI 9.6-12.3%) |
| leakage suspected (automated) | 14/100 = 14.0% (95% CI 8.5-22.1%) | 243/2000 = 12.2% (95% CI 10.8-13.7%) |
| accepted answer is the first answer | 82/100 = 82.0% (95% CI 73.3-88.3%) | 1658/2000 = 82.9% (95% CI 81.2-84.5%) |
| accepted answer written by the asker | 26/100 = 26.0% (95% CI 18.4-35.4%) | 543/2000 = 27.1% (95% CI 25.2-29.1%) |
| final body has ≥5 tokens not in initial body (later additions) | 44/100 = 44.0% (95% CI 34.7-53.8%) | 924/2000 = 46.2% (95% CI 44.0-48.4%) |

Projection (automated, NOT precision-adjusted): ≥2 & self-contained & leak-free ≈ 15,628 threads (95% CI of the pool rate × frame: 14,589–16,710); ≥3: 5,794 (5,108–6,561). Distinct target answers in the pool: 588.

### serverfault (Stage-A frame = 42,424)

| metric (automated) | simple-random audit sample n=100 | seeded pool n=2000 |
|---|---|---|
| ≥2 states | 37/100 = 37.0% (95% CI 28.2-46.8%) | 743/2000 = 37.1% (95% CI 35.1-39.3%) |
| ≥3 states | 7/100 = 7.0% (95% CI 3.4-13.7%) | 257/2000 = 12.8% (95% CI 11.5-14.4%) |
| accepted answer auto-self-contained | 88/100 = 88.0% (95% CI 80.2-93.0%) | 1796/2000 = 89.8% (95% CI 88.4-91.1%) |
| ≥2 states AND self-contained AND no leakage flag | 28/100 = 28.0% (95% CI 20.1-37.5%) | 605/2000 = 30.2% (95% CI 28.3-32.3%) |
| ≥3 states AND self-contained AND no leakage flag | 4/100 = 4.0% (95% CI 1.6-9.8%) | 202/2000 = 10.1% (95% CI 8.9-11.5%) |
| leakage suspected (automated) | 14/100 = 14.0% (95% CI 8.5-22.1%) | 184/2000 = 9.2% (95% CI 8.0-10.5%) |
| accepted answer is the first answer | 79/100 = 79.0% (95% CI 70.0-85.8%) | 1555/2000 = 77.8% (95% CI 75.9-79.5%) |
| accepted answer written by the asker | 23/100 = 23.0% (95% CI 15.8-32.2%) | 555/2000 = 27.8% (95% CI 25.8-29.8%) |
| final body has ≥5 tokens not in initial body (later additions) | 44/100 = 44.0% (95% CI 34.7-53.8%) | 843/2000 = 42.1% (95% CI 40.0-44.3%) |

Projection (automated, NOT precision-adjusted): ≥2 & self-contained & leak-free ≈ 12,833 threads (95% CI of the pool rate × frame: 11,996–13,703); ≥3: 4,285 (3,757–4,878). Distinct target answers in the pool: 605.

## Precision check of the automated "≥2 valid states" flag (LLM-assisted, single reviewer — NOT an independent human)
Fresh set (rows not used to design the rules): 16/20 = 80.0% (95% CI 58.4-91.9%) judged to have ≥2 genuine states; leak-free: 15/20 = 75.0% (95% CI 53.1-88.8%); accepted answer judged relevant: 19/20 = 95.0% (95% CI 76.4-99.1%). Pre-tightening tuning sample (n=18) is excluded because the rules were adjusted after viewing it. Among 41 reviewed threads 4 were not troubleshooting questions (lexical filter false positives).
Precision-adjusted ≥2-state share of the frame (pool rate × precision, ranges from the two CIs): AU ≈ 23–36%, SF ≈ 22–34% (crude product of two intervals; the 20-row review has wide uncertainty and misses false negatives entirely).
