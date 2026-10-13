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

## 새 실험 기록 양식

ID / 실제 실행 날짜·작성 도구 / 상태(계획·smoke·진행·완료·실패) / 초기 모델 / 환경·training seed·예산 / 평가 seed·정책·horizon / 결과 / 비교 기준·한계 / 원본 경로 / 재현 명령.
