# PGCT 실험·평가 기록

최초 정리: 2026-10-13 Codex. 최신 정량 스냅샷은 14:37 KST. 원본 로그·체크포인트는 보존한다. 이 파일의 계획과 명령은 실행 사실을 뜻하지 않는다.

## E00. 기존 curriculum — 완료

경로: `runs/pgct09700_physical_mixing_20260929_155338_079437/`.

| Stage | Home ratio | 추가 환경 step | 최종 delivery | Shelf return | Same 전이 | Cross 전이 |
|---|---:|---:|---:|---:|---:|---:|
| stage01 | 1.000 | 1,000,448 | 61.00 | 58.95 | 1,131 | 0 |
| stage02 | .875 | 2,000,896 | 50.60 | 48.85 | 380 | 0 |
| stage03 | .750 | 3,000,320 | 49.85 | 47.95 | 0 | 443 |
| stage04 | .500 | 4,000,768 | 47.25 | 45.95 | 0 | 1,221 |

전이는 무방향 pair-update로 집계했다. Stage04 cross 내역은 3–4: 1,170회, 1–4: 51회다. Stage마다 혼합률과 모델, 당시 평가 seed가 달라 delivery 차이를 PGCT의 인과 효과로 해석하지 않는다.

Stage04의 same-team 물리 후보는 4,364회지만 승인 0회였고, cross 후보는 9,743회 중 1,221회 승인됐다. 최종 raw JS는 1–3 .338519, 2–4 .394231, 1–2 .584076, 1–4 .206173, 2–3 .439278, 3–4 .129985다. Gate는 이웃에서 갱신되는 EMA < .12를 사용하므로 최종 raw 값과 과거 승인을 구분한다.

근거: [Gate 진단](output/gating_diagnosis/summary.json), [공간 분석](output/pgct_spatial_analysis/REPORT.md).

## E01. 기존 home1 IPPO continuation — 완료, 대조 조건 미일치

Run: `runs/recurrent_ippo_consensus/ex5_semantic_cnn_none_from_scratch_4ag_sr5_square_home1.00_seed1_pretrain_off_9700_continue/`.

- Graph none, communication off, peer coefficient 0, consensus 0인 IPPO다.
- 최종 delivery 61.45, shelf return 59.50. 기존 checkpoint900의 가중치에서 이어졌으며 새 counters가 시작된다.
- 사전학습 예산·초기 상태가 Stage03 분기와 달라 E1 PGCT의 matched baseline으로 사용하지 않는다.
- 과거 영상의 agent별 성공 시점 차이를 순차 optimizer 업데이트로 해석하지 않는다.

근거: 해당 run의 `final_eval_metrics.json`, 기존 from-scratch 실행기와 과거 진단.

## E02. 공간 분기 — E1/E2 완료, E3 진행

경로: `runs/sp_20261008_120638_983201/experiment.json`.
초기 모델: E00의 `stage03_4ag_physical_home0.750/final.pt`.
실행기: `examples/run_pgct_spatial_experiments.ps1`, `examples/train_pgct_spatial_experiments.py`.

조건: 4 agents/2 teams, individual reward, home .5, Q4(팀당 2), sensor/range 5, LR1e-4, entropy .02, rollout1024, training seed1. 각 분기는 4M 요청 예산을 올림하여 4,000,768 step을 학습한다. 같은 초기 actor/critic에서 출발하고 optimizer/graph는 초기화한다. 따라서 Stage03 이후 추가 전이의 조건부 효과를 비교한다.

Task 평가는 deterministic masked policy, 공통 reset seeds 5,000,001–5,000,020, 20회×500 step이다.

| Run | 상태 | 저장 step | 최종/최근 delivery | Shelf return | 정규화 평가 delivery AUC | 마지막 10회 평균 |
|---|---|---:|---:|---:|---:|---:|
| e1_pgct_s1 | 완료 | 4,000,768 | 44.35 | 42.65 | 45.8559 | 46.170 |
| e1_ippo_s1 | 완료 | 4,000,768 | 44.65 | 43.70 | 44.5734 | 44.515 |
| e2_pgct_s1 | 완료 | 4,000,768 | 37.85 | 36.15 | 34.1674 | 37.470 |
| e2_ippo_s1 | 완료 | 4,000,768 | 38.20 | 36.85 | 34.2449 | 37.605 |
| e3_pgct_s1 | 진행 | 2,252,800 | 27.25 | 25.95 | 22.2601(부분) | 26.835 |
| e3_ippo_s1 | 시작 전 | — | — | — | — | — |

E3 최근 평가는 2,201,600 step이다. AUC는 기록된 51,200 step부터 최종/최근 평가까지 사다리꼴 적분하고 구간 길이로 나눈 값이다. 기록에 없는 step0 점수는 만들지 않았다. E3 부분 AUC를 완료된 4M AUC와 직접 비교하지 않는다.

| Pair | E1 PGCT 승인 | E2 PGCT 승인 | E3 PGCT 승인(부분) |
|---|---:|---:|---:|
| 1–3 same | 0 | 89 | 410 |
| 2–4 same | 0 | 781 | 348 |
| 1–2 cross | 0 | 932 | 306 |
| 1–4 cross | 0 | 1,276 | 441 |
| 2–3 cross | 0 | 39 | 72 |
| 3–4 cross | 2,005 | 113 | 102 |

Pair-update는 양방향을 중복 세지 않는다. E1 same 후보 4,435회/승인 0회, 3–4 후보 2,525회/승인 2,005회다. E2 same 후보 3,176회/승인 870회, cross 후보 6,434회/승인 2,360회다. 물리 범위 밖 전이는 0회, IPPO 전이도 0회다.

| 최종/최근 delivery/episode | Agent 1 | Agent 2 | Agent 3 | Agent 4 |
|---|---:|---:|---:|---:|
| E1 PGCT | 8.70 | 8.50 | 13.65 | 13.50 |
| E1 IPPO | 9.30 | 8.10 | 13.35 | 13.90 |
| E2 PGCT | 9.60 | 9.35 | 9.00 | 9.90 |
| E2 IPPO | 9.40 | 9.60 | 9.75 | 9.45 |
| E3 PGCT | 7.00 | 6.60 | 6.70 | 6.95 |

원본 agent count는 20개 에피소드 합계이므로 20으로 나눴다. 해당 로그의 개별 actor update skip은 모두 0이었다.

근거: [전체 분석](output/learning_review_20261013/REPORT.md), [수치](output/learning_review_20261013/analysis.json), [학습곡선](output/learning_review_20261013/learning.png), [Agent별 성과](output/learning_review_20261013/agents.png), [전이 차트](output/learning_review_20261013/gates.png).

## E03. 기존 Stage04 공간 활동 — 고정 모델 평가 완료

기존 Stage04 final을 20×500 step 평가했고 가중치가 바뀌지 않았음을 확인했다. 왼쪽 체류율은 Agent1 99.57%, Agent2 .55%, Agent3 38.01%, Agent4 56.53%다. 3–4 occupancy JS는 .152835로 가장 낮았다.

다만 Agent3 요청 pickup의 약 81%는 오른쪽, Agent4의 약 72%는 왼쪽이었다. 동일 작업이나 역할을 수행했다고 결론 내리지 않는다.

근거: [Frozen 평가](output/pgct_spatial_analysis/frozen_rollout_summary.json), [분석](output/pgct_spatial_analysis/REPORT.md).

## E04. 기존 Stage04 probe 중복 민감도 — 진단 완료

동일 canonical 입력, zero hidden, unmasked, natural-log JS다. 48개 중 고유 입력은 26개다.

| Pair | 기존 48개 평균 | 고유 26개 평균 |
|---|---:|---:|
| 1–3 same | .338519 | .358212 |
| 2–4 same | .394231 | .404173 |
| 1–2 cross | .584076 | .492518 |
| 1–4 cross | .206173 | .137414 |
| 2–3 cross | .439278 | .494423 |
| 3–4 cross | .129985 | .226997 |

3–4의 두 actor 모두 FORWARD 확률이 .9 이상인 입력은 30/48개이며 그 평균 JS는 .007116, 나머지 18개의 평균은 .334768이다. 고유 입력에서는 각각 10/26개와 16/26개다. 정책 출력으로 사후 분류한 그룹이며 실제 작업 중요도를 나타내지 않는다.

중복 제거가 과거 EMA 연결 역전을 증명하지 않는다. 실제 학습 gate는 변경하지 않았다.

근거: [수치](output/pgct_transfer_review/probe_bias_check.json), [차트](output/pgct_transfer_review/probe_bias_check.png).

## E05. 공통 rollout 이력의 policy/critic 일치 — 진단 완료

모델은 기존 Stage04 final과 새 E1 PGCT checkpoint600(614,400 step)이다. 둘 다 PGCT이므로 on/off 비교가 아니다.

Reference는 기존 Stage04 stochastic policy, 20×500 step, seeds 5,000,001–5,000,020이다. 전체 이력으로 hidden을 전개하고, 10-step 간격×4개 관측 stream으로 4,000개 표본을 측정했다. 각 network가 동일 이력으로 자기 hidden을 형성하며 다른 정책에는 off-policy 이력일 수 있다.

| 기존 Stage04 pair | Recurrent masked JS | Critic 예측 간 MSE |
|---|---:|---:|
| 1–3 | .191996 | 13.976555 |
| 2–4 | .212130 | 11.427813 |
| 1–2 | .335800 | 7.109442 |
| 1–4 | .180121 | 14.928075 |
| 2–3 | .213066 | 10.376292 |
| 3–4 | .059547 | .106799 |

새 E1 checkpoint600의 3–4는 JS .068073, critic 예측 간 MSE .120176이다. 모델 hash 불변을 확인했다. 3–4 유사성이 canonical 중복에만 존재하지는 않지만, 예측 일치·정확도·전이 유익성은 다르다. 전체 6쌍에서 관계가 단조롭지도 않았다.

근거: [진단 수치](output/pgct_transfer_review/common_rollout_stage04_e1_u600/summary.json), [이력 cache](output/pgct_transfer_review/common_rollout_stage04_e1_u600/histories.npz), [차트](output/pgct_transfer_review/common_rollout_stage04_e1_u600/compatibility.png).
코드: `examples/diagnose_pgct_rollout_compatibility.py`.

## E06. 2026-10-13 최종 critic의 실제 return 예측 — 평가 완료

완료된 E1/E2 PGCT/IPPO final 각각 10회×500 step을 평가했다. Stochastic masked actor, reset/action RNG seeds 5,100,001–5,100,010이며 모델별 seed는 같아도 방문 상태는 달라질 수 있다. 모든 40개 에피소드는 time-limit truncation이었고 모델 hash는 불변이었다.

Target은 shaping/penalty를 포함한 실제 reward의 유한 discounted return, zero tail이다. TD는 truncation에서 bootstrap한다.

| 모델 | 전체 MC MSE | 초기 200-step MC MSE | Mean absolute TD |
|---|---:|---:|---:|
| E1 PGCT | 4.190251 | 1.724620 | .064855 |
| E1 IPPO | 3.713456 | 1.103477 | .060764 |
| E2 PGCT | 2.189594 | .286130 | .045222 |
| E2 IPPO | 2.146145 | .281301 | .044082 |

초기 200 step은 미래 300 step 이상이 남아 tail 편향을 줄이지만 없애지는 않는다. E1 Agent3의 초기 MC MSE는 PGCT1.546733/IPPO .407245, Agent4는 .937810/.453493이다.

현재 최종 critic 정확도 개선은 미확인이다. 서로 다른 방문 분포, target 분산, 단일 training seed 때문에 전이가 critic을 손상시켰다고 단정할 수도 없다.

근거: [전체 수치](output/learning_review_20261013/critic_summary.json), 같은 폴더의 개별 `*_critic.json`, [차트](output/learning_review_20261013/critic.png).
재현 코드: `output/learning_review_20261013/evaluate_critics.py`.

## E07. 2026-10-13 최종 canonical 응답 — 진단 완료

맵마다 해당 PGCT의 저장 bank를 두 조건에 공통 적용했다. E1은 48개/고유26개, E2는 48개/고유25개다. Zero hidden/unmasked 평가이며 모델 hash 불변을 확인했다.

| 모델·pair | JS48 | 고유 입력 JS |
|---|---:|---:|
| E1 PGCT 3–4 | .0921 | .1421 |
| E1 PGCT 1–4 | .2114 | .1232 |
| E1 IPPO 3–4 | .2029 | .2659 |
| E2 PGCT 1–4 | .0074 | .0102 |
| E2 IPPO 1–4 | .0330 | .0326 |

E1의 순위 민감성은 지속된다. E2의 1–4 유사성은 두 가중 방식과 두 학습 조건 모두에서 나타났다. 맵별 bank가 달라 raw JS의 맵 간 직접 비교에는 주의한다.

근거: [응답 수치](output/learning_review_20261013/probe_responses.json), [차트](output/learning_review_20261013/probes.png).

## E08. Transfer 전용 실행기 — 구현 완료, 장기 실험 미실행

- 실행기: `examples/run_pgct_transfer_experiments.ps1`, `examples/train_pgct_transfer_experiments.py`.
- Modes: pgct/ippo/random/drop34/drop34_refill. 동일 Stage03→E1, 각 4,000,768 step, 기본 seeds1·2·3.
- 과거 검증 기록: 관련 35 tests 통과, 조건별 64-step smoke. 경로는 `runs/tr_smoke_20261008_final`, `runs/sp_check_20261008_120401_732`다. PGCT/IPPO 64-step weights가 기존 공간 실행기와 bitwise 일치한 기록이 있다.
- 공통 이력 진단의 추가 2 tests 통과 기록도 있다. 이번 공용 노트 생성에서 테스트 전체를 재실행한 것은 아니다.
- `runs/tr_reuse_plan_20261008_final`은 계획이며 seeds2·3 완료가 아니다. Random/drop의 64-step 결과를 장기 효과로 해석하지 않는다.
- Ablation의 실제 전이는 `transfer.jsonl`을 사용한다. `communication.jsonl`과 영상은 원래 gate를 표시할 수 있다.

완료한 기존 E1 seed1을 재사용하고 seeds2·3만 새로 학습하는 실행 예시다. **이 기록 작성에서는 실행하지 않았다.**

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_pgct_transfer_experiments.ps1 -Seeds 1,2,3 `
  -ReuseExperiment "runs/sp_20261008_120638_983201"
```

Random schedule, 부족량, 평가 지표, 모드별 제약은 [실행기 문서](examples/PGCT_TRANSFER_EXPERIMENTS.md)를 확인한다.

## E09. E2 연결 성분과 완전 연결 구분 — 2026-10-13 진단 완료

대상: 완료된 `e2_pgct_s1/communication.jsonl`의 전체 3,907 update. `transfer_weights`의 어느 한 방향이라도 양수인 쌍을 무방향 edge로 계산했다. 이 run은 양방향 support가 비대칭인 update가 0회였다. 분모에는 warmup과 연결 없는 update도 포함한다.

| 최대 연결 성분 크기 | Update 수 | 완전 연결 여부 |
|---|---:|---|
| 1 | 1,636 | 전이 edge 없음 |
| 2 | 1,592 | 두 개씩 분리된 경우는 이 중 13회 |
| 3 | 661 | 세 쌍 모두 연결 244회, 일부만 연결 417회 |
| 4 | 18 | 모두 일부만 연결; 네 agent의 여섯 쌍이 모두 열린 경우는 0회 |

예시: 1,266,688 step의 1·2·4는 세 쌍 모두 열렸다. 2,538,496 step에서는 1–2, 1–4, 2–3 세 edge가 네 agent를 연결했지만 1–3, 2–4, 3–4는 열리지 않았다. 모든 agent가 서로 유사하거나 실제 팀 구성이 바뀌었다는 뜻은 아니다.

이 분석은 probe가 이동 상태에 치우쳤는지나 전이가 유익했는지를 측정하지 않는다. 학습·원본 로그·모델은 변경하지 않았다.

근거: [연결 수치와 예시](output/learning_review_20261013/e2_components.json), 재현 코드 `output/learning_review_20261013/analyze_e2_components.py`.

## E10. 분리된 장애물·배송 제약 환경 — 2026-10-13 구현 및 시험 완료

새 환경ID는 `rware-constrained-4ag-2teams-v0`다. 기존ID 등록 파일과 원래trainer는 수정하지 않았다. 전용 실행기 `examples/run_hard_rware_experiments.ps1`의 기본은동일 Stage03→detour의PGCT/IPPO seed1 각4,000,768step이며, **해당 장기 학습은 아직 실행하지 않았다.**

| Profile | 제약 | 선반 수 | 평균 적재 최단 경로 | 고정 E2 모델 delivery/episode |
|---|---|---:|---:|---:|
| control | 원래 E2와 같은 동역학 | 108 | 13.370 | 37.8 |
| detour(기본) | (3,14)/(12,14)에 벽2개 | 108 | 14.444 | 5.4 |
| bottleneck | y=7의벽14개, x=3·12만개방 | 108 | 17.074 | 2.2 |
| dock | bottleneck + 배송후8-step적재진입대기 | 108 | 17.074 | 2.2 |

경로 수치는preview reset seed5,000,001의모든shelf→해당팀goal 최단거리다. Frozen평가는`runs/sp_20261008_120638_983201/e2_pgct_s1/final.pt`의deterministic masked policy, seeds5,000,001–5,000,005,5×500이다. 모델hash불변. 이표의성능은초기distribution shift이며재학습난이도·성능상한·PGCT이득을판단하지않는다.

검증: 새환경17개를포함한관련32 tests통과. 4 profiles×PGCT/IPPO8조건각64-step CPU학습·평가·final저장완료. 새control weights는기존E2 smoke의128 tensor와bitwise일치. 기존핵심10개파일SHA256보존. 모든shelf의적재가능경로, 50reset seed의spawn, 벽/마스크/로컬관측, dock종료시간, 실제배송/반납, RGB영상저장검증.

성공smoke: `runs/hard_smoke_20261013_final/experiment.json`.
근거: [검증 결과](output/hard_rware_validation_20261013/validation.json), [Frozen 평가](output/hard_rware_validation_20261013/frozen_difficulty_pilot_v2.json), [지도](runs/hard_smoke_20261013_final/maps.png), [실행 문서](examples/HARD_RWARE_EXPERIMENTS.md).

수동canonical probe와gate/threshold는유지했다. 기존probe constructor에새환경인자3개를전달하지않도록임시호환adapter만사용한다. 장애물전용probe는추가하지않았다. Shader/OpenGL없는별도RGBrenderer와1593차원호환semantic wrapper를사용한다.

원래W&B·학습을건드리지않도록전용runner는기본W&B/영상off이며필요시`-Track -SaveVideo`로켠다. 자세한제약·reward해석·실행명령은문서를참조한다. v1/v2실패폴더와v3의초기3-profile검증은최종장기학습결과로세지않는다.

## E02 추가 — E3 PGCT 중단 (2026-10-13 Claude Code 실측)

18:21 KST Windows 재부팅으로 `e3_pgct_s1` 프로세스가 종료됐다. 시스템 로그에는 정상 종료와 Kernel API에 의한 reboot가 기록됐다. 마지막 metrics 2,855,936 step, 마지막 checkpoint `checkpoint_02700.pt`(2,764,800 step), 마지막 평가 2,816,000 step delivery 28.6 / return 26.8, 관측 구간 AUC 23.49. `experiment.json`은 `running`/`planned`로 남아 있으며 수정하지 않았다. 기존 실행기는 같은 폴더로 이어 학습을 지원하지 않는다. 재개하지 않았다.

## E11. 실험 A — 국소 행동으로 팀 식별 가능성과 critic consensus 전제 — 2026-10-13 Claude Code, 완료

- 코드: `latent_team/exp_a_team_identifiability.py`. 출력: `output/latent_team/exp_a_20261013/`(`REPORT.md`, `summary.json`, `identifiability.png`, 모델별 npz).
- 모델: Stage03(E1 환경에서 평가), E1/E2 IPPO·PGCT seed1 final, Stage04 PGCT final. 각 모델 자체의 stochastic masked policy로 20회×500 step, reset seeds 5,200,001–5,200,020. 모든 모델 weight hash 불변. 학습·gate·probe 변경 없음.
- 측정: canonical JS(각 run의 48개 bank, zero hidden), 이력 정책 JS(두 agent 각자의 관측 이력, 각 network의 자기 hidden), 방문 분포 JS, 국소 목격 증거(관측자 센서 범위 안의 상대 pickup·delivery를 관측자 팀 기준으로 분류, Beta(1,1)), critic 예측 차이, blend gain(초기 200 step 유한 MC return에서 `MSE(V_i) - MSE((V_i+V_j)/2)`).

| 모델 | canonical JS AUROC / 팀원식별 | 이력 JS | 방문 JS | 국소 증거 | critic gap | blend gain |
|---|---|---|---|---|---|---|
| Stage03→E1 env | .500 / .250 | .282 / .013 | .379 / .062 | 1.000 / 1.000 | .242 / .050 | .325 / .150 |
| E1 IPPO | .375 / .000 | .267 / .000 | .408 / .113 | 1.000 / 1.000 | .001 / .000 | .251 / .113 |
| E1 PGCT | .375 / .000 | .267 / .000 | .333 / .013 | 1.000 / 1.000 | .000 / .000 | .290 / .125 |
| E2 IPPO | .375 / .250 | .810 / .675 | .867 / .825 | 1.000 / 1.000 | .452 / .250 | .493 / .263 |
| E2 PGCT | .500 / .250 | .853 / .850 | .821 / .725 | 1.000 / 1.000 | .554 / .450 | .470 / .225 |
| Stage04 PGCT | .500 / .250 | .291 / .000 | .365 / .075 | 1.000 / .994 | .013 / .000 | .289 / .113 |

AUROC는 같은 팀 쌍 점수가 높을수록 1이다. 팀원식별은 각 agent의 최고 점수 상대가 팀원인 비율이고, 우연 수준은 .333이다.

- 국소 증거는 모든 모델에서 첫 episode(500 step)만으로 6쌍 모두 증거를 얻어 팀원을 맞혔다. 20 episode 누적 동안 같은 팀 쌍의 반대 증거는 0–13회였다(최대는 Stage04 2–4 13회, 같은 쪽 증거는 수백 회). 다른 팀 쌍의 같은 팀 증거는 0회였다. Episode 단위 팀원식별은 Stage04만 .994였다.
- E1 계열 critic: 같은 팀 쌍의 예측 차이가 더 크다. E1 IPPO gap 1–3 12.19, 2–4 14.56, 3–4 .54. 초기 MC MSE는 Agent1·2(1.7–3.7)가 Agent3·4(.37–.69)보다 높아 agent별 숙련/역할 차이가 팀보다 지배적이다. E2는 모든 쌍의 gap .03–.06, blend gain 약 0이다.
- 한계: 단일 training seed 체크포인트, 종속 표본, 2 same/4 cross 쌍이다. 국소 증거는 env 이벤트와 위치로 관측자가 볼 수 있는 사건을 재구성한 것이며, 관측 텐서에서 학습된 추론기가 아니다. 이 환경은 팀을 요청·목표로 정의하므로 증거가 거의 정답 수준이다. 일반화는 미확인이다. Blend gain은 유한 horizon MC(zero tail)와 각 모델의 방문 분포에 의존한다. 결과 해석(관측이 팀 기준이고 individual reward에서 팀원이 경쟁)은 가설이다.

## E12. 실험 B 실행기 — oracle/all/wrong critic peer-loss 분기 — 2026-10-13 Claude Code, 구현·smoke만

- 코드: `latent_team/exp_b_oracle_consensus.py`, `latent_team/run_exp_b.ps1`, 설명 `latent_team/README.md`. 기존 trainer의 `graph_mode=oracle/unrestricted/wrong`을 그대로 사용한다. 기존 E1 PGCT seed1과 같은 Stage03·환경·PPO·예산 4,000,768 step·평가 seed를 쓰고, 그 run의 canonical bank를 미리 넣는다. 처음 100 update는 전이를 보류한다. `transfer.jsonl`에서 실제 allocation과 팀/물리 범위 위반 여부를 검사한다. 기존 PGCT/IPPO run은 읽기 전용으로 비교한다.
- 검증: dry-run에서 세 mode 모두 기존 E1 PGCT와 `graph_mode`만 다름을 확인했다. `runs/lt_b_smoke_20261013` 64-step CPU smoke에서 oracle 같은 팀 arc 6/다른 팀 0, all 6/12, wrong 0/12, 모두 물리 이웃 범위 안이었다. 세 run의 canonical bank가 기존 E1 PGCT bank와 동일했다. 비교표가 기존 E1 AUC 45.8559/44.5734를 재현했다. `tests/test_latent_team.py` 6 tests, 관련 기존 테스트 포함 19 passed.
- **장기 학습 미실행.** 예상 소요는 기존 E1 속도 기준 run당 약 30시간이다. Learned-team mode는 구현하지 않았다.

## E13. 국소 증거의 관측 가능성 검증 — 2026-10-13 Claude Code, 완료

- 코드: `latent_team/verify_evidence_observability.py`. 결과: `output/latent_team/exp_a_20261013/observability_check.json`.
- 조건: E1 IPPO, E2 IPPO, Stage04 PGCT final. 자체 stochastic masked policy로 5회×500 step, seeds 5,200,001–5,200,005. weight 불변.
- 결과: 실험 A가 센 (관측자, 대상, 사건)마다 관측자의 post-step semantic 관측에서 대상 칸을 확인했다. pickup 985건(362/193/430)과 delivery 1,161건(474/214/473) 모두 agent+loaded로 보였다. `requested_shelf`(pickup)·`relevant_goal`(delivery) 채널 값도 증거 라벨과 100% 일치했다.
- 한계: 관측의 agent 칸에는 ID가 없다. 사건을 특정 이웃에게 귀속하는 것은 이웃 식별 가정이다. 정지 상태로 운반 중인 agent와 막 pickup한 agent는 관측상 구분되지 않는다.

## E12 추가 — 짧은 matched-prefix 예산 지원 (2026-10-13 Claude Code)

트레이너에 학습률 schedule이 없음을 확인했다(`total_timesteps`는 update 수만 결정). 이에 따라 `--timesteps`가 기준 run보다 짧으면 `total_timesteps` 차이만 추가로 허용하고, 비교표는 기준 run을 같은 step에서 자르도록 했다. Dry-run에서 1,024,000 step oracle 계획을 확인했다. 기존 E1 첫 1,024,000 step의 delivery AUC는 IPPO 43.828, PGCT 44.605(평가 20회)다. 관련 test 1개를 추가해 20 passed. **학습은 실행하지 않았다.**

## E14. 처음부터 학습 실행기 — 2026-10-13 Claude Code, 구현·smoke만

- 코드: `latent_team/train_from_scratch.py`, `latent_team/run_from_scratch.ps1`(병렬은 job별 별도 프로세스, 스레드 4). `exp_b_oracle_consensus.matched_transfer`에 초기 가중치 hash 기록과 ippo/pgct 허용 조건을 추가했다.
- 기본 조건: E1 맵 11×10, 4 agents/2 teams, home .5, 요청 4, individual reward, 무작위 초기화, lr 2e-4, entropy .05(기존 Stage03 분기 실험은 1e-4/.02), rollout 1024, 10M step, 평가 51,200 step마다 20×500(seeds 5,000,001–), checkpoint 250 update마다.
- 검증:
  - `runs/scratch_smoke_20261013`: 5 modes 순차 64-step CPU.
  - `runs/scratch_smoke_parallel_20261013`: 4 modes 병렬. 첫 병렬 시도 2회는 상태 파일 읽기 경합으로 비교/상태 기록 오류가 났고, 원자적 교체와 재시도로 수정한 뒤 재실행해 전부 complete.
  - 모든 mode의 초기 가중치 hash가 동일했다(`baaa10bf…`, Stage03 `b5e2158b…`와 다름).
  - 전이 arc는 ippo 0/0, pgct 6/12, oracle 6/0, all 6/12, wrong 0/12(같은 팀/다른 팀)였다.
  - 전체 tests 179 passed(plan 검사 test 포함).
- **장기 학습 미실행.** 기존 E1 속도 기준 예상 소요는 run당 2M 약 15시간, 10M 약 75시간이며, 병렬 시 더 느려질 수 있다.

## E14 추가 — 2단계 자동 파이프라인 (2026-10-13 Claude Code)

사용자 요청("1번 끝나면 자동으로 2번 돌아가게")에 따라 다음을 추가했다.
- `latent_team/run_scratch_pipeline.ps1`: 1단계 pilot의 모든 job이 complete이면 2단계 본 비교를 시작한다. `-Detach`로 백그라운드 실행.
- `run_from_scratch.ps1`의 `-Wait` 옵션.

`-SmokeTest -Detach` 검증(`runs/scratch_pipeline_smoke_20261013_*`, 각 64-step): 19:23:37 시작, 1단계 2 jobs 완료 후 19:23:46 2단계 시작, 4 jobs 완료 후 19:23:55 종료. 장기 학습은 시작하지 않았다.

## E14 점검 — 실행 전 코드·설정 검토 (2026-10-13 Claude Code, 학습 미실행)

사용자 붙여넣기 점검 요청 4항목. 실제 크기 plan을 scratchpad에만 만들었고(plan-only, bank 생성), env 학습은 하지 않았다.
1. **Stage1 checkpoint 재사용 없음**:
   - 두 단계 모두 `init_checkpoint=""`이고, pipeline은 출력 폴더만 다르다.
   - Stage1과 Stage2의 같은 mode 설정 차이는 `total_timesteps`, `save_dir`, `wandb_group`뿐이며 probe bank는 동일하다.
   - 트레이너에 학습률 schedule이 없으므로 **Stage1 2M ippo/oracle은 Stage2 10M ippo/oracle의 앞 2M과 같은 학습(prefix)**이다. GPU 비결정성으로 bitwise 일치는 보장되지 않는다.
2. **같은 초기 파라미터**:
   - 실제 트레이너 smoke(CPU)에서 stage1/stage2 6개 run의 초기 actor+critic hash가 모두 같았다(`baaa10bf…`).
   - 트레이너는 네트워크를 CPU에서 만든 뒤 `.to(device)` 하므로(`train_recurrent_ippo_consensus.py` 4757–4766행) device=auto(CUDA)에서도 초기화는 CPU RNG를 따른다. 별도 재현 코드에서 cpu와 cuda hash가 같음을 확인했다.
   - 다만 그 재현 hash(`69ca…`)는 트레이너 hash와 달라 재현이 완전하지 않다. 실제 GPU run의 일치 여부는 `initial_weights_sha256.txt`/`comparison.md`로 확인해야 한다.
3. **성능 gate 없음**: 현재 pipeline은 Stage1 job이 오류 없이 끝났는지만 본다. 학습이 안 돼도 약 75시간짜리 Stage2가 시작된다. 위 1의 prefix 관계 때문에 Stage1은 Stage2와 중복 계산(약 15시간×2 프로세스)이다.
4. **GPU/CPU**:
   - GPU: RTX 5070 Ti 16,303 MiB(사용 중 780 MiB). agent당 1,268,550 파라미터. 4 agents + PPO 크기 minibatch(16×64 step) fwd/bwd의 peak 할당은 143 MiB이고, CUDA context는 프로세스당 수백 MiB로 추정한다. 4 프로세스 병렬도 메모리 여유가 크다.
   - CPU: Core Ultra 7 265K 20코어, RAM 31.3GB(여유 17.4GB). 4 job×4 thread=16. 기존 E1 37 step/s는 Python 환경 step과 평가가 지배하는 것으로 추정한다(GPU 사용률 측정은 미실시). 병렬 시 job별 속도는 실측이 필요하다.
   - Windows Update 활성 시간이 8–17시이고, E3를 중단시킨 18:21 재부팅은 활성 시간 밖이었다. 자동 업데이트 재시작일 가능성이 있다(가설).

## E15. W&B 통합 + MAPPO/SePS/HetDPS 구현 — 2026-10-13 Claude Code, smoke만

- **W&B**: 트레이너의 `init_wandb`/`log_to_wandb(step=env_steps)`를 재사용하고 runner에서 project·group·tags·config·gate 지표를 추가했다.
  - `runs/wbsmoke_20261013_*`(`-Detach -Track`)에서 project `rware-from-scratch-smoke`에 3 run이 finished로 기록됐다. Step은 [32, 64]이고 config에 algorithm/stage/seed가 들어갔다.
  - pipeline 로그를 UTF-8로 바꿨다.
- **학습 구간 근거**: `runs/recurrent_ippo_consensus/ex5_semantic_cnn_policy_complete_from_scratch_.../wandb/run-bhh1l6x8.wandb` history(9,766 rows)를 읽기 전용으로 파싱했다(수치는 D21).
  - 같은 폴더의 IPPO from-scratch 기록(tkz072ou/kfomo827)은 약 1M step뿐이다. pickup은 0.76M에 시작했고 delivery는 1M 안에 거의 없었다.
  - 이전 run과 현재 계획의 차이: home 1.0 vs .5, communication complete vs physical. 보상과 맵은 같다.
- **baseline smoke**(각 64-step CPU):
  - `runs/baseline_smoke_mappo_20261013`, `runs/baseline_smoke_seps_20261013`(sklearn 부재로 seps 실패 기록), `runs/baseline_smoke_seps2_20261013`, `runs/baseline_smoke_hetdps_20261013`
  - `runs/baseline_smoke_all_20261013`: ippo/mappo/seps/hetdps, W&B 포함, 4 run finished
- **추가 비용 측정**(GPU, 무작위 데이터, env 학습 아님): HetDPS 측정 1회 약 4.4초(15M step 기준 4,687회 약 5.8시간), SePS VAE 1회 약 9.1초.
- **테스트**: 전체 182 passed.
- **본 학습은 실행하지 않았다.** 상세 구현·차이: `latent_team/BASELINES.md`.

## E16. 본 학습 전 실제 설정 검증 — 2026-10-13 Claude Code, 검증만

- **실행**: `runs/verify_realcfg_20261013`. `run_from_scratch.ps1 -Modes ippo,pgct,oracle,all -TotalTimesteps 4096 -Parallel -ThreadsPerJob 4`, 실제 학습 설정(device=cuda, rollout 1024, seq 64, 평가 20×500은 종료 시 1회). W&B는 끄고 4 update만 실행했다. **본 학습 아님.**
- **초기 파라미터**: 4 run 모두 첫 update 전 actor+critic hash `f78ec390e0fad60c…`로 같다.
  - CPU smoke 설정의 hash(`baaa…`)와 다른 것은 설정 차이 때문이다. 같은 설정 안에서 mode 간 일치가 요구 조건이다.
  - 모든 run이 complete였고 오류 로그는 없다. PGCT/oracle 전이는 warm-up 100 update 때문에 이 4 update에서는 발생하지 않는다. 전이 경로는 smoke(E14)에서 검증했다.
- **속도**: 4 프로세스 병렬에서 update당 38.5–39.5초(job당 약 26 step/s, 합계 약 105 step/s). 15M이면 약 6.6일 이상이고 평가 시간이 추가된다.
- **용량**: checkpoint 61MB × 250 update 간격 → run당 약 3.6GB. 디스크 여유는 1.5TB다.
- **resume 검증**: 코드 검토 결과 불가능하다(D22).

## E17. From-scratch 핵심 비교 본 학습 — 2026-10-13 20:23:52 KST 시작(사용자 실행), 진행 중

- **경로**: `runs/scratch_20261013_202352_stage2`, 로그 `runs/scratch_20261013_202352_pipeline.log`.
- **조건**: IPPO/PGCT/Oracle/All, seed1, 15M, 병렬 4 프로세스(PID 10392/29856/12684/24828), W&B.
- **20:27 KST 무렵 확인**
  - 4 run 모두 2,048 step, update당 약 40.6초로 15M까지 약 7일 예상.
  - GPU: nvidia-smi 사용률 70–81%(사용자 작업관리자에서는 95–99%로 보임), 전력 78–83W/300W, 온도 50–52°C, 팬 0%, VRAM 2.6/16.3GB.
  - CPU 59%, 프로세스당 RAM 약 2.1GB, 여유 RAM 10GB.
- **해석**: 사용률 수치는 GPU가 작은 kernel을 실행 중인 시간 비율이다. 전력·온도로 보면 하드웨어 부하는 낮다. 6–7일 연속 실행의 주요 위험은 GPU 마모가 아니라 재부팅·절전·정전, 다른 GPU 작업과의 경합이다.

## E17 추가 — Windows Update 재부팅으로 중단 (2026-10-15 Claude Code 실측)

- 2026-10-15 00:59 KST에 MoUsoCoreWorker가, 01:01 KST에 TrustedInstaller가 "운영 체제: 업그레이드/서비스 팩" 사유로 재시작을 실행했다(System 이벤트 1074/109). 원인은 Windows Update다.
- 마지막 metrics: ippo 2,487,296, pgct 2,502,656, oracle 2,471,936, all 2,455,552 step(00:58–00:59 기록). 마지막 checkpoint는 4개 모두 `checkpoint_02250.pt`(2,304,000 step)이고 job_status는 `running`으로 남아 있다.
- 최근 평가 delivery(약 2.4–2.46M): IPPO 2.9, PGCT 2.2, Oracle 10.7, All 4.2. 단일 seed이고 중단된 초기 구간의 값이다.
- 폴더와 로그는 보존했다. 정확한 재개는 불가능하다(D22).

## E18. E17 중단 시점(약 2.5M) 학습 현황 분석 — 2026-10-15 Claude Code, 읽기 전용

- **코드·산출물**: `output/scratch_review_20261015/`(analyze.py, analysis.json, curves.png, REPORT.md, reference_home1_pgct_eval.json).
- **조건**: E17 seed1. 공통 평가 구간 51,200–2,406,400 step. deterministic 20×500 평가. 인접 평가 간 차이의 std는 .2–.8 delivery.
- **평가 delivery**(마지막 3회 평균 / AUC per step)
  - IPPO 3.10 / .41, PGCT 1.92 / .26, **Oracle 9.98 / 1.28**, All 3.45 / .69.
  - 요청 pickup은 20.7 / 2.2 / 10.4 / 15.2, return은 1.12 / .98 / 9.43 / 1.37.
- **onset**(3점 평균): pickup≥1은 IPPO 1.89M, PGCT 1.89M, Oracle 1.64M, All 1.79M. delivery≥1은 2.05 / 2.15 / 1.89 / 1.89M. delivery≥5는 Oracle만 2.25M.
- 모든 mode에서 0.5–1.5M은 보상이 거의 없는 정체 구간이었다.
- **agent별 delivery**(마지막 3회): IPPO [1.63, 1.47, 0, 0], PGCT [1.92, 0, 0, 0], Oracle [0, 9.98, 0, 0], All [0, 2.12, 1.33, 0]. 성능이 1–2명에게서만 나온다. **Oracle 우위는 Agent2 한 명의 선행 학습이며, 단일 seed로는 효과에 귀속할 수 없다.**
- **전이**(warm-up 후 전이 update 비율 / same / cross arc-update)
  - PGCT 77% / 3,496 / 5,590, Oracle 76% / 4,688 / 0, All 99% / 5,526 / 10,524. IPPO는 0이다.
  - PGCT gate의 pair별 개방 횟수는 같은 팀(826, 922)과 다른 팀(500–886)이 비슷해, 초기에 팀을 구분하지 않았다.
- **학습 지표**(1.5M 이후): entropy IPPO .83, PGCT .83, Oracle .76, All .89. value loss .002–.006. approx_kl 약 .003. 속도 job당 약 24 step/s.
- **참고**(조건 다름): 이전 home 1.0·complete graph PGCT는 2.4M에 delivery 26.7이었다.
- **한계**: seed 1개, 초기 구간, 중단된 run이다. 결론이 아니라 방향 관찰이다.

## E19. 신규 from-scratch 재실행 발견 — 2026-10-15 11:49 KST Codex, 읽기 전용 확인

- **경로:** `runs/scratch_20261015_093349_stage2/experiment.json`. 이번 작업 이전에 생성된 실행이다. 본 turn에서는 학습을 시작·중단·재시작하지 않았다.
- **조건:** E1 11×10, home.5, individual reward, 4agents/2teams, sensor/communication range5, IPPO/PGCT/Oracle/All, training seed1, 무작위 초기화(`init_checkpoint=""`), 요청 예산15,000,000/실제 반올림15,000,576 env steps.
- **진행 스냅샷(11:49):** IPPO200,704 / PGCT198,656 / Oracle196,608 / All199,680 env steps. `job_status.json`은 모두running이며 metrics 수정시각은11:48:58–11:49:28이다. 반복 확인에서 로그가 증가했다. CIM 프로세스 조회는 접근 제한으로 확인하지 못했다.
- **초기화:** 4mode의 `initial_weights_sha256.txt`가 모두 `f78ec390e0fad60c9bee9ea045525a79befbd71357f41235f04d61356b91c7e3`다.
- **평가:** 네 mode 모두 최근153,600step, delivery0.0/episode. deterministic masked, reset seeds5,000,001–5,000,020, 20×500. 초기 단계의 결과이며 실패로 판정하지 않는다.
- **E17과의 관계:** 중단된2.5M run의 resume이 아니라 같은 seed1의 처음부터 재실행이다. 독립training seed 추가나 이전곡선의 연장으로 세지 않는다.
- **근거:** `output/ijcai_review_20261015/live_run_snapshot.json`, 해당 run의 manifest/metrics/status/초기hash. 논문용 해석과 후속 제안은 같은 폴더REPORT 및 D23에 기록했다. 새 실험·추가 평가·tests는 실행하지 않았다.

## E20. 환경·canonical probe 시각화 — 2026-10-15 Claude Code, 읽기 전용

- **환경 그림**: `output/env_view_20261015/environment_seed5000001.png`. 실행 중 run의 환경 설정으로 그린 전체 맵, Agent1·2의 11×11 팀 기준 관측. 팀 목표가 (4,10)/(5,10)으로 인접한다.
- **probe 그림**: `output/env_view_20261015/probes/`(official 렌더링 48장과 contact sheet, decoded_bank.png, probes.csv, README.md).
- **bank 검증**: 저장소 builder로 같은 env 상태(reset seed 1)와 rng(seed+9173)로 다시 만든 bank가 run의 `canonical_bank_e1_s1.pt`와 완전히 같다.
- **중복 구조**: 고유 입력 26/48.
  - `dual_requested_*` 7종이 팀마다 하나의 입력으로 겹친다(8개 × 2그룹).
  - goal_pair·goal_zone_pair·lane_choice가 팀마다 하나로 겹친다(4개 × 2그룹).
  - neutral은 2개 × 2그룹이다.
- **겹침 원인(추정)**: 해독한 시야에서 요청 선반이 대부분 가장자리에 1개만 보인다. 서로 다른 두 번째 선반 위치가 11×11 관측 밖이라는 추정이며, builder 코드로는 확인하지 않았다.
- **상태 구성**: 빈 손 38, 요청 선반 적재 10(반납 단계 4). 요청되지 않은 선반을 든 상태는 0이다.

## E21. runs/ 정리 — 2026-10-15 Claude Code (사용자 승인 삭제)

- **승인 범위**: 사용자가 ① smoke·dry·실패 시험, ② 삭제된 09700 일반화 도구의 옛 평가 결과, ③ 중단된 `scratch_20261013_202352_stage2`의 checkpoint, ④ 큰 결과 폴더의 중간 checkpoint를 모두 선택했다. 500개 항목 27.26GB를 삭제해 runs/는 35GB에서 7.4GB가 됐다.
- **삭제 목록**: `output/cleanup_20261015/removed_manifest.json`.
- **위 E-항목에서 이제 존재하지 않는 경로**
  - ①: `sp_smoke/sp_check/sp_dry_20261008*`, `tr_*_20261008*`, `hard_smoke_20261013_v1~v3`, `lt_b_smoke_20261013`, `baseline_smoke_*_20261013`, `scratch_smoke*_20261013`, `scratch_pipeline_smoke_*`, `wbsmoke_20261013_*`, `verify_realcfg_20261013`, `communication_smoke`, `ex5_smoke`, `fov_passive`, `generalization_*`, `pgct09700_curriculum_*`, `pgct_09700_graph_smoke`
  - ②: `pgct_09700_generalization_6_8_seed12345`, `pgct_09700_maps_6_8_seed12345`
  - 해당 항목의 수치 기록은 노트에 남아 있지만, 원본 smoke 출력은 재검사할 수 없다.
- **유지한 것**
  - 실행 중인 `scratch_20261015_093349_stage2` 전체(삭제 후에도 4개 run 모두 로그 갱신 확인)
  - `sp_20261008`, 커리큘럼, `recurrent_ippo_consensus`, `hard_smoke_20261013_final`의 모든 로그와 final.pt
  - final.pt가 없는 run의 마지막 checkpoint: E3 `checkpoint_02700`, IPPO 사전학습 `checkpoint_00900`, PGCT 9700 사전학습 `checkpoint_09700`
  - E05가 참조하는 E1 PGCT `checkpoint_00600`
  - 중단된 run의 metrics/transfer/spatial 로그(E18 분석 근거)
- **영향**: 중간 시점 checkpoint를 재평가할 수 없게 됐다(예: Stage·E1/E2의 50k–3.9M 중간 모델). 전체 tests는 삭제 후 182 passed.

## E22. probe bank v2 / E1-F 구현 검증 — 2026-10-15 Claude Code, 구현·smoke만

- **bank**: `output/env_view_20261015/probes_v2/`(e1f·e1 각 gate 48 + transfer 64, 역할 내 중복 0, 검증 거부 0).
  - transfer 구성: 탐색 14, 목표 보임 16, 목표 안 보임 16, 반납 16, 목표 도착 2.
  - gate 위치는 모두 y≤4로, 어느 목표도 시야 밖이다.
- **smoke** `runs/smoke_e1f_v2_20261015`: e1f × ippo/pgct/oracle/all 64-step 모두 complete. PGCT의 `canonical_probes.pt`는 v2 gate와 같다. PGCT/Oracle/All의 증류 입력은 64개다(`distill_probe_count`).
- **tests**: E1-F 모서리 목표에서 적재 agent가 전진하면 delivery event가 발생함을 확인했다. 전체 183 passed.
- **한계**: E1-F 학습 정책에서 same/cross JS 판별력, Oracle 이득은 아직 미측정이다.

## E19 추가 — HANDOFF 이후 진행 상태 재확인 (2026-10-15 13:17 KST Codex)

- **같은 실행의 후속 확인:** `runs/scratch_20261015_093349_stage2`, E1 11×10/home .5/individual reward/4 agents·2 teams, 무작위 초기화 training seed 1, 기존 canonical bank, 15M 목표. IPPO 321,536 / PGCT 316,416 / Oracle 314,368 / All 318,464 env steps. 로그 시각 13:16:39–13:17:05, 네 status는 running, 속도 23.49–24.04 step/s다. 최초 확인보다 로그가 증가했고 초기 hash 4개도 동일하다.
- **최근 평가:** 네 mode 공통 307,200 step, deterministic masked 20×500, reset seeds 5,000,001–5,000,020. 요청 pickup/delivery/return 각 0.0이다. 초기 단계이며 성능 판정을 하지 않는다. 마지막 checkpoint는 모두 00250(256,000 step)이다.
- **실행 건강 확인:** .err.log의 Traceback/Error/Exception/failed 일치 0건. Gymnasium 정밀도·reward 형식 경고와 W&B 안내가 있다. 이는 전체 학습 정확성의 독립 검증은 아니다.
- **별도 구현 확인:** E22 seed 1의 64-step smoke 4 mode가 complete이며 PGCT/Oracle의 transfer.jsonl에서 distill_probe_count 64와 Oracle cross arc 0을 확인했다. v2 summary는 gate 48/transfer 64, 고유 입력 검증 통과다. 장기 E1-F/v2 실행은 발견되지 않았다. 183 tests 통과는 Claude 기록이고 재실행하지 않았다.
- **산출물/범위:** `output/status_review_20261015_131716/snapshot.json`. HANDOFF·RESEARCH_STATE·대화 원문을 갱신하고 통합 사본을 재생성한다. 새 학습·추가 평가·tests·알고리즘 변경·삭제·학습 중단은 하지 않았다.

## E23. 기존 E1 모델의 probe별 팀 구분 시각화 — 2026-10-15 Claude Code, 읽기 전용

- **코드·산출물**: `output/probe_team_check_20261015/`(probe_team_check.py, js_matrices.png, same_vs_cross.png, results.json).
- **모델**(고정, 실행 전후 hash 동일, CPU): Stage03 final(3.0M), Stage04 PGCT final(4.0M), sp_20261008 E1 IPPO/PGCT final(4.0M). 모두 E1 11×10이고 목표가 인접한다. Stage03 계열 seed 1이라 독립 반복이 아니다.
- **bank**
  - canonical 48: `sp_20261008/e1_pgct_s1/canonical_probes.pt`, 고유 26개.
  - v2 e1 gate 48: `output/env_view_20261015/probes_v2/probe_bank_v2_e1_s1.pt`.
  - v2 transfer 부분집합: 적재+목표 보임 18 / 적재+목표 비가시 16 / 빈손 탐색 14.
- **조건**: 같은 입력, zero hidden, unmasked, seq 1(PGCT 규칙), 자연로그 JS. 같은 팀 = A1–A3, A2–A4.
- **결과**
  - 20개(모델×bank) 모두 같은 팀 평균 JS > 다른 팀 평균 JS.
    - canonical: 같은 팀 .36–.42 / 다른 팀 .30–.36.
    - v2 gate: 같은 팀 .24–.28 / 다른 팀 .18–.22.
  - 쌍 단위 AUROC는 0–.62(대부분 .12–.38)다.
  - 가장 가까운 상대가 팀원인 agent는 4명 중 0–2명이다(우연 기대치 1.33).
  - 가장 가까운 쌍은 대부분 A3–A4(다른 팀)다.
  - 목표 보임과 목표 비가시 부분집합 사이에 뚜렷한 차이가 없다.
- **해석·한계**
  - E1에서는 bank 종류와 관계없이 actor 응답 JS로 팀이 구분되지 않는다. E11의 canonical 결과와 같은 방향이다.
  - v2 gate의 E1-F 효과는 E1-F 학습 모델이 없어 미검증이다.
  - E1 모델의 v2 gate 같은 팀 JS(.24–.28)가 0.12를 넘는다. threshold 우려(D31)의 참고 근거다.

## E23 추가 — agent별 행동 특성 (2026-10-15 Claude Code, 읽기 전용)

- **산출물**: `output/probe_team_check_20261015/agent_profiles.json`.
- **최종 평가 delivery**(A1/A2/A3/A4)
  - Stage04: 197/168/287/293
  - E1 IPPO: 186/162/267/278
  - E1 PGCT: 174/170/273/270
  - Stage03: 237/250/225/285
- **canonical probe 응답**
  - A3·A4는 Forward 위주다(A4 .81–.94, A3 .64–.75). A1·A2는 회전 비중이 크다(A2 Right .47–.57).
  - argmax 일치율: A3–A4 .69–.81, A1–A2 .08–.17, 같은 팀 쌍 .40–.58.
  - entropy는 .04–.3 nats로 정책이 거의 결정적이다.
- **해석**: E1 정책 유사도는 팀이 아니라 성능·행동 습관 묶음({A3,A4} / {A1,A2})을 따른다. Stage03에서도 A3–A4가 가까워 성능만으로는 다 설명되지 않는다.
- **가설(미검증)**: v2 gate에서 같은 팀원의 회전 방향 습관이 반대다(A1 Right, A3 Left). 공간 분담 가능성이며, 공간 기록은 미확인이다.

## E24. 현재 from-scratch run 약 6.4M 중간 분석 — 2026-10-18 Claude Code, 읽기 전용

- **대상**: `runs/scratch_20261015_093349_stage2`. E1 11×10, home .5, individual reward, seed 1, 무작위 초기화, IPPO/PGCT/Oracle/All, 각 15M 목표. 4개 모두 running이다.
- **진행(12:23 KST)**: IPPO 6,553,600 / PGCT 6,467,584 / Oracle 6,414,336 / All 6,502,400 step. job당 약 24 step/s, 15M까지 약 4.0–4.2일 남았다. run 6.4GB, C: 여유 1.5TB.
- **코드·산출물**: `output/scratch_review_20261018/`(analyze.py, analysis.json, overview.png). checkpoint probe JS는 CPU에서 고정 모델로 계산했다.
- **평가**(deterministic masked 20×500, reset seeds 5,000,001–5,000,020)

| mode | 배송 시작 ≥1(3점 평균) | 최근 5회 평균 delivery | 6.4M까지 AUC/step | agent별 최근 5회 delivery |
|---|---|---|---|---|
| IPPO | 2.05M | 24.3 | 10.4 | 12.3 / 11.9 / 0 / 0 |
| PGCT | 1.79M | 27.9 | 11.7 | 10.5 / 12.3 / 5.1 / 0 |
| Oracle | 1.64M | 32.3 | 13.2 | 11.0 / 11.3 / 9.9 / 0 |
| All | 3.99M | 20.4 | 3.7 | 4.3 / 7.0 / 5.3 / 3.8 |

  - 인접 평가 차이의 표준편차는 1.5–1.9다.
  - All은 늦게 시작했지만 4명 모두 배송하며, 현재 가장 가파르게 오른다. 요청 pickup은 52로 가장 많다.
- **실제 전이**(transfer.jsonl, warm-up 이후)
  - Oracle: 같은 팀(1–3, 2–4)만, update의 약 78–86%에서 전이했다.
  - All: 거의 모든 update에서 모든 쌍에 전이했다.
  - PGCT: 0–2M에는 모든 쌍에 열렸다(전이 update 87–95%). 2–3M 55%, 3–6M 12–33%로 줄었고, 같은 팀 arc는 3M 이후 거의 0이다. 남은 연결은 3–4와 1–2이며, 6M 이후에는 1–2 위주로 66%까지 늘었다.
- **canonical probe JS**(checkpoint 1M 간격): 3M 이후 대부분 시점·mode에서 같은 팀 평균 > 다른 팀 평균이다. Oracle 같은 팀 .29–.36이다. 2M 이후 같은 팀·다른 팀 평균이 모두 0.12를 넘는다.
- **E17과 비교**(같은 seed·초기 가중치)
  - IPPO는 2.46M까지 평가값이 완전히 같다.
  - PGCT/Oracle/All은 첫 평가 차이가 1.48/1.38/1.59M에서 생긴다. 원인은 미확인이며, 전이 경로의 비결정적 연산을 추정한다.
  - All 배송 시작이 1.79M → 3.99M으로 달라졌다. Oracle은 두 번 모두 A2가 먼저 배웠다.
  - 단일 seed 결과의 불안정성을 보여주는 근거다.
- **한계**: seed 1, 15M 중간 시점이다. 우열이나 효과 귀속 결론이 아니다.

## E25. E1-F 실험 실행기(pilot/main)·팀 보상 옵션·팀 분화 분석 도구 — 2026-10-18 Claude Code, 구현·smoke만

- **구현**
  - `train_from_scratch.py`에 `--team-reward individual|team`을 추가했다. 기본값 individual은 이전과 동일하며, 환경의 기존 `team_reward_mode`를 쓴다. team이면 배송·반납 보상이 팀 전원에게 가고 shaping은 개인으로 남는다. job 이름에 `_teamrew`가 붙는다.
  - `run_from_scratch.ps1`과 `run_scratch_pipeline.ps1`에 `-TeamReward`를 전달한다.
  - 새 `run_e1f.ps1`
    - pilot: IPPO individual/team, 5M.
    - main: 4 mode(canonical bank) + PGCT(v2 bank), 10M.
  - 새 `e1f_team_divergence.py`: checkpoint별로 배송 중 왼쪽 이동 비율(agent별)과 v2 gate·canonical 같은 팀/다른 팀 JS를 계산한다.
- **검증**
  - smoke `runs/smoke_e1f_runner_20261018_{pilot_individual,pilot_team,main_canonical,main_v2}`: 7 job 모두 complete.
  - checkpoint의 effective_env_kwargs에 team_reward_mode와 goals [(0,10)],[(9,10)]이 들어 있다.
  - canonical probe builder가 E1-F 목표를 사용한다.
  - 분석 도구 검증: E1 `scratch_20261015_093349_stage2/e1_oracle_s1/checkpoint_06000`에서 2×500 rollout, left_share A1–A3 .56/.47/.51(A4는 운반 없음). 출력은 scratchpad에만 남겼다.
  - tests 2개를 추가해 전체 185 passed.
- **미실행**: E1-F pilot/main 본 학습은 사용자 승인 대기다.
- **관련 관측(E24 보완, 현재 E1 run 6.4M, 읽기 전용)**
  - 최근 5회 평가 agent별 pickup: IPPO A3·A4 0(이동 비율 .37/.40), PGCT·Oracle A4 0.
  - 평가에서 episode당 pickup 1 이상이 된 시점: IPPO 1.89/2.05M/없음/없음, PGCT 2.46/1.43/5.27M/없음, Oracle 2.30/1.38/2.30M/없음, All 5.22/3.99/1.38/5.07M.

## E24 추가 — 사용자 요청으로 6.5M에서 중지 (2026-10-18 12:43 KST Claude Code)

- 사용자 지시("현재 실험은 중지하고, 다음 실험으로 run_e1f main 진행")에 따라 pipeline PowerShell(PID 21540)과 학습 4개(PID 27140/23940/2980/15160)를 종료했다. PID는 pipeline 로그 기록과 일치함을 확인했다.
- 종료 직전 상태
  - 마지막 env_steps: IPPO 6,579,200 / PGCT 6,498,304 / Oracle 6,444,032 / All 6,528,000.
  - 마지막 checkpoint는 모두 `checkpoint_06250.pt`다.
  - `final.pt`는 없고, `job_status.json`은 trainer가 쓴 running 그대로다. W&B run은 중단 상태로 남는다.
- 중지 기록 파일: `runs/scratch_20261015_093349_stage2/STOPPED_BY_USER.txt`. 로그·checkpoint는 모두 보존했다.
- 보완(같은 날, 사용자가 W&B running 표시 지적): 강제 종료한 학습 프로세스의 자식 wandb-core 4개와 wandb-xpu 4개가 남아 heartbeat를 보내고 있었다. 부모 PID로 확인해 종료했다. 이후 W&B에서는 crashed로 표시된다. 앞으로 학습을 중지할 때는 프로세스 트리 전체를 종료한다.
- W&B API 확인: 마지막 heartbeat는 13:45:30–33 KST이고, 13:55:14 KST에 4개 모두 `crashed`로 바뀌었다.
- 이 run은 15M 계획 대비 약 6.5M에서 끝난 seed 1 결과다. D36의 10M 고정 예산과도 다르므로, 이후 seed 반복 시 예산을 다시 정해야 한다.

## E26. E1-F main 본 학습 — 2026-10-18 12:43 KST 시작(사용자 승인, Claude Code 실행), 진행 중

- **명령**: `.\latent_team\run_e1f.ps1 -Phase main -Track`
- **조건**
  - E1 맵, 팀 목표 (0,10)/(9,10), home .5, individual reward, seed 1, 무작위 초기화, 10,000,384 step, W&B 프로젝트 rware-from-scratch.
  - `runs/e1f_20261018_124343_main_canonical`: IPPO/PGCT/Oracle/All, canonical bank.
  - `runs/e1f_20261018_124343_main_v2`: PGCT, probe bank v2.
  - 병렬 5개 프로세스, 스레드 4.
- **분석**(읽기 전용, 언제든): `python latent_team/e1f_team_divergence.py --run runs/e1f_20261018_124343_main_canonical`(main_v2도 동일).
- **참고**: E1-F pilot(IPPO 개인/팀 보상)은 실행하지 않고 바로 main을 시작했다. 팀 보상 비교는 미실행이다.
- **시작 확인(12:45)**: 5개 모두 첫 update를 기록했고 Traceback은 없다. job당 약 20–21 step/s로, 10M까지 약 5.5일(10월 24일 무렵) 예상이다. 초기 hash는 5개 모두 `f78ec390…`로 E1 seed 1과 같다.

## E27. E1 run(6.4M 중단) 논문용 자료 — 2026-10-18 Claude Code, 읽기 전용

- **폴더**: `output/paper_e1_20261018/`
  - `make_paper_materials.py`
  - `figures/`: fig1–4, figA1 (PDF+PNG)
  - `tables/`: table1–3, tableA1 (LaTeX)
  - `RESULTS_DRAFT.md`(영어 문단·캡션·한계), `README.md`(한국어, 주장 가능 범위), `numbers.json`
- **조건**: `runs/scratch_20261015_093349_stage2`, seed 1, 공통 평가 구간 0–6.4M. 평가는 51,200 step 간격, deterministic 20×500, reset seeds 5,000,001–5,000,020.
- **결과(seed 1)**
  - 배송 시작(≥1, 3점 평균): IPPO 2.05 / PGCT 1.79 / Oracle 1.64 / All 3.99M.
  - 학습 중 평균 배송: 10.4 / 11.7 / 13.2 / 3.7.
  - 최근 5회 배송: 23.2±1.1 / 27.3±1.4 / 32.2±1.7 / 19.4±1.6.
  - 배운 agent: 2 / 3 / 3 / 4.
  - PGCT 전이 update 비율은 91% → 37% → 29%이고, 같은 팀 arc/update는 1.86 → 0.10 → 0.03이다.
  - probe JS 같은 팀/다른 팀(6M): IPPO .27/.18, PGCT .26/.19, Oracle .29/.23, All .15/.14.
- **정정**
  - E17 All의 delivery 시작은 1.89M이다(E18과 동일). E24·T034에 쓴 1.79M은 pickup 기준과 혼동한 값이다.
  - E24 표의 최근 5회 값은 각 run의 마지막 평가 기준이다. E27은 공통 구간 6.4M 기준이라 IPPO 값 등이 조금 다르다.
- **한계**: seed 1개, 미수렴, E1의 팀 대칭성. 성능 우열·공유 범위 가설은 다중 seed 전까지 관찰로만 쓴다.

## 새 실험 기록 양식

ID / 실제 실행 날짜·작성 도구 / 상태(계획·smoke·진행·완료·실패) / 초기 모델 / 환경·training seed·예산 / 평가 seed·정책·horizon / 결과 / 비교 기준·한계 / 원본 경로 / 재현 명령.
