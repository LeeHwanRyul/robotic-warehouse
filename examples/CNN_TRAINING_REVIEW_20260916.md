> 후속 정정: 기준 PDF가 ex6에서 ex5로 변경되었습니다. 아래 ex6/FoV 관련 설명은 과거 검토 기록이며 현재 구현은 [EX5_PGCT.md](EX5_PGCT.md)를 따릅니다.

# CNN RWARE 학습 검토 및 수정 (2026-09-16)

후속 FoV/완전 독립 비교 구현 및 최신 실행법은 [FOV_COMMUNICATION.md](FOV_COMMUNICATION.md)를 참조한다. 기본 CNN 태스크 관측은 정사각형 SR5이고, 방향성 FoV는 통신 그래프에만 적용한다. 아래의 FoV/temporal 미구현 평가는 후속 수정 이전 상태다.

## 결론과 검증 범위

팀당 한 명만 일하는 현상을 단순히 회전 벌점 부족으로 판단하면 안 된다. 현재 정책은 에이전트마다 독립적인 CNN + GRU actor/critic이고, PGCT는 critic의 값만 전달한다. 동료가 배송을 배워도 다른 actor가 그 행동을 복사하는 구조가 아니다. 개인 보상으로 바꾸는 것만으로 모든 에이전트의 작업 학습을 보장하지도 않는다.

코드에서 확인한 관측 누락, 보상 오염, 행동 마스크 오류, 시간 제한 bootstrap 오류를 수정했다. 4/8/16명, PGCT 유무 각각의 회귀 테스트에서 모든 actor가 업데이트됨을 확인했다. 이것은 장시간 학습 수렴이나 전원 배송 성공의 증명은 아니다. 현재 실행 중인 학습 프로세스나 가중치는 변경하지 않았다. 수정 코드는 재시작한 프로세스에 적용된다.

작업 시작 전에 존재하던 환경·시각화·학습 스크립트 수정과 삭제된 그래프 이미지는 보존했다. 확인 가능한 runs에는 과거 단일 에이전트 run만 있었으며, 사용자가 설명한 현재 실패 run의 체크포인트를 재평가한 결과는 아니다.

## 확인한 결함과 변경

| 항목 | 기존 동작 및 영향 | 수정 |
|---|---|---|
| 반환 상태 | semantic 관측에 배송 여부와 선반의 반환 위치가 없어 동일한 위치·적재 상태에서 배송/반환 행동이 모호함. 64-step 학습 구간과 GRU에 긴 운송 기억을 전적으로 맡김 | 적재한 선반의 요청 여부, 반환 단계, home 유효 여부 및 정규화한 상대 home 좌표 추가 |
| 빈손 접근 보상 | 요청 목록에 동료가 운반 중인 선반도 포함. 정지·회전 중인 에이전트의 거리 보상이 동료 이동에 따라 변함 | 운반 중인 선반 제외. 한 transition의 목표 좌표를 고정해서 본인의 이동만 평가. 제자리에서는 접근 보상 0 |
| 행동 마스크 | 바로 앞에 적재한 동료가 있으면 FORWARD를 항상 금지. 환경은 동시 전진을 허용하므로 통로에서 합법적인 연속 이동이 막힘 | 고정 선반은 계속 차단하되 적재한 동료의 이동은 환경의 충돌 판정에 맡김 |
| 시간 제한 | max_steps를 진짜 terminal로 처리해서 마지막 관측의 후속 가치를 0으로 학습 | max_steps는 truncation. reset 전 관측과 GRU 상태로 critic bootstrap. GAE와 hidden state는 reset에서 끊음. inactivity 종료의 기존 의미는 유지 |
| 반환 프로브 | 반환 중 선반을 요청되지 않은 선반으로 구성했지만 실제 반환 환경은 완료될 때까지 요청을 유지 | 반환 프로브도 requested=True, has_delivered=True로 정합성 수정 |
| 학습 진단 | 전체 평균으로는 특정 에이전트만 보상을 못 받는 상황을 구분하기 어려움 | 에이전트별 actor update skip, 양의 보상 비율, advantage 표준편차 추가. 기존 에이전트별 이동·배송·반환 지표와 함께 사용 |

추가 home 관측은 **자신이 운반하는 선반의 반환 목적지를 알고 있다는 태스크 메타데이터 가정**이다. 타 에이전트의 팀 ID나 원격 요청 선반 위치는 추가하지 않았다. home이 센서 범위 밖이어도 이 메타데이터는 유지한다. 원래 위치를 전혀 알 수 없는 순수 센서 기반 문제를 원한다면, pickup 시 기억한 위치와 선반 식별 메모리를 별도로 정의해야 한다.

기존 semantic ego 15차원에서 20차원으로 변경되었다. SR5는 20 + 13 × 11 × 11 = **1593차원**이다. 기존 SR3/15차원 checkpoint를 동일 모델의 연속 학습으로 간주하지 말고 수정된 구조로 새로 시작한다. 범용 transfer 함수는 shape가 다른 tensor를 건너뛰므로 오래된 checkpoint를 넣으면 일부 가중치만 복사될 수 있다. 새 curriculum 안에서는 같은 구조의 새 checkpoint만 연결한다.

## 4/8/16명, SR5, 빨강/파랑 선반 혼합

`run_semantic_cnn_marl_pgct_from_scratch.ps1`의 기본 sensor range를 5로 변경하고 AgentCount=4/8/16을 지원한다. team count는 2, 기존 렌더링의 team 0 빨강/team 1 파랑을 유지한다. 요청 수는 전체 N개, 팀당 N/2개로 설정하고 좌표를 정규화한다. 기본 JSON도 사용자가 지목한 individual + zones 설정으로 연결했다.

새 `balanced_soft_zones` 모드는 두 공간 구역에서 같은 개수의 선반 소유권을 서로 교환한다. 기존 독립 확률 방식 `soft_zones`는 그대로 남겼다. 새 모드는 tiny 맵의 32개 선반을 언제나 16:16으로 유지한다.

| home 비율 | 왼쪽 구역 (빨강, 파랑) | 오른쪽 구역 (빨강, 파랑) |
|---|---|---|
| 1.0 | 16, 0 | 0, 16 |
| 0.875 | 14, 2 | 2, 14 |
| 0.75 | 12, 4 | 4, 12 |
| 0.5 | 8, 8 | 8, 8 |

혼합은 선반 위치 이동이 아니라 **공간에 배치된 선반의 팀 소유권 교환**이다. 각 episode reset 때 해당 비율로 다시 배정하며, stage가 진행될수록 혼합 비율이 커진다. 임의 비율은 선반 개수 단위로 반올림된다. 두 구역의 선반 수가 다른 맵에서는 정확한 50:50을 가장하지 않고 오류를 낸다.

기본 비교는 모든 N에서 tiny 맵을 유지한다. 따라서 16명은 4명보다 혼잡도가 크며 이는 N/A 증가 실험이다. 에이전트 수 효과와 밀도 효과를 분리하려면 별도 면적 sweep이 필요하다. 16명도 tiny에서 학습 가능한지에 대한 장시간 검증은 아직 없다.

```powershell
# 수정된 4명 SR5 학습: 먼저 통신 없는 기준선
.\examples\run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run none -AgentCount 4

# 같은 조건의 PGCT 비교
.\examples\run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run policy-complete -AgentCount 4

# N별로 독립 시작, 각 N 안에서 1 -> .875 -> .75 -> .5 순서로 가중치 전이
.\examples\run_semantic_cnn_mixing_curriculum.ps1 -Run none -AgentCounts 4,8,16

# 물리 거리 통신 비교 (아직 directional FoV가 아님)
.\examples\run_semantic_cnn_mixing_curriculum.ps1 -Run policy-physical -AgentCounts 4,8,16
```

curriculum은 각 stage의 actor/critic 가중치를 다음 stage에 넘기고 optimizer와 그래프 통계는 초기화한다. 고정 예산 기반 진행이며 성공률 자동 승급은 아니다. 학습이 실패한 stage도 예산이 끝나면 넘어가므로, 본 실험 전에는 4명 첫 stage의 전원 기여를 먼저 확인한다. `-NoTrack`으로 W&B를 끌 수 있고 `-Seed`로 반복 실험을 구분한다. 자동으로 수백만 step 학습을 시작하지는 않았다.

## 공통 프로브 검토

128개가 본질적으로 불가능한 크기는 아니지만, 기본 구성은 팀별 24개 항목을 여러 변형으로 반복한다. 항목 중 home-pair/goal-pair/neutral도 중복 가중되어 있다. 16명의 독립 critic에 매 PPO minibatch마다 PGCT loss를 계산하면 비용이 늘며, 숫자를 늘리는 것만으로 실제 rollout 분포를 잘 대표하지 않는다.

실행 기본 batch를 **48개**로 바꿨다. shared 모드에서 두 팀 × 24개 항목을 한 번씩 다룬다. 모든 항목이 서로 다른 48개 상황이라는 뜻은 아니다. 먼저 이 크기를 기준으로 하고, 성능 주장을 하려면 48/96/128의 학습 성과와 프로브 시간을 비교해야 한다. 이번 변경은 최적 프로브 개수를 입증한 것이 아니다.

더 중요한 문제는 기존 `agent-team` 모드가 `_agent_team_ids_from_env()`에서 **실제 team ID**를 읽고 서로 다른 팀 상황을 입력했다는 점이다. 정책 차이와 입력 차이가 함께 측정되므로 정답 없이 팀을 발견했다는 해석은 불가능하다. 기본을 **shared**로 바꿨고 agent-team은 명시적인 특권 정보 진단 옵션으로 남겼다. `-ProbeTeamConditioning agent-team`은 그 비교 목적에만 사용한다.

sequence length 1은 GRU의 hidden=0에서 정적인 반응만 비교한다. 이를 recurrent 행동 전체의 유사성으로 해석하면 안 된다. 현재 긴 probe sequence 구현은 독립 상태들을 reshape하므로 length만 늘린다고 실제 궤적이 되지 않는다. 이 때문에 기본 length=1은 유지했다. 실제 GRU 의존성 검증은 episode 경계와 burn-in을 보존한 공통 궤적 설계가 필요하다.

shared 모드로 바뀐 policy distance 분포에 기존 threshold=0.12가 최적인지도 아직 입증되지 않았다. 무작위 초기 정책은 모두 거의 균일해서 팀과 관계없이 유사하다. warmup=100은 초기 오염을 줄이는 장치일 뿐, 팀 발견 정확도 보장은 아니다.

## 신경망 전략 평가

2-layer CNN -> ego 결합 -> 독립 GRU actor/critic -> recurrent PPO는 현재 11×11 부분 관측 작업을 표현할 수 있는 구조다. 테스트에서 모든 agent가 optimizer update를 받는다. 한 명이 일하지 않는다는 관찰만으로 그 agent의 backward가 실행되지 않는다고 판단할 근거는 없다.

관측에 반환 단계가 없던 문제가 먼저 해결되어야 하며, CNN을 더 크게 만드는 것부터 시작할 이유는 없다. 개인 보상은 본인 기여를 학습시키지만 초기 성공 경험의 불균형은 남는다. PGCT critic 전달은 actor 행동 전수나 경험 공유가 아니다. 팀별 parameter sharing이나 중앙 critic을 조용히 추가하면 독립 분산 학습이라는 실험 조건이 바뀌므로 도입하지 않았다.

평가의 deterministic argmax는 거의 균일한 초기 정책에서도 한 회전 행동만 계속 선택할 수 있다. 학습 중 이동률·entropy·개인별 배송과 deterministic 영상의 회전을 구분해야 한다. 초기 128-step smoke에서도 학습 이동률은 agent마다 양수였지만 평가에서는 회전이 많았다. 이것은 장기 실패 원인을 해결했다는 증거도, 역전파가 안 된다는 증거도 아니다.

## ex6.pdf와 프로젝트의 정합성

첨부 PDF는 연구 설계 참고 자료로 읽었다. 문서 내부의 권장 실험 순서를 사용자의 추가 실행 지시로 취급하지 않았다.

| PDF의 요구/구분 | 현재 프로젝트 |
|---|---|
| 방향성 FoV, 거리 R와 각도 phi, receiver i가 sender j를 보는 j -> i | 관측은 축 정렬 정사각형 11×11. physical 통신은 Chebyshev 거리로 대칭. 방향성 각도 제한 없음 |
| 이동이 그래프를 생성 | physical 모드는 위치 의존적. 기본 policy-complete는 위치와 무관한 완전 통신 baseline |
| occupation C/rho와 entry N/lambda의 분리 | PGCT 유사도/군집 지표는 있지만 요구된 encounter 통계와 gap-tail 실험 없음 |
| union root와 시간순 temporal root 구분 | 현재 그래프 연결/군집만으로 time-respecting 정보 전파를 입증할 수 없음 |
| passive mobility를 먼저 검증하고 active mobility 분리 | 현재 PPO가 이동과 그래프를 함께 바꾸는 active setting |
| agreement와 모든 agent 정보 집계/학습 성과 구분 | critic 유사화와 팀 clustering은 학습 최적성/모든 agent 기여의 증명이 아님 |
| no comm / static / mobility-induced 비교 | none / policy-complete / policy-physical의 비교 틀은 있으나 PDF의 directed FoV 비교와는 다름 |

따라서 **프로젝트 전체가 PDF를 이미 구현했다고 결론낼 수 없다.** 이번 수정은 RWARE 학습 파이프라인 결함과 요청한 인원·범위·혼합 실험 구성을 다룬다. directional graph를 기존 대칭 PGCT에 억지로 넣거나 미구현 temporal 통계를 측정했다고 주장하지 않았다. 논문 수준 정합성을 완성하려면 방향 convention, 각도 센서, ordered-pair encounter 통계, 동시/시간순 propagation 검증과 passive baseline을 별도 실험으로 구현해야 한다.

## 검증 결과와 다음 장기 실험의 판정

- `python -m pytest tests -q --disable-warnings`: 118 passed (수정 후 전체 suite).
- PowerShell 두 실행 파일 구문 검사 통과.
- 실제 CLI로 SR5 semantic CNN + shared 48 probe + PGCT, 128 환경 step 학습, 최종 평가 및 checkpoint 저장까지 완료. task 성공률은 0이었으며, 이 실행은 연결성/수치 정상 동작 smoke이지 성능 실험이 아니다.
- 짧은 episode에서 실제 timeout bootstrap과 reset 경계 검증. 4/8/16명의 모든 CNN actor 가중치 변경을 PGCT 켬/끔 각각 확인.
- 고정 seed에서 4개 혼합 단계 × 3개 인원수의 팀·요청 수와 선반 비율 확인.

긴 run의 통과 기준은 팀 합계 배송량뿐 아니라 **모든 agent의 delivery/return 기여, 최저 개인 기여, task-only return, 이동률, 실패 전진, 반복 정체, 여러 seed의 편차**를 함께 보는 것이다. shaping return만 좋아지는 run은 성공으로 판단하지 않는다. 첫 단계가 실패하면 그 checkpoint로 혼합 난도를 높이지 않는다.

회전 현상 소멸과 학습 수렴은 아직 확인되지 않았다. 현재 제공할 수 있는 확실한 결과는 코드 결함 수정, 재현 가능한 회귀 검증, 실험 조건 정렬과 정합성 평가다.
