# PGCT 현재 연구 상태

## 최신 확인 — 2026-10-18 14:30 KST, Claude Code

- **새 세션 시작점**: `HANDOFF.md`(전면 갱신)를 먼저 읽는다.
- **현재 실행**: E1-F main 5개(`runs/e1f_20261018_124343_main_canonical` 4 mode, `..._main_v2` PGCT-v2)가 running이다. 각 약 0.12M step, job당 약 19 step/s이고 10M까지 약 6일(10월 24일 무렵) 예상이다(E26).
- **연구 방향**: PGCT는 원 기획(잠재 팀 발견 + 팀 내 critic 전이)이다(D41). E1은 팀 대칭 대조 조건, E1-F가 본 시험이다.
- **논문**: 방법 논문 초안 v0.2 `output/ijcai_method_paper_20261018/`(D42). E1-F와 다중 seed는 TBD다.
- **대기(사용자 승인 필요)**: E1 seed 2·3(10M), E1-F 팀 보상 pilot, 개입 실험, 비결정성 조사, baseline 3종.

## 최신 확인 — 2026-10-18 12:44 KST, Claude Code

- **E1 run 중지(사용자 지시)**: `scratch_20261015_093349_stage2`를 약 6.5M에서 중지했다. 마지막 checkpoint는 06250이다(E24 추가).
- **현재 실행**: E1-F main `runs/e1f_20261018_124343_main_canonical`(IPPO/PGCT/Oracle/All, canonical)과 `..._main_v2`(PGCT, v2). individual reward, seed 1, 10M, 5 프로세스, W&B. 초기 hash는 E1 seed 1과 동일하다(E26).
- **다음**: 2M 무렵부터 `e1f_team_divergence.py`로 팀 분화와 probe JS를 확인한다. E1 seed 2·3, 팀 보상 pilot은 미실행이다.

## 최신 확인 — 2026-10-18 12:23 KST, Claude Code

- **현재 실행**: `scratch_20261015_093349_stage2` 4개 running, 약 6.4–6.55M step. 15M까지 약 4일 남아 10월 22일 무렵 종료 예상이다.
- **중간 성능(seed 1, 평가 최근 5회 delivery)**: Oracle 32.3 > PGCT 27.9 > IPPO 24.3 > All 20.4.
  - All은 배송 시작이 3.99M으로 늦었지만, 4명 모두 배송하며 가장 가파르게 오른다.
  - IPPO/PGCT/Oracle은 A4 배송이 0이다.
- **PGCT 전이**: 2M 이후 같은 팀 전이가 거의 사라졌고, 다른 팀 1–2·3–4 연결만 남았다.
- **재현성**: 같은 seed의 E17과 비교하면 IPPO는 완전히 재현됐다. 전이 mode는 1.4–1.6M에서 갈라졌고, All 시작 시점이 2M 차이 난다. 다중 seed가 필요하다(E24).
- **대기**: 15M 완료 후 seed 2·3, E1-F IPPO 시험 등은 사용자 결정 대기다.

## 최신 확인 — 2026-10-15 13:17 KST, Codex

- **읽기 전용 점검:** HANDOFF와 D24–D30/E20–E22, 현재 manifest/metrics/status/초기 hash/오류 로그, E1-F/v2 smoke 산출물을 대조했다. 기존 E1/canonical, home .5, individual reward, training seed 1, from-scratch 15M 비교가 진행 중이다. IPPO 321,536 / PGCT 316,416 / Oracle 314,368 / All 318,464 env steps이며 로그가 증가한다. 속도는 23.49–24.04 step/s다.
- **최근 평가:** 공통 307,200 step, deterministic masked, reset seeds 5,000,001–5,000,020, 20×500에서 요청 pickup/delivery/return 모두 0이다. 초기 구간으로 성공·실패나 mode 우열을 판정하지 않는다. 네 run의 마지막 checkpoint는 00250(256,000 step)이다. 오류 로그는 Gymnasium 경고/W&B 안내이며 Traceback 등 치명 오류 문자열은 발견하지 못했다.
- **Claude 추가 작업 확인:** E1-F 목표 분리와 gate 48/transfer 64의 v2 bank 옵션, seed 1 각 64-step smoke 완료 및 실제 distill_probe_count 64를 확인했다. 전체 183 tests 통과는 Claude 기록이며 이번에 재실행하지 않았다. 현재 본 학습은 여전히 E1/canonical이다. E1-F/v2 본 학습·팀 판별력/공유 이득 검증은 미실행이다.
- **대기/한계:** 4–5M 읽기 전용 점검, 독립 seed 추가와 E1-F/v2 및 MAPPO/SePS/HetDPS 본 학습은 기존 대기 상태다. learned-team online 모드도 미구현이다. E21 정리로 일부 과거 중간 checkpoint/smoke 출력은 없고 주요 로그/final은 보존됐다는 기록을 인계받았다. 이번 점검에서 삭제하지 않았다.
- **근거:** `output/status_review_20261015_131716/snapshot.json`, HANDOFF 및 EXPERIMENTS E19 추가. 새 학습/평가/tests/학습 코드 변경 없이 상태·대화 기록을 갱신했다.

## 최신 확인 — 2026-10-15 12:49 KST, Claude Code

- **새 세션 시작점**: `HANDOFF.md`가 현재 상태·대기 항목·원칙을 요약한다. 모든 기록을 합친 사본은 `research_archive/RESEARCH_ARCHIVE.md`다(D30).
- **현재 실행**: `scratch_20261015_093349_stage2` 4개 run running. IPPO 281,600 / PGCT 277,504 / Oracle 275,456 / All 279,552 step, job당 약 24 step/s. 4–5M 읽기 전용 점검 예정(약 10월 17일).
- **이후 추가 구현(학습 미실행)**: E1-F 환경 변형과 probe bank v2 옵션(D29, E22). 본 학습은 사용자 승인 대기다.

## 최신 확인 — 2026-10-15 11:49 KST, Codex

- **현재 실행(로그 확인):** `runs/scratch_20261015_093349_stage2`의 IPPO/PGCT/Oracle/All, E1 11×10, home .5, individual reward, training seed1, 무작위 초기화, 각 15M 목표. 마지막 env steps는 각각 200,704 / 198,656 / 196,608 / 199,680이다. 상태 파일은 `running`이며 11:48–11:49 로그 갱신을 확인했다. 네 초기 actor+critic hash가 같다. 이번 Codex 작업이 시작한 학습이 아니다.
- **평가:** 네 mode 모두 최근 153,600 step의 deterministic masked 20×500 평가(reset seeds5,000,001–5,000,020) delivery0.0이다. 초기 구간이므로 성능 판정을 하지 않는다.
- **이전 실행과 구분:** E17은 약2.5M 중단 run이고 이번 run은 seed1의 처음부터 재실행이다. 정확한 resume이나 독립 seed 추가가 아니다. 아래 과거 항목의 ‘재실행 결정 대기’와 ‘실행 중 없음’은 최신 상태로 읽지 않는다.
- **논문 분석(제안, 사용자 결정 아님):** 원래 목표인 국소 행동/작업 증거→잠재 팀 추론→critic 공유를 유지한다. 현재 learned-team online 모드는 미구현이고 성능 개선도 미확정이다. 기존 결과는 진단 근거로 쓰며, from-scratch 반복·Oracle/All 비교·online 방법 검증 후 주장을 확정한다.
- **산출물:** `output/ijcai_review_20261015/REPORT.md`(MD 교차 분석, 주장/증거, IJCAI 구성, 영문 탐색적 초록, 추가 실험 제안), `live_run_snapshot.json`. E19·D23 참고. 새 학습/평가/tests, 알고리즘·환경 변경은 하지 않았다.

아래는 이전 시점의 연구 스냅샷과 판단을 보존한 기록이다.

기록 작성: 2026-10-13, Codex. 최신 정량 분석 스냅샷: **2026-10-13 14:37 KST**. 진행 중인 실험은 이후 달라질 수 있다.
갱신: 2026-10-13 저녁(정확한 시각 미기록), Claude Code — 실행 상태 재확인, 연구 주제 재정립, 실험 A 결과 추가.

## 2026-10-13 갱신 — 연구 주제 재정립과 실험 A (Claude Code)

- **실행 상태(실측)**: 현재 실행 중인 학습 없음. E3 PGCT는 18:21 KST Windows 재부팅(시스템 이벤트 로그상 정상 재부팅)으로 2,855,936 step에서 중단. 마지막 checkpoint 2,764,800 step(`checkpoint_02700.pt`), 마지막 평가 2,816,000 step delivery 28.6. 매니페스트에는 여전히 `running`, E3 IPPO는 `planned`. 기존 실행기는 이어 학습을 지원하지 않는다. 재개 여부는 사용자 결정 대기.
- **연구 주제**: 사용자 원래 목표 A(국소 행동으로 잠재 팀 추론 → 팀 내부 critic consensus)를 본 연구로 확정. 팀 무관 JS 기반 transfer(B)는 별도 가설. D17.
- **실험 A(고정 모델, 학습 없음)**: 국소 pickup·delivery 목격 증거는 6개 모델 모두 같은/다른 팀 AUROC 1.00, 1 episode(500 step) 내 팀원 식별. 현재 canonical JS는 AUROC .375–.50, 팀원 식별률 0–.25(우연 .33). 정책 이력 JS는 E1 계열 .27–.29, E2 .81–.85.
- **핵심 문제**: 같은 팀 critic이 더 호환된다는 전제가 이 환경에서 성립하지 않았다. E1 계열 blend gain AUROC .25–.33(같은 팀이 더 나쁨), E2는 모든 쌍의 이득이 0 근처. 관측이 자기 팀 기준이고 individual reward에서 팀원이 같은 요청을 두고 경쟁하기 때문이라는 해석은 가설이다. E11.
- **실험 B 실행기**: oracle/all/wrong 분기 구현·smoke 완료, 장기 학습 미실행. E12.
- **본 학습 진행 중(E17)**: 사용자가 2026-10-13 20:23:52에 `scratch_20261013_202352_stage2`(IPPO/PGCT/Oracle/All, 15M, seed1)를 시작했다. 약 7일 예상이다. 4–5M 점검은 무중단, 읽기 전용으로 한다.
- **2026-10-15 중단**: E17이 Windows Update 재부팅(01:01)으로 약 2.46–2.50M step에서 끊겼다. 재개 방식은 사용자 결정 대기다(처음부터 재시작 권장).
- **2.5M 중단 시점 분석(E18)**
  - 네 mode 모두 1.6–1.9M부터 학습이 시작됐다.
  - 2.4M에서 Oracle이 delivery 약 10으로 가장 앞섰지만, 그 성능은 Agent2 한 명에게서 나왔다(seed 1, 귀속 불가).
  - PGCT gate는 초기에 같은 팀과 다른 팀에 비슷하게 열렸다.
  - 다음 단계로 재실행 시 seed 2·3을 병행하고, agent별 onset을 관찰할 것을 권장한다.
- **핵심 비교 계획(D22, E16)**
  - IPPO/PGCT/Oracle/All from-scratch 15M, seed1, 병렬로 진행하고 4–5M에 무중단 점검한다.
  - GPU 실제 설정에서 4 mode 초기 파라미터 일치를 확인했다.
  - 정확한 resume은 불가능하다(트레이너에 재개 경로 없음).
  - 본 학습은 사용자 실행/승인 대기다.
  - 목적은 critic 공유 효과 검증이며 잠재 팀 발견 해결이 아니다. 팀 목표 대칭성을 해석에 반영한다.
- **W&B·비교군 추가(D21, E15)**: from-scratch 파이프라인에 W&B(Step=env steps)와 MAPPO/SePS/HetDPS mode를 추가했고 smoke까지 완료했다. 기본 예산은 Stage1 4M, Stage2 15M이다. 본 학습은 사용자 승인 대기다.
- **처음부터 학습으로 전환(D20, E14)**: 사용자는 커리큘럼 기반 기존 데이터를 신뢰하기 어렵다고 판단했다. IPPO/PGCT/oracle/all/wrong 무작위 초기화 실행기를 구현하고 smoke까지 완료했다. 권장 첫 실행은 IPPO+oracle 2M pilot이며, 사용자가 직접 실행한다. Stage03 기반 oracle(D18)은 후순위다.
- **외부 검토 반영(D18)**: 국소 증거는 관측자 자신의 관측 채널과 100% 일치했다(E13, 2,146건). 상대 팀 ID는 미사용이고, 이웃 식별 가정이 남는다. 짧은 matched-prefix oracle 실행을 지원한다. 권장 다음 실행은 E1 oracle 1,024,000 step(약 7–8시간, 사용자 승인 대기)이다. team reward는 공통 사전학습부터 재정렬이 필요하고, 관측이 팀 기준인 한 팀별 critic 함수가 갈라지지 않을 수 있다(가설).

## 한눈에 보는 현재 판단 (14:37 스냅샷 기준, Codex)

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
| E3 20×22 PGCT seed1 | 2,252,800 | 27.25 | 25.95 | 14:37 기준 진행 중. **18:21 재부팅으로 2,855,936 step에서 중단**(최종 평가 2,816,000 step 28.6) |
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

- (2026-10-13 Claude Code) 사용자 결정 대기: ① E3 재개 여부(권장: 재개하지 않음), ② 실험 B를 현재 환경에서 확인용으로 실행할지(oracle+all, E1 seed1, 약 60시간), ③ 팀 소속이 value를 바꾸는 조건(예: 기존 옵션 `team_reward_mode="team"`)을 먼저 정할지. 아래 기존 항목 중 JS gate·맵 확장·seed 반복은 방향 B 검증이므로 A보다 후순위다.

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
