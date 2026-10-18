# 새 세션 인수인계 — PGCT / 잠재 팀 연구

**갱신: 2026-10-18 14:30 KST, Claude Code.** 새 세션(Codex·Claude Code)은 이 문서를 **가장 먼저** 읽는다. 세부 근거는 D(결정)·E(실험)·T(대화) 번호로 `DECISIONS.md`·`EXPERIMENTS.md`·`CONVERSATION_LOG.md`에서 찾는다. 모든 기록을 한 파일로 합친 읽기 전용 사본은 `research_archive/RESEARCH_ARCHIVE.md`다(원본을 고친 뒤 `python research_archive/build_archive.py`로 다시 만든다).

이 문서는 작성 시점의 스냅샷이다. 실행 상태는 반드시 실제 로그로 다시 확인한다. 이전 버전(2026-10-15)의 내용은 E19–E24, D29–D36에 있다.

## 0. 30초 요약

- **연구 목표(D17, D41 재확인)**: **PGCT = 모르는 같은 팀을 probe 응답으로 찾아내고, 그 팀끼리 critic을 전이해 학습을 돕는 방법.** 사용자는 이 원래 기획을 유지한다. "전이 적합성 발견"으로 중심을 옮기지 않는다.
- **현재 실행 중**: **E1-F main**(팀 목표를 양쪽 모서리로 분리). IPPO/PGCT/Oracle/All(canonical) + PGCT(v2), seed 1, 각 10M. 약 0.12M step(14:30), job당 약 19 step/s이며 **10월 24일 무렵 종료** 예상이다(E26).
- **E1 결과(seed 1, 6.4M, 중단)**: PGCT가 IPPO와 All보다 낫고 Oracle의 89%다. 이득은 "뒤처진 agent 구제"에서 나왔다. E1은 팀이 색 라벨로만 다른 **팀 대칭 대조 조건**이라 팀 발견을 시험할 수 없다(D40, D41).
- **논문**: IJCAI 2027(초록 1/4, 본문 1/11 AoE). **방법 논문 초안 v0.2**가 `output/ijcai_method_paper_20261018/`에 있다(영어+한국어, Overleaf zip). E1-F와 seed 결과 자리는 TBD다.

## 1. 지금 돌고 있는 학습 — 건드리지 말 것

| 폴더 | 내용 |
|---|---|
| `runs/e1f_20261018_124343_main_canonical` | e1f_ippo/pgct/oracle/all_s1, canonical bank |
| `runs/e1f_20261018_124343_main_v2` | e1f_pgct_s1, probe bank v2(gate 48 + distill 64) |

- 조건: E1 맵, 팀 목표 (0,10)/(9,10), home .5, individual reward, seed 1, 무작위 초기화(초기 hash `f78ec390…`, E1 seed 1과 동일), 10,000,384 step, W&B `rware-from-scratch`.
- 시작: 2026-10-18 12:43 KST(사용자 승인, `.\latent_team\run_e1f.ps1 -Phase main -Track`).
- 분석(읽기 전용, 언제든): `python latent_team/e1f_team_divergence.py --run runs/e1f_20261018_124343_main_canonical`(main_v2도). 2M 무렵부터 의미가 있다. 배송 중 왼쪽 이동 비율(빨강≈1, 파랑≈0이면 팀별 행동 분화)과 v2/canonical probe의 같은 팀/다른 팀 JS를 계산한다.
- **E1-F에서 볼 것(D41 순서)**
  - ① Oracle > All인가
  - ② 팀원의 critic이 더 호환되는가(E11 blend gain을 E1-F checkpoint에 적용, 스크립트 확장 필요)
  - ③ PGCT/PGCT-v2가 같은 팀을 고르는가(transfer.jsonl 같은 팀 arc 비율, probe AUROC)
  - ④ 성능
- **분기(D41)**
  - Oracle>All이고 PGCT가 같은 팀을 고른다 → 원 기획 논문
  - 같은 팀을 고르지 못한다 → v2와 비교하고 probe를 개선
  - Oracle≈All → 팀 보상 등 조건을 추가하거나 방향을 재논의

## 2. 끝난·중단된 학습

- **E1 from-scratch**(`runs/scratch_20261015_093349_stage2`): 사용자 지시로 2026-10-18 12:43에 약 6.5M에서 중지했다(`STOPPED_BY_USER.txt`). 마지막 checkpoint는 06250이고 W&B에서는 crashed로 표시된다(E24 추가).
  - 결과(공통 6.4M, 평가 20×500 deterministic)는 아래 표와 같다. 논문용 그림·표는 `output/paper_e1_20261018/`(E27)에 있다.

| | 시작(≥1) | 학습 중 평균 | 최종(최근 5회) | 배운 agent |
|---|---|---|---|---|
| IPPO | 2.05M | 10.4 | 23.2±1.1 | 2/4 |
| PGCT | 1.79M | 11.7 | 27.3±1.4 | 3/4 |
| Oracle | 1.64M | 13.2 | 32.2±1.7 | 3/4 |
| All | 3.99M | 3.7 | 19.4±1.6 | 4/4 |

  - PGCT gate: 2M 이후 같은 팀 전이가 거의 0이고, 다른 팀(3–4, 이후 1–2)만 연결된다. E1은 팀 대칭 조건이라 예상된 결과다.
  - **재현성**: 같은 seed의 이전 run(E17)과 비교하면 IPPO는 완전히 재현되지만, 전이 mode는 1.4–1.6M에서 갈라진다(원인 미확인). All의 배송 시작이 1.89M에서 3.99M으로 바뀌었다. **seed 반복이 필수다.**
- 이전 기록: E17(2.5M 재부팅 중단), Stage03 연장 실험 E02(E1 PGCT AUC 45.86 vs IPPO 44.57), 고정 모델 진단 E11/E13/E20/E23.

## 3. 사용자 승인이 필요한 대기 항목

1. **E1 seed 2·3**: 예산 10M 고정을 제안했다(D36). E1-F가 끝나는 10월 24일 이후에 하거나, 속도 저하를 감수하고 병행한다.
2. **E1-F 팀 보상 pilot**: `.\latent_team\run_e1f.ps1 -Phase pilot -Track`(IPPO 개인/팀 보상 각 5M, E25). main을 먼저 시작했으므로 미실행이다.
3. **개입 실험**: 뒤처진 agent의 distillation을 차단해 "구제" 메커니즘을 검증한다(미구현).
4. **비결정성 원인 조사**: 전이 경로의 GPU 연산. 코드 확인만으로 가능하다.
5. **MAPPO/SePS/HetDPS 본 학습**: 효과 조건을 확정한 뒤 한다(D34).
6. **v0.3 논문용 추가 실험**: Random-gated(전이량 통제)와 budget-matched Oracle 구현·실행, checkpoint에서 실측 Δ·ρ·추론 정밀도/재현율(학습 불필요), gradient 정렬 진단(D44).

## 4. 논문 상태

| 폴더 | 내용 | 상태 |
|---|---|---|
| `output/ijcai_method_paper_20261018/` | **방법 논문 v0.3(현행)** "Probe-Gated Critic Transfer: Local Teammate Inference...". 이론 절(명제 1–6, 부록 증명), 2×2 설계, Random-gated baseline(TBD). v0.1·v0.2 보존 | 외부 검토 반영(D44). 명제 3·6 가정은 교수님 검토 필요 |
| `output/ijcai_paper_20261018/` | 진단 논문 초안 "Policy Similarity Is Not Team Membership" | 보존용(D38) |
| `output/paper_e1_20261018/` | E1 그림 5, LaTeX 표 4, 영어 결과 초안, `make_paper_materials.py` | E27 |
| `output/ijcai_review_20261015/REPORT.md` | Codex의 IJCAI 기획(RQ1–3, 통계, 일정) | D23 |

- 로컬에 LaTeX가 없어 원고를 컴파일하지 않았다. Overleaf에 zip을 올리고 IJCAI sty와 `named.bst`를 추가해야 한다.
- 참고문헌 HetDPS(`hu2025heterogeneity`)는 서지 정보가 TODO다.

## 5. 사용자가 정한 작업 원칙

- "현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서" 진행한다. trainer(`examples/train_recurrent_ippo_consensus.py`), 환경(`rware/`), `rware/utils/probe_maps.py`는 수정하지 않았다. 새 기능은 옵션으로만 넣고 기본값은 유지한다.
- "실제 수백만 step의 본 학습은 제 승인 없이 시작하지 마세요." 실행 중인 학습을 임의로 중단·재시작하지 않는다.
- "기존 학습 체크포인트, 실험 로그, 결과물은 보존해 주세요." 삭제 허가는 그 요청 범위에만 적용된다(D27).
- 매 turn 사용자 메시지와 답변을 `CONVERSATION_LOG.md`에 원문으로 기록한다(AGENTS.md). 현재 T047까지 있다.
- 사용자에게는 한국어로 쉽게 설명하고, 수치에는 조건(seed·step·평가)을 붙인다. 단정과 가설을 구분한다.

## 6. 작업 요령(실수에서 배운 것)

- **학습 중지 시** python 프로세스뿐 아니라 자식 `wandb-core`/`wandb-xpu`까지 종료해야 W&B가 running에서 벗어난다. 서버 반영에 약 10분 걸린다. PID는 pipeline 로그와 `Win32_Process`의 ParentProcessId로 확인한다(E24 추가).
- **Bash 도구는 heredoc 안의 `\\`를 `\`로 바꾸고, `\r`·`\t` 같은 조합이 제어 문자로 들어갈 수 있다.** 백슬래시가 들어가는 내용(LaTeX, 정규식, Windows 경로)은 Write 도구로 파일에 쓰고, Python 스크립트도 파일로 저장해 실행한다(T043).
- **pytest**는 `--basetemp <scratchpad>`를 줘야 권한 오류가 없다(전체 185 passed, 2026-10-18).
- 기록 파일의 줄 끝: `CONVERSATION_LOG.md`는 CRLF, `DECISIONS.md`·`EXPERIMENTS.md`·`RESEARCH_STATE.md`는 LF다.
- 속도: E1 run(4개 동시)은 job당 약 24 step/s, E1-F(5개 동시)는 약 19 step/s다.

## 7. 코드 지도

| 위치 | 내용 |
|---|---|
| `latent_team/train_from_scratch.py` | from-scratch 실행기. modes ippo/pgct/oracle/all/wrong/mappo/seps/hetdps, `--env-variant e1/e1f`, `--probe-bank canonical/v2`, `--team-reward individual/team`, `--track` |
| `latent_team/run_e1f.ps1` | E1-F 실행기. `-Phase pilot`(IPPO 개인/팀 보상), `-Phase main`(4 mode canonical + PGCT v2) |
| `latent_team/run_from_scratch.ps1`, `run_scratch_pipeline.ps1` | 병렬 실행과 2단계 파이프라인(`-TeamReward` 전달) |
| `latent_team/exp_b_oracle_consensus.py` | trainer 함수를 프로세스 안에서만 감싸 oracle/all/wrong 분기, transfer.jsonl 기록 |
| `latent_team/probes_v2.py` | E1-F 변형, probe bank v2 |
| `latent_team/e1f_team_divergence.py` | E1-F 팀 분화와 probe JS 분석(읽기 전용) |
| `latent_team/exp_a_team_identifiability.py` | 실험 A(E11): 식별 AUROC, blend gain |
| `latent_team/marl_baselines.py` | MAPPO/SePS/HetDPS(smoke만) |
| `output/scratch_review_20261018/analyze.py` | 학습 중간 분석(E24) |
| `output/paper_e1_20261018/make_paper_materials.py` | 논문 그림·표 생성(E27) |
| `tests/test_latent_team.py` | 전체 185 passed |

Python: `C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe`. 브랜치는 `feature/PGCT_Change`이고 커밋하지 않은 변경이 많다(사용자 요청 시에만 커밋).

## 8. 핵심 결정 색인 (최근)

- D33 A3–A4 연결은 "원정 담당" 역할 짝이다(팀 아님).
- D36 E1을 15M 대신 10M 고정 예산으로 제안
- D37 공유 범위와 배운 agent 수의 관계(가설)
- D38 진단 논문 초안
- D39 사용자는 방법 논문 초판을 원함
- D40 E1은 색 라벨만 다른 대칭 환경
- **D41 PGCT의 정체성은 원 기획(잠재 팀 발견)이다. E1-F 결과로 분기한다.**
- D42 방법 논문 v0.2(원 기획 서사)와 인수인계 갱신
- D43 이론 보강 방향과 교수님 JS convexity 질문(ex5.pdf 참고)
- **D44 방법 논문 v0.3: 외부 검토 반영, 이론 절 신설, Random-gated baseline 추가(TBD)**
