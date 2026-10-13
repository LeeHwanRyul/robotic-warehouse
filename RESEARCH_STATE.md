# PGCT 현재 연구 상태

기록 작성: 2026-10-13, Codex. 최신 정량 분석 스냅샷: **2026-10-13 14:37 KST**. 진행 중인 실험은 이후 달라질 수 있다.

## 한눈에 보는 현재 판단

**E1에서 PGCT의 평가 학습곡선 평균에 약 2.9% 이득 신호가 있지만, 최종 성능·critic 정확도·안정성 개선은 입증되지 않았다. E2의 on/off 성능은 거의 같고, E3는 대조군이 아직 없다.**

JS 수학 계산의 오류보다는 **어떤 probe/관측 분포에서 측정한 정책 유사성이 유익한 critic transfer를 예측하는가**가 현재 연구 질문이다. 실제 팀 발견을 목표로 유지할지, 팀 소속과 무관한 선택적 critic transfer로 확장할지는 확정하지 않았다.

## 프로젝트와 핵심 조건

- 루트: `C:\RWARE\MARL_RWARE\third_party\robotic-warehouse`.
- Python: `C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe`.
- 4 agents / 2 teams. 표시번호 1·3 = team 0, 2·4 = team 1. 코드의 agent index는 0-based다.
- `team_reward_mode=individual`. 같은 팀 소속이 동일한 개인 value target을 보장하지 않는다.
- Recurrent IPPO, semantic CNN observation, sensor range 5, action mask 사용.
- PGCT는 공통 canonical probe의 actor 응답으로 JS를 계산하고, 물리 이웃에서 갱신하는 EMA < 0.12 등을 만족할 때 critic 보조 전이를 허용한다.
- 실제 학습 probe는 48개, sequence length 1, zero hidden, unmasked다. 최종 raw JS와 과거 EMA 연결을 동일시하지 않는다.

## 모델·실험 경로

- 기존 curriculum: `runs/pgct09700_physical_mixing_20260929_155338_079437/`.
- 기존 최종 모델: 위 폴더의 `stage04_4ag_physical_home0.500/final.pt`.
- 새 비교의 공통 초기 모델: 위 폴더의 `stage03_4ag_physical_home0.750/final.pt`.
- 실제 공간 실험: `runs/sp_20261008_120638_983201/experiment.json`.
- 모든 공간 분기는 같은 Stage03 actor/critic에서 출발하며 optimizer/graph는 초기화된다. 따라서 **Stage03 이후 추가 전이의 조건부 효과**를 검증한다.

| 조건 | 학습 step | 마지막 delivery/episode | shelf return/episode | 상태(스냅샷) |
|---|---:|---:|---:|---|
| E1 11×10 PGCT seed1 | 4,000,768 | 44.35 | 42.65 | 완료 |
| E1 11×10 IPPO seed1 | 4,000,768 | 44.65 | 43.70 | 완료 |
| E2 16×16 PGCT seed1 | 4,000,768 | 37.85 | 36.15 | 완료 |
| E2 16×16 IPPO seed1 | 4,000,768 | 38.20 | 36.85 | 완료 |
| E3 20×22 PGCT seed1 | 2,252,800 | 27.25 | 25.95 | 진행 중; 평가는 2,201,600 step |
| E3 20×22 IPPO seed1 | — | — | — | 시작 전 |

Home ratio .5, 요청 4개, LR1e-4, entropy .02. Task 평가는 공통 seeds5,000,001–5,000,020의 deterministic masked policy, 20×500이다. 구체적인 결과·분모는 `EXPERIMENTS.md`를 확인한다.

## 최신 핵심 관측

1. E1 평가 delivery의 정규화 AUC: PGCT45.856, IPPO44.573(+2.88%). 마지막10회 평균46.170/44.515. 최종 snapshot은 IPPO가0.30 높다. 단일 training seed이며 독립 반복 재현은 미확인이다.
2. E2 정규화 AUC34.167/34.245(−0.23%). Same-team gate가 다시 생겼지만 성능 이득과 연결되지 않았다.
3. E1 실제 전이는 3–4만2,005 pair-updates, same-team0. E2 same870/cross2,360. Gate 활성량을 성공으로 대체하지 않는다.
4. 네 agent 모두 업데이트하고 작업을 수행한다. E1은3·4가 delivery의 약61%를 담당하지만 E2/E3는 더 균등하다. 공간 편중은 IPPO에서도 관측된다.
5. 완료된 네 모델의 추가 stochastic critic 평가(각10×500)에서 정확도 개선은 미확인이다. 초기200-step 유한 MC MSE: E1 PGCT1.725/IPPO1.103, E2 .286/.281. 방문 분포 차이·유한 horizon 편향이 남는다.
6. 기존 Stage04 공통 recurrent rollout 진단에서는3–4 policy JS .060, critic 예측 간 MSE .107로 가장 낮았다. 이는 예측의 일치이며 실제 return 정확도나 전이 효과와 다르다.
7. Probe 중복 민감성은 지속된다. 최신 E1 PGCT에서3–4 JS48 .0921→고유26 .1421, 1–4 .2114→.1232로 순위 역전. E2 bank의 고유 입력은25개다.

## 추가 검토: E2 연결 집단 — 2026-10-13

E2의 완료 로그 3,907 update에서 최대 연결 성분 크기 3이 661회(세 쌍 모두 연결244회), 크기4가18회(완전 연결0회)였다. 환경의 팀 배정은 여전히 1·3/2·4다. 큰 성분을 모든 쌍의 유사성으로 읽어서는 안 되지만, 팀이 섞인 3개 완전 연결도 있어 단순 연쇄만으로 설명할 수 없다.

공통 이동 probe의 비중이 원인이라는 가설은 아직 검증하지 않았다. 원래 팀 발견 목표와 전이 유익성 목표를 구분하고, 사후 목표 변경으로 기존 실패를 정당화하지 않는다. 근거: `output/learning_review_20261013/e2_components.json`, `DECISIONS.md` D12, `EXPERIMENTS.md` E09.

## 다음 단계와 미해결 질문

- 새 환경 요청 수행(2026-10-13): 원래 코드와 별도 환경ID/실행기로control·detour(기본)·bottleneck·dock4단계 장애물/배송 대기 환경을 추가했다. 관련32tests와8조건64-step CPU smoke를 완료했다. 추가4M 장기 학습은 시작하지 않았다. `examples/HARD_RWARE_EXPERIMENTS.md`, `EXPERIMENTS.md` E10, `output/hard_rware_validation_20261013/validation.json` 참고. 기존 E1/E2/E3의 정량 스냅샷과 혼합하지 않는다.
- 방향별 전이 유익성(2026-10-13 검토): 대칭 JS와 `C(receiver←donor)`를 구분한다. 현재 allocation도 수신자별 정규화로 비대칭일 수 있으나 방향별 유익성은 측정하지 않는다. 동일 receiver 조건에서 peer 유무를 비교하는 검증 surrogate가 후속 아이디어이며 아직 실행하지 않았다.
- 사용자 정정(2026-10-13): SMAC 도입을 요청한 것이 아니다. 같은 형태의 agent라도 역할 분담의 성격과 차이가 크게 달라지는데 행동 유사도 기반 전이가 이를 감당할 수 있는지가 질문의 핵심이다. 환경 추가 요청으로 해석하지 않는다.
- 기존 진행 중인 E3와 예정된 IPPO 결과를 보존한다. 이 노트는 중단·재시작 명령이 아니다.
- E1 seeds2·3의 동일 조건 반복이 우선 제안이다. 장기 학습 완료 결과는 아직 확인되지 않았다.
- 이후 random donor와 drop34로 JS donor 선택과3–4 연결의 기여를 검증한다. 구현·64-step 검증은 있지만 장기 결과는 없다.
- 다른 사전학습 seed의 Stage03에서도 재현되는가? 현재 하나의 사전학습 모델 조건부 비교다.
- 낮은 policy JS가 전이 전 critic compatibility나 실제 성능 기여를 예측하는가? 이전 전이로 critic이 비슷해진 역인과 가능성이 있다.
- Probe 가중치는 실제 방문 빈도 또는 중요한 value 상태의 비중을 반영하는가? 아직 정당화되지 않았다.
- 공간 확대 시 shelf 밀도·경로 길이·접촉 빈도도 바뀌므로 순수 맵 크기 효과는 분리되지 않았다.

## 근거와 사용 안내

- [최신 전체 분석](output/learning_review_20261013/REPORT.md), [수치 스냅샷](output/learning_review_20261013/analysis.json).
- [추가 critic 평가](output/learning_review_20261013/critic_summary.json), [최종 probe 응답](output/learning_review_20261013/probe_responses.json).
- [공통 rollout 진단](output/pgct_transfer_review/common_rollout_stage04_e1_u600/summary.json).
- [기존 공간·gate 진단](output/pgct_spatial_analysis/REPORT.md), [transfer 실행기 문서](examples/PGCT_TRANSFER_EXPERIMENTS.md).

현재 공용 기록은 `AGENTS.md`·`CLAUDE.md`·이 파일·`DECISIONS.md`·`EXPERIMENTS.md`·`CONVERSATION_LOG.md`다. 원본 대화 자동 수집이나 Hook/MCP 동기화는 구성하지 않았다.

2026-10-13 추가 사용자 지시: 이후 모든 대화를 원문으로 기록한다. `CONVERSATION_LOG.md`의 L01–L12는 과거 요약이며, T001부터 사용자 메시지·진행 안내·최종 답변 원문을 남긴다. AGENTS.md와 CLAUDE.md에 지속 기록 규칙을 반영했다.
