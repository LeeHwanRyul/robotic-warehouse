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

## 새 항목 작성 양식

`ID / 날짜·작성 도구 / 사용자 질문·요청 / 관측 / 판단과 근거 / 수행 또는 제안 / 변경된 이전 판단 / 미해결 질문` 중 해당 내용을 적는다.
