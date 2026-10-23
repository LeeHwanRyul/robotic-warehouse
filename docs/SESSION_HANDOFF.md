# 세션 인수인계 — 2026-10-23 17:33 KST 기준

> 2026-10-23 Codex 후속 변경: 사용자 승인으로 `--reward-probe-ac` 실행 옵션을 구현했다.
> 개인 보상, 좌표 마스크, 지역 전이/가상 action branch, 자기 경험 조건부 평균 예측, 지원 부족 시 보류를 연결했다.
> CNN 구현이나 본 학습 결과는 아니다. 새/기존 검사 31개 통과, 학습 프로세스는 건드리지 않았다.
> 현재 코드 안내는 `docs/REWARD_PROBE_AC.md`와 `RESEARCH_STATE.md` 맨 위를 본다. 아래 실행 상태는 과거 스냅샷이다.

작성: Claude Code(세션 `3d772392…`이 길어져 새 세션으로 넘김). 아래 실행 상태는 스냅샷이다. 새 세션은 먼저 실제 프로세스와 로그로 다시 확인한다(5절 명령).

## 1. 지금 돌고 있는 것

### 학습 프로세스 (사용자가 앱 밖 PowerShell에서 시작, 건드리지 말 것)

| PID | job | 17:33 진행 | 예상 종료(약 16 step/s 추정) |
|---|---|---|---|
| 32376 | `b6_adjacent_team_pen005_ippo_s1` | 850,944 / 1M | 10-23 20–21시 |
| 21104 | `b6_adjacent_team_pen005_ippo_s2` | 840,704 / 1M | 10-23 20–21시 |
| 30744 | `b6_adjacent_indiv_pen005_ippo_s1` | 585,728 / 1M | 10-24 01시 무렵 |
| 31960 | `b6_adjacent_indiv_pen005_ippo_s2` | 573,440 / 1M | 10-24 01시 무렵 |

- 폴더: `runs/queue_20261022_140114_b6_adjacent_{team,indiv}_pen005/`. 1M 2×2 pilot의 인접 칸이다. 모서리·개인 칸은 이미 complete다.

### 메인 1단계 대기열 (PID 32236, 시작한 job 0)

- 명령(사용자 실행, 17:22): `run_queue.ps1 -Candidates b6_corner_indiv_pen005 -Modes ippo,oracle,all -Seeds 1,2,3 -TotalTimesteps 5000000 -MaxConcurrent 4 -Track`
- 폴더: `runs/queue_20261023_172201_b6_corner_indiv_pen005/`(계획만 있음)
- 인접 칸이 끝나면 자동으로 job을 띄운다. **인접·팀이 끝나는 오늘 밤 20–21시에 첫 2 job이 시작된다.**

## 2. 사용자에게 아직 답을 받지 못한 결정 (가장 급함)

**질문(T130 끝)**: 메인 대기열을 멈추고, 팀당 요청 수 pilot을 먼저 할까?

- 배경
  - 사용자 지적: 개인 보상에서 팀원끼리 경쟁하는 것은 요청 선반이 너무 적어서다. 물량이 많은 편이 낫다.
  - E55(무작위 정책, 학습 없음): 팀당 요청 3 → 6 → 9개면 agent당 자기 팀 요청 pickup이 1.02 → 1.96 → 2.73/ep다.
- Claude 권고(T130)
  1. 지금 대기열 창을 닫는다. 아직 시작한 job이 없다.
  2. Claude가 팀당 요청 6·9개 변형을 만들고 smoke까지 확인한다.
  3. 사용자가 IPPO 1M × seed 2 pilot(4 job)을 건다.
  4. 결과를 3개짜리 1M과 비교해 요청 수를 정한 뒤 5M 메인을 다시 건다. 메인은 하루쯤 늦어진다.
- 위험: 문제가 쉬워지면 IPPO도 잘 배워 전이의 여지가 줄 수 있다. 요청 수를 바꾸면 기존 3개짜리 1M 결과와는 따로 비교해야 한다.
- 구현 메모(아직 안 함): `latent_team/env_candidates.py`에 새 후보(예: `b6_corner_indiv_pen005_req6`, `_req9`)를 추가한다. env override는 `request_queue_size=2k`, `request_queue_size_per_team=[k,k]`다. `run_candidate_pilot.ps1`·`run_queue.ps1` 후보 목록과 `tests/test_latent_team.py`도 늘린다. 기존 후보와 기본값은 바꾸지 않는다.
- 새 세션은 이 질문에 대한 사용자 답을 먼저 확인한다. 답이 없는 채로 20–21시가 지나면 메인 job이 이미 시작됐을 수 있다. 시작된 학습은 사용자 지시 없이 멈추지 않는다.

## 3. 최근 결정과 근거 (10-22 – 10-23)

| D | 내용 | 근거 |
|---|---|---|
| D70 | 감점 0은 환경 후보로 부적합하다 | E46: 정체는 풀렸지만 TOGGLE 남발, 평가 배송 없음 |
| D71 | 기여 후보는 "식별 가능성 조건 (가)(나) + 조건별 probe"다. 중심은 팀 발견으로 유지한다 | 선배 지적(불필요한 가정), Du et al.과의 근접성 |
| D72 | 보상 결합 probe는 팀 보상에서 자명하다 | E49: AUROC 1.00 |
| D74 | 2×2를 같은 기반(6 agent·통신 3·pen005)으로 통일한다. 자동화는 감시·판정·보고까지만 하고, 시작은 사용자가 한다 | 외부 검토의 교란 지적 |
| D76 | 12 job 대신 IPPO 대 Oracle-team부터 하고, "배운 agent" 기준을 사전 고정한다 | 외부 검토 세 건 |
| D77 | All-peer를 추가한다 | E53 |
| D78 | **1M 결과로 최종 결론을 낸 것은 과했다.** 메인은 5M | 사용자 지적: 옛 sensor 5 설정은 2–5M에 배우기 시작했고 4 agent가 모두 배운 모델은 8M에 완성됐다 |
| D79 | 새 환경 후보는 LBF 변형이다. SMAC·Hide-and-Seek은 부적합하다. E1-F 옛 설정은 재시작하지 않는다 | 잠재 팀 구조의 유무 |
| D80 | 정책 probe는 JS 대신 goal 방향 축으로 본다 | E54: 부호 규칙 .76–.83 |
| D81 | **메인은 개인 보상(모서리·개인 칸)이다.** 팀 보상 칸은 참조로 둔다 | 사용자 의견. 팀 보상에서는 보상 결합이 곧 팀의 정의 |

## 4. 미해결 문제

1. **개인 보상에서 Oracle-team이 정말 도움이 되는가.** 팀원끼리 같은 요청을 두고 경쟁해 critic이 같은 값을 추정하지 않을 수 있다(D81 위험). 모서리·개인 1M의 최다 agent 비율은 .97–.99였다.
2. **한 agent 독주.** 1M에서 한 agent가 배송의 82–99%를 했다. 5M에 풀리는지, 요청 수로 풀리는지 모른다.
3. **goal 방향 축은 아직 오프라인 측정뿐이다.** 시점별(EMA)·온라인 정확도와 충분히 학습된 정책에서의 유지 여부는 확인하지 않았다. 인접 칸(판별 probe 3개)에서는 실패할 것으로 예상한다.
4. **보상 결합 gate**에는 개인 보상용 판정 보류 규칙이 없다. 개인 보상 칸에서 15쌍 중 5–9쌍을 오판정했다.
5. **정확한 이어 학습 불가.** `--init-checkpoint`는 actor만 복사하고 optimizer·graph를 초기화한다. 난수 상태도 저장되지 않는다. 학습이 외부 요인으로 끊기면 처음부터 다시 해야 한다.
6. **단일·소수 seed.** E1(seed 1), E1-F(seed 1), 2×2(seed 2개)뿐이다. 같은 seed에서도 전이 mode는 비결정적으로 갈라진다.
7. **보고서 수치 재현성.** E54의 agent 단위 수치(152명 .74, 배운 19명 .90)는 계산 스크립트가 남아 있지 않다.
8. **Overleaf 보고서**(`output/pgct_progress_paper_20261023/`)는 "개인 보상 메인" 결정(D81) 전의 구도다. 다음에 함께 고치겠다고 사용자에게 약속했다(T129).
9. 10-21 발표본은 로컬에 없다. 교수님 피드백 내용도 노트에 없다.

## 5. 다음 세션의 첫 작업 (우선순위 순)

1. **상태 재확인(읽기 전용).**
   ```powershell
   Get-CimInstance Win32_Process -Filter "Name='python.exe' or Name='powershell.exe'" | Where-Object { $_.CommandLine -match 'run-job|run_queue' } | Select-Object ProcessId, CreationDate, CommandLine
   ```
   ```powershell
   Get-Content runs\queue_20261023_172201_queue.log
   ```
   각 job 폴더의 `metrics.jsonl` 마지막 줄에서 `env_steps`, `job_status.json`에서 상태를 본다.
2. **2절 질문에 대한 사용자 답 확인.** 요청 수 pilot을 하기로 하면 변형을 추가하고 smoke와 설정 대조까지만 한다. 학습은 사용자가 건다.
3. **인접 칸 분석**(끝난 뒤, 학습 없음).
   - `python latent_team/pilot_verdict.py --plan runs/queue_20261022_140114_b6_adjacent_team_pen005`(인자: `--plan`, `--spam-reference`, `--compare`, `--poll`, `--once`). 기본은 모든 job이 complete가 될 때까지 기다린다. `--once`는 진행 중에도 바로 판정한다. 5번 기준(비요청 pickup)은 `--spam-reference`(nopen run)가 있어야 판정된다.
   - `output/pen005_analysis_20261023/probes_pen005.py`(인자: plan, candidate, 출력 이름)로 보상 결합·정책 probe 측정
   - goal 방향 축: 인접 배치에서는 판별 probe가 3개뿐이라 실패가 예상된다. 결과는 조건 (가)의 음성 사례 후보다.
4. **PGCT-axis gate 구현**(새 옵션, 기본값 불변, smoke만): 부호 규칙 + EMA. 기존 오프라인 checkpoint로 시점별 정확도를 먼저 잰다.
5. **PGCT-reward gate**(보조, smoke만): 판정 보류 규칙을 포함한다.
6. **이어 학습 wrapper**: optimizer·graph 상태 복원. 새 파일로 만든다.
7. **메인 중간 확인**: 각 job이 2M·3M에 도달하면 읽기 전용으로 본다(첫 job 기준 10-25–27 무렵). 판정은 5M에서 한다.
8. **Overleaf 보고서 갱신**: 개인 보상 메인 구도(D81)와 E55를 반영한다.
9. 작업 끝에 `RESEARCH_STATE.md`, `DECISIONS.md`, `EXPERIMENTS.md`, `CONVERSATION_LOG.md`를 갱신한다.

## 6. 작업 원칙 (사용자가 정한 것)

- 수백만 step 학습은 사용자 승인 없이 시작하지 않는다. 긴 학습은 사용자가 Claude 앱 밖 PowerShell에서 직접 건다. 앱이 업데이트되면 앱의 하위 프로세스가 함께 죽기 때문이다(E26).
- 실행 중인 학습은 임의로 멈추거나 다시 시작하지 않는다.
- 기존 checkpoint·로그·결과는 덮어쓰거나 지우지 않는다. 새 실험은 새 폴더에 저장한다.
- trainer(`examples/train_recurrent_ippo_consensus.py`), 환경(`rware/`), `examples/`는 수정하지 않는다. 새 기능은 `latent_team/`에 옵션으로 넣고 기본값은 유지한다.
- 자동화는 감시·판정·보고까지만 한다. 대기열 시작은 사용자가 한다(D74).
- 연구 방향은 사용자가 능동적으로 고른다. 교수님 합의를 기다리지 않는다(T105). Claude는 무조건 동의하지 말고 냉정하게 의견을 낸다.
- 커밋은 요청이 있을 때만 한다. 브랜치는 `feature/PGCT_Change`이고 커밋하지 않은 변경이 많다.
- 논문은 AI가 쓴 것처럼 보이지 않게 쓴다. 불필요한 가정을 줄인다(선배 조언, 메모리 `paper-minimize-assumptions`).
- 사용자에게 한국어로 설명한다. 수치에는 모델·환경·seed·step·평가 조건을 붙인다.
- 모든 turn을 `CONVERSATION_LOG.md`에 원문으로 기록한다(KST, 도구명, 진행 안내·최종 답변, CRLF). API 키·토큰·비밀번호는 기록하지 않는다.

## 7. 작업 요령 (실수에서 배운 것)

- **wrap_up의 질문 상자는 turn을 끝낸다.** 질문을 넣으면 그 뒤의 본문이 화면에 나오지 않는다. 답변 본문은 wrap_up 호출 전에 쓴다(T099, T125에서 답변이 안 보였다).
- **heredoc 안의 백슬래시**: Bash heredoc의 Python 문자열 `"\ref"`가 CR+`ef`로 바뀌어 main.tex의 참조 11개가 깨진 적이 있다. LaTeX·정규식·Windows 경로·Python 스크립트는 Write 도구로 파일에 쓴 뒤 실행한다.
- **PowerShell 배열 인자**: `powershell -File`로 `-Candidates a,b`를 넘기면 한 문자열이 되어 ValidateSet에서 거부된다. `powershell -ExecutionPolicy Bypass -Command "& '.\latent_team\run_queue.ps1' -Candidates a,b ..."`로 쓴다.
- **대기열 이름 재사용**: 같은 `-Name`으로 다시 걸면 계획 단계에서 멈춘다(기존 폴더 보호).
- **"중지됨" 표시**: 세션을 재시작한 뒤 앱의 백그라운드 작업이 "중지됨"으로 보여도 프로세스는 살아 있을 수 있다. PID로 확인한다. 사용자가 "왜 멋대로 중지했냐"고 오해한 적이 있다.
- **학습 중지 시**에는 python뿐 아니라 자식 `wandb-core`·`wandb-xpu`도 종료해야 W&B가 crashed로 바뀐다(E24).
- **pytest**: `--basetemp <scratchpad>`가 필요하다. `tests/test_env.py::test_inactivity_1`은 가끔 실패하고 다시 돌리면 통과한다.
- **PDF**: 이 PC에는 PDF 도구가 없다. scratchpad의 `pylib`에 pypdf 4.3.1을 설치해 읽었다(세션 scratchpad라 새 세션에는 없다).
- **LaTeX**: 로컬에 없다. 보고서는 Overleaf에서 컴파일한다(pdfLaTeX, 한글 오류 시 XeLaTeX). Overleaf zip은 gitignore 대상이다.
- **Python**: `C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe`.
- **줄 끝**: `CONVERSATION_LOG.md`는 CRLF, 다른 노트는 LF다.

## 8. 자주 쓰는 명령 (사용자 실행용 예시, 실행 사실 아님)

```powershell
cd C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
```

```powershell
powershell -ExecutionPolicy Bypass -Command "& '.\latent_team\run_queue.ps1' -Candidates b6_corner_indiv_pen005 -Modes ippo,oracle,all -Seeds 1,2,3 -TotalTimesteps 5000000 -MaxConcurrent 4 -Track"
```

`run_queue.ps1`의 인자는 `-Candidates -Modes -Seeds -TotalTimesteps -MaxConcurrent -PollSeconds -Name -RandomReference -Track -SmokeTest -PlanOnly`다. `-PlanOnly`로 학습 없이 계획만 만들 수 있다.

## 9. 문서 지도

| 문서 | 용도 |
|---|---|
| `docs/RESEARCH_CONTEXT.md` | 동기, 알고리즘·식, 검토한 신호, 방향 전환, 해결·실패·보류 |
| `docs/EXPERIMENT_HISTORY.md` | 실험별 설정·결과·경로 |
| `docs/SESSION_HANDOFF.md` | 이 문서 |
| `HANDOFF.md` | 10-18 기준 옛 인수인계(맨 위에 이 문서로 안내) |
| `RESEARCH_STATE.md` / `DECISIONS.md` / `EXPERIMENTS.md` / `CONVERSATION_LOG.md` | 원본 기록(D·E·T 번호) |
| `EXPERIMENT_STORY.md` | 실험 흐름을 쉬운 말로 정리 |
