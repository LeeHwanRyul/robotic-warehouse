# 실험 이력 — PGCT / 잠재 팀 발견

작성: 2026-10-23, Claude Code. 상세 원본은 `EXPERIMENTS.md`의 E번호 항목이다. 이 문서는 주요 실험만 같은 형식으로 다시 정리한다. 숫자가 다르면 원본이 우선한다.

- 환경 설정은 2026-10-23에 각 run의 `checkpoint_00250.pt`의 `effective_env_kwargs`를 직접 읽어 확인했다(읽기 전용).
- 경로는 2026-10-23에 존재를 확인했다. 예외는 E21에서 삭제된 경로이며 따로 표시했다.
- "seed"는 training seed다. 같은 seed의 재실행(E17 → E24)은 독립 seed가 아니다.
- smoke·dry-run·plancheck는 학습 결과가 아니다.

## 1. 공통 설정

### 1.1 보상 구조 [확인: checkpoint의 `effective_env_kwargs`]

모든 from-scratch run에서 아래 값이 같다. 다른 것은 1.2의 표에 적었다.

| 항목 | 값 |
|---|---|
| 배송 `delivery_reward` | +1.0 |
| 반납 `shelf_return_reward` | +1.0 (`require_delivered_shelf_return=True`) |
| 자기 팀 요청 선반 pickup `requested_shelf_pickup_reward` | +0.15 |
| 진척 shaping | `requested_shelf_progress_reward` .002, `goal_progress_reward` .005, `return_progress_reward` .02 |
| 다른 팀 요청 선반 pickup `wrong_shelf_pickup_penalty` | −.05 |
| 비요청 선반 pickup `unrequested_shelf_pickup_penalty` | −.02 / 0 / −.005 (run마다 다름) |
| 조기 내려놓기 `premature_drop_penalty` | −.02 / 0 / −.005 (run마다 다름) |
| 기타 감점 | 잘못된 반납 .005, 잘못된 TOGGLE .002, 전진 실패 .005, NOOP .003, 반복 정지(5 step 뒤) .006, 교착(5 step 뒤) .02, 막기 .01 |
| `team_reward_mode` | individual: 자기 보상만. team: 배송·반납 보상이 팀 전원에게 가고 shaping은 개인으로 남는다(E25) |

### 1.2 환경 계보

공통: 11×10 지도, `shelf_columns` 3, `column_height` 8, `sensor_range` 5, `home_ratio` .5, `shelf_team_mode` balanced_soft_zones, 500 step episode.

| 이름 | agent | 통신 | goal (팀1 / 팀2) | 보상 | 감점 p | 요청(전체 / 팀당) | 대표 run |
|---|---|---|---|---|---|---|---|
| E1 | 4 (2+2) | 5 | 인접 (4,10)/(5,10) | 개인 | .02 | 4 / 2 | `runs/scratch_20261015_093349_stage2` |
| E1-F | 4 | 5 | 모서리 (0,10)/(9,10) | 개인 | .02 | 4 / 2 | `runs/e1f_20261018_124343_main_*` |
| A `a_e1f4_team` | 4 | 5 | 모서리 | 팀 | .02 | 4 / 2 | `runs/pilot_20261019_180044_a_e1f4_team` |
| B `b_e1f6_comm3` | 6 (3+3) | 3 | 모서리 | 팀 | .02 | 6 / 3 | `runs/pilot_20261019_180044_b_e1f6_comm3` |
| B nopen | 6 | 3 | 모서리 | 팀 | 0 | 6 / 3 | `runs/pilot_20261021_133652_b_e1f6_comm3_nopen` |
| B pen005 = **모서리·팀** | 6 | 3 | 모서리 | 팀 | .005 | 6 / 3 | `runs/pilot_20261022_112521_b_e1f6_comm3_pen005` |
| **모서리·개인** `b6_corner_indiv_pen005` | 6 | 3 | 모서리 | 개인 | .005 | 6 / 3 | `runs/queue_20261022_140114_b6_corner_indiv_pen005` |
| **인접·팀** `b6_adjacent_team_pen005` | 6 | 3 | 인접 (4,10)/(5,10) | 팀 | .005 | 6 / 3 | `runs/queue_20261022_140114_b6_adjacent_team_pen005` |
| **인접·개인** `b6_adjacent_indiv_pen005` | 6 | 3 | 인접 | 개인 | .005 | 6 / 3 | `runs/queue_20261022_140114_b6_adjacent_indiv_pen005` |

- 후보 환경(A 이후)은 짝수 seed에서 goal 좌우가 바뀐다. 이것은 seed 간 강건성 시험이며, 방향과 팀을 분리하지 않는다(E40, D63).
- 모든 계보에서 팀당 요청 수 = 팀원 수다(agent당 1개).
- 관측은 13채널(11×11)과 ego 정보 20개다. 채널은 팀 기준이라 자기 팀 요청 선반과 자기 goal이 전용 채널에 표시된다. 다른 agent의 팀은 보이지 않는다(진행 보고서 5.1절, E13).
- 쓰지 않은 후보 정의: c1/c2/c3(E40), C `c_e1f6_wide_comm3`(11×16, E41). smoke만 했다.

### 1.3 학습·평가 규약 [확인: `experiment.json`]

- from-scratch: 무작위 초기화, lr 2e-4, entropy .05, rollout 1024(E14). 커리큘럼 분기(E02)는 lr 1e-4, entropy .02였다.
- 평가: 50 update(51,200 step)마다 deterministic masked 정책, 20 episode × 500 step, reset seed 5,000,001–5,000,020. trainer의 agent별 평가 수는 20 episode 합이라 20으로 나눠야 한다.
- checkpoint: 250 update(256,000 step)마다. `checkpoint_01500.pt` = 1,536,000 step.
- 초기 가중치: 같은 seed·같은 설정이면 mode 간 hash가 같다. seed 1의 GPU 설정 hash는 `f78ec390e0fad60c…`다(E16, E19, E26). CPU smoke 설정은 `baaa10bf…`다.
- 학습률 일정이 없다. 짧은 run은 긴 run의 prefix다. 단, 전이 mode는 GPU 비결정성 때문에 1.4–1.6M에서 갈라진다(E24).
- 속도: E1 4개 동시 약 24 step/s/job, E1-F 5개 동시 약 19, A 약 23.7, B 약 16.3, 2×2 칸 약 16.
- "배운 agent"(D76 사전 고정): 마지막 평가 5회에서 agent별 배송 ≥ 0.25/episode.

## 2. 커리큘럼 계보 (2026-09-29 – 10-13) — 지금은 주 근거로 쓰지 않음

### E00 커리큘럼
- 경로: `runs/pgct09700_physical_mixing_20260929_155338_079437/stage0{1..4}_*`
- 조건: 4 agent, 개인 보상, home ratio를 1.0 → .875 → .75 → .5로 낮춤, PGCT, seed 1.
- 결과(최종 delivery): Stage01 61.00, Stage02 50.60, Stage03 49.85, Stage04 47.25. 같은 팀 전이는 Stage01 1,131회 → Stage03·04 0회. 다른 팀 전이는 Stage04 1,221회(3–4가 1,170회).
- 한계: stage마다 혼합률·모델·평가 seed가 달라 PGCT의 인과 효과로 해석하지 않는다.

### E02 공간 분기 (Stage03 → E1/E2/E3)
- 경로: `runs/sp_20261008_120638_983201`. 실행기 `examples/run_pgct_spatial_experiments.ps1`.
- 조건: Stage03 final에서 출발(optimizer·graph 초기화), 4 agent, 개인 보상, home .5, 요청 4(팀당 2), 센서·통신 5, lr 1e-4, entropy .02, 각 4,000,768 step, seed 1. 기준선은 IPPO 분기.

| run | 최종 delivery | AUC | 같은 팀 전이 승인 | 다른 팀 전이 승인 |
|---|---|---|---|---|
| E1 PGCT | 44.35 | 45.86 | 0 | 3–4만 2,005 |
| E1 IPPO | 44.65 | 44.57 | — | — |
| E2 PGCT | 37.85 | 34.17 | 870 | 2,360 |
| E2 IPPO | 38.20 | 34.24 | — | — |
| E3 PGCT | 2.86M에서 중단 | 부분 | — | — |

- E3 PGCT는 10-13 18:21 Windows 재부팅으로 끊겼다(마지막 checkpoint 02700). E3 IPPO는 시작하지 않았다.
- 해석 한계: Stage03 이후 추가 전이의 조건부 효과일 뿐이다. 처음부터 PGCT를 쓰지 않은 IPPO 비교가 아니다.
- 근거: `output/learning_review_20261013/`.

### E11·E13 고정 모델 팀 식별 (학습 없음)
- 코드: `latent_team/exp_a_team_identifiability.py`, `verify_evidence_observability.py`. 결과 `output/latent_team/exp_a_20261013/`.
- 모델: Stage03, E1/E2 IPPO·PGCT final, Stage04 PGCT. 20×500 확률 정책.
- 결과: canonical JS AUROC .375–.5. 국소 목격 증거 AUROC 1.00(첫 episode 안). blend gain에서 E1 계열은 같은 팀이 오히려 나쁘다(.25–.33).
- 한계: 국소 증거는 팀 기준 관측 채널 값과 100% 일치한다(E13). 거의 정답 정보이고, 이웃 귀속 가정이 필요하다.

## 3. From-scratch E1 (2026-10-13 – 10-18)

### E17 첫 본 학습 — Windows Update로 중단
- 경로: `runs/scratch_20261013_202352_stage2`(로그 보존, **checkpoint는 E21에서 사용자 승인으로 삭제**).
- 조건: E1, IPPO/PGCT/Oracle/All, seed 1, 15M 목표, 4개 동시. 사용자가 10-13 20:23에 시작했다.
- 중단: 10-15 01:01 Windows Update 재부팅. 마지막 metrics는 2.46–2.50M이다.
- 결과(약 2.4M, E18): Oracle 9.98이 가장 높았지만 Agent2 한 명에게서 나왔다. 단일 seed라 귀속할 수 없다.

### E24·E27 E1 재실행 — 사용자 지시로 6.5M에서 중지
- 경로: `runs/scratch_20261015_093349_stage2/{e1_ippo,e1_pgct,e1_oracle,e1_all}_s1/`, `STOPPED_BY_USER.txt`.
- 조건: E1(1.2 표), seed 1, 무작위 초기화(`f78ec390…`), 15M 계획, 10-18 12:43에 약 6.5M에서 중지. 마지막 checkpoint는 `checkpoint_06250.pt`(6.4M), final.pt는 없다.
- 결과(공통 6.4M, E27):

| mode | 배송 시작(≥1) | 학습 중 평균 | 최근 5회 | 배운 agent |
|---|---|---|---|---|
| IPPO | 2.05M | 10.4 | 23.2±1.1 | 2/4 |
| PGCT | 1.79M | 11.7 | 27.3±1.4 | 3/4 |
| Oracle | 1.64M | 13.2 | 32.2±1.7 | 3/4 |
| All | 3.99M | 3.7 | 19.4±1.6 | 4/4 |

- PGCT 전이 update 비율은 0–1M .95, 2–3M .55, 3–4M .19였다. 같은 팀 arc는 3M 이후 약 0이다. 남은 연결은 다른 팀(3–4, 1–2)이다(E28).
- E17과 비교: IPPO는 2.46M까지 완전히 재현됐다. 전이 mode는 1.4–1.6M에서 갈라졌고, All의 배송 시작은 1.89M → 3.99M으로 바뀌었다. 첫 발견 시점은 0.2–2.1M 흔들렸다(E28).
- 해석 한계: E1은 팀이 색 라벨로만 다른 대칭 조건이다(D40). 성능 차이를 "팀원을 골라서"로 설명할 수 없다. seed 1개, 미수렴이다.
- 근거: `output/scratch_review_20261018/`, `output/paper_e1_20261018/`(그림·표·`numbers.json`), 영상 `output/videos_20261019/e1/`.

## 4. E1-F (2026-10-18 – 10-19) — 외부 종료

### E26 E1-F main
- 경로: `runs/e1f_20261018_124343_main_canonical`(IPPO/PGCT/Oracle/All, canonical bank), `runs/e1f_20261018_124343_main_v2`(PGCT, v2 bank). 실행기 `latent_team/run_e1f.ps1 -Phase main -Track`.
- 조건: E1-F(1.2 표), seed 1, 10M 계획, 5개 동시. Claude Code 세션이 사용자 승인을 받아 실행했다.
- 종료: 10-19 13:07–13:08. Claude 데스크톱 앱 업데이트 때 앱 프로세스 트리와 함께 끝났다. 마지막 metrics는 1.67–1.70M, 마지막 checkpoint는 `checkpoint_01500.pt`(1.536M), final.pt는 없다. 각 plan 폴더에 `STOPPED_EXTERNALLY.txt`가 있다.
- 결과: 평가 배송은 거의 0이다(IPPO가 1.48M에 0.05 한 번). PGCT gate의 같은 팀 arc 비율은 다른 팀과 비슷했다(.40 대 .44; v2 .27 대 .27, E28).
- 재시작하지 않았다. 옛 설정(감점 .02, 4 agent)이라 같은 정체가 반복될 것으로 보고, 모서리·개인 칸으로 대체하기로 했다(D79).

## 5. probe 신뢰성 점검 (2026-10-19, 학습 없음)

| E | 질문 | 대상 | 결과 | 경로 |
|---|---|---|---|---|
| E29 | gate 신호가 팀을 따라가나 | E1, E1-F 기록 | 기록별 AUROC E1 .28–.49, E1-F .25–.61. 0.25M 사이 자기 변화(0.012–0.106)가 팀 신호(−.077~+.029)보다 크거나 비슷하다 | `latent_team/probe_wandb_viz.py` |
| E30 | 이전 모델에서 probe가 팀을 연결하나 | 커리큘럼·sp 모델 | Stage01만 1.00, 이후 .38–.62 | `output/probe_connect_20261019/` |
| E31·E36 | 학습된 보상 예측기 probe | E1-F, E1, Stage03·04 | .25–.62. 인공 gate 상태에서 팀별 실제 보상이 다른 query는 2–7.5% | `output/reward_probe_20261019/` |
| E32–E34 | probe 가중치·규칙 bank | 여러 계보 | 다른 계보로 일반화되지 않는다 | `output/probe_weight_20261019/`, `output/probe_redesign_20261019/` |
| E37·E38 | 궤적 probe, source 교체 | E1 10개 모델 | 정책 궤적은 이득 없음. 실제 상태 보상 MLP는 .71–1.00 | `output/trajectory_probe_20261019/` |
| E39 | 보상 probe 신호의 원천 | 같은 창 | 신호는 주로 실제 보상 차이(Q_diff)에서 온다. 처음부터 계보 .67–.79 | `output/trajectory_probe_20261019/results_cf/` |
| E42 | 보상 상관 AUROC .12의 의미 | Stage04, 20 episode | 모든 쌍 \|r\| ≤ .015. 신호가 아니라 0이다 | `output/reward_corr_check_20261019/` |

- 공통 한계: seed 1, 쌍 6개(AUROC 해상도 1/8), 대부분 같은 커리큘럼 계보다.

## 6. 후보 환경과 pickup 정체 (2026-10-19 – 10-22)

### E40·E41 후보 정의와 연결률 (구현·smoke만)
- 코드: `latent_team/env_candidates.py`, `connectivity_check.py`, `reward_correlation_baseline.py`.
- 연결률(무작위 정책, 5×500): E1-F에서 쌍의 약 절반만 통신 범위 안이다(D62의 "물리 제약이 사실상 없다"를 정정). B는 고립 23%, 팀원 가용 44%다.

### E43 A·B IPPO pilot, 2M
- 경로: `runs/pilot_20261019_180044_{a_e1f4_team,b_e1f6_comm3}/`. 사용자가 10-19 18:00에 앱 밖에서 시작했다. 4 job 모두 complete(2,000,896 step).
- 조건: A, B(1.2 표), IPPO, seed 1·2.
- 결과:

| run | 평가 배송 첫 >0 | 최근 5회 평가 | 배송 agent |
|---|---|---|---|
| A s1 | 없음 | 0 | 0 |
| A s2 | 1.89M | 0–.7 | 1 |
| B s1 | 0.97M | 2.25–4.2 | 1 |
| B s2 | 없음 | 0 | 0 |

- 공통 패턴: 초반 무작위 pickup → pickup 회피 정체 → 한 agent만 재발견. 정체 시작 시점은 E44에서 0.1–0.2M으로 정정했다.
- 표기 주의: manifest의 `team_reward: individual`은 CLI 기본값이 남은 것이다. 실제 env는 team이다.
- 근거: `output/env_candidates_20261019/pilot_analysis.json`.

### E44 pickup 정체 원인 분해 (학습 없음)
- 코드: `output/pickup_stall_20261021/`(pickup_stall.py, action_values.py).
- 결과: TOGGLE/ep가 0.1–0.2M에 15–38 → 0.9–9로 떨어진다. 무작위 정책의 즉시 보상은 FORWARD −.0002, LEFT/RIGHT −.0022, NOOP −.0053, **TOGGLE −.0183(최저)**이다. TOGGLE 결과의 93%가 −.02 감점(비요청 pickup 45%, 조기 내려놓기 48%)에 걸린다. 자기 팀 요청 선반 pickup은 3.6%이고, 그 운반 구간의 보상 합은 +.002다.

### E45·E46 감점 0(nopen), IPPO 1M × seed 1·2
- 경로: `runs/pilot_20261021_133652_{a_e1f4_team,b_e1f6_comm3}_nopen/`. 사용자가 10-21 13:36에 시작했다. 초기 hash는 기존 pilot과 같다.
- 차이: 기존 A·B와 두 감점(.02 → 0)과 길이(2M → 1M)만 다르다.
- 결과: TOGGLE은 1M 내내 100–310/ep로 유지됐다(정체 해소). 비요청 pickup은 50–150/ep로 폭증했다. 평가 배송 ≥1에 도달한 run은 없다. B s1 마지막 5회 평균은 0.37이다.
- 판정: 사전 기준 1·2 통과, 3·5 실패(D70).
- 근거: `output/nopen_pilot_20261022/compare.py`, `results.json`.

### E47 감점 크기 sweep (학습 없음)
- 코드: `output/penalty_sweep_20261022/penalty_sweep.py`.
- 결과: TOGGLE ≈ 0.0002 − 0.93p. NOOP과 교차하는 경계는 p ≈ .0056(B)–.0059(A)다. .005를 골랐다. 이 값은 경계 바로 아래라 여유가 작다.

## 7. 팀 식별 측정 (2026-10-22 – 10-23, 학습 없음)

### E49 보상 결합 대 정책 probe (B nopen)
- 모델: `runs/pilot_20261021_133652_b_e1f6_comm3_nopen/b_e1f6_comm3_nopen_ippo_s{1,2}/{checkpoint_00750,final}.pt`.
- 롤아웃: 확률 정책, 80 episode × 500 step, reset seed 9,100,001부터.
- 결과(15쌍): 보상 결합 1.00(네 checkpoint, bootstrap 1.00–1.00). 정책 canonical .59–.78, v2 gate .41–.76.
- 코드: `output/reward_coupling_20261022/reward_coupling.py`.

### E50 온라인 식별 시점 (B nopen)
- 코드: `output/reward_coupling_20261022/identification_time.py`.
- 결과: K=1이면 대개 6,106–36,472 step에 15쌍을 모두 맞혔다. 오판정은 20개 조건 중 1쌍(s2 1M, K=1)뿐이다. K=3은 일부 조건에서 4만 step 안에 다 맞히지 못했다.
- 한계: nopen은 TOGGLE 남발로 우연한 배송이 잦다. 감점 환경에서는 사건이 드물 수 있다.

### E54 판별 probe 13개와 goal 방향 축
- 코드: `output/probe_discriminative_20261023/discriminative_probes.py`, `goal_axis_gate.py`. 결과 `goal_axis_results.json`, `goal_axis_stdout.txt`.
- 대상: 모서리 goal checkpoint 28개(pen005 팀·개인 각 6, nopen 4, B .02 4, A 4, E1-F 4).
- 결과 1: 13개 probe의 JS 평균 AUROC .493(48개 .512). 개선이 없다.
- 결과 2(goal 방향 축, 칸별 평균):

| 칸 | 방향 AUROC | 쌍 AUROC 축 / JS13 | 부호 규칙 정확도 |
|---|---|---|---|
| 모서리·팀 pen005 (6 ag) | .89 | .70 / .53 | .76 |
| 모서리·개인 pen005 (6 ag) | .96 | .73 / .52 | .83 |
| B nopen (6 ag) | .89 | .72 / .54 | .83 |
| B .02 (6 ag, 2M) | .92 | .57 / .47 | .57 |
| A .02 (4 ag, 2M) | .44 | .53 / .31 | .58 |
| E1-F (4 ag, 1.54M) | .56 | .41 / .56 | .33 |

- 28개 평균: 쌍 AUROC 축 .625 대 JS13 .493, 축이 나은 경우 21개, 나쁜 경우 5개.
- 진행 보고서 7.7절의 "agent 단위 152명 .74, 배운 19명 .90"은 이 세션의 일회성 계산이다. 계산 스크립트가 저장소에 남아 있지 않으므로 다시 계산해야 한다.
- 한계: 6-agent는 seed 2개다. goal 후보 칸을 안다고 가정한다. 4-agent run에서는 신호가 없다.

## 8. 감점 .005와 2×2 (2026-10-22 – 진행 중)

### E48·E52 모서리·팀(B pen005), IPPO 1M × seed 1·2
- 경로: `runs/pilot_20261022_112521_b_e1f6_comm3_pen005/`. 사용자가 10-22 11:25에 시작했고, 10-23 03:00 무렵 complete. 초기 hash는 기존 B와 같다.
- 차이: B nopen과는 감점(0 → .005)만, 기존 B와는 감점(.02 → .005)과 길이(2M → 1M)만 다르다.

### E51·E52 2×2 IPPO 1M × seed 1·2 (대기열)
- 경로: `runs/queue_20261022_140114_{b6_corner_indiv,b6_adjacent_team,b6_adjacent_indiv}_pen005/`. 대기열 로그 `runs/queue_20261022_140114_queue.log`, PID 기록 `..._pids.json`.
- 설정 대조(`runs/plancheck_2x2_*`): 모서리·팀 대비 env 차이는 `team_reward_mode`와 `team_goal_positions`뿐이다.
- 상태(10-23 17:33): 모서리·개인 complete(07:20–07:28). 인접·팀 s1 0.85M, s2 0.84M. 인접·개인 s1 0.59M, s2 0.57M. 모두 running.

### 모서리 두 칸의 1M 결과 (E52, 0.9–1M 구간)

| 지표 | 모서리·팀 s1 / s2 | 모서리·개인 s1 / s2 | (참고) 기존 B .02 s1 / s2 |
|---|---|---|---|
| 학습 배송/ep | 1.17 / 1.01 | 1.16 / 1.35 | 0.23 / 0.005 |
| 평가 마지막 5회 | .81 / .38 | .99 / .83 | — |
| 최다 agent 비율 | .91 / .82 | .99 / .97 | — |
| 보상 결합 AUROC | 1.00 (네 checkpoint) | .83 / .38(s1), .62 / .88(s2) | — |
| 정책 probe AUROC | .46–.74 | .43–.69 | — |

- 판정(`latent_team/pilot_verdict.py`, `output/pilot_verdicts/`): 두 칸 모두 overall fail이다. 실패 항목은 4번(배송 분산)뿐이다.
- 개인 보상 칸에서 보상 결합은 15쌍 중 5–9쌍을 오판정한다(반응이 모두 0 근처).
- 근거: `output/pen005_analysis_20261023/probes_pen005.py`, `results.json`, `results_corner_indiv.json`.

### E53 독주 진단
- 코드: `output/pen005_analysis_20261023/dominance_diag.py`, 결과 `dominance_diag.json`.
- 결과: 독주 agent를 NOOP으로 두든 위쪽 모서리로 옮기든, 나머지는 0–0.3/ep(결정적 평가 0)다. 경쟁·차단이 아니라 나머지가 배우지 못한 것이다. 배운 agent 4명 사이의 정책 JS는 같은 goal .095, 다른 goal .091이다(AUROC .56).
- 정정(D78): "학습 신호 문제", "정책 probe 실패는 구조적"은 1M 시점에 대한 과대 해석이라 철회했다.

### E55 팀당 요청 수 (학습 없음)
- 코드: `output/request_sweep_20261023/request_sweep.py`, 결과 `results.json`. 모서리·개인 칸 env에서 `request_queue_size_per_team`만 3/6/9로 바꿨다. 무작위 정책, 20×500.
- 결과: agent당 자기 팀 요청 pickup/ep 1.02 / 1.96 / 2.73. TOGGLE 평균 즉시 보상 −.0043 / −.0020 / −.0013(NOOP −.0053).
- 한계: 무작위 정책 계산이다. 학습에서 독주가 풀리는지는 검증하지 않았다.

## 9. 메인 1단계 (대기 중)

- 경로: `runs/queue_20261023_172201_b6_corner_indiv_pen005/`(계획만 있고 job 폴더는 없다). 로그 `runs/queue_20261023_172201_queue.log`.
- 조건: 모서리·개인, IPPO / Oracle-team / All-peer × seed 1·2·3, 각 5,000,000 step, 최대 4개 동시, W&B. 사용자가 10-23 17:22에 앱 밖 PowerShell(PID 32236)에서 걸었다.
- 상태(17:33): 9 job 계획, 시작 0. 인접 칸 job이 끝나 python 학습 프로세스가 4개 미만이 되면 순서대로 시작한다. 추정(약 16 step/s): 인접·팀 종료 약 20–21시 → 첫 2 job 시작, 인접·개인 종료 10-24 01시 무렵 → 다음 2 job 시작.
- 사전 고정 지표(D76, D77): 배운 agent 수, 독주 agent 제외 배송 합, 팀별 배송, 독주 agent 자신의 배송, 독주 agent가 없는 팀의 배송·배운 agent 수(IPPO·Oracle·All 비교). 2M·3M 중간 결과는 참고하고, 판정은 5M에서 한다(D78).
- 예상 비용: job당 약 3.5일, 9 job 약 10–11일(D78).
- 미결: 요청 수 pilot을 먼저 할지(SESSION_HANDOFF 참고).

### 버린 계획 (학습 없음, 폴더 보존)
- `runs/queue_20261023_123903_b_e1f6_comm3_pen005/`: 모서리·팀 IPPO 대 Oracle 2M. 시작한 job 없이 창을 닫았다(D78에서 5M으로 변경).
- `runs/queue_20261023_150050_b_e1f6_comm3_pen005/`: 모서리·팀 IPPO·Oracle·All 5M. 시작한 job 없이 창을 닫았다(D81에서 개인 보상으로 변경).
- 같은 이름(`-Name`)으로 대기열을 다시 걸면 계획 단계에서 멈춘다. 기존 폴더를 보호하려는 설계다.

## 10. 실험 간 차이 요약

| 비교 | 바뀐 것 | 같은 것 |
|---|---|---|
| E1 → E1-F | goal 인접 → 모서리 | 4 agent, 개인, .02, 요청 4 |
| E1-F → A | 개인 → 팀 보상 | 나머지 |
| A → B | 4 → 6 agent, 통신 5 → 3, 요청 4 → 6 | 팀 보상, 모서리, .02 |
| B → B nopen | 감점 .02 → 0, 2M → 1M | 나머지, 초기 hash |
| B nopen → B pen005 | 감점 0 → .005 | 나머지 |
| B pen005 → 2×2 세 칸 | `team_reward_mode` 및/또는 `team_goal_positions` | config 전부 |
| 1M pilot → 메인 | 1M → 5M, mode 추가(Oracle, All), seed 3개 | 모서리·개인 env |

## 11. 삭제·손실된 자료

- E21(10-15, 사용자 승인): runs/에서 27.26GB를 삭제했다. smoke·옛 평가, E17 checkpoint, 큰 run의 중간 checkpoint가 포함된다. 목록은 `output/cleanup_20261015/removed_manifest.json`에 있다. 이 때문에 Stage·E1/E2 중간 모델은 재평가할 수 없다.
- 10-22: Overleaf zip 두 개를 `git rm`했다(`output/ijcai_*_20261018/`). 이후 zip은 gitignore 대상이다.
- E17(재부팅), E26(앱 업데이트): 마지막 checkpoint 이후 구간은 checkpoint가 없다.
- E28 발견 시점 스크립트(`discovery.py`)와 E54 agent 단위 계산은 scratchpad에만 있었고 보존되지 않았다. 정의는 노트에 있다.

## 12. 문서·보고서 산출물

| 경로 | 내용 |
|---|---|
| `output/ijcai_method_paper_20261018/` | 방법 논문 v0.1–v0.4.1(.tex), 한국어판 |
| `output/ijcai_paper_20261018/` | 진단 논문 초안(보존용) |
| `output/pgct_beamer_20261021/main.tex` | 영어 beamer 15쪽 |
| `output/pgct_report_20261022/report.tex` | 한국어 보고서(보상 결합 정의 3.1절) |
| `output/pgct_progress_paper_20261023/` | 한국어 논문형 진행 보고서(main.tex, figures/, make_figures*.py). 컴파일은 확인하지 못했다 |
| `EXPERIMENT_STORY.md` | 실험 흐름을 쉬운 말로 정리한 문서 |
