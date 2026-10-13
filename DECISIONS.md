# PGCT 질문·결론·설계 판단

2026-10-13 Codex가 현재 대화와 저장된 근거로 최초 정리했다. 과거 날짜가 없는 항목은 대화 순서만 보존한다. 사용자가 붙여넣은 외부 답변은 검토 자료이며, 아래의 제안은 자동 실행 허가가 아니다.

## D01. 초록색 연결선 소멸은 학습 실패인가? (과거 대화, 날짜 미상)

- 질문: 학습 후반에 same-team gating이 사라진 이유가 분업에 따른 행동분포 차이인가?
- 관측: 기존 stage03–04에서 same-team 승인0, cross-team 일부 승인. 동일 canonical 입력에 대한 policy response가 분화했다.
- 판단: 선 소멸만으로 실패를 판단하지 않는다. Zero-hidden canonical 응답의 차이는 실제 작업 역할 분담과 동일하지 않다.
- 수정 이력: 초기의 “분업 때문에 gate가 닫혔다”는 설명은 가설로 낮췄다. Occupancy는 공간 활동 차이를 지지하지만 역할·원인까지 확정하지 않는다.
- 근거: `output/gating_diagnosis/summary.json`, `output/pgct_spatial_analysis/REPORT.md`.

## D02. PGCT가 팀을 찾아야 하는가, 호환되는 donor를 찾아야 하는가?

- 두 목표를 구분한다: (A) 잠재 팀 발견과 팀 내부 consensus, (B) 팀 소속과 무관한 선택적 critic transfer.
- 현재 연결은 팀 라벨보다 actor 응답 유사성을 반영한다. A를 주장하려면 same/cross 판별 실패를 설명해야 한다.
- B로 확장하려면 실제 전이의 학습 이득과 JS donor 선택의 유용성이 필요하다. 연구 목표 확정은 보류했다.
- 특히 individual reward에서 비슷한 행동이 비슷한 미래 reward/value를 보장하지 않는다.

## D03. PGCT-off 코드를 새로 추가해야 하는가? / 해당 run은 IPPO인가?

- 기존 `run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run none` 경로가 있다.
- `ex5_semantic_cnn_none_from_scratch_4ag_sr5_square_home1.00_seed1_pretrain_off_9700_continue`는 graph none, communication false, peer coefficient0, consensus0의 IPPO continuation이다.
- 한 agent가 먼저 성공하는 현상과 agent별 optimizer 업데이트 순서는 다르다. 이번 E1/E2 로그에서 개별 actor update skip은 모두0이다.
- 기존 home1 사전학습과 Stage03→home.5 비교는 조건이 다르므로 공정한 on/off 대조군으로 섞지 않는다.

## D04. W&B 영상 저장 오류와 절전 가설

- 관측: eval 영상1024000에서 긴 상대 목적지 경로의 `FileNotFoundError`, Windows의 파일 이동 실패 후 copy fallback 실패가 반복됐다.
- 진단: 긴 W&B media 경로가 유력한 원인이다. Traceback만으로 자동 절전이 원인이라고 확정하지 않는다. 실제 실패 지점은920000이 아니라 영상 이름의1,024,000 step이었다.
- 관측: `subst R:`로 우회한 뒤 `os.path.relpath`에서 R:/C: mount 불일치 `ValueError`가 발생했다. 이 두 오류는 구분한다.
- 대응 방향: 짧은 출력 폴더·run 이름, 필요시 영상 저장 비활성화, W&B Git 탐색 비활성화 설정을 사용한다. 원래 긴 경로 설정으로 단순 재실행하면 재발할 가능성이 있다.
- 한계: 모든 환경에서 문제가 완전히 해결됐다고 보장하지 않는다. 기존 checkpoint continuation은 counters/optimizer 복원 정책을 별도 확인한다.

## D05. 코드 수정·정리 요청의 범위

- 초기 사용자는 “코드 수정은 하지마”라고 요청했다. 당시 진단은 알고리즘을 변경하지 않는 범위였다.
- 이후 사용자는 IPPO/PGCT와 무관한 구버전 코드 정리, 실제 실험 코드 준비를 별도로 요청했다. 그 요청 범위에서 오래된 파일 제거와 별도 실행기·진단 코드 추가가 이뤄졌다.
- 이후 분석에서 원래 trainer·환경·실제 학습 gate/probe/threshold는 유지했다. 과거 정리 허가는 미래의 포괄적 삭제 허가가 아니다.
- 현재 요청은 공용 연구 기록 생성이다. 학습 실행/중단/알고리즘 변경은 포함하지 않는다.

## D06. 맵 확대를 gate 문제의 해결책으로 볼 것인가?

- 제안: E1 11×10, E2 16×16, E3 20×22, 4 agents/range5 유지.
- 판단: 공간 확대는 진단용 후속 실험이다. 접촉 기회 감소와 shelf 밀도 변화가 함께 있어 순수한 공간 크기 효과가 아니다.
- 우선순위: E1 on/off를 먼저 해석하고, 이미 실행 중인 공간 실험은 보존한다.
- 2026-10-13 갱신: E2 same-team gate가 다시 나타났지만 성능은 IPPO와 거의 같았다. 연결 회복 자체를 성공으로 볼 수 없다.

## D07. JS 계산과 probe 분포

- 구현 확인: natural-log JS divergence 평균이며 sqrt Jensen–Shannon distance가 아니다. 같은 공통 입력에서 각 actor의 확률을 비교한다.
- 기존48개 probe는 고유26개 입력이다. 반복된 입력의 횟수는 해당 상태의 가중치로 작동한다.
- 고유 입력 균등 평균에서 donor 순위가 바뀌었다. 중복이 자동으로 잘못된 것은 아니지만 빈도에 대한 연구적 정당화는 미확인이다.
- 결정: 현재 학습 bank와 threshold는 유지한다. Dedup은 진단이며 기존 .12를 적용해 “gate 개선”이라고 주장하지 않는다.
- 후속 관측: 최신 E1에서도 순위 민감성 지속; E2 고유 입력은25개다. 모든 bank가26개라고 일반화하지 않는다.

## D08. 공정한 추가 전이 실험

- 동일 Stage03 weights, 동일 환경·예산·PPO 조건·평가 seed로 PGCT-on/IPPO-off 분기.
- 여러 training seed는 해당 사전학습 checkpoint에 조건부인 반복이다. 사전학습 seed 다양성은 별도 문제다.
- Random donor는 현재 물리 이웃으로 제한하고 receiver별 전이 일정·allocation mass를 맞추되 불가능한 부족량을 기록한다. 동일 횟수·weight가 동일 peer loss/gradient를 뜻하지 않는다.
- Drop34는3↔4만 제거하고 나머지 weight를 재정규화하지 않는다. Drop34_refill은 보충하는 별도 질문이다.
- 제안 우선순위: on/off 반복 → random/drop34. 구현과 smoke 검증을 실제 장기 학습으로 표현하지 않는다.

## D09. Critic 진단의 의미

- 공통 이력의 `E[(V_i-V_j)^2]`는 예측 일치다. 실제 reward return에 대한 MC MSE는 예측 정확도다.
- 같은 이력을 각 모델이 자기 recurrent network로 처리해 hidden state를 형성한다. 서로 다른 네트워크 사이에 hidden vector를 그대로 복사하지 않는다.
- Reference rollout 이력은 다른 actor/model에 off-policy일 수 있다.
- 유한 horizon MC zero tail에는 continuing-value 편향이 있다. 자연 종료와 truncation, bootstrap 정책을 명시한다.
- 2026-10-13 갱신: E1 최종 critic에서 PGCT 정확도 개선을 확인하지 못했다. 이는 과거3–4 예측 간 일치와 모순이 아니다. 과거 전이가 예측 일치를 만든 역인과 가능성도 있다.

## D10. 2026-10-13 결과로 주장 가능한 범위

- 가능: E1 seed1의 정규화 평가 AUC +2.88%, E2 −0.23%, E1 최종 score는 IPPO가0.30 높음.
- 아직 불가: 다수 training seed의 유의한 개선, 최종 성능 우위, critic 정확도·안정성 개선,3–4 연결 자체의 인과적 유익성.
- E1을 “초기에만 전이하고 후반에는 불필요”로 해석하지 않는다. 실제3–4 전이는 후반에도 지속됐다.
- E3의 학습 향상은 대조군 전에는 PGCT 효과로 귀속하지 않는다.

## D11. 2026-10-13 공용 기록 구성

- 사용자 요청: “지금까지 있었던 대화 내용들 1번처럼 로그로 남겨줘”.
- 수행: 루트에 AGENTS/CLAUDE 공통 진입점, 현재 상태, 결정, 실험, 대화 요약을 생성했다.
- 범위: 제공된 대화와 로컬 근거로 구성한 연구 인수인계 기록이다. 모든 원본 발화·별도 Claude 대화를 완전 복원한 transcript가 아니다.
- Hook·Memory MCP·자동 대화 수집은 설치하지 않았다. 이후 각 도구가 작업 종료 시 관련 Markdown을 갱신하는 규칙을 추가했다.

## D12. E2의 3~4개 연결 집단과 probe 신뢰성 — 2026-10-13 Codex

- 사용자 질문: 큰 연결 집단이 생겼다면 공통 이동 probe가 팀 구분 probe보다 많고, 현재 PGCT를 좋은 알고리즘으로 볼 수 없는 것 아닌가? 첨부된 외부 답변의 타당성을 검토했다.
- 실제 추가 확인: 완료된 E2 PGCT의 3,907 update에서 전이 가중치의 양방향 support로 연결 성분을 계산했다. 최대 성분 크기 3은 661회(완전 연결 244회, 불완전 연결 417회), 크기 4는 18회(모두 불완전 연결)다. 환경의 실제 팀 배정은 변하지 않았다.
- 판단: 큰 연결 성분을 모든 쌍의 유사성으로 읽으면 안 된다. 그러나 세 쌍 모두 열린 3개 집단도 있어 연쇄 연결만으로 혼합 현상을 설명할 수 없다.
- 미확정: 이 현상이 이동 probe의 개수/가중치가 크기 때문에 생겼다는 인과 관계는 아직 분해하지 않았다. 실제 정책 수렴, probe 표현력, zero hidden, 평균 집계, EMA 이력 등의 가능성을 구분한다.
- 연구 주장: 원래 목표가 같은 팀 발견이라면 현재 혼합 연결은 그 목표에 대한 반례다. 사후에 이름만 행동 호환성으로 바꾸어 정당화하지 않는다. 목표를 변경한다면 명시하고 전이 유익성을 별도로 검증한다.
- 현재 평가: 검증 중인 후보 알고리즘이며, 일반적인 donor 선택의 신뢰성·성능 우위는 입증되지 않았다. E2 on/off 성능이 거의 같다고 전체 알고리즘의 무효나 해로움까지 확정하지 않는다.
- 후속 제안만 기록: 실제 입력 기준 navigation/task 그룹과 objective 조건 민감도 진단, random donor 및 반복 seed 비교. 이번 요청에서 학습·gate·probe 변경이나 새 장기 실험은 수행하지 않았다.
- 근거: `output/learning_review_20261013/e2_components.json`, 기존 E2 결과, 사용자 첨부 `0adf2737-c22e-4047-9552-5f91073abb82/붙여넣은 텍스트.txt`.

## D13. 이후 모든 대화 원문 기록 — 2026-10-13 Codex

- 사용자 지시: “앞으로도 대화한 내역들은 전부 로그로 남겨줘 알겠지?”
- 변경: 기존의 의미 있는 대화만 요약하는 규칙을 넘어, 이후 모든 사용자 메시지와 사용자에게 보인 진행 안내·최종 답변을 원문으로 기록한다. 짧은 확인이나 반복 대화도 생략하지 않는다.
- 저장: `CONVERSATION_LOG.md`의 T001부터 역할·순서·날짜·작성 도구로 구분한다. 과거 L01–L12 요약은 그대로 보존하고 소급 원문 복원이라고 주장하지 않는다.
- AGENTS.md와 CLAUDE.md에도 반영했다. 별도 Hook·MCP 자동 수집을 설치한 것은 아니다.

## D14. 역할 분담 차이의 크기가 질문의 핵심 — 2026-10-13

- 사용자 정정: SMAC를 사용하겠다는 뜻이 아니다. 같은 형태의 MARL agent라도 분업의 성격과 차이가 크게 달라질 수 있는데, 현재 정책 유사도 기준이 이를 다룰 수 있느냐는 질문이다.
- 이후 해석: SMAC 예시를 환경 도입·설치·벤치마크 추가 요청으로 취급하지 않는다. 담당 구역/경로 수준의 차이와 기능적 역할 차이를 구분해 논의한다.
- 판단: 역할에 따른 정당한 정책 차이를 전이 부적합으로 읽는 문제는 probe 수를 늘리는 것과 별개다. 실제 분업 차이가 크다고 canonical JS가 반드시 증가하는 것은 아니므로 입력·이력·정책 표현과 구분한다.
- 미해결: 역할이 다른 agent 사이에서 공유 가능한 지식과 개인별 목표에 종속된 value를 어떻게 구분할 것인가? 전체 critic 전이가 유익하다는 결론은 별도 검증이 필요하다.
- 코드·probe 변경 및 실험 실행은 하지 않았다.

## D15. 대칭 정책 거리와 방향별 전이 유익성 — 2026-10-13 Codex

- 사용자 제공 검토: 동형 agent의 역할 분화에서 행동 차이와 목표 차이를 구분하고, 대칭 JS와 비대칭 critic transfer 유익성을 분리하자는 연구 제안.
- 동의 범위: 역할 차이를 행동/목표 두 축으로 구분하고 방향별 유익성을 검증하는 문제 정의는 타당하다. 자동 probe와 compatibility gate는 아직 검증되지 않은 제안이다.
- 코드 확인: 현재도 수신자×donor allocation을 수신자별로 정규화한다. JS가 대칭이어도 전달 가중치는 비대칭일 수 있다. 행렬의 방향성 또는 비대칭 전달량 자체가 새로운 유익성 판단을 뜻하지 않는다.
- 필요한 검증: 동일 receiver 모델·optimizer 상태·경험에서 peer 없는 update와 특정 donor를 추가한 update를 비교하고, 별도 receiver 검증 경험에서 오차 차이를 측정하는 surrogate를 고려할 수 있다. 이것도 장기 return 개선을 보장하지 않는다.
- 보완: 같은 목적이어도 역할·이력·정책이 달라 value가 다를 수 있고, 다른 역할이어도 일부 지식은 공유 가능하다. JS hard cutoff로 후보를 제외하는 가정 역시 검증 대상이다.
- 범위: 의견 검토와 기록만 수행했다. 기존 학습·probe·gate 변경, 새로운 실험 실행, 원래 팀 발견 목표의 확정적 변경은 하지 않았다.

## D16. 기존 코드와 분리된 난이도 환경 — 2026-10-13

- 사용자 요청: on/off 차이가 작은 이유가 환경이 쉬워서인지 질문하고, 기존 코드에 간섭하지 않는 장애물·제약 환경을 만들어 달라고 요청했다. 이는 새 환경·실행기 구현 허가이며 기존 알고리즘 변경이나 진행 중 학습 중단 요청이 아니다.
- 판단: 난이도 부족은 가설이다. 작은 on/off 차이는 전이 효과가 작거나 조건부 효과가 없는 경우에도 생기므로 쉬운 환경이라고 확정하지 않는다.
- 구현: 새 `rware/constrained_warehouse.py`, 전용 Python/PowerShell 실행기, 문서·테스트를 추가했다. E2와 같은16×16/108 shelves/4 agents/보상을 유지하는 control, 벽2개의 detour(기본), 벽14개와 통로2곳의 bottleneck, 병목+배송 dock8-step cooldown의4 profiles다.
- 격리: 기존 환경 등록·trainer·wrapper·probe·renderer·실행기 파일10개의 SHA256을 보존했다. 새 프로세스/새 환경ID에만 factory·mask·probe 인자 호환 어댑터를 임시 적용하고 종료 시 복원한다. 실제 canonical bank는 기존 E2와 동일하다. 출력은새 runs/hard_*이며 덮어쓰기를 거부한다.
- 검증: 관련32 tests,4 profiles×PGCT/IPPO 각64-step 학습·평가·저장8조건 완료. Control 모델의128 tensor가 기존 E2 smoke와 bitwise 일치했다. 모든 선반 적재 경로와 실제pickup→delivery→return을 검사했다.
- 난이도 보정: 평균 적재 경로는13.370→detour14.444(+8.0%), 병목17.074(+27.7%)칸. 기존 E2 PGCT final의5×500 고정 평가 delivery는control37.8/detour5.4/bottleneck2.2/dock2.2다. 기존 정책의 초기 일반화 실패이며 재학습 후 난이도나 PGCT 성능 이득의 증거는 아니다.
- 실제 수행 범위: CPU smoke와 frozen 평가만 실행했다. 새로운4M 장기 학습은 시작하지 않았으며 기존 학습을 중단하지 않았다.
- 근거: `examples/HARD_RWARE_EXPERIMENTS.md`, `runs/hard_smoke_20261013_final/experiment.json`, `output/hard_rware_validation_20261013/validation.json`, `frozen_difficulty_pilot_v2.json`.

## D17. 연구 주제를 원래 목표 A로 재정립하고 먼저 검증한다 — 2026-10-13 Claude Code

- 사용자 질문: (1) 현재 진행 중인 PGCT를 계속 돌리는 것이 맞는가? (2) 사용자가 원한 것 — 행동 유사도로 팀을 찾고 팀끼리 critic consensus — 과 assistant가 원한 것 — 다른 팀이라도 행동이 비슷하면 critic transfer — 중 무엇이 맞는가? GPT 답변(A 복귀, 실험 A·B 분리 검증)을 붙여넣었다. 지시: "현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서 GPT의 대답처럼 먼저 확인". 붙여넣은 답변은 참고 자료로 취급했다.
- 판단: 연구 주제는 A다. B는 cross-team gate 결과를 해석하는 과정에서 생긴 이탈이며 별도 가설로만 둔다(D02·D12와 일치).
- 실행 상태(실측): 실행 중인 학습이 없다. E3 PGCT는 18:21 재부팅으로 2,855,936 step에서 중단됐다. GPT의 "E3 마무리" 제안과 달리 재개하지 않을 것을 권장한다. 근거: 기존 실행기는 이어 학습을 지원하지 않고, E3는 방향 B의 JS gate 실험이며, 실험 A에서 그 신호가 팀을 구분하지 못했다. 최종 결정은 사용자에게 남겼다.
- 코드 확인: 관측의 `requested_shelf`, `relevant_goal`, `self_carrying_requested_shelf`는 관측자 자신의 팀 기준이다. E1 목표 칸은 (4,10)/(5,10), E2는 (7,15)/(8,15)로 인접한다. home .5에서는 선반 소유가 섞이고 보상은 individual이다. 따라서 공통 입력 JS는 구조적으로 팀을 거의 구분하지 못한다는 가설을 세웠다.
- 실험 A 결과(E11): 국소 pickup·delivery 증거는 팀을 완벽히 구분했다. canonical JS는 우연 수준 이하였다. 같은 팀 critic이 더 호환된다는 전제는 E1 계열에서 반대 방향(같은 팀이 덜 호환)이었고, E2에서는 차이가 없었다.
- 수정된 판단: "행동으로 팀을 찾는다"는 가능하다. 다만 신호는 응답 유사성이 아니라 "누구의 요청·목표를 수행하는가"라는 결과 수준 증거여야 한다. 현재 환경에서는 팀을 정확히 찾아도 critic consensus 이점의 근거가 약하다. 팀 소속이 value를 실제로 바꾸는 조건(팀 보상 공유 등)이 필요할 수 있다. 이는 제안이며 환경·보상을 변경하지 않았다.
- 수행 범위: 새 `latent_team/` 폴더와 테스트를 추가했다. 기존 trainer·환경·실행기·probe·gate는 변경하지 않았다. 학습 중단·재시작이나 장기 학습은 하지 않았다. 실험 B 장기 실행은 사용자 승인 대기.

## D18. 외부 검토(GPT) 반영: 소규모 oracle 우선, team reward는 재정렬 후 — 2026-10-13 Claude Code

- 사용자 제공: 실험 A 결과에 대한 GPT 검토를 별도 지시문 없이 붙여넣었다. 요지는 다음과 같다. E3 재개 안 함, 60시간 B 보류, 기존 환경에서 소규모 oracle/IPPO 비교, team reward의 학습 목표 변화 분석 후 공통 사전학습부터 재정렬, 국소 증거의 팀 ID 간접 사용 여부와 blend gain 정의 확인. "같은 팀"의 정의(공통 목표 팀 vs 협력적 목표 팀)도 제기했다. 참고 자료로 취급했고 학습은 시작하지 않았다.
- 동의:
  - 국소 증거로 팀을 구분한 것은 "정보가 존재한다"는 확인일 뿐 잠재 팀 추론 알고리즘의 성과가 아니다.
  - 정적 blend gain만으로 학습 중 consensus의 효과를 판정할 수 없다.
  - team reward는 Stage03에서 바로 이어가지 않는다.
  - 출발점은 공통 목표 팀(같은 팀 보상)으로 둔다.
- 확인 결과(E13): 국소 증거 판정 2,146건이 관측자 자신의 관측 채널과 100% 일치했다. 상대 팀 ID는 쓰지 않는다. 다만 관측의 agent는 익명이므로 이웃 식별 가정이 남는다.
- 추가 판단(가설): 관측이 자기 팀 기준이고 두 팀 과제가 대칭이면, team reward를 써도 같은 입력에서 두 팀 critic 함수는 비슷할 수 있다. 같은 팀 consensus가 다른 팀보다 원리적으로 유리하려면 절대 기준 관측(팀 색)이나 비대칭 과제가 필요할 수 있다. 현재 env에 그런 관측 옵션은 없다.
- 준비: 학습률 schedule이 없음을 확인했다. 이에 따라 실험 B를 짧은 예산으로 실행하면 기존 run과 matched prefix로 비교하도록 보완했다(1,024,000 step oracle 약 7–8시간). **실행은 사용자 승인 대기.**

## D19. 미사용 파일 정리 — 2026-10-13 Claude Code

- 사용자 요청: "examples 폴더라든가 … 기존에 사용하고 안쓴 쓸모없는 파일들이 많은데 정리좀 해줘". 참조 검색 후 세 묶음을 제시했고, 사용자가 ①임시·캐시, ②대체된 문서, ③끝난 과거 실험 도구를 모두 선택했다(archive 이동은 선택하지 않음).
- 삭제(git 추적 파일은 이력에 남음):
  - ① `.codex-video-frames/`(34), `tmp_video_analysis/`(3), `tmp/fov_on_video_frame.png`, `tmp/.cache/`, `examples/generated_configs/`, `__pycache__`, 빈 `.agents/`
  - ② `examples/FOV_COMMUNICATION.md`, `examples/CNN_TRAINING_REVIEW_20260916.md`
  - ③ `examples/eval_checkpoint_generalization.py`와 `tests/test_generalization_graph.py`, `run_pgct_09700_generalization.ps1`, `run_pgct_09700_map_variants.ps1`, `PGCT_09700_GENERALIZATION.md`, `visualize_graph_connectivity.py`, `create_probe_ppt_images.py`, `run_semantic_cnn_mixing_curriculum.ps1`, `Success_checkpoint/checkpoint_Fixed_1.pt`
- 유지:
  - 현재 실험·테스트·노트가 참조하는 파일 전부
  - `tmp/pdfs`(ex4/ex5 원문 추출, 선택지에 없었음)
  - `runs/`·`output/`의 모든 과거 결과
  - `.pytest-tmp`·`.pytest_cache`(권한 거부로 삭제 불가)
- 수정: `examples/README.md` 목록·정리 범위, `examples/EX5_PGCT.md`의 삭제된 실행기 명령을 안내문으로 교체했다. 전체 pytest 178 passed(삭제 전 대비 generalization 테스트 3개 제외). 커밋은 하지 않았다.
- 범위: 이번 삭제 허가는 위 목록에 한정한다. 이후의 포괄적 삭제 허가로 해석하지 않는다.

## D20. 커리큘럼 없이 처음부터 학습하는 비교로 전환 — 2026-10-13 Claude Code

- 사용자 판단: 기존 실험은 커리큘럼으로 초기 학습량이 너무 많아 데이터를 믿기 어렵다. IPPO, PGCT, 기타 MARL을 처음부터 학습시켜 데이터를 얻어야 한다. 각각 커리큘럼 없이 학습하는 코드를 구현하고 실행 코드를 알려 달라. 함께 붙여넣은 GPT 답변(초기 학습 문제와 팀 구조 문제의 분리, 무작위 초기화 pilot 우선, AUC·도달 step·seed 분산, 사전학습 비용 포함)은 참고 자료다.
- 판단: 기존 Stage03 분기 결과(E1/E2, 실험 B 계획)는 "충분히 학습한 뒤 추가하는 공유"의 조건부 효과다. 연구 질문인 학습 과정의 효율과 다르다는 데 동의한다. Stage03 기반 1M oracle 실험(D18)의 우선순위를 낮춘다.
- 구현: `latent_team/train_from_scratch.py`, `run_from_scratch.ps1`. mode는 ippo/pgct/oracle/all/wrong이다. 같은 seed의 모든 mode가 같은 무작위 초기 가중치와 같은 probe bank를 쓰며, donor 집합만 다르다. 학습률·엔트로피는 이전 성공한 from-scratch run 설정(2e-4/.05)을 쓰고, 기본 예산은 10M이다.
- "기타 MARL"은 현재 트레이너가 지원하는 critic 공유 변형(oracle/all/wrong)으로 구현했다. MAPPO(중앙 critic)나 parameter sharing 같은 표준 baseline은 트레이너에 없어 구현하지 않았다(추가 여부는 사용자 결정).
- 주의(가설): 현재 환경은 팀 과제가 대칭이고 관측이 팀 기준이다. 처음부터 학습해도 oracle이 all보다 유리하다는 보장은 없다. 학습 시점의 문제와 팀 구조의 문제는 별개다.
- 실행: smoke만 실행했다. 장기 학습은 시작하지 않았다.

## D21. W&B 관리, 학습 구간 재설정, MAPPO/SePS/HetDPS 비교군 — 2026-10-13 Claude Code

- 사용자 요청:
  - W&B 기반 관리(기존 로깅 재사용, 알고리즘별 run, Step=env steps, -Detach 확인)
  - 학습 구간 재검토(기억: pickup 2–4M, 완수 약 9M; 15–20M 필요성)
  - SePS·HetDPS·MAPPO 추가(핵심 구조 유지, 차이·비용 기록, MAPPO는 추가 정보 비교군)
  - 본 학습은 승인 없이 시작하지 않음
  - 구현 순서는 MAPPO → SePS → HetDPS
- 판단·근거(학습 구간)
  - 로컬 W&B 기록(이전 from-scratch PGCT, home 1.0, complete graph): pickup 약 1.5M, delivery 1.7M, eval 20 이상 2.3M, 40 이상 3.3M, 6–9M에 56–60.
  - 사용자의 기억과 다르며, 현재 home .5 조건의 기록은 없다.
  - 2M에서 실패를 판단하지 않는다.
  - 기본값을 Stage1 4M pilot, Stage2 15M으로 바꿨다(20M은 seed 반복 비용을 고려해 보류, 옵션으로 가능).
  - Stage1은 초기화가 아니라 같은 mode의 앞 구간이므로 `-SkipStage1`을 제공한다.
- 구현 판단: baseline의 학습기는 공통 recurrent PPO로 통일하고 각 알고리즘의 고유 구조를 구현했다.
  - MAPPO: 중앙 critic·ValueNorm·Huber
  - SePS: VAE·KMeans·선택적 공유
  - HetDPS: BiHierarchicalVAE·W2·AP·동적 분할/병합
  - SePS의 원 학습기 A2C, HetDPS의 MLP/MAPSNet, 병렬 env 수는 차이로 기록했다.
  - scikit-learn/scipy가 환경에 없어 패키지를 설치하지 않고 numpy로 재구현했다.
- 범위: 기존 IPPO/PGCT/oracle/all 코드와 trainer는 변경하지 않았다. smoke와 비용 micro-benchmark만 실행했고 본 학습은 시작하지 않았다. 상세는 `latent_team/BASELINES.md`, E15.

## D22. 핵심 비교를 IPPO/PGCT/Oracle/All 4개로 한정, resume 불가 시 무중단 운영 — 2026-10-13 Claude Code

- **사용자 결정**
  - 7개 동시 본 학습은 하지 않는다. IPPO·PGCT·Oracle·All-peer from-scratch 비교부터 한다.
  - 15M을 기본으로 하되 4–5M에 학습 가능성과 추세를 점검한다. 2M 성능으로 실패를 판단하지 않는다.
  - MAPPO·SePS·HetDPS 구현은 보존하고, 핵심 비교 이후에 학습한다.
- **실험 목적(사용자 강조)**: 무작위 초기화에서 critic 공유가 학습 효율을 개선하는지, 특히 정확한 팀 정보를 쓰는 Oracle이 IPPO·All-peer보다 유리한지 검증한다.
  - 이 실험은 **critic 공유 효과의 검증이지 잠재 팀 발견 문제의 해결이 아니다.**
  - 결과 해석에서는 현재 환경의 팀 목표 대칭성(팀 기준 관측, 인접 목표, individual reward)을 고려한다.
- **resume 검증 결과: 정확한 재개는 불가능하다.**
  - checkpoint에는 agents, optimizers, graph(EMA 등 통계), iteration/env_steps, config가 저장된다.
  - 그러나 트레이너에 재개 경로가 없다. `init_checkpoint`는 network 가중치만 복사하고 optimizer와 graph 통계는 새로 시작한다(`transfer_checkpoint_to_agents` 문서).
  - update 카운터는 1부터 다시 시작한다.
  - Python/NumPy/Torch 전역 RNG, train() 내부의 rng/probe_rng Generator, env 상태, 진행 중 episode·hidden state는 저장되지 않는다.
  - 트레이너를 수정하지 않는 원칙과 정확한 재현성을 위해 resume을 새로 구현하지 않는다.
  - 따라서 4–5M 점검은 **학습을 멈추지 않고** W&B, metrics.jsonl, checkpoint를 읽기 전용으로 확인한다.
  - 중단되면(재부팅 등) 해당 run은 처음부터 다시 실행하는 것이 원칙이다. 근사 재개는 별도 조건으로만 기록한다.
- **실행 계획(승인 대기)**
  - `run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -Stage2Seeds 1`
  - 기본 Stage2 mode는 ippo/pgct/oracle/all, 15M, 병렬 4 프로세스, 스레드 4.
  - 예상: update당 약 39초, 15M ≈ 14,649 update ≈ 약 6.6–7일. 4–5M 도달은 약 1.9–2.4일 뒤.
  - seed 2·3 반복은 seed1 결과를 본 뒤 결정한다.

## 새 항목 작성 양식

`ID / 날짜·작성 도구 / 사용자 질문·요청 / 관측 / 판단과 근거 / 수행 또는 제안 / 변경된 이전 판단 / 미해결 질문` 중 해당 내용을 적는다.
