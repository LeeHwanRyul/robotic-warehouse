# 새 세션 인수인계 — PGCT / 잠재 팀 연구

작성: 2026-10-15 12:50 KST, Claude Code. 새 세션(Codex·Claude Code)이 **가장 먼저 읽는 문서**다. 세부 근거는 각 항목의 D/E 번호로 `DECISIONS.md`·`EXPERIMENTS.md`에서 찾는다. 모든 기록을 한 파일로 합친 사본은 `research_archive/RESEARCH_ARCHIVE.md`다(생성 명령은 아래).

이 문서는 작성 시점의 스냅샷이다. 실행 상태는 반드시 실제 로그로 다시 확인한다.

**최신 재확인: 2026-10-18 12:23 KST, Claude Code.** 4개 run 약 6.4–6.55M, 정상 진행 중이며 10월 22일 무렵 15M 도달 예정이다. 최근 5회 평가 delivery: Oracle 32.3 / PGCT 27.9 / IPPO 24.3 / All 20.4(All은 늦게 시작했지만 4명 모두 배송). 같은 seed의 E17과 비교하면 전이 mode는 1.4–1.6M에서 갈라졌다. 상세는 EXPERIMENTS E24, `output/scratch_review_20261018/`.

**이전 재확인: 2026-10-15 13:17 KST, Codex.** 기존 E1/canonical seed1 학습 로그가 계속 갱신된다(IPPO321,536 / PGCT316,416 / Oracle314,368 / All318,464 env steps). 네 mode의 최근307,200step 평가(delivery/pickup/return)는 모두0이며 초기 구간이라 성능 판단을 보류한다. 오류 로그에서 Traceback/Error/Exception/failed는 발견하지 못했다. E1-F/v2는64-step smoke 완료 상태이며 본 학습은 아직 확인되지 않는다. 근거: `output/status_review_20261015_131716/snapshot.json`, EXPERIMENTS E19 추가. 이번 점검은 새 학습·코드 변경 없이 수행했다. 아래12:49 수치는 과거 스냅샷으로 보존한다.

## 1. 연구 목표

- **본 연구(D17, D25)**: 각 agent가 국소 관측된 행동으로 **잠재 팀을 추론**하고, 추론한 팀 안에서 **critic을 전이**해 학습 효율을 높인다.
- **검증 순서(D25)**: H1 식별 가능성 → H2 Oracle(정답 팀) 공유 이득 → 분산 추론 → 학습 개선.
- **현재 본 학습의 목적(D22, 사용자 강조)**: critic 공유 효과 검증이다. 잠재 팀 발견 문제를 푸는 실험이 아니다.
- **알려진 구조 문제**
  - 관측이 팀 기준이고 두 팀 목표가 인접·대칭이다. 그래서 같은 팀 critic이 더 호환되지 않는다(E11).
  - 기존 canonical probe 48개는 고유 입력이 26개다. "적재 중 + 목표 비가시" 상태가 0개라 원리적으로 팀 식별력이 없다(D26, E20).
  - 그래서 E1-F(목표 분리)와 probe bank v2를 옵션으로 구현했다(D29, E22).

## 2. 지금 돌고 있는 학습 — 건드리지 말 것

- **run**: `runs/scratch_20261015_093349_stage2`
- **조건**: E1 11×10, home .5, individual reward, IPPO/PGCT/Oracle/All, seed 1, 무작위 초기화, 15M, W&B 프로젝트 `rware-from-scratch`. 네 초기 가중치 hash가 같다(E19).
- **스냅샷(2026-10-15 12:49 KST)**: IPPO 281,600 / PGCT 277,504 / Oracle 275,456 / All 279,552 step. 4개 모두 running이고 job당 약 24 step/s다. 15M까지 약 7일 걸린다.
- **다음 할 일**: 4–5M에서 읽기 전용 점검(약 2026-10-17). 15M까지 계속할지는 사용자가 결정한다.
- **재개 불가(D22)**: trainer에 resume이 없다. 중단되면 처음부터 다시 돌린다. 이전 run E17은 Windows Update 재부팅으로 2.5M에서 끊겼고, 분석은 E18에 있다.
- **E18 요약(seed 1, 2.4M)**: Oracle의 delivery가 약 10으로 앞섰지만 Agent2 한 명에게서 나온 값이라 효과로 귀속할 수 없다. PGCT gate는 같은 팀과 다른 팀을 구분하지 않았다.

## 3. 사용자 승인이 필요한 대기 항목

- **E1-F + probe v2 본 학습**: 구현과 smoke는 완료했다. 시작하지 않았다.
  ```powershell
  .\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -EnvVariant e1f -ProbeBank v2 -Stage2Seeds 1
  ```
  현재 run과 동시에 돌리면 8개 프로세스가 되어 양쪽이 모두 느려진다.
- **MAPPO/SePS/HetDPS 본 학습**: 구현과 smoke만 했다(E15, `latent_team/BASELINES.md`). 핵심 비교 이후로 미뤘다(D22).
- **seed 2·3 반복**: seed 1 결과를 본 뒤 결정한다.

## 4. 사용자가 정한 작업 원칙 (원문 취지)

- "현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서" 진행한다. trainer(`examples/train_recurrent_ippo_consensus.py`), 환경(`rware/`), `rware/utils/probe_maps.py`는 수정하지 않았다.
- "현재 PGCT, IPPO, Oracle, All 구현은 변경하지 않는 것을 원칙으로" 한다. 새 기능은 옵션으로만 추가하고 기본값은 바꾸지 않는다.
- "실제 수백만 step의 본 학습은 제 승인 없이 시작하지 마세요."
- "기존 학습 체크포인트, 실험 로그, 결과물은 보존해 주세요." 삭제 허가는 그 요청 범위에만 적용된다(D05, D19, D27).
- 실행 중인 학습을 중단하거나 재시작하지 않는다.
- 매 turn의 사용자 메시지와 답변을 `CONVERSATION_LOG.md`에 원문으로 기록한다(AGENTS.md).
- 사용자에게는 한국어로 쉽게 설명한다. 수치에는 조건(seed·step·평가)을 붙인다.

## 5. 코드 지도

| 위치 | 내용 |
|---|---|
| `latent_team/train_from_scratch.py` | from-scratch 실행기. MODES = ippo, pgct, oracle, all, wrong, mappo, seps, hetdps. `--env-variant {e1,e1f}`, `--probe-bank {canonical,v2}`, `--track` |
| `latent_team/run_from_scratch.ps1`, `run_scratch_pipeline.ps1` | 병렬 실행 / Stage1→Stage2 파이프라인(`-Detach`이면 UTF-8 로그) |
| `latent_team/exp_b_oracle_consensus.py` | `matched_transfer`: trainer 함수를 프로세스 안에서만 감싸 oracle/all/wrong 분기, transfer.jsonl 기록 |
| `latent_team/marl_baselines.py` | MAPPO / SePS / HetDPS (numpy로 다시 구현한 clustering) |
| `latent_team/probes_v2.py` | E1-F 환경 변형, probe bank v2(gate 48 + transfer 64) |
| `latent_team/exp_a_team_identifiability.py`, `verify_evidence_observability.py` | 실험 A(E11), 증거 관측 가능성(E13) |
| `tests/test_latent_team.py` | 전체 183 passed (2026-10-15) |
| `output/` | 분석 보고서. scratch_review_20261015(E18), env_view_20261015(E20, probes_v2), ijcai_review_20261015(D23), cleanup_20261015(E21 삭제 목록) |

Python: `C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe`. 브랜치는 `feature/PGCT_Change`이고 커밋하지 않은 변경이 많다(사용자 요청 시에만 커밋).

## 6. 기록 파일 역할

| 파일 | 역할 |
|---|---|
| `HANDOFF.md` | 이 문서. 새 세션 시작점 |
| `RESEARCH_STATE.md` | 현재 상태 스냅샷(위쪽이 최신). 2026-10-15 오후 Claude 작업(E20–E22)은 이 HANDOFF에 반영됨 |
| `DECISIONS.md` | D01–D29 질문·결론·판단 |
| `EXPERIMENTS.md` | E00–E22 실험 기록 |
| `CONVERSATION_LOG.md` | L01–L12 과거 요약, T001–T028 원문(Codex·Claude 공용) |
| `research_archive/RESEARCH_ARCHIVE.md` | 위 모든 파일과 output 보고서, 실행기 문서를 합친 읽기 전용 사본 + 날짜순 통합 타임라인 |

통합본 다시 만들기(원본을 바꾼 뒤):
```powershell
C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe research_archive\build_archive.py
```
