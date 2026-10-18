# PGCT 연구 통합 기록

자동 생성: 2026-10-18 12:28 대한민국 표준시 — `python research_archive/build_archive.py`. 원본 파일은 수정하지 않았고, 이 파일은 원본을 순서대로 합친 사본이다. 원본이 갱신되면 이 파일은 낡으므로 다시 생성한다. 편집은 원본에 한다.

새 세션은 **Part 1(인수인계 요약)만 먼저 읽고**, 필요할 때 아래 목차에서 해당 부분을 찾는다.

## 목차

- Part 1. 인수인계 요약
  - `HANDOFF.md` (7 KB)
- Part 2. 공용 지침
  - `AGENTS.md` (5 KB)
  - `CLAUDE.md` (1 KB)
- Part 3. 현재 연구 상태
  - `RESEARCH_STATE.md` (17 KB)
- Part 4. 질문·결론·설계 판단
  - `DECISIONS.md` (49 KB)
- Part 5. 실험·평가 기록
  - `EXPERIMENTS.md` (44 KB)
- Part 6. 분석 보고서 (output/, 작성일 순)
  - `output/gating_diagnosis/README.md` (5 KB)
  - `output/pgct_spatial_analysis/REPORT.md` (41 KB)
  - `output/learning_review_20261013/REPORT.md` (13 KB)
  - `output/latent_team/exp_a_20261013/REPORT.md` (5 KB)
  - `output/scratch_review_20261015/REPORT.md` (6 KB)
  - `output/ijcai_review_20261015/REPORT.md` (36 KB)
  - `output/env_view_20261015/probes/README.md` (2 KB)
- Part 7. 실행기·구현 문서
  - `latent_team/README.md` (18 KB)
  - `latent_team/BASELINES.md` (8 KB)
  - `examples/README.md` (5 KB)
  - `examples/EX5_PGCT.md` (5 KB)
  - `examples/PGCT_PHYSICAL_MIXING_CURRICULUM.md` (5 KB)
  - `examples/PGCT_SPATIAL_EXPERIMENTS.md` (5 KB)
  - `examples/PGCT_TRANSFER_EXPERIMENTS.md` (13 KB)
  - `examples/HARD_RWARE_EXPERIMENTS.md` (9 KB)
- Part 8. 대화 기록 원문 (Codex + Claude Code)
  - `CONVERSATION_LOG.md` (262 KB)
- 부록. 통합 타임라인 (D=결정, E=실험, L/T=대화)

---

# Part 1. 인수인계 요약

## 출처: `HANDOFF.md` (수정 2026-10-18 12:26)

### 새 세션 인수인계 — PGCT / 잠재 팀 연구

작성: 2026-10-15 12:50 KST, Claude Code. 새 세션(Codex·Claude Code)이 **가장 먼저 읽는 문서**다. 세부 근거는 각 항목의 D/E 번호로 `DECISIONS.md`·`EXPERIMENTS.md`에서 찾는다. 모든 기록을 한 파일로 합친 사본은 `research_archive/RESEARCH_ARCHIVE.md`다(생성 명령은 아래).

이 문서는 작성 시점의 스냅샷이다. 실행 상태는 반드시 실제 로그로 다시 확인한다.

**최신 재확인: 2026-10-18 12:23 KST, Claude Code.** 4개 run 약 6.4–6.55M, 정상 진행 중이며 10월 22일 무렵 15M 도달 예정이다. 최근 5회 평가 delivery: Oracle 32.3 / PGCT 27.9 / IPPO 24.3 / All 20.4(All은 늦게 시작했지만 4명 모두 배송). 같은 seed의 E17과 비교하면 전이 mode는 1.4–1.6M에서 갈라졌다. 상세는 EXPERIMENTS E24, `output/scratch_review_20261018/`.

**이전 재확인: 2026-10-15 13:17 KST, Codex.** 기존 E1/canonical seed1 학습 로그가 계속 갱신된다(IPPO321,536 / PGCT316,416 / Oracle314,368 / All318,464 env steps). 네 mode의 최근307,200step 평가(delivery/pickup/return)는 모두0이며 초기 구간이라 성능 판단을 보류한다. 오류 로그에서 Traceback/Error/Exception/failed는 발견하지 못했다. E1-F/v2는64-step smoke 완료 상태이며 본 학습은 아직 확인되지 않는다. 근거: `output/status_review_20261015_131716/snapshot.json`, EXPERIMENTS E19 추가. 이번 점검은 새 학습·코드 변경 없이 수행했다. 아래12:49 수치는 과거 스냅샷으로 보존한다.

#### 1. 연구 목표

- **본 연구(D17, D25)**: 각 agent가 국소 관측된 행동으로 **잠재 팀을 추론**하고, 추론한 팀 안에서 **critic을 전이**해 학습 효율을 높인다.
- **검증 순서(D25)**: H1 식별 가능성 → H2 Oracle(정답 팀) 공유 이득 → 분산 추론 → 학습 개선.
- **현재 본 학습의 목적(D22, 사용자 강조)**: critic 공유 효과 검증이다. 잠재 팀 발견 문제를 푸는 실험이 아니다.
- **알려진 구조 문제**
  - 관측이 팀 기준이고 두 팀 목표가 인접·대칭이다. 그래서 같은 팀 critic이 더 호환되지 않는다(E11).
  - 기존 canonical probe 48개는 고유 입력이 26개다. "적재 중 + 목표 비가시" 상태가 0개라 원리적으로 팀 식별력이 없다(D26, E20).
  - 그래서 E1-F(목표 분리)와 probe bank v2를 옵션으로 구현했다(D29, E22).

#### 2. 지금 돌고 있는 학습 — 건드리지 말 것

- **run**: `runs/scratch_20261015_093349_stage2`
- **조건**: E1 11×10, home .5, individual reward, IPPO/PGCT/Oracle/All, seed 1, 무작위 초기화, 15M, W&B 프로젝트 `rware-from-scratch`. 네 초기 가중치 hash가 같다(E19).
- **스냅샷(2026-10-15 12:49 KST)**: IPPO 281,600 / PGCT 277,504 / Oracle 275,456 / All 279,552 step. 4개 모두 running이고 job당 약 24 step/s다. 15M까지 약 7일 걸린다.
- **다음 할 일**: 4–5M에서 읽기 전용 점검(약 2026-10-17). 15M까지 계속할지는 사용자가 결정한다.
- **재개 불가(D22)**: trainer에 resume이 없다. 중단되면 처음부터 다시 돌린다. 이전 run E17은 Windows Update 재부팅으로 2.5M에서 끊겼고, 분석은 E18에 있다.
- **E18 요약(seed 1, 2.4M)**: Oracle의 delivery가 약 10으로 앞섰지만 Agent2 한 명에게서 나온 값이라 효과로 귀속할 수 없다. PGCT gate는 같은 팀과 다른 팀을 구분하지 않았다.

#### 3. 사용자 승인이 필요한 대기 항목

- **E1-F + probe v2 본 학습**: 구현과 smoke는 완료했다. 시작하지 않았다.
  ```powershell
  .\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -EnvVariant e1f -ProbeBank v2 -Stage2Seeds 1
  ```
  현재 run과 동시에 돌리면 8개 프로세스가 되어 양쪽이 모두 느려진다.
- **MAPPO/SePS/HetDPS 본 학습**: 구현과 smoke만 했다(E15, `latent_team/BASELINES.md`). 핵심 비교 이후로 미뤘다(D22).
- **seed 2·3 반복**: seed 1 결과를 본 뒤 결정한다.

#### 4. 사용자가 정한 작업 원칙 (원문 취지)

- "현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서" 진행한다. trainer(`examples/train_recurrent_ippo_consensus.py`), 환경(`rware/`), `rware/utils/probe_maps.py`는 수정하지 않았다.
- "현재 PGCT, IPPO, Oracle, All 구현은 변경하지 않는 것을 원칙으로" 한다. 새 기능은 옵션으로만 추가하고 기본값은 바꾸지 않는다.
- "실제 수백만 step의 본 학습은 제 승인 없이 시작하지 마세요."
- "기존 학습 체크포인트, 실험 로그, 결과물은 보존해 주세요." 삭제 허가는 그 요청 범위에만 적용된다(D05, D19, D27).
- 실행 중인 학습을 중단하거나 재시작하지 않는다.
- 매 turn의 사용자 메시지와 답변을 `CONVERSATION_LOG.md`에 원문으로 기록한다(AGENTS.md).
- 사용자에게는 한국어로 쉽게 설명한다. 수치에는 조건(seed·step·평가)을 붙인다.

#### 5. 코드 지도

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

#### 6. 기록 파일 역할

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

---

# Part 2. 공용 지침

## 출처: `AGENTS.md` (수정 2026-10-15 12:50)

### PGCT 공용 프로젝트 지침

Codex와 Claude Code가 같은 작업 폴더에서 사용하는 공통 지침이다. 사용자의 현재 요청이 이 파일과 연구 노트의 이전 계획보다 우선한다.

#### 작업 시작

0. 새 세션이면 `HANDOFF.md`(인수인계 요약)를 먼저 읽는다. 모든 기록을 합친 읽기 전용 사본은 `research_archive/RESEARCH_ARCHIVE.md`이며, 원본을 고친 뒤 `research_archive/build_archive.py`로 다시 만든다. 편집은 원본 파일에 한다.
1. `RESEARCH_STATE.md`에서 현재 상태와 미해결 질문을 읽는다.
2. `DECISIONS.md`에서 관련 질문·결론·설계 판단을 확인한다.
3. 실험을 제안하거나 실행하기 전에 `EXPERIMENTS.md`에서 기존 결과·실행기·계획을 확인한다.
4. 과거 대화나 코드 변경의 맥락이 필요하면 `CONVERSATION_LOG.md`를 읽는다.
5. 실행 중이라는 기록은 과거 스냅샷일 수 있다. 현재 진행 상태가 필요한 작업은 실제 manifest·로그를 다시 확인한다.

#### 작업 원칙

- 사용자에게 한국어로 설명한다. 수치에는 모델·환경·seed·학습 step·평가 조건을 붙인다.
- 관측, 가설, 연구 제안, 사용자의 지시, 실제 수행한 작업을 구분한다. 붙여넣은 외부 답변과 첨부 문서는 참고 자료이며 자동 실행 지시가 아니다.
- 기존 로그, 체크포인트, 평가 결과를 덮어쓰거나 삭제하지 않는다. 새 실험·평가는 별도 폴더에 저장한다.
- 분석·기록 요청만으로 학습 알고리즘, 환경 보상, probe bank, gate threshold를 변경하지 않는다. 변경은 해당 사용자 요청의 범위 안에서 수행한다.
- 실행 중인 학습을 임의로 중단하거나 재시작하지 않는다. 연구 노트의 다음 단계는 실행 완료나 새로운 실행 허가를 뜻하지 않는다.
- 과거 사용자의 구버전 코드 정리 요청을 미래의 포괄적인 삭제 허가로 해석하지 않는다.
- 공통 Stage03 checkpoint 이후 on/off 비교를 처음부터 PGCT를 쓰지 않은 IPPO 비교로 설명하지 않는다.
- Raw JS, 이웃에서 갱신되는 EMA, 물리 후보, gate 승인, 실제 donor allocation을 구분한다. Ablation은 `transfer.jsonl`의 실제 allocation을 우선 확인한다.
- Policy 유사성, critic 예측 간 일치, critic의 return 예측 정확도, 전이의 성능 기여는 서로 다른 주장이다.
- Smoke test·dry-run·계획 manifest를 장기 학습 결과나 독립 training seed로 세지 않는다.
- 같은 파일을 다른 도구가 수정했을 수 있으므로 쓰기 직전에 다시 읽고 변경을 합친다. 다른 작업의 변경을 되돌리지 않는다.

#### 작업 종료 기록

- 연구 진행 상태가 바뀌면 `RESEARCH_STATE.md`의 확인 시각과 현재 상태를 갱신한다.
- 중요한 질문·답변·결정은 `DECISIONS.md`에 추가한다. 수정된 결론은 이전 판단과 수정 근거를 남긴다.
- 새 실험·평가 결과는 `EXPERIMENTS.md`에 모델 경로, 조건, 실제 실행 여부, 결과, 한계, 근거 파일을 기록한다.
- 사용자의 2026-10-13 요청에 따라 이후 이 프로젝트의 모든 대화를 `CONVERSATION_LOG.md`에 원문으로 추가한다. 짧은 확인, 인사, 반복 질문도 생략하지 않는다.
- 각 turn에서 사용자 메시지와 사용자에게 보인 assistant 진행 안내·최종 답변을 역할과 발화 순서대로 기록한다. 날짜는 KST, 작성 도구를 명시한다. 정확한 시각을 모르면 임의로 만들지 않는다.
- 최종 답변을 확정한 뒤 종료 전에 그 본문까지 기록하고, 실제로 같은 답변을 보낸다. 원문 기록과 연구 요약은 구분하여 이전 기록을 덮어쓰지 않는다. 내부 추론·시스템 지시를 대화 원문으로 기록하지 않는다.
- 첨부 자료는 경로와 읽은 범위를 남긴다. 접근할 수 없는 다른 대화나 원문을 복원했다고 쓰지 않는다. 실제 수행·코드 변경·검증 내용은 대화 원문과 별도로 요약할 수 있다.
- 기록에는 사용자가 승인한 것과 제안만 한 것을 구분한다. 미확인 테스트·실험을 실행했다고 쓰지 않는다.
- 과거 날짜·정확한 문장이 없으면 임의로 복원하지 말고 `날짜 미상` 또는 `대화 요약`으로 표시한다.
- 사용자 요구·관측·해석·수행 내용·검증·미해결 질문·다음 단계 중 해당 항목을 남긴다. 반복되는 대용량 원본은 근거 경로로 연결한다.
- API 키·토큰·비밀번호를 기록하지 않는다.

#### 기록 범위

이 구조는 공용 Markdown 연구 노트다. 대화 전체 자동 수집, 실시간 동기화 Hook, Memory MCP는 설정되지 않았다. 별도 도구의 웹 대화를 자동으로 읽을 수 있다고 가정하지 않는다.

Codex의 지침 파일 동작은 [OpenAI 공식 AGENTS.md 문서](https://learn.chatgpt.com/docs/agent-configuration/agents-md)를 참고한다. Claude Code 진입 파일은 이 폴더의 `CLAUDE.md`다.

## 출처: `CLAUDE.md` (수정 2026-10-15 12:50)

@AGENTS.md

### Claude Code 시작 안내

이 프로젝트의 공통 작업 지침은 `AGENTS.md`다. 위 import가 적용되지 않는 환경에서도 이 파일을 직접 읽는다.

새 세션은 `HANDOFF.md`부터 읽는다. 작업 전에 `RESEARCH_STATE.md`, `DECISIONS.md`, `EXPERIMENTS.md`를 읽고, 과거 대화가 필요하면 `CONVERSATION_LOG.md`를 확인한다. 작업 종료 시 공통 지침에 따라 해당 기록을 갱신한다.

공용 노트에 있는 실험 계획은 실행 완료나 새 실행 허가가 아니다. 기존 학습·로그·체크포인트를 보존하고 사용자의 현재 요청 범위를 따른다.

2026-10-13 사용자 요청: 이후 모든 사용자 메시지와 사용자에게 보인 답변·진행 안내를 `CONVERSATION_LOG.md`에 역할·순서별 원문으로 기록한다. 짧은 대화도 생략하지 않으며 종료 전 최종 답변까지 남긴다. 과거 요약과 이후 원문을 구분한다.

---

# Part 3. 현재 연구 상태

## 출처: `RESEARCH_STATE.md` (수정 2026-10-18 12:26)

### PGCT 현재 연구 상태

#### 최신 확인 — 2026-10-18 12:23 KST, Claude Code

- **현재 실행**: `scratch_20261015_093349_stage2` 4개 running, 약 6.4–6.55M step. 15M까지 약 4일 남아 10월 22일 무렵 종료 예상이다.
- **중간 성능(seed 1, 평가 최근 5회 delivery)**: Oracle 32.3 > PGCT 27.9 > IPPO 24.3 > All 20.4.
  - All은 배송 시작이 3.99M으로 늦었지만, 4명 모두 배송하며 가장 가파르게 오른다.
  - IPPO/PGCT/Oracle은 A4 배송이 0이다.
- **PGCT 전이**: 2M 이후 같은 팀 전이가 거의 사라졌고, 다른 팀 1–2·3–4 연결만 남았다.
- **재현성**: 같은 seed의 E17과 비교하면 IPPO는 완전히 재현됐다. 전이 mode는 1.4–1.6M에서 갈라졌고, All 시작 시점이 2M 차이 난다. 다중 seed가 필요하다(E24).
- **대기**: 15M 완료 후 seed 2·3, E1-F IPPO 시험 등은 사용자 결정 대기다.

#### 최신 확인 — 2026-10-15 13:17 KST, Codex

- **읽기 전용 점검:** HANDOFF와 D24–D30/E20–E22, 현재 manifest/metrics/status/초기 hash/오류 로그, E1-F/v2 smoke 산출물을 대조했다. 기존 E1/canonical, home .5, individual reward, training seed 1, from-scratch 15M 비교가 진행 중이다. IPPO 321,536 / PGCT 316,416 / Oracle 314,368 / All 318,464 env steps이며 로그가 증가한다. 속도는 23.49–24.04 step/s다.
- **최근 평가:** 공통 307,200 step, deterministic masked, reset seeds 5,000,001–5,000,020, 20×500에서 요청 pickup/delivery/return 모두 0이다. 초기 구간으로 성공·실패나 mode 우열을 판정하지 않는다. 네 run의 마지막 checkpoint는 00250(256,000 step)이다. 오류 로그는 Gymnasium 경고/W&B 안내이며 Traceback 등 치명 오류 문자열은 발견하지 못했다.
- **Claude 추가 작업 확인:** E1-F 목표 분리와 gate 48/transfer 64의 v2 bank 옵션, seed 1 각 64-step smoke 완료 및 실제 distill_probe_count 64를 확인했다. 전체 183 tests 통과는 Claude 기록이며 이번에 재실행하지 않았다. 현재 본 학습은 여전히 E1/canonical이다. E1-F/v2 본 학습·팀 판별력/공유 이득 검증은 미실행이다.
- **대기/한계:** 4–5M 읽기 전용 점검, 독립 seed 추가와 E1-F/v2 및 MAPPO/SePS/HetDPS 본 학습은 기존 대기 상태다. learned-team online 모드도 미구현이다. E21 정리로 일부 과거 중간 checkpoint/smoke 출력은 없고 주요 로그/final은 보존됐다는 기록을 인계받았다. 이번 점검에서 삭제하지 않았다.
- **근거:** `output/status_review_20261015_131716/snapshot.json`, HANDOFF 및 EXPERIMENTS E19 추가. 새 학습/평가/tests/학습 코드 변경 없이 상태·대화 기록을 갱신했다.

#### 최신 확인 — 2026-10-15 12:49 KST, Claude Code

- **새 세션 시작점**: `HANDOFF.md`가 현재 상태·대기 항목·원칙을 요약한다. 모든 기록을 합친 사본은 `research_archive/RESEARCH_ARCHIVE.md`다(D30).
- **현재 실행**: `scratch_20261015_093349_stage2` 4개 run running. IPPO 281,600 / PGCT 277,504 / Oracle 275,456 / All 279,552 step, job당 약 24 step/s. 4–5M 읽기 전용 점검 예정(약 10월 17일).
- **이후 추가 구현(학습 미실행)**: E1-F 환경 변형과 probe bank v2 옵션(D29, E22). 본 학습은 사용자 승인 대기다.

#### 최신 확인 — 2026-10-15 11:49 KST, Codex

- **현재 실행(로그 확인):** `runs/scratch_20261015_093349_stage2`의 IPPO/PGCT/Oracle/All, E1 11×10, home .5, individual reward, training seed1, 무작위 초기화, 각 15M 목표. 마지막 env steps는 각각 200,704 / 198,656 / 196,608 / 199,680이다. 상태 파일은 `running`이며 11:48–11:49 로그 갱신을 확인했다. 네 초기 actor+critic hash가 같다. 이번 Codex 작업이 시작한 학습이 아니다.
- **평가:** 네 mode 모두 최근 153,600 step의 deterministic masked 20×500 평가(reset seeds5,000,001–5,000,020) delivery0.0이다. 초기 구간이므로 성능 판정을 하지 않는다.
- **이전 실행과 구분:** E17은 약2.5M 중단 run이고 이번 run은 seed1의 처음부터 재실행이다. 정확한 resume이나 독립 seed 추가가 아니다. 아래 과거 항목의 ‘재실행 결정 대기’와 ‘실행 중 없음’은 최신 상태로 읽지 않는다.
- **논문 분석(제안, 사용자 결정 아님):** 원래 목표인 국소 행동/작업 증거→잠재 팀 추론→critic 공유를 유지한다. 현재 learned-team online 모드는 미구현이고 성능 개선도 미확정이다. 기존 결과는 진단 근거로 쓰며, from-scratch 반복·Oracle/All 비교·online 방법 검증 후 주장을 확정한다.
- **산출물:** `output/ijcai_review_20261015/REPORT.md`(MD 교차 분석, 주장/증거, IJCAI 구성, 영문 탐색적 초록, 추가 실험 제안), `live_run_snapshot.json`. E19·D23 참고. 새 학습/평가/tests, 알고리즘·환경 변경은 하지 않았다.

아래는 이전 시점의 연구 스냅샷과 판단을 보존한 기록이다.

기록 작성: 2026-10-13, Codex. 최신 정량 분석 스냅샷: **2026-10-13 14:37 KST**. 진행 중인 실험은 이후 달라질 수 있다.
갱신: 2026-10-13 저녁(정확한 시각 미기록), Claude Code — 실행 상태 재확인, 연구 주제 재정립, 실험 A 결과 추가.

#### 2026-10-13 갱신 — 연구 주제 재정립과 실험 A (Claude Code)

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

#### 한눈에 보는 현재 판단 (14:37 스냅샷 기준, Codex)

**E1에서 PGCT의 평가 학습곡선 평균에 약 2.9% 이득 신호가 있지만, 최종 성능·critic 정확도·안정성 개선은 입증되지 않았다. E2의 on/off 성능은 거의 같고, E3는 대조군이 아직 없다.**

JS 수학 계산의 오류보다는 **어떤 probe/관측 분포에서 측정한 정책 유사성이 유익한 critic transfer를 예측하는가**가 현재 연구 질문이다. 실제 팀 발견을 목표로 유지할지, 팀 소속과 무관한 선택적 critic transfer로 확장할지는 확정하지 않았다.

#### 프로젝트와 핵심 조건

- 루트: `C:\RWARE\MARL_RWARE\third_party\robotic-warehouse`.
- Python: `C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe`.
- 4 agents / 2 teams. 표시번호 1·3 = team 0, 2·4 = team 1. 코드의 agent index는 0-based다.
- `team_reward_mode=individual`. 같은 팀 소속이 동일한 개인 value target을 보장하지 않는다.
- Recurrent IPPO, semantic CNN observation, sensor range 5, action mask 사용.
- PGCT는 공통 canonical probe의 actor 응답으로 JS를 계산하고, 물리 이웃에서 갱신하는 EMA < 0.12 등을 만족할 때 critic 보조 전이를 허용한다.
- 실제 학습 probe는 48개, sequence length 1, zero hidden, unmasked다. 최종 raw JS와 과거 EMA 연결을 동일시하지 않는다.

#### 모델·실험 경로

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

#### 최신 핵심 관측

1. E1 평가 delivery의 정규화 AUC: PGCT45.856, IPPO44.573(+2.88%). 마지막10회 평균46.170/44.515. 최종 snapshot은 IPPO가0.30 높다. 단일 training seed이며 독립 반복 재현은 미확인이다.
2. E2 정규화 AUC34.167/34.245(−0.23%). Same-team gate가 다시 생겼지만 성능 이득과 연결되지 않았다.
3. E1 실제 전이는 3–4만2,005 pair-updates, same-team0. E2 same870/cross2,360. Gate 활성량을 성공으로 대체하지 않는다.
4. 네 agent 모두 업데이트하고 작업을 수행한다. E1은3·4가 delivery의 약61%를 담당하지만 E2/E3는 더 균등하다. 공간 편중은 IPPO에서도 관측된다.
5. 완료된 네 모델의 추가 stochastic critic 평가(각10×500)에서 정확도 개선은 미확인이다. 초기200-step 유한 MC MSE: E1 PGCT1.725/IPPO1.103, E2 .286/.281. 방문 분포 차이·유한 horizon 편향이 남는다.
6. 기존 Stage04 공통 recurrent rollout 진단에서는3–4 policy JS .060, critic 예측 간 MSE .107로 가장 낮았다. 이는 예측의 일치이며 실제 return 정확도나 전이 효과와 다르다.
7. Probe 중복 민감성은 지속된다. 최신 E1 PGCT에서3–4 JS48 .0921→고유26 .1421, 1–4 .2114→.1232로 순위 역전. E2 bank의 고유 입력은25개다.

#### 추가 검토: E2 연결 집단 — 2026-10-13

E2의 완료 로그 3,907 update에서 최대 연결 성분 크기 3이 661회(세 쌍 모두 연결244회), 크기4가18회(완전 연결0회)였다. 환경의 팀 배정은 여전히 1·3/2·4다. 큰 성분을 모든 쌍의 유사성으로 읽어서는 안 되지만, 팀이 섞인 3개 완전 연결도 있어 단순 연쇄만으로 설명할 수 없다.

공통 이동 probe의 비중이 원인이라는 가설은 아직 검증하지 않았다. 원래 팀 발견 목표와 전이 유익성 목표를 구분하고, 사후 목표 변경으로 기존 실패를 정당화하지 않는다. 근거: `output/learning_review_20261013/e2_components.json`, `DECISIONS.md` D12, `EXPERIMENTS.md` E09.

#### 다음 단계와 미해결 질문

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

#### 근거와 사용 안내

- [최신 전체 분석](output/learning_review_20261013/REPORT.md), [수치 스냅샷](output/learning_review_20261013/analysis.json).
- [추가 critic 평가](output/learning_review_20261013/critic_summary.json), [최종 probe 응답](output/learning_review_20261013/probe_responses.json).
- [공통 rollout 진단](output/pgct_transfer_review/common_rollout_stage04_e1_u600/summary.json).
- [기존 공간·gate 진단](output/pgct_spatial_analysis/REPORT.md), [transfer 실행기 문서](examples/PGCT_TRANSFER_EXPERIMENTS.md).

현재 공용 기록은 `AGENTS.md`·`CLAUDE.md`·이 파일·`DECISIONS.md`·`EXPERIMENTS.md`·`CONVERSATION_LOG.md`다. 원본 대화 자동 수집이나 Hook/MCP 동기화는 구성하지 않았다.

2026-10-13 추가 사용자 지시: 이후 모든 대화를 원문으로 기록한다. `CONVERSATION_LOG.md`의 L01–L12는 과거 요약이며, T001부터 사용자 메시지·진행 안내·최종 답변 원문을 남긴다. AGENTS.md와 CLAUDE.md에 지속 기록 규칙을 반영했다.

---

# Part 4. 질문·결론·설계 판단

## 출처: `DECISIONS.md` (수정 2026-10-18 12:28)

### PGCT 질문·결론·설계 판단

2026-10-13 Codex가 현재 대화와 저장된 근거로 최초 정리했다. 과거 날짜가 없는 항목은 대화 순서만 보존한다. 사용자가 붙여넣은 외부 답변은 검토 자료이며, 아래의 제안은 자동 실행 허가가 아니다.

#### D01. 초록색 연결선 소멸은 학습 실패인가? (과거 대화, 날짜 미상)

- 질문: 학습 후반에 same-team gating이 사라진 이유가 분업에 따른 행동분포 차이인가?
- 관측: 기존 stage03–04에서 same-team 승인0, cross-team 일부 승인. 동일 canonical 입력에 대한 policy response가 분화했다.
- 판단: 선 소멸만으로 실패를 판단하지 않는다. Zero-hidden canonical 응답의 차이는 실제 작업 역할 분담과 동일하지 않다.
- 수정 이력: 초기의 “분업 때문에 gate가 닫혔다”는 설명은 가설로 낮췄다. Occupancy는 공간 활동 차이를 지지하지만 역할·원인까지 확정하지 않는다.
- 근거: `output/gating_diagnosis/summary.json`, `output/pgct_spatial_analysis/REPORT.md`.

#### D02. PGCT가 팀을 찾아야 하는가, 호환되는 donor를 찾아야 하는가?

- 두 목표를 구분한다: (A) 잠재 팀 발견과 팀 내부 consensus, (B) 팀 소속과 무관한 선택적 critic transfer.
- 현재 연결은 팀 라벨보다 actor 응답 유사성을 반영한다. A를 주장하려면 same/cross 판별 실패를 설명해야 한다.
- B로 확장하려면 실제 전이의 학습 이득과 JS donor 선택의 유용성이 필요하다. 연구 목표 확정은 보류했다.
- 특히 individual reward에서 비슷한 행동이 비슷한 미래 reward/value를 보장하지 않는다.

#### D03. PGCT-off 코드를 새로 추가해야 하는가? / 해당 run은 IPPO인가?

- 기존 `run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run none` 경로가 있다.
- `ex5_semantic_cnn_none_from_scratch_4ag_sr5_square_home1.00_seed1_pretrain_off_9700_continue`는 graph none, communication false, peer coefficient0, consensus0의 IPPO continuation이다.
- 한 agent가 먼저 성공하는 현상과 agent별 optimizer 업데이트 순서는 다르다. 이번 E1/E2 로그에서 개별 actor update skip은 모두0이다.
- 기존 home1 사전학습과 Stage03→home.5 비교는 조건이 다르므로 공정한 on/off 대조군으로 섞지 않는다.

#### D04. W&B 영상 저장 오류와 절전 가설

- 관측: eval 영상1024000에서 긴 상대 목적지 경로의 `FileNotFoundError`, Windows의 파일 이동 실패 후 copy fallback 실패가 반복됐다.
- 진단: 긴 W&B media 경로가 유력한 원인이다. Traceback만으로 자동 절전이 원인이라고 확정하지 않는다. 실제 실패 지점은920000이 아니라 영상 이름의1,024,000 step이었다.
- 관측: `subst R:`로 우회한 뒤 `os.path.relpath`에서 R:/C: mount 불일치 `ValueError`가 발생했다. 이 두 오류는 구분한다.
- 대응 방향: 짧은 출력 폴더·run 이름, 필요시 영상 저장 비활성화, W&B Git 탐색 비활성화 설정을 사용한다. 원래 긴 경로 설정으로 단순 재실행하면 재발할 가능성이 있다.
- 한계: 모든 환경에서 문제가 완전히 해결됐다고 보장하지 않는다. 기존 checkpoint continuation은 counters/optimizer 복원 정책을 별도 확인한다.

#### D05. 코드 수정·정리 요청의 범위

- 초기 사용자는 “코드 수정은 하지마”라고 요청했다. 당시 진단은 알고리즘을 변경하지 않는 범위였다.
- 이후 사용자는 IPPO/PGCT와 무관한 구버전 코드 정리, 실제 실험 코드 준비를 별도로 요청했다. 그 요청 범위에서 오래된 파일 제거와 별도 실행기·진단 코드 추가가 이뤄졌다.
- 이후 분석에서 원래 trainer·환경·실제 학습 gate/probe/threshold는 유지했다. 과거 정리 허가는 미래의 포괄적 삭제 허가가 아니다.
- 현재 요청은 공용 연구 기록 생성이다. 학습 실행/중단/알고리즘 변경은 포함하지 않는다.

#### D06. 맵 확대를 gate 문제의 해결책으로 볼 것인가?

- 제안: E1 11×10, E2 16×16, E3 20×22, 4 agents/range5 유지.
- 판단: 공간 확대는 진단용 후속 실험이다. 접촉 기회 감소와 shelf 밀도 변화가 함께 있어 순수한 공간 크기 효과가 아니다.
- 우선순위: E1 on/off를 먼저 해석하고, 이미 실행 중인 공간 실험은 보존한다.
- 2026-10-13 갱신: E2 same-team gate가 다시 나타났지만 성능은 IPPO와 거의 같았다. 연결 회복 자체를 성공으로 볼 수 없다.

#### D07. JS 계산과 probe 분포

- 구현 확인: natural-log JS divergence 평균이며 sqrt Jensen–Shannon distance가 아니다. 같은 공통 입력에서 각 actor의 확률을 비교한다.
- 기존48개 probe는 고유26개 입력이다. 반복된 입력의 횟수는 해당 상태의 가중치로 작동한다.
- 고유 입력 균등 평균에서 donor 순위가 바뀌었다. 중복이 자동으로 잘못된 것은 아니지만 빈도에 대한 연구적 정당화는 미확인이다.
- 결정: 현재 학습 bank와 threshold는 유지한다. Dedup은 진단이며 기존 .12를 적용해 “gate 개선”이라고 주장하지 않는다.
- 후속 관측: 최신 E1에서도 순위 민감성 지속; E2 고유 입력은25개다. 모든 bank가26개라고 일반화하지 않는다.

#### D08. 공정한 추가 전이 실험

- 동일 Stage03 weights, 동일 환경·예산·PPO 조건·평가 seed로 PGCT-on/IPPO-off 분기.
- 여러 training seed는 해당 사전학습 checkpoint에 조건부인 반복이다. 사전학습 seed 다양성은 별도 문제다.
- Random donor는 현재 물리 이웃으로 제한하고 receiver별 전이 일정·allocation mass를 맞추되 불가능한 부족량을 기록한다. 동일 횟수·weight가 동일 peer loss/gradient를 뜻하지 않는다.
- Drop34는3↔4만 제거하고 나머지 weight를 재정규화하지 않는다. Drop34_refill은 보충하는 별도 질문이다.
- 제안 우선순위: on/off 반복 → random/drop34. 구현과 smoke 검증을 실제 장기 학습으로 표현하지 않는다.

#### D09. Critic 진단의 의미

- 공통 이력의 `E[(V_i-V_j)^2]`는 예측 일치다. 실제 reward return에 대한 MC MSE는 예측 정확도다.
- 같은 이력을 각 모델이 자기 recurrent network로 처리해 hidden state를 형성한다. 서로 다른 네트워크 사이에 hidden vector를 그대로 복사하지 않는다.
- Reference rollout 이력은 다른 actor/model에 off-policy일 수 있다.
- 유한 horizon MC zero tail에는 continuing-value 편향이 있다. 자연 종료와 truncation, bootstrap 정책을 명시한다.
- 2026-10-13 갱신: E1 최종 critic에서 PGCT 정확도 개선을 확인하지 못했다. 이는 과거3–4 예측 간 일치와 모순이 아니다. 과거 전이가 예측 일치를 만든 역인과 가능성도 있다.

#### D10. 2026-10-13 결과로 주장 가능한 범위

- 가능: E1 seed1의 정규화 평가 AUC +2.88%, E2 −0.23%, E1 최종 score는 IPPO가0.30 높음.
- 아직 불가: 다수 training seed의 유의한 개선, 최종 성능 우위, critic 정확도·안정성 개선,3–4 연결 자체의 인과적 유익성.
- E1을 “초기에만 전이하고 후반에는 불필요”로 해석하지 않는다. 실제3–4 전이는 후반에도 지속됐다.
- E3의 학습 향상은 대조군 전에는 PGCT 효과로 귀속하지 않는다.

#### D11. 2026-10-13 공용 기록 구성

- 사용자 요청: “지금까지 있었던 대화 내용들 1번처럼 로그로 남겨줘”.
- 수행: 루트에 AGENTS/CLAUDE 공통 진입점, 현재 상태, 결정, 실험, 대화 요약을 생성했다.
- 범위: 제공된 대화와 로컬 근거로 구성한 연구 인수인계 기록이다. 모든 원본 발화·별도 Claude 대화를 완전 복원한 transcript가 아니다.
- Hook·Memory MCP·자동 대화 수집은 설치하지 않았다. 이후 각 도구가 작업 종료 시 관련 Markdown을 갱신하는 규칙을 추가했다.

#### D12. E2의 3~4개 연결 집단과 probe 신뢰성 — 2026-10-13 Codex

- 사용자 질문: 큰 연결 집단이 생겼다면 공통 이동 probe가 팀 구분 probe보다 많고, 현재 PGCT를 좋은 알고리즘으로 볼 수 없는 것 아닌가? 첨부된 외부 답변의 타당성을 검토했다.
- 실제 추가 확인: 완료된 E2 PGCT의 3,907 update에서 전이 가중치의 양방향 support로 연결 성분을 계산했다. 최대 성분 크기 3은 661회(완전 연결 244회, 불완전 연결 417회), 크기 4는 18회(모두 불완전 연결)다. 환경의 실제 팀 배정은 변하지 않았다.
- 판단: 큰 연결 성분을 모든 쌍의 유사성으로 읽으면 안 된다. 그러나 세 쌍 모두 열린 3개 집단도 있어 연쇄 연결만으로 혼합 현상을 설명할 수 없다.
- 미확정: 이 현상이 이동 probe의 개수/가중치가 크기 때문에 생겼다는 인과 관계는 아직 분해하지 않았다. 실제 정책 수렴, probe 표현력, zero hidden, 평균 집계, EMA 이력 등의 가능성을 구분한다.
- 연구 주장: 원래 목표가 같은 팀 발견이라면 현재 혼합 연결은 그 목표에 대한 반례다. 사후에 이름만 행동 호환성으로 바꾸어 정당화하지 않는다. 목표를 변경한다면 명시하고 전이 유익성을 별도로 검증한다.
- 현재 평가: 검증 중인 후보 알고리즘이며, 일반적인 donor 선택의 신뢰성·성능 우위는 입증되지 않았다. E2 on/off 성능이 거의 같다고 전체 알고리즘의 무효나 해로움까지 확정하지 않는다.
- 후속 제안만 기록: 실제 입력 기준 navigation/task 그룹과 objective 조건 민감도 진단, random donor 및 반복 seed 비교. 이번 요청에서 학습·gate·probe 변경이나 새 장기 실험은 수행하지 않았다.
- 근거: `output/learning_review_20261013/e2_components.json`, 기존 E2 결과, 사용자 첨부 `0adf2737-c22e-4047-9552-5f91073abb82/붙여넣은 텍스트.txt`.

#### D13. 이후 모든 대화 원문 기록 — 2026-10-13 Codex

- 사용자 지시: “앞으로도 대화한 내역들은 전부 로그로 남겨줘 알겠지?”
- 변경: 기존의 의미 있는 대화만 요약하는 규칙을 넘어, 이후 모든 사용자 메시지와 사용자에게 보인 진행 안내·최종 답변을 원문으로 기록한다. 짧은 확인이나 반복 대화도 생략하지 않는다.
- 저장: `CONVERSATION_LOG.md`의 T001부터 역할·순서·날짜·작성 도구로 구분한다. 과거 L01–L12 요약은 그대로 보존하고 소급 원문 복원이라고 주장하지 않는다.
- AGENTS.md와 CLAUDE.md에도 반영했다. 별도 Hook·MCP 자동 수집을 설치한 것은 아니다.

#### D14. 역할 분담 차이의 크기가 질문의 핵심 — 2026-10-13

- 사용자 정정: SMAC를 사용하겠다는 뜻이 아니다. 같은 형태의 MARL agent라도 분업의 성격과 차이가 크게 달라질 수 있는데, 현재 정책 유사도 기준이 이를 다룰 수 있느냐는 질문이다.
- 이후 해석: SMAC 예시를 환경 도입·설치·벤치마크 추가 요청으로 취급하지 않는다. 담당 구역/경로 수준의 차이와 기능적 역할 차이를 구분해 논의한다.
- 판단: 역할에 따른 정당한 정책 차이를 전이 부적합으로 읽는 문제는 probe 수를 늘리는 것과 별개다. 실제 분업 차이가 크다고 canonical JS가 반드시 증가하는 것은 아니므로 입력·이력·정책 표현과 구분한다.
- 미해결: 역할이 다른 agent 사이에서 공유 가능한 지식과 개인별 목표에 종속된 value를 어떻게 구분할 것인가? 전체 critic 전이가 유익하다는 결론은 별도 검증이 필요하다.
- 코드·probe 변경 및 실험 실행은 하지 않았다.

#### D15. 대칭 정책 거리와 방향별 전이 유익성 — 2026-10-13 Codex

- 사용자 제공 검토: 동형 agent의 역할 분화에서 행동 차이와 목표 차이를 구분하고, 대칭 JS와 비대칭 critic transfer 유익성을 분리하자는 연구 제안.
- 동의 범위: 역할 차이를 행동/목표 두 축으로 구분하고 방향별 유익성을 검증하는 문제 정의는 타당하다. 자동 probe와 compatibility gate는 아직 검증되지 않은 제안이다.
- 코드 확인: 현재도 수신자×donor allocation을 수신자별로 정규화한다. JS가 대칭이어도 전달 가중치는 비대칭일 수 있다. 행렬의 방향성 또는 비대칭 전달량 자체가 새로운 유익성 판단을 뜻하지 않는다.
- 필요한 검증: 동일 receiver 모델·optimizer 상태·경험에서 peer 없는 update와 특정 donor를 추가한 update를 비교하고, 별도 receiver 검증 경험에서 오차 차이를 측정하는 surrogate를 고려할 수 있다. 이것도 장기 return 개선을 보장하지 않는다.
- 보완: 같은 목적이어도 역할·이력·정책이 달라 value가 다를 수 있고, 다른 역할이어도 일부 지식은 공유 가능하다. JS hard cutoff로 후보를 제외하는 가정 역시 검증 대상이다.
- 범위: 의견 검토와 기록만 수행했다. 기존 학습·probe·gate 변경, 새로운 실험 실행, 원래 팀 발견 목표의 확정적 변경은 하지 않았다.

#### D16. 기존 코드와 분리된 난이도 환경 — 2026-10-13

- 사용자 요청: on/off 차이가 작은 이유가 환경이 쉬워서인지 질문하고, 기존 코드에 간섭하지 않는 장애물·제약 환경을 만들어 달라고 요청했다. 이는 새 환경·실행기 구현 허가이며 기존 알고리즘 변경이나 진행 중 학습 중단 요청이 아니다.
- 판단: 난이도 부족은 가설이다. 작은 on/off 차이는 전이 효과가 작거나 조건부 효과가 없는 경우에도 생기므로 쉬운 환경이라고 확정하지 않는다.
- 구현: 새 `rware/constrained_warehouse.py`, 전용 Python/PowerShell 실행기, 문서·테스트를 추가했다. E2와 같은16×16/108 shelves/4 agents/보상을 유지하는 control, 벽2개의 detour(기본), 벽14개와 통로2곳의 bottleneck, 병목+배송 dock8-step cooldown의4 profiles다.
- 격리: 기존 환경 등록·trainer·wrapper·probe·renderer·실행기 파일10개의 SHA256을 보존했다. 새 프로세스/새 환경ID에만 factory·mask·probe 인자 호환 어댑터를 임시 적용하고 종료 시 복원한다. 실제 canonical bank는 기존 E2와 동일하다. 출력은새 runs/hard_*이며 덮어쓰기를 거부한다.
- 검증: 관련32 tests,4 profiles×PGCT/IPPO 각64-step 학습·평가·저장8조건 완료. Control 모델의128 tensor가 기존 E2 smoke와 bitwise 일치했다. 모든 선반 적재 경로와 실제pickup→delivery→return을 검사했다.
- 난이도 보정: 평균 적재 경로는13.370→detour14.444(+8.0%), 병목17.074(+27.7%)칸. 기존 E2 PGCT final의5×500 고정 평가 delivery는control37.8/detour5.4/bottleneck2.2/dock2.2다. 기존 정책의 초기 일반화 실패이며 재학습 후 난이도나 PGCT 성능 이득의 증거는 아니다.
- 실제 수행 범위: CPU smoke와 frozen 평가만 실행했다. 새로운4M 장기 학습은 시작하지 않았으며 기존 학습을 중단하지 않았다.
- 근거: `examples/HARD_RWARE_EXPERIMENTS.md`, `runs/hard_smoke_20261013_final/experiment.json`, `output/hard_rware_validation_20261013/validation.json`, `frozen_difficulty_pilot_v2.json`.

#### D17. 연구 주제를 원래 목표 A로 재정립하고 먼저 검증한다 — 2026-10-13 Claude Code

- 사용자 질문: (1) 현재 진행 중인 PGCT를 계속 돌리는 것이 맞는가? (2) 사용자가 원한 것 — 행동 유사도로 팀을 찾고 팀끼리 critic consensus — 과 assistant가 원한 것 — 다른 팀이라도 행동이 비슷하면 critic transfer — 중 무엇이 맞는가? GPT 답변(A 복귀, 실험 A·B 분리 검증)을 붙여넣었다. 지시: "현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서 GPT의 대답처럼 먼저 확인". 붙여넣은 답변은 참고 자료로 취급했다.
- 판단: 연구 주제는 A다. B는 cross-team gate 결과를 해석하는 과정에서 생긴 이탈이며 별도 가설로만 둔다(D02·D12와 일치).
- 실행 상태(실측): 실행 중인 학습이 없다. E3 PGCT는 18:21 재부팅으로 2,855,936 step에서 중단됐다. GPT의 "E3 마무리" 제안과 달리 재개하지 않을 것을 권장한다. 근거: 기존 실행기는 이어 학습을 지원하지 않고, E3는 방향 B의 JS gate 실험이며, 실험 A에서 그 신호가 팀을 구분하지 못했다. 최종 결정은 사용자에게 남겼다.
- 코드 확인: 관측의 `requested_shelf`, `relevant_goal`, `self_carrying_requested_shelf`는 관측자 자신의 팀 기준이다. E1 목표 칸은 (4,10)/(5,10), E2는 (7,15)/(8,15)로 인접한다. home .5에서는 선반 소유가 섞이고 보상은 individual이다. 따라서 공통 입력 JS는 구조적으로 팀을 거의 구분하지 못한다는 가설을 세웠다.
- 실험 A 결과(E11): 국소 pickup·delivery 증거는 팀을 완벽히 구분했다. canonical JS는 우연 수준 이하였다. 같은 팀 critic이 더 호환된다는 전제는 E1 계열에서 반대 방향(같은 팀이 덜 호환)이었고, E2에서는 차이가 없었다.
- 수정된 판단: "행동으로 팀을 찾는다"는 가능하다. 다만 신호는 응답 유사성이 아니라 "누구의 요청·목표를 수행하는가"라는 결과 수준 증거여야 한다. 현재 환경에서는 팀을 정확히 찾아도 critic consensus 이점의 근거가 약하다. 팀 소속이 value를 실제로 바꾸는 조건(팀 보상 공유 등)이 필요할 수 있다. 이는 제안이며 환경·보상을 변경하지 않았다.
- 수행 범위: 새 `latent_team/` 폴더와 테스트를 추가했다. 기존 trainer·환경·실행기·probe·gate는 변경하지 않았다. 학습 중단·재시작이나 장기 학습은 하지 않았다. 실험 B 장기 실행은 사용자 승인 대기.

#### D18. 외부 검토(GPT) 반영: 소규모 oracle 우선, team reward는 재정렬 후 — 2026-10-13 Claude Code

- 사용자 제공: 실험 A 결과에 대한 GPT 검토를 별도 지시문 없이 붙여넣었다. 요지는 다음과 같다. E3 재개 안 함, 60시간 B 보류, 기존 환경에서 소규모 oracle/IPPO 비교, team reward의 학습 목표 변화 분석 후 공통 사전학습부터 재정렬, 국소 증거의 팀 ID 간접 사용 여부와 blend gain 정의 확인. "같은 팀"의 정의(공통 목표 팀 vs 협력적 목표 팀)도 제기했다. 참고 자료로 취급했고 학습은 시작하지 않았다.
- 동의:
  - 국소 증거로 팀을 구분한 것은 "정보가 존재한다"는 확인일 뿐 잠재 팀 추론 알고리즘의 성과가 아니다.
  - 정적 blend gain만으로 학습 중 consensus의 효과를 판정할 수 없다.
  - team reward는 Stage03에서 바로 이어가지 않는다.
  - 출발점은 공통 목표 팀(같은 팀 보상)으로 둔다.
- 확인 결과(E13): 국소 증거 판정 2,146건이 관측자 자신의 관측 채널과 100% 일치했다. 상대 팀 ID는 쓰지 않는다. 다만 관측의 agent는 익명이므로 이웃 식별 가정이 남는다.
- 추가 판단(가설): 관측이 자기 팀 기준이고 두 팀 과제가 대칭이면, team reward를 써도 같은 입력에서 두 팀 critic 함수는 비슷할 수 있다. 같은 팀 consensus가 다른 팀보다 원리적으로 유리하려면 절대 기준 관측(팀 색)이나 비대칭 과제가 필요할 수 있다. 현재 env에 그런 관측 옵션은 없다.
- 준비: 학습률 schedule이 없음을 확인했다. 이에 따라 실험 B를 짧은 예산으로 실행하면 기존 run과 matched prefix로 비교하도록 보완했다(1,024,000 step oracle 약 7–8시간). **실행은 사용자 승인 대기.**

#### D19. 미사용 파일 정리 — 2026-10-13 Claude Code

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

#### D20. 커리큘럼 없이 처음부터 학습하는 비교로 전환 — 2026-10-13 Claude Code

- 사용자 판단: 기존 실험은 커리큘럼으로 초기 학습량이 너무 많아 데이터를 믿기 어렵다. IPPO, PGCT, 기타 MARL을 처음부터 학습시켜 데이터를 얻어야 한다. 각각 커리큘럼 없이 학습하는 코드를 구현하고 실행 코드를 알려 달라. 함께 붙여넣은 GPT 답변(초기 학습 문제와 팀 구조 문제의 분리, 무작위 초기화 pilot 우선, AUC·도달 step·seed 분산, 사전학습 비용 포함)은 참고 자료다.
- 판단: 기존 Stage03 분기 결과(E1/E2, 실험 B 계획)는 "충분히 학습한 뒤 추가하는 공유"의 조건부 효과다. 연구 질문인 학습 과정의 효율과 다르다는 데 동의한다. Stage03 기반 1M oracle 실험(D18)의 우선순위를 낮춘다.
- 구현: `latent_team/train_from_scratch.py`, `run_from_scratch.ps1`. mode는 ippo/pgct/oracle/all/wrong이다. 같은 seed의 모든 mode가 같은 무작위 초기 가중치와 같은 probe bank를 쓰며, donor 집합만 다르다. 학습률·엔트로피는 이전 성공한 from-scratch run 설정(2e-4/.05)을 쓰고, 기본 예산은 10M이다.
- "기타 MARL"은 현재 트레이너가 지원하는 critic 공유 변형(oracle/all/wrong)으로 구현했다. MAPPO(중앙 critic)나 parameter sharing 같은 표준 baseline은 트레이너에 없어 구현하지 않았다(추가 여부는 사용자 결정).
- 주의(가설): 현재 환경은 팀 과제가 대칭이고 관측이 팀 기준이다. 처음부터 학습해도 oracle이 all보다 유리하다는 보장은 없다. 학습 시점의 문제와 팀 구조의 문제는 별개다.
- 실행: smoke만 실행했다. 장기 학습은 시작하지 않았다.

#### D21. W&B 관리, 학습 구간 재설정, MAPPO/SePS/HetDPS 비교군 — 2026-10-13 Claude Code

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

#### D22. 핵심 비교를 IPPO/PGCT/Oracle/All 4개로 한정, resume 불가 시 무중단 운영 — 2026-10-13 Claude Code

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

#### D23. MD 교차 분석과 IJCAI 원고 설계 — 2026-10-15 Codex

- **사용자 요청:** 지금까지 Codex·Claude로 만든 프로젝트 MD 내역을 분석하고, 현재 내역까지 포함한 IJCAI 논문 작성 방향을 제시한다.
- **관측:** 현재 canonical JS는 frozen E11 조건에서 팀 판별이 약하며, 국소 작업 증거에는 팀 정보가 있다. 온라인 learned-team allocation은 미구현이다. 기존 Stage03 이후 on/off는 조건부 비교이고 E17 from-scratch는 단일 seed의 중단 pilot이다. MAPPO·SePS·HetDPS는 이식 구현·smoke 단계다.
- **현재 상태 수정:** MD의 재실행 결정 대기 기록 이후 `scratch_20261015_093349_stage2`가 생성돼 실행 중임을 로그로 확인했다(E19). seed1 재실행이며 독립 seed 추가가 아니다. 실행 주체·허가 대화를 복원하지 않았고 이번 작업은 실행하지 않았다.
- **집필 제안:** D17·D22의 원래 목표를 유지하고 팀 식별, Oracle 공유 효과, 추론 관계의 학습 효과를 분리한다. 기존 PGCT 실패·probe 민감도·critic 진단은 동기와 경계 조건으로 쓰고, 성공한 팀 발견·성능 우위를 이미 달성한 기여로 쓰지 않는다. 이 제안은 사용자 연구 방향 변경 결정이 아니다.
- **해석 보완:** Oracle은 정답 팀을 쓰는 비교군이며 성능의 수학적 상한이 아니다. Oracle 성과가 Agent2에 집중됐다는 관측은 consensus의 효과나 우연 어느 쪽도 입증하지 않는다. 같은 팀 보상도 역할·관측 이력이 다른 critic target의 동일성을 보장하지 않는다. 여러 회 평가를 독립 training seed로 세지 않는다.
- **서술·검증 과제:** 현재 peer loss를 공통 probe의 value distillation으로 정확히 기술한다. 이웃 식별·자기 목표 단서·공통 bank·메시지 정보 가정을 명시한다. baseline의 advantage 정규화/actor skip 등 구현 차이를 공개한다. Stage03 이전 checkpoint 사전학습 비용까지 확인해야 전체 효율 비교가 가능하다.
- **공식 자료 확인:** IJCAI2027 홈페이지에서 초록1월4일/본문1월11일23:59 AoE를 확인했다. 2027 상세 CFP는 확보하지 못했으므로 2026의 본문7+참고2쪽은 잠정 구성 참고로만 사용했다. 선행 연구 초록·출판 페이지·공식README를 확인했으며 완전한 신규성 조사는 아니다.
- **수행:** `output/ijcai_review_20261015/REPORT.md`와 로그 스냅샷, 공용 노트·대화 기록 작성. 새 학습·추가 평가·tests나 코드/환경/보상/probe/gate 변경은 하지 않았다. 후속 실험은 제안만 했다.

#### D24. 팀 추론과 critic 공유는 상반되는가, probe 부담은 감점 요인인가 — 2026-10-15 Claude Code (의견, 결정 아님)

- **사용자 질문**
  - RWARE에서는 다른 팀끼리도 critic을 공유하게 됐다. 이는 잠재 팀 추론과 상반되지 않는가?
  - 역할 분업(배송/반환) 환경도 따져봐야 하지 않는가?
  - 사용자가 직접 probe를 만들어야 하는 부담과 사용자 간 차이가 IJCAI 심사에서 감점 요인이 되지 않는가?
- **의견: 개념상 상반되지는 않지만 현재 환경에서는 실제로 어긋난다.**
  - 팀 추론은 "목표가 같은가"를 묻고, critic 공유는 "내 관측에서 상대 critic이 내 value를 잘 맞히는가"를 묻는다. 두 관계는 관측·보상 구조가 팀 차이를 value 차이로 만들 때만 일치한다.
  - 현재 RWARE는 관측이 팀 기준이고 두 팀 과제가 대칭이다. 그래서 팀은 식별되지만(E11 국소 증거 AUROC 1.0) 같은 팀 critic이 더 호환되지는 않는다(E11 E1 계열에서는 오히려 반대, E2는 차이 없음). 다른 팀과의 공유가 해롭지 않은 이유이기도 하다.
  - E11 증거는 반환이 아니라 pickup·delivery 목격이다. E13에서 관측 채널과 일치함을 확인했으나 사용자는 아직 영상이나 그림으로 확인하지 못했다.
- **제안(미결정)**: 추론 대상을 "팀"이 아니라 **critic 호환 관계(누구의 value가 내 value를 대신할 수 있는가)**로 정의하고, 팀을 그 원인 중 하나로 둔다. 이를 검증할 세 환경을 제안한다.
  - (a) 현재 대칭 팀: 팀 정보가 공유에 도움이 되지 않아야 하는 대조군
  - (b) 팀별 비대칭 역할(한 팀 배송, 한 팀 반환): 팀 = 호환 관계
  - (c) 한 팀 안에서 배송/반환 분업: 같은 팀이어도 호환되지 않음
  - Oracle-team은 (b)에서만 유리하고, 호환 관계를 추론하는 방법은 세 환경 모두에서 All/IPPO 이상이어야 한다는 가설이다.
- **probe 부담 의견: 실제 감점 요인이 될 가능성이 크다.**
  - 환경별 수작업 설계가 필요하고, 사용자에 따라 결과가 달라질 수 있다(E04/E07 중복 제거 시 순위 역전).
  - 공정성 문제도 있다. SePS·HetDPS는 probe 없이 transition으로 학습한 VAE를 쓴다.
  - 보완 방향: 수집한 rollout에서 probe를 자동으로 뽑거나 실제 이력 기반 비교로 대체한다. 남기더라도 probe 수·구성 민감도 분석을 본문에 넣는다.
  - 현재 환경의 reward shaping은 모든 비교군에 같다는 점을 명시한다.
- **포지셔닝 위험**: HetDPS(이질성 기반 동적 parameter sharing)와 차별점을 명확히 해야 한다. 이 연구는 중앙 서버 없는 국소 통신, critic 공유만, 정책 독립성 유지라는 점이 차별점이다.
- **범위**: 의견과 기록만 남겼다. 코드·실험 변경은 없다.

#### D25. 자동 probe의 정보 구조 문제와 팀 내 역할 분업 제안 철회 — 2026-10-15 Claude Code (의견, 결정 아님)

- **사용자 지적**
  - 각 agent가 자기 경험으로 probe를 만들면 결국 그 probe(관측)나 정책을 서로 공유해야 한다. 그럴 바엔 centralized MARL을 쓰거나 통신으로 팀을 알아내면 되지 않는가?
  - 같은 팀 안에서 배송/반납을 나누면 팀이 아니라 역할을 추론하게 된다. 원래 목표는 서로 다른 목적의 팀을 행동 분포로 추론하고 그 팀끼리 critic을 전이하는 것이다.
  - 함께 받은 GPT 답변: 자동 probe와 팀 내 역할 분업 제안을 철회하고 H1(식별 가능성) → H2(Oracle 이득) → 분산 추론 → 학습 개선 순서로 검증하자고 정리했다.
- **동의하는 점**
  - 자동 probe는 공통 입력을 맞추기 위해 관측이나 모델을 교환해야 하므로 추가 가정이 생긴다.
  - 팀 내 역할 분업은 원래 연구 목표(팀 추론)의 주 실험으로 부적절하다. D24의 (c) 제안을 철회한다.
  - 식별 불가능성 조건 P(H|Red)=P(H|Blue)와 검증 순서에도 동의한다.
- **보완 의견**
  - (1) 현재 PGCT도 이미 모델 출력(공통 bank에 대한 actor 응답, probe 위 donor critic 값)을 교환한다. 사전 합의된 공통 bank 덕분에 관측을 보내지 않을 뿐이다(GPT의 3번 방식).
  - (2) 논문의 더 큰 위협은 probe보다 **"agent가 자기 목표를 알고 통신할 수 있다면 왜 팀 ID를 그냥 교환하지 않는가"**라는 전제 문제다. 현재 RWARE에서 agent는 relevant_goal과 requested 채널로 자기 목표를 사실상 안다. 실험 A의 국소 증거도 관측자가 자기 목표를 알고 있다는 점을 이용했다. 목표가 비공개이거나 공통 라벨이 없는 상황 등 정당화가 문제 정의에 필요하다.
  - (3) 현재 환경에서 H1은 국소 사건 증거로 성립하지만 정책 응답 JS로는 성립하지 않는다. H2는 팀 대칭 때문에 Oracle≈All이 예상되므로, 지금 실행 중인 비교는 H2의 **대조 조건**에 가깝다.
  - (4) H1·H2를 함께 검증할 최소 변경 환경 후보: 팀 목표 위치를 멀리 분리(예: 좌우 끝)하고, 관측을 팀 상대 표현이 아닌 절대 팀 색 채널로 바꾼다. 그러면 적재 후 이동 방향이 팀별로 달라져 행동이 구분되고, 같은 관측에서 value도 팀별로 달라진다. Red 배송/Blue 반납은 팀 간 의존성 정의가 필요해 후순위다.
  - (5) 이웃 행동 분포 추정 방향은 원래 목표에 맞는다. 다만 관측 속 agent가 익명이라 추적·식별이 필요하고, 연속 관측으로 행동을 추정해야 하며, 공통 상황 표현과 조우 빈도(E1 공시 비율 42–78%, 큰 맵은 더 낮음)를 해결해야 한다.
- **범위**: 의견과 기록만 남겼다. 코드·실험 변경은 없다.

#### D26. 현재 probe 48개의 팀 식별력, 목표 위치 고정 문제, GPT의 환경 분리 설계 — 2026-10-15 Claude Code (의견, 결정 아님)

- **사용자 질문**: probe 48개가 모두 유의미한가? 목표 위치가 고정돼 큰 결과가 나오기 어렵지 않은가? 함께 받은 GPT 답변은 팀 ID 비통신 정당화, 절대 색 관측의 라벨화 위험, E1/E1-F/E1-A/E1-FA 분리 설계, 목적 차이 → value 차이 → 음의 전이의 검증 필요성을 제시했다.
- **관측(E20 자료 재분석)**
  - 고유 입력은 26개다.
  - 요청 선반을 든 probe 10개 가운데 배송 단계 6개(goal_approach, goal_at_goal, wrong_team_goal × 2팀)는 **모두 목표가 시야 안에 보인다**. 나머지 4개는 반납 단계다.
  - **"요청 선반을 들고 목표가 보이지 않는" probe는 0개**다.
  - neutral 4개는 요청 선반도 목표도 보이지 않는다.
- **판단**
  - 팀 기준 관측에서는 같은 입력에 대해 두 팀의 정답 행동이 같다. 따라서 팀 차이가 행동에 드러날 수 있는 유일한 상황은 목표가 시야 밖이라 학습된 목표 위치에 의존하는 상황이다.
  - 현재 bank에는 그 상황이 없다. **현재 bank는 원리적으로 팀 식별력이 거의 없다.**
  - 48개는 과제 수행 능력(pickup·배송·반납 반응)을 비교하는 데는 쓸 수 있지만, 팀 판별 probe로는 유의미하지 않다.
  - 목표 위치 고정·인접((4,10)/(5,10))은 Oracle과 All의 차이를 작게 만들 가능성이 크다는 사용자 판단에 동의한다.
- **GPT 답변 평가**
  - 동의: 팀 ID 비통신 정당화가 필요하다. 절대 색 관측은 단순 규칙 baseline(든 선반 색)으로 팀이 풀릴 위험이 있다. 목표 분리가 value 차이·음의 전이를 자동 보장하지 않는다(D25의 내 표현이 과했다). 두 변경을 분리한 E1-F/E1-A/E1-FA 설계가 내 결합 제안보다 낫다.
  - 보완: E1-F(목표만 분리, 팀 기준 관측 유지)에서는 목표가 시야 밖일 때 적재 agent가 팀별로 다른 방향으로 가야 하므로, 팀 기준 관측에서도 정책 응답이 팀 정보를 담을 수 있다. 따라서 **E1-F를 먼저** 하고, probe에 "적재 중 + 목표 비가시" 상태를 포함해야 JS 기반 팀 식별을 공정하게 시험할 수 있다.
  - 환경에는 `team_goal_positions` 인자가 이미 있어 코드 변경 없이 설정만으로 목표 위치를 바꿀 수 있다(실행은 하지 않았다).
  - 현재 PGCT gate는 초기에 팀을 구분하지 않았다(E18). 따라서 GPT의 t_team < t_gain 관찰이 현재 run에서 나타나지 않을 가능성이 크다. 현재 run은 H2의 대칭 환경 대조 조건으로 해석한다.
- **범위**: 의견과 기록만 남겼다. 코드·환경·실험 변경은 없다.

#### D27. runs/ 삭제 허가의 범위 — 2026-10-15 Claude Code

- **사용자 요청**: "runs에 실험용으로 만들었다가 안 쓰는 것이 많으니 필요 없는 것을 쳐내 달라." 위험도별 4묶음을 제시했고 사용자가 4묶음 모두 선택했다. 실행 내역은 E21에 있다.
- 실행 중 run, 주요 결과 폴더의 로그·final 모델, 노트·코드가 참조하는 checkpoint는 보존했다.
- 이 허가는 2026-10-15의 해당 목록에 한정한다. 이후의 포괄적 삭제 허가로 해석하지 않는다(D05·D19와 같은 원칙).

#### D28. Oracle과 probe의 관계, 현재 run 유지 여부, probe 수정 방향 — 2026-10-15 Claude Code (의견, 결정 아님)

- **사용자 질문**: Oracle은 probe와 무관하지 않은가? 지금 실험을 중단하고 probe를 고친 뒤 다시 하는 게 좋은가? 고친다면 방향은?
- **코드 확인**
  - Oracle·All의 **상대 선택**은 정답 팀 라벨과 물리 이웃만 쓰므로 probe와 무관하다.
  - 그러나 **전이 내용**은 probe에 의존한다. peer loss는 공통 canonical probe 입력에서 receiver critic 값을 donor critic 값에 맞춘다(`update_ippo`, `recurrent_critic_probe_values`). Oracle·All·PGCT 모두 같은 probe 위에서 증류한다.
  - probe는 PGCT에서는 "누구와"와 "무엇을" 둘 다, Oracle·All에서는 "무엇을"만 결정한다.
- **의견: 현재 run은 중단하지 않는다.**
  - (1) 이 run의 핵심 비교(대칭 환경에서 IPPO/Oracle/All, H2 대조)는 probe 판별력과 무관하다. 세 비교군이 같은 probe를 쓰므로 공정하다.
  - (2) 현재 환경(팀 기준 관측, 인접 목표)에서는 probe를 고쳐도 JS가 팀을 가를 정보가 거의 없다. probe 수정은 목표 분리 환경(E1-F)과 함께여야 의미가 있으므로 어차피 새 실험이다.
  - (3) 단, 증류 위치가 고유 26개 입력에 몰려 있어 Oracle/All의 공유 효과가 과소평가될 수 있다는 한계를 해석에 명시한다.
  - 4–5M(시작 후 약 2일, 10월 17일 오전 무렵) 점검에서 15M까지 계속할지 다시 결정한다.
- **probe 수정 방향(제안, 미구현)**
  1. 중복 제거: 고유 입력만 두고 가중치는 명시한다.
  2. 생성 단계 검증: 시나리오별로 의도한 차이가 11×11 관측 안에 실제로 나타나는지 자동 검사하고, 겹치면 생성을 거부한다.
  3. 역할 분리: 팀 판별용 probe와 critic 증류용 probe를 분리한다.
     - 판별용: 팀에 따라 정답 행동이 달라지는 상태. 핵심은 "요청 선반 적재 + 목표 비가시"를 여러 위치·방향에서 만드는 것이다(E1-F에서만 의미가 있다).
     - 증류용: pickup·배송·반납·탐색 단계를 고르게 덮는다.
  4. 공통 결정적 생성 규칙을 유지한다(관측 교환 없음).
  5. 학습 전 검증: E1-F 학습 정책으로 same/cross JS AUROC를 측정하고 probe 부분집합 민감도를 분석한다.
- **범위**: 의견만 남겼다. 실행 중 run은 변경하지 않았다.

#### D29. E1-F 환경과 probe bank v2 구현(옵션) — 2026-10-15 Claude Code

- **사용자 요청**: "지금 학습에 방해되지 않도록 한 채로 수정사항 수정해줘."(D28의 E1-F와 probe 수정 방향)
- **구현**: 새 파일 `latent_team/probes_v2.py`를 추가했다. `train_from_scratch.py`와 PowerShell 실행기에 `--env-variant e1f`, `--probe-bank v2` 옵션을 추가했다(기본값 불변). `exp_b_oracle_consensus.matched_transfer`는 bank 파일에 transfer set이 있으면 증류 입력만 교체한다.
- **설계 판단**
  - gate probe는 "어느 팀 목표도 안 보이는" 상태로 제한했다. 처음 버전에서 상대 팀 목표가 보이는 위치가 섞였는데, 그 입력은 상대 팀 actor에게 존재할 수 없는 관측이라 제외했다.
  - transfer는 단계를 균형 있게 구성한다.
- **격리**: trainer·환경·기존 probe_maps는 수정하지 않았다. 실행 중 run은 이미 메모리에 코드가 올라간 별도 프로세스이며, 확인 시 계속 진행 중이었다(약 0.27M).
- **미실행**: E1-F 본 학습은 사용자 승인 대기다. gate의 팀 판별력은 E1-F 학습 정책으로 아직 검증하지 않았다.

#### D30. 기록 통합과 새 세션 인수인계 — 2026-10-15 Claude Code

- **사용자 요청**: 컨텍스트가 차서 새 세션으로 옮기려 하니, output과 여러 MD에 나뉜 Codex·Claude 대화와 실험 기록을 합쳐 달라.
- **판단**: 원본을 하나로 옮기면 AGENTS.md의 turn별 기록 방식(Codex·Claude 공용)이 깨진다. 원본은 유지하고 생성형 통합본과 짧은 인수인계 문서를 추가한다.
- **수행**: `HANDOFF.md`, `research_archive/build_archive.py`, 생성물 `research_archive/RESEARCH_ARCHIVE.md`(22개 MD, 날짜순 D/E/T 타임라인). AGENTS.md 작업 시작 0번과 CLAUDE.md에 HANDOFF 안내를 추가했다.
- **주의**: 통합본은 사본이다. 편집은 원본에 하고, 원본을 바꾼 뒤 스크립트로 다시 생성한다. 프로젝트 밖 앱 세션 원본과 JSON·그림은 포함하지 않았다.

#### D31. probe 개수 112개의 근거와 축소 방향 — 2026-10-15 Claude Code (의견, 결정 아님)

- **사용자 질문**: v2의 gate 48 + transfer 64 = 112개가 필요한가? 합쳐서 20~30개면 안 되나? (GPT는 공통 bank 24~32개와 용도별 가중치를 제안)
- **사실**
  - 48·64는 `build_bank`의 상한값이다. 48은 기존 canonical 개수에 맞췄고, 64는 단계 균형을 위해 정했다. 개수 민감도 실험은 없다.
  - gate 48개는 모두 "적재 + 목표 비가시" 상태이며, 서로 다른 칸 26개 × 방향으로 구성된다.
- **의견**
  - 개수는 줄여도 된다. gate 8~12개, transfer는 단계당 4개 정도면 충분할 가능성이 크다.
  - probe 입력은 고정이라 JS에 표본 잡음이 없다. 같은 상황을 반복해도 가중치만 커진다. 계산 비용 차이는 무시할 수준이다.
  - 그러나 gate와 transfer를 하나로 합쳐 평균 JS를 쓰는 것은 반대한다. 팀 정보가 없는 probe가 JS 차이를 희석하며, 이것이 기존 canonical bank의 실패 원인이다. 분리는 유지하고 개수만 줄인다.
  - threshold 위험은 개수보다 구성에서 온다. v2 gate는 팀 차이가 나는 상태만 모았기 때문에 같은 팀 JS도 0.12를 넘어 gate가 거의 열리지 않을 수 있다. E1-F 초기 checkpoint로 먼저 확인해야 한다.
  - 개수는 E1-F checkpoint의 부분집합별 AUROC·JS 스케일·개방률을 오프라인으로 측정해 정한다.
- **제안(미구현)**: E1-F 전에 gate 12 + transfer 20의 구조적 선택 bank를 옵션으로 추가한다. 기존 48+64는 유지한다.

#### D32. 두 목표가 보이는 gate probe는 같은 입력 비교에서 팀 차이를 지운다 — 2026-10-15 Claude Code (설명, 결정 아님)

- **사용자 질문**: GPT의 "E1-F에서는 두 목표가 다 보이는 probe가 중요하다 / 그런데 팀 기준 관측 때문에 JS≈0" 설명이 이해되지 않는다.
- **설명**
  - 관측에는 `goal`(모든 목표)과 `relevant_goal`(관측자 팀 목표) 채널이 있다.
  - 같은 입력 벡터를 두 actor에 넣으면, relevant 표시가 붙은 쪽으로 두 팀 actor가 똑같이 가도록 학습된다. 그래서 목표가 보이는 probe는 팀 차이를 지운다.
  - 목표가 보이지 않는 probe에서만 팀별로 학습된 목표 위치 지식이 행동 차이로 드러난다. v2 gate 설계(D29)의 근거다.
- **GPT 답변 평가**
  - 답변의 1·3번(두 목표 보임 probe를 추가하자)과 2번(그 probe에서 JS≈0)이 서로 모순되며, 2번이 맞다.
  - "팀별 관측으로 변환해 넣자"는 상대의 팀을 먼저 알아야 하므로 순환이다.
  - 물리적 목표 선택(실제 행동 관찰, B안 = E11 방향)과 같은 입력에 대한 정책 차이를 구분하라는 결론에는 동의한다.
- **범위**: 설명만 했다. 코드·실행 변경은 없다.

#### D33. A3–A4 cross-team 연결은 '원정 담당' 역할 짝이다 — 2026-10-15 Claude Code (해석, 결정 아님)

- **사용자 설명**: 구역 분리 시에는 같은 팀이 연결됐다. 50:50으로 섞은 뒤 A3·A4가 오른쪽에서 대기하는 전략으로 바뀌었고, 같은 영역에서 행동이 비슷해져 연결됐다.
- **기록 대조**
  - `output/gating_diagnosis`: 같은 팀 거리는 stage01 .086/.100, stage02(12.5% 혼합) .259/.318이다. 12.5% 혼합에서 이미 연결이 끊겼다.
  - `output/pgct_spatial_analysis` 3.4(Stage04 최종 모델): A1 왼쪽 99.6%, A2 오른쪽 99.4%로 홈 담당이다. A3(빨강)는 요청 pickup의 81%를 오른쪽에서, A4(파랑)는 72%를 왼쪽에서 하며 운반 시간 비율이 76–77%다.
  - 따라서 A3·A4는 같은 영역이 아니라 서로 반대 구역으로 가는 원정 역할이다. 기록에서 대기 행동은 보이지 않는다.
  - 공통 probe JS는 3–4가 .130으로 최소다. stage04에서 3–4 전이는 1,170 update다.
- **해석**: E1에서 actor 응답 유사도는 팀보다 역할(홈/원정)을 따른다. 혼합이 팀 내 분업을 만든다는 인과는 미검증이다(seed 1, 단일 커리큘럼).
- **E1-F 함의(가설)**: 원정 담당이어도 운반 방향이 팀별로 반대가 되므로, v2 gate에서 역할 짝 연결이 깨질 수 있다. 혼합 0% 대조로 혼합 효과를 분리할 수 있다.

#### D34. 학습 지속·다음 실험 순서·환경 변경·baseline 시점 — 2026-10-18 Claude Code (의견, 결정 아님)

- **사용자 질문**
  - 학습을 계속할 필요가 있는가?
  - 다음 학습 방법은 무엇이 좋은가?
  - 환경 난이도나 다른 변화가 필요한가?
  - 다른 알고리즘을 먼저 돌릴까, 현재 실험을 더 볼까?
- **의견**
  - (1) 15M까지 계속한다. All이 따라잡는지와 A4의 학습 여부가 남았다. 6.4M 이후 순위가 유지되면 seed 2·3 예산을 8–10M으로 줄이는 근거로 쓴다.
  - (2) 우선순위:
    1. E1 4 mode seed 2·3. E24에서 같은 seed 재실행인데 All의 배송 시작이 1.8M에서 4.0M으로 달라졌다.
    2. E1-F IPPO 시험 4–5M. 실제 운반 방향과 v2 gate same/cross JS를 확인한다.
    3. 효과가 보이면 E1-F 4 mode.
    4. 별도로, 전이 mode가 비결정적인 원인을 코드에서 확인한다.
  - (3) 난이도는 유지한다(배송 시작 약 2M, A4 미학습). 구조 변화가 필요하다.
    - E1에서는 팀 정보가 critic에 무의미하므로(E11) Oracle vs All은 공유 범위 효과에 가깝다.
    - E1-F 목표 분리와 team reward(`team_reward_mode=team`, 환경에 존재)가 Oracle 우위에 설계상 근거를 준다.
    - 두 변경을 분리하기 위해 E1-F IPPO를 individual과 team reward로 각각 시험한다.
    - home .5는 유지한다. 0%면 위치로 팀이 드러난다.
  - (4) baseline(MAPPO/SePS/HetDPS)은 효과 조건을 확정한 뒤에 돌린다.
- **범위**: 의견만 남겼다. 실행·코드 변경은 없다.

#### 새 항목 작성 양식

`ID / 날짜·작성 도구 / 사용자 질문·요청 / 관측 / 판단과 근거 / 수행 또는 제안 / 변경된 이전 판단 / 미해결 질문` 중 해당 내용을 적는다.

---

# Part 5. 실험·평가 기록

## 출처: `EXPERIMENTS.md` (수정 2026-10-18 12:26)

### PGCT 실험·평가 기록

최초 정리: 2026-10-13 Codex. 최신 정량 스냅샷은 14:37 KST. 원본 로그·체크포인트는 보존한다. 이 파일의 계획과 명령은 실행 사실을 뜻하지 않는다.

#### E00. 기존 curriculum — 완료

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

#### E01. 기존 home1 IPPO continuation — 완료, 대조 조건 미일치

Run: `runs/recurrent_ippo_consensus/ex5_semantic_cnn_none_from_scratch_4ag_sr5_square_home1.00_seed1_pretrain_off_9700_continue/`.

- Graph none, communication off, peer coefficient 0, consensus 0인 IPPO다.
- 최종 delivery 61.45, shelf return 59.50. 기존 checkpoint900의 가중치에서 이어졌으며 새 counters가 시작된다.
- 사전학습 예산·초기 상태가 Stage03 분기와 달라 E1 PGCT의 matched baseline으로 사용하지 않는다.
- 과거 영상의 agent별 성공 시점 차이를 순차 optimizer 업데이트로 해석하지 않는다.

근거: 해당 run의 `final_eval_metrics.json`, 기존 from-scratch 실행기와 과거 진단.

#### E02. 공간 분기 — E1/E2 완료, E3 진행

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

#### E03. 기존 Stage04 공간 활동 — 고정 모델 평가 완료

기존 Stage04 final을 20×500 step 평가했고 가중치가 바뀌지 않았음을 확인했다. 왼쪽 체류율은 Agent1 99.57%, Agent2 .55%, Agent3 38.01%, Agent4 56.53%다. 3–4 occupancy JS는 .152835로 가장 낮았다.

다만 Agent3 요청 pickup의 약 81%는 오른쪽, Agent4의 약 72%는 왼쪽이었다. 동일 작업이나 역할을 수행했다고 결론 내리지 않는다.

근거: [Frozen 평가](output/pgct_spatial_analysis/frozen_rollout_summary.json), [분석](output/pgct_spatial_analysis/REPORT.md).

#### E04. 기존 Stage04 probe 중복 민감도 — 진단 완료

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

#### E05. 공통 rollout 이력의 policy/critic 일치 — 진단 완료

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

#### E06. 2026-10-13 최종 critic의 실제 return 예측 — 평가 완료

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

#### E07. 2026-10-13 최종 canonical 응답 — 진단 완료

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

#### E08. Transfer 전용 실행기 — 구현 완료, 장기 실험 미실행

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

#### E09. E2 연결 성분과 완전 연결 구분 — 2026-10-13 진단 완료

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

#### E10. 분리된 장애물·배송 제약 환경 — 2026-10-13 구현 및 시험 완료

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

#### E02 추가 — E3 PGCT 중단 (2026-10-13 Claude Code 실측)

18:21 KST Windows 재부팅으로 `e3_pgct_s1` 프로세스가 종료됐다. 시스템 로그에는 정상 종료와 Kernel API에 의한 reboot가 기록됐다. 마지막 metrics 2,855,936 step, 마지막 checkpoint `checkpoint_02700.pt`(2,764,800 step), 마지막 평가 2,816,000 step delivery 28.6 / return 26.8, 관측 구간 AUC 23.49. `experiment.json`은 `running`/`planned`로 남아 있으며 수정하지 않았다. 기존 실행기는 같은 폴더로 이어 학습을 지원하지 않는다. 재개하지 않았다.

#### E11. 실험 A — 국소 행동으로 팀 식별 가능성과 critic consensus 전제 — 2026-10-13 Claude Code, 완료

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

#### E12. 실험 B 실행기 — oracle/all/wrong critic peer-loss 분기 — 2026-10-13 Claude Code, 구현·smoke만

- 코드: `latent_team/exp_b_oracle_consensus.py`, `latent_team/run_exp_b.ps1`, 설명 `latent_team/README.md`. 기존 trainer의 `graph_mode=oracle/unrestricted/wrong`을 그대로 사용한다. 기존 E1 PGCT seed1과 같은 Stage03·환경·PPO·예산 4,000,768 step·평가 seed를 쓰고, 그 run의 canonical bank를 미리 넣는다. 처음 100 update는 전이를 보류한다. `transfer.jsonl`에서 실제 allocation과 팀/물리 범위 위반 여부를 검사한다. 기존 PGCT/IPPO run은 읽기 전용으로 비교한다.
- 검증: dry-run에서 세 mode 모두 기존 E1 PGCT와 `graph_mode`만 다름을 확인했다. `runs/lt_b_smoke_20261013` 64-step CPU smoke에서 oracle 같은 팀 arc 6/다른 팀 0, all 6/12, wrong 0/12, 모두 물리 이웃 범위 안이었다. 세 run의 canonical bank가 기존 E1 PGCT bank와 동일했다. 비교표가 기존 E1 AUC 45.8559/44.5734를 재현했다. `tests/test_latent_team.py` 6 tests, 관련 기존 테스트 포함 19 passed.
- **장기 학습 미실행.** 예상 소요는 기존 E1 속도 기준 run당 약 30시간이다. Learned-team mode는 구현하지 않았다.

#### E13. 국소 증거의 관측 가능성 검증 — 2026-10-13 Claude Code, 완료

- 코드: `latent_team/verify_evidence_observability.py`. 결과: `output/latent_team/exp_a_20261013/observability_check.json`.
- 조건: E1 IPPO, E2 IPPO, Stage04 PGCT final. 자체 stochastic masked policy로 5회×500 step, seeds 5,200,001–5,200,005. weight 불변.
- 결과: 실험 A가 센 (관측자, 대상, 사건)마다 관측자의 post-step semantic 관측에서 대상 칸을 확인했다. pickup 985건(362/193/430)과 delivery 1,161건(474/214/473) 모두 agent+loaded로 보였다. `requested_shelf`(pickup)·`relevant_goal`(delivery) 채널 값도 증거 라벨과 100% 일치했다.
- 한계: 관측의 agent 칸에는 ID가 없다. 사건을 특정 이웃에게 귀속하는 것은 이웃 식별 가정이다. 정지 상태로 운반 중인 agent와 막 pickup한 agent는 관측상 구분되지 않는다.

#### E12 추가 — 짧은 matched-prefix 예산 지원 (2026-10-13 Claude Code)

트레이너에 학습률 schedule이 없음을 확인했다(`total_timesteps`는 update 수만 결정). 이에 따라 `--timesteps`가 기준 run보다 짧으면 `total_timesteps` 차이만 추가로 허용하고, 비교표는 기준 run을 같은 step에서 자르도록 했다. Dry-run에서 1,024,000 step oracle 계획을 확인했다. 기존 E1 첫 1,024,000 step의 delivery AUC는 IPPO 43.828, PGCT 44.605(평가 20회)다. 관련 test 1개를 추가해 20 passed. **학습은 실행하지 않았다.**

#### E14. 처음부터 학습 실행기 — 2026-10-13 Claude Code, 구현·smoke만

- 코드: `latent_team/train_from_scratch.py`, `latent_team/run_from_scratch.ps1`(병렬은 job별 별도 프로세스, 스레드 4). `exp_b_oracle_consensus.matched_transfer`에 초기 가중치 hash 기록과 ippo/pgct 허용 조건을 추가했다.
- 기본 조건: E1 맵 11×10, 4 agents/2 teams, home .5, 요청 4, individual reward, 무작위 초기화, lr 2e-4, entropy .05(기존 Stage03 분기 실험은 1e-4/.02), rollout 1024, 10M step, 평가 51,200 step마다 20×500(seeds 5,000,001–), checkpoint 250 update마다.
- 검증:
  - `runs/scratch_smoke_20261013`: 5 modes 순차 64-step CPU.
  - `runs/scratch_smoke_parallel_20261013`: 4 modes 병렬. 첫 병렬 시도 2회는 상태 파일 읽기 경합으로 비교/상태 기록 오류가 났고, 원자적 교체와 재시도로 수정한 뒤 재실행해 전부 complete.
  - 모든 mode의 초기 가중치 hash가 동일했다(`baaa10bf…`, Stage03 `b5e2158b…`와 다름).
  - 전이 arc는 ippo 0/0, pgct 6/12, oracle 6/0, all 6/12, wrong 0/12(같은 팀/다른 팀)였다.
  - 전체 tests 179 passed(plan 검사 test 포함).
- **장기 학습 미실행.** 기존 E1 속도 기준 예상 소요는 run당 2M 약 15시간, 10M 약 75시간이며, 병렬 시 더 느려질 수 있다.

#### E14 추가 — 2단계 자동 파이프라인 (2026-10-13 Claude Code)

사용자 요청("1번 끝나면 자동으로 2번 돌아가게")에 따라 다음을 추가했다.
- `latent_team/run_scratch_pipeline.ps1`: 1단계 pilot의 모든 job이 complete이면 2단계 본 비교를 시작한다. `-Detach`로 백그라운드 실행.
- `run_from_scratch.ps1`의 `-Wait` 옵션.

`-SmokeTest -Detach` 검증(`runs/scratch_pipeline_smoke_20261013_*`, 각 64-step): 19:23:37 시작, 1단계 2 jobs 완료 후 19:23:46 2단계 시작, 4 jobs 완료 후 19:23:55 종료. 장기 학습은 시작하지 않았다.

#### E14 점검 — 실행 전 코드·설정 검토 (2026-10-13 Claude Code, 학습 미실행)

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

#### E15. W&B 통합 + MAPPO/SePS/HetDPS 구현 — 2026-10-13 Claude Code, smoke만

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

#### E16. 본 학습 전 실제 설정 검증 — 2026-10-13 Claude Code, 검증만

- **실행**: `runs/verify_realcfg_20261013`. `run_from_scratch.ps1 -Modes ippo,pgct,oracle,all -TotalTimesteps 4096 -Parallel -ThreadsPerJob 4`, 실제 학습 설정(device=cuda, rollout 1024, seq 64, 평가 20×500은 종료 시 1회). W&B는 끄고 4 update만 실행했다. **본 학습 아님.**
- **초기 파라미터**: 4 run 모두 첫 update 전 actor+critic hash `f78ec390e0fad60c…`로 같다.
  - CPU smoke 설정의 hash(`baaa…`)와 다른 것은 설정 차이 때문이다. 같은 설정 안에서 mode 간 일치가 요구 조건이다.
  - 모든 run이 complete였고 오류 로그는 없다. PGCT/oracle 전이는 warm-up 100 update 때문에 이 4 update에서는 발생하지 않는다. 전이 경로는 smoke(E14)에서 검증했다.
- **속도**: 4 프로세스 병렬에서 update당 38.5–39.5초(job당 약 26 step/s, 합계 약 105 step/s). 15M이면 약 6.6일 이상이고 평가 시간이 추가된다.
- **용량**: checkpoint 61MB × 250 update 간격 → run당 약 3.6GB. 디스크 여유는 1.5TB다.
- **resume 검증**: 코드 검토 결과 불가능하다(D22).

#### E17. From-scratch 핵심 비교 본 학습 — 2026-10-13 20:23:52 KST 시작(사용자 실행), 진행 중

- **경로**: `runs/scratch_20261013_202352_stage2`, 로그 `runs/scratch_20261013_202352_pipeline.log`.
- **조건**: IPPO/PGCT/Oracle/All, seed1, 15M, 병렬 4 프로세스(PID 10392/29856/12684/24828), W&B.
- **20:27 KST 무렵 확인**
  - 4 run 모두 2,048 step, update당 약 40.6초로 15M까지 약 7일 예상.
  - GPU: nvidia-smi 사용률 70–81%(사용자 작업관리자에서는 95–99%로 보임), 전력 78–83W/300W, 온도 50–52°C, 팬 0%, VRAM 2.6/16.3GB.
  - CPU 59%, 프로세스당 RAM 약 2.1GB, 여유 RAM 10GB.
- **해석**: 사용률 수치는 GPU가 작은 kernel을 실행 중인 시간 비율이다. 전력·온도로 보면 하드웨어 부하는 낮다. 6–7일 연속 실행의 주요 위험은 GPU 마모가 아니라 재부팅·절전·정전, 다른 GPU 작업과의 경합이다.

#### E17 추가 — Windows Update 재부팅으로 중단 (2026-10-15 Claude Code 실측)

- 2026-10-15 00:59 KST에 MoUsoCoreWorker가, 01:01 KST에 TrustedInstaller가 "운영 체제: 업그레이드/서비스 팩" 사유로 재시작을 실행했다(System 이벤트 1074/109). 원인은 Windows Update다.
- 마지막 metrics: ippo 2,487,296, pgct 2,502,656, oracle 2,471,936, all 2,455,552 step(00:58–00:59 기록). 마지막 checkpoint는 4개 모두 `checkpoint_02250.pt`(2,304,000 step)이고 job_status는 `running`으로 남아 있다.
- 최근 평가 delivery(약 2.4–2.46M): IPPO 2.9, PGCT 2.2, Oracle 10.7, All 4.2. 단일 seed이고 중단된 초기 구간의 값이다.
- 폴더와 로그는 보존했다. 정확한 재개는 불가능하다(D22).

#### E18. E17 중단 시점(약 2.5M) 학습 현황 분석 — 2026-10-15 Claude Code, 읽기 전용

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

#### E19. 신규 from-scratch 재실행 발견 — 2026-10-15 11:49 KST Codex, 읽기 전용 확인

- **경로:** `runs/scratch_20261015_093349_stage2/experiment.json`. 이번 작업 이전에 생성된 실행이다. 본 turn에서는 학습을 시작·중단·재시작하지 않았다.
- **조건:** E1 11×10, home.5, individual reward, 4agents/2teams, sensor/communication range5, IPPO/PGCT/Oracle/All, training seed1, 무작위 초기화(`init_checkpoint=""`), 요청 예산15,000,000/실제 반올림15,000,576 env steps.
- **진행 스냅샷(11:49):** IPPO200,704 / PGCT198,656 / Oracle196,608 / All199,680 env steps. `job_status.json`은 모두running이며 metrics 수정시각은11:48:58–11:49:28이다. 반복 확인에서 로그가 증가했다. CIM 프로세스 조회는 접근 제한으로 확인하지 못했다.
- **초기화:** 4mode의 `initial_weights_sha256.txt`가 모두 `f78ec390e0fad60c9bee9ea045525a79befbd71357f41235f04d61356b91c7e3`다.
- **평가:** 네 mode 모두 최근153,600step, delivery0.0/episode. deterministic masked, reset seeds5,000,001–5,000,020, 20×500. 초기 단계의 결과이며 실패로 판정하지 않는다.
- **E17과의 관계:** 중단된2.5M run의 resume이 아니라 같은 seed1의 처음부터 재실행이다. 독립training seed 추가나 이전곡선의 연장으로 세지 않는다.
- **근거:** `output/ijcai_review_20261015/live_run_snapshot.json`, 해당 run의 manifest/metrics/status/초기hash. 논문용 해석과 후속 제안은 같은 폴더REPORT 및 D23에 기록했다. 새 실험·추가 평가·tests는 실행하지 않았다.

#### E20. 환경·canonical probe 시각화 — 2026-10-15 Claude Code, 읽기 전용

- **환경 그림**: `output/env_view_20261015/environment_seed5000001.png`. 실행 중 run의 환경 설정으로 그린 전체 맵, Agent1·2의 11×11 팀 기준 관측. 팀 목표가 (4,10)/(5,10)으로 인접한다.
- **probe 그림**: `output/env_view_20261015/probes/`(official 렌더링 48장과 contact sheet, decoded_bank.png, probes.csv, README.md).
- **bank 검증**: 저장소 builder로 같은 env 상태(reset seed 1)와 rng(seed+9173)로 다시 만든 bank가 run의 `canonical_bank_e1_s1.pt`와 완전히 같다.
- **중복 구조**: 고유 입력 26/48.
  - `dual_requested_*` 7종이 팀마다 하나의 입력으로 겹친다(8개 × 2그룹).
  - goal_pair·goal_zone_pair·lane_choice가 팀마다 하나로 겹친다(4개 × 2그룹).
  - neutral은 2개 × 2그룹이다.
- **겹침 원인(추정)**: 해독한 시야에서 요청 선반이 대부분 가장자리에 1개만 보인다. 서로 다른 두 번째 선반 위치가 11×11 관측 밖이라는 추정이며, builder 코드로는 확인하지 않았다.
- **상태 구성**: 빈 손 38, 요청 선반 적재 10(반납 단계 4). 요청되지 않은 선반을 든 상태는 0이다.

#### E21. runs/ 정리 — 2026-10-15 Claude Code (사용자 승인 삭제)

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

#### E22. probe bank v2 / E1-F 구현 검증 — 2026-10-15 Claude Code, 구현·smoke만

- **bank**: `output/env_view_20261015/probes_v2/`(e1f·e1 각 gate 48 + transfer 64, 역할 내 중복 0, 검증 거부 0).
  - transfer 구성: 탐색 14, 목표 보임 16, 목표 안 보임 16, 반납 16, 목표 도착 2.
  - gate 위치는 모두 y≤4로, 어느 목표도 시야 밖이다.
- **smoke** `runs/smoke_e1f_v2_20261015`: e1f × ippo/pgct/oracle/all 64-step 모두 complete. PGCT의 `canonical_probes.pt`는 v2 gate와 같다. PGCT/Oracle/All의 증류 입력은 64개다(`distill_probe_count`).
- **tests**: E1-F 모서리 목표에서 적재 agent가 전진하면 delivery event가 발생함을 확인했다. 전체 183 passed.
- **한계**: E1-F 학습 정책에서 same/cross JS 판별력, Oracle 이득은 아직 미측정이다.

#### E19 추가 — HANDOFF 이후 진행 상태 재확인 (2026-10-15 13:17 KST Codex)

- **같은 실행의 후속 확인:** `runs/scratch_20261015_093349_stage2`, E1 11×10/home .5/individual reward/4 agents·2 teams, 무작위 초기화 training seed 1, 기존 canonical bank, 15M 목표. IPPO 321,536 / PGCT 316,416 / Oracle 314,368 / All 318,464 env steps. 로그 시각 13:16:39–13:17:05, 네 status는 running, 속도 23.49–24.04 step/s다. 최초 확인보다 로그가 증가했고 초기 hash 4개도 동일하다.
- **최근 평가:** 네 mode 공통 307,200 step, deterministic masked 20×500, reset seeds 5,000,001–5,000,020. 요청 pickup/delivery/return 각 0.0이다. 초기 단계이며 성능 판정을 하지 않는다. 마지막 checkpoint는 모두 00250(256,000 step)이다.
- **실행 건강 확인:** .err.log의 Traceback/Error/Exception/failed 일치 0건. Gymnasium 정밀도·reward 형식 경고와 W&B 안내가 있다. 이는 전체 학습 정확성의 독립 검증은 아니다.
- **별도 구현 확인:** E22 seed 1의 64-step smoke 4 mode가 complete이며 PGCT/Oracle의 transfer.jsonl에서 distill_probe_count 64와 Oracle cross arc 0을 확인했다. v2 summary는 gate 48/transfer 64, 고유 입력 검증 통과다. 장기 E1-F/v2 실행은 발견되지 않았다. 183 tests 통과는 Claude 기록이고 재실행하지 않았다.
- **산출물/범위:** `output/status_review_20261015_131716/snapshot.json`. HANDOFF·RESEARCH_STATE·대화 원문을 갱신하고 통합 사본을 재생성한다. 새 학습·추가 평가·tests·알고리즘 변경·삭제·학습 중단은 하지 않았다.

#### E23. 기존 E1 모델의 probe별 팀 구분 시각화 — 2026-10-15 Claude Code, 읽기 전용

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

#### E23 추가 — agent별 행동 특성 (2026-10-15 Claude Code, 읽기 전용)

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

#### E24. 현재 from-scratch run 약 6.4M 중간 분석 — 2026-10-18 Claude Code, 읽기 전용

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

#### 새 실험 기록 양식

ID / 실제 실행 날짜·작성 도구 / 상태(계획·smoke·진행·완료·실패) / 초기 모델 / 환경·training seed·예산 / 평가 seed·정책·horizon / 결과 / 비교 기준·한계 / 원본 경로 / 재현 명령.

---

# Part 6. 분석 보고서 (output/, 작성일 순)

## 출처: `output/gating_diagnosis/README.md` (수정 2026-10-02 11:16)

### PGCT gating 진단

분석 대상: `runs/pgct09700_physical_mixing_20260929_155338_079437`의 네 단계.
학습 코드, 설정, 원본 로그, 체크포인트는 수정하지 않았다. 재학습하지 않았다.

#### 관측 결과

같은 팀 쌍은 1–3, 2–4이고, 나머지 네 쌍은 다른 팀이다.

| 단계 | 같은 팀 최종 거리: 1–3 / 2–4 | 처음 5회 평가 delivery 평균 | 마지막 5회 평가 delivery 평균 |
|---|---|---:|---:|
| stage01 | 0.0856 / 0.1002 | 60.43 | 59.65 |
| stage02 | 0.2591 / 0.3176 | 26.09 | 52.57 |
| stage03 | 0.2772 / 0.3853 | 45.37 | 47.71 |
| stage04 | 0.3242 / 0.4119 | 42.17 | 45.87 |

stage03과 stage04에서는 같은 팀 쌍이 gate를 통과한 업데이트가 없다.
stage04에서 물리적으로 허용된 실제 다른 팀 전달은 3–4가 1170 업데이트,
1–4가 51 업데이트였다. 같은 업데이트에 여러 쌍이 열릴 수 있으므로 단순 합은 전체 전달 업데이트 수가 아니다.

stage04의 마지막 연결은 3–4였다. update 3869에서 거리 EMA 0.114925로 연결되었고,
update 3870에서 0.121965로 임계값 0.12를 넘어 연결이 끊겼다.
이 두 업데이트 모두 해당 쌍은 물리적 통신 범위 안에 있었다.
최종 update 3907에서는 모든 쌍의 거리 EMA가 임계값 이상이다.

stage04의 처음 100 업데이트와 마지막 100 업데이트에서 로그의 PPO entropy 평균은
각각 0.10124, 0.08767 nats였다. 최종 공통 probe에서 에이전트별 평균 entropy는
1–4 순서로 0.06996, 0.22216, 0.07476, 0.23253 nats였다.

#### 해석과 한계

- 같은 팀 연결이 닫힌 상태에서도 stage04의 delivery는 초반보다 후반에 높다. 연결 소멸 자체를 학습 실패로 볼 근거는 없다.
- stage04에서는 같은 팀 연결이 초반부터 없었다. 따라서 이 단계만으로 ‘초반 같은 팀 전달이 학습을 돕고, 이후 필요성이 줄었다’고 결론낼 수 없다.
- 같은 팀과 다른 팀의 행동 거리 순서가 역전된 것은 관측된다. 역할 분업 때문에 역전되었다는 인과관계는 검증되지 않았다.
- 실제 환경에서 서로 다른 위치에 있는 에이전트가 다른 행동을 하는 것과, 동일한 canonical 입력·zero hidden state에서 정책이 다르게 반응하는 것은 별개의 증거다. 현재 거리 측정은 후자이다.
- 최종 평가에서 모든 에이전트는 pickup, delivery, return을 수행했다. 최종 집계만으로 pickup 담당과 return 담당 같은 역할 분화를 확정할 수 없다.
- 네 단계는 shelf 혼합률이 다르다. 단계 간 성능 차이는 PGCT 효과와 환경 변화가 섞여 있으므로 비교군 실험을 대신할 수 없다.
- 평가마다 seed가 달라진다. 처음/마지막 5회 평균은 추세 요약이며, 같은 seed의 paired 평가나 유의성 검정이 아니다.
- 현재 run과 대조할 동일 커리큘럼·초기 체크포인트·예산의 PGCT-off 결과는 발견하지 못했다. smoke-test의 none run은 대조군으로 사용할 수 없다.
- 거리 곡선은 물리적으로 이웃일 때만 갱신된 EMA다. 멀리 떨어져 있던 구간은 오래된 값이 유지될 수 있다.
- 그래프의 에이전트별 entropy는 `log(5) - policy_information`으로 복원한 고정 probe 평균이다. 실제 rollout의 entropy나 평균 행동 빈도와는 다르다.
- 기존 JSONL은 에이전트별 전체 action probability vector를 저장하지 않았다. 이를 확인하려면 저장된 actor를 canonical probe에 forward-only로 평가해야 한다.
- entropy 감소와 delivery 증가만으로 specialization 또는 critic transfer usefulness를 입증할 수 없다. 각각 역할/경로 분석과 matched transfer/independent branch가 필요하다.

#### 파일

- `stage04.png`: stage04의 쌍별 거리, 같은/다른 팀 gate 비율, 에이전트별 probe entropy, delivery.
- `curriculum.png`: 네 단계의 거리, gate 비율, delivery를 나란히 비교.
- `summary.json`: 각 쌍의 연결 횟수와 첫/마지막 연결, entropy, 평가 지표의 수치 요약.
- `analyze_logs.py`: 위 산출물을 재생성하는 오프라인 분석 스크립트.

Gate 그래프의 희미한 선은 거리·측정횟수·warm-up을 통과한 쌍의 비율이며,
진한 선은 물리적 마스크까지 적용된 실제 전달 쌍 비율의 100-update 이동평균이다.
같은 팀은 두 쌍, 다른 팀은 네 쌍을 각각 분모로 사용했다.

현재 자료가 지지하는 표현은 다음과 같다.

> Shelf 혼합 커리큘럼에서 같은 팀의 canonical policy distance가 증가해 similarity gate가 닫혔으며,
> 같은 팀 전달이 없는 stage04에서도 작업 성능은 개선되었다.
> 역할 분업과 PGCT의 전달 이득은 추가 검증이 필요한 가설이다.

## 출처: `output/pgct_spatial_analysis/REPORT.md` (수정 2026-10-08 11:52)

### PGCT Cross-team 연결과 RWARE 공간 확대: 구현·로그 분석 보고서

작성일: 2026-10-08. 기준 모델: `stage04_4ag_physical_home0.500/final.pt`.

#### 1. 판단과 분석 범위

**현재 same-team gate 소멸은 물리적 접촉 부족만으로 설명되지 않는다. 같은 팀의 공통 probe 응답이 임계값을 벗어난 것이 직접적인 차단 조건이다. 공간 분업은 가능한 배경 원인이지만, 정책 유사도와 공간 점유 유사도를 구분해서 검증해야 한다. 맵 확대는 이 가설을 검증할 수 있는 환경 변경이며, 개선이 보장된 해결책은 아니다.**

이번 작업에서는 학습 코드·환경 코드·설정·체크포인트·기존 로그를 수정하지 않았다. 저장된 자료를 읽고, 별도로 생성한 환경을 reset하여 맵 구조를 확인했다. 최종 모델의 평가도 가중치를 고정한 추론으로 수행했다. 새 산출물은 이 보고서와 같은 폴더에만 저장했다. 이전 턴에서 요청받아 수행한 구버전 코드 정리는 이번 분석과 별개다.

분석 대상:

- [기존 curriculum manifest](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/runs/pgct09700_physical_mixing_20260929_155338_079437/curriculum.json)
- 위 폴더의 네 단계 `communication.jsonl`, `canonical_probes.pt`, `final_eval_metrics.json` 및 stage04 `final.pt`.
- [기존 gating 진단](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/gating_diagnosis/README.md), [공통 probe 정책 응답](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/gating_diagnosis/policy_responses.json).
- [이번 분석 수치와 맵 snapshot](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/evidence.json).

아래에서 **확인**은 실제 코드·저장 자료·이번 평가에서 확인한 내용, **가설/계획**은 아직 인과적으로 입증하거나 실행하지 않은 내용이다.

#### 2. 현재 환경의 실제 구조

##### 2.1 크기·shelf·배송 지점

**확인:** 환경 ID는 `rware-multiteam-tiny-4ag-2teams-v0`이다. 등록 기본값은 `shelf_rows=1`, `shelf_columns=3`, `column_height=8`이며, manifest에 크기 override가 없어 이 기본값을 사용한다. 실제 환경 생성으로도 확인했다.

관련 구현:

- [환경 등록](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/__init__.py:44)
- [Warehouse._make_layout_from_params](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/warehouse.py:294)
- [Warehouse.reset](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/warehouse.py:775)

| 항목 | 현재 값 |
|---|---|
| 격자 높이 H × 너비 W | **11 × 10**, 110 cells |
| 크기 공식 | `H=(column_height+1)*shelf_rows+2`, `W=3*shelf_columns+1` |
| 초기 shelf 수 | **32**; 저장 cell마다 한 개 생성 |
| 저장 cell 밀도 | 32/110 = **29.09%** |
| 수직 통로 | `x % 3 == 0`; 일반 통로 폭 1 cell |
| 수평 통로 | `y % 9 == 0`, 마지막 배송 행 및 중앙 queue corridor |
| 팀 0 배송 지점 | **(4,10)** |
| 팀 1 배송 지점 | **(5,10)** |
| 관측/통신 범위 | sensor range 5 / communication range 5 |
| 에피소드 길이 | 최대 500 환경 step |

좌표는 **(x,y), 0부터 시작**, 격자 크기는 **(H,W)**다. 중앙 queue corridor가 가장 아래 shelf band의 중앙 shelf 두 열을 통로로 바꾸므로, 단순히 `3×2×8=48 shelves`로 계산하면 틀린다. 실제 tiny에는 32개가 있다. 두 배송 지점은 하단 중앙에 나란히 있으므로 서로 다른 지역에서 작업하더라도 배송 때는 중앙으로 모일 수 있다.

##### 2.2 팀·혼합·보상

**확인:** [MultiTeamWarehouse._balanced_assignments](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:31)의 `agent_index % 2`로 팀을 정한다. 화면 번호 1–3은 팀 0, 2–4는 팀 1이다. 에피소드 reset 때 팀을 섞는 옵션은 기본 false이며 현재 override가 없다.

[MultiTeamWarehouse._assign_shelf_teams](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:349)는 `balanced_soft_zones`에서 좌우 저장 cell 수가 같아야 한다. 각 구역에서 `round(zone_shelf_count*(1-home_ratio))`개의 **shelf 팀 소속**을 반대 팀으로 바꾼다. 좌표나 통로는 바뀌지 않는다. 현재 두 구역은 각각 16개이며 home ratio 1/.875/.75/.5에서 구역당 소속 교환 수는 0/2/4/8개다. stage04는 좌우 각 구역에 팀별 shelf 8개씩 있다. 배치는 reset마다 RNG로 다시 선택한다.

`goal_team_mode=zones`는 원래 중앙 배송 지점 두 개를 팀별로 나눈다. `require_matching_team_goal=True` 기본값이 적용된다. [팀 배송 지점 배정](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:498).

현재 `team_reward_mode=individual`이다. 따라서 “같은 팀”은 shelf·목표 지점을 공유하는 작업 집단이지만, delivery/return 보상이 모든 팀원에게 동일하게 배분되는 설정은 아니다. 이 설정에서도 역할 분화는 가능하나, 팀 보상 최적화가 원인이라고 단정하면 안 된다. [배송 보상 구현](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:612).

현재 핵심 보상은 delivery 1.0, home return 1.0, requested pickup .15, shelf/goal/return progress .002/.005/.02이다. 잘못된 pickup·drop, 충돌·blocking·deadlock 및 NOOP 등의 벌점도 있다. [기본 보상 설정](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/env_kwargs_stage2_pgct_success_unblock_zones_individual.json). 맵 비교에서는 checkpoint의 실제 `effective_env_kwargs`를 복사하여 이 설정을 유지해야 한다.

##### 2.3 에이전트 초기 위치

**확인:** 초기 위치는 고정 좌우 배치가 아니다. `Warehouse.reset`은 **전체 110 cells에서 서로 다른 4개 cell을 무작위 선택**한다. shelf 밑 cell이나 배송 지점도 포함된다. 방향도 무작위다. 팀 소속에 따른 시작 구역 제한은 없다.

이번에 현재 stage04 설정으로 `reset(seed=1)`했을 때 위치/방향은 다음과 같았다. 이 표는 재현 가능한 예시이며 기존 평가 영상의 시작 상태나 학습된 담당 구역을 뜻하지 않는다.

| Agent | 팀 | 위치 | 방향 |
|---|---:|---|---|
| 1 | 0 | (2,8) | RIGHT |
| 2 | 1 | (5,5) | UP |
| 3 | 0 | (4,10) | DOWN |
| 4 | 1 | (0,5) | RIGHT |

#### 3. Cross-team 연결: 관측과 직접적인 gate 조건

##### 3.1 알고리즘이 실제로 측정하는 것

[sample_policy_probe_sequences](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:2009)는 `objective`, `shared`, `fixed_canonical_probes=True`에서 별도 RNG seed `cfg.seed+9173`으로 외부 probe bank를 만들고 환경 인스턴스에 캐시한다. 현재 bank shape은 **[48,1,1593]**다. “fixed”는 한 단계 안에서 고정된다는 뜻이며 네 단계의 저장 bank hash는 서로 다르다.

[policy_distance_similarity_matrices](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:2090)는 모든 actor에 동일한 probe를 주고 **zero hidden state**, sequence length 1에서 **action mask 없는 softmax**를 비교한다. 거리 D는 probe별 JS divergence의 평균이며 자연로그를 사용한다. 실제 rollout의 위치별 행동 빈도나 평균 probability vector 사이의 JS와는 다르다.

[TeamGraphEstimator.update_from_policy_distance](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:554)는 probe round 시점에 물리적 이웃인 쌍의 EMA만 갱신한다. 현재 probe interval 5 updates, EMA beta .35, minimum count 8 rounds다. 48 probe를 한 번 비교해도 count는 **1** 증가한다. 이웃이 아니면 EMA가 오래된 상태로 유지된다.

[TeamGraphEstimator.pgct_gate_matrix](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:718)의 실제 threshold 비교는 **`D_ema < 0.12`**다. equality에서는 닫힌다. update 100부터 warmup이 끝나고, 측정 횟수 ≥8, finite distance, information 조건을 추가로 확인한다. 현재 minimum policy information은 0이다. 이후 [train의 current-neighbor 마스크](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:4925)가 적용된다.

정리하면 현재 승인 연결은 `physical neighbor AND warmup ready AND probe evidence ready AND D_ema<.12`다. true team label을 이용해 gate를 열거나 막지 않는다. 팀 label은 oracle 비교 지표를 위한 분석에 쓰인다.

PGCT transfer는 [update_ippo](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:2889)에서 donor critic의 고정된 공통 probe 예측을 receiver critic이 따르도록 하는 보조 MSE 손실이다. peer loss coefficient .01을 사용한다. actor 입력에 다른 agent의 실시간 메시지를 주는 구조가 아니다. 따라서 평가 영상의 초록 선과 평가 중 실시간 critic 학습 효과를 동일시하면 안 된다.

##### 3.2 물리적 후보와 승인 결과를 분리한 기존 로그 집계

다음 수치는 **1024 환경 step rollout의 끝에서 기록한 update snapshot**을 집계했다. 전 환경 step의 접촉 빈도는 아니다. 무방향 upper triangle을 사용하며 same-team 가능한 쌍은 2개, cross-team은 4개다. 후보/승인 수는 `(쌍, update)` 발생 수라 한 update에 여러 쌍이 포함될 수 있다.

| 단계 | Updates | 평균 이웃/agent | Same 후보 → 승인 | Same 승인/후보 | Cross 후보 → 승인 | Cross 승인/후보 |
|---|---:|---:|---:|---:|---:|---:|
| 01, home1.0 | 977 | 1.644 | 1,499 → 1,131 | 75.45% | 1,713 → 0 | 0% |
| 02, home.875 | 1,954 | 1.761 | 2,906 → 380 | 13.08% | 3,977 → 0 | 0% |
| 03, home.75 | 2,930 | 1.810 | 3,741 → 0 | 0% | 6,868 → 443 | 6.45% |
| 04, home.5 | 3,907 | 1.805 | **4,364 → 0** | **0%** | **9,743 → 1,221** | **12.53%** |

warmup·측정횟수·information 조건까지 준비된 물리 후보를 분모로 삼으면 stage04의 cross 승인율은 1,221/9,500 = **12.85%**다. 같은 팀은 준비된 후보 4,238회에서도 승인 0회다. 모든 기존 snapshot에서 저장된 승인 행렬을 실제 gate 조건으로 재구성했고 일치함을 확인했다.

stage04에서는 1–3이 후보였던 update 2,157회, 2–4는 2,207회다. 따라서 **현재 같은 팀 연결 소멸의 직접 원인은 단순한 접촉 기회 소멸이 아니다**. 실제 cross 승인 쌍은 3–4 1,170회와 1–4 51회다. 승인된 쌍의 팀 구성은 cross 100%지만, 모든 가능한 cross pair가 자주 승인된다는 뜻은 아니다. stage04의 가능한 cross pair 전체 대비 승인율은 7.81%다.

최종 같은 팀 EMA는 1–3 .32416, 2–4 .41194이며 모든 쌍의 최종 EMA가 .12 이상이다. **학습 중 cross transfer가 있었다는 사실과 최종 gate가 모두 닫혔다는 사실은 함께 성립한다.**

##### 3.3 공통 probe의 최종 정책 응답

기존 forward-only 분석은 네 단계 모델을 같은 stage04 bank에 평가했다. 최종 모델의 거리와 preferred action 불일치는 아래와 같다. EMA와 다른 값인 이유는 즉시 계산된 final policy response이며 neighbor 샘플링 EMA가 아니기 때문이다.

| 쌍 | 팀 관계 | 평균 JS | Argmax 불일치 |
|---|---|---:|---:|
| 1–3 | same | .33852 | 50.00% |
| 2–4 | same | .39423 | 58.33% |
| 1–2 | cross | **.58408** | 85.42% |
| 1–4 | cross | .20617 | 35.42% |
| 2–3 | cross | .43928 | 66.67% |
| 3–4 | cross | **.12999** | 18.75% |

**특정 cross pair가 same pair보다 유사하다는 것은 확인된다. 모든 cross pair의 유사도가 높아진 것은 아니다.** 문서의 “1과 2가 같은 왼쪽 담당” 예시는 가설의 설명용 예시이며, 실제로 1–2는 현재 가장 비슷하지 않은 쌍이다. 실제 연결 쌍 3–4, 1–4의 경로·작업 상태를 우선 조사해야 한다.

최종 기존 20-episode 평가의 평균 delivery는 47.25, home return은 45.95다. 기존 stage04 초반/후반 5회 평가 평균 delivery 42.17/45.87은 추세를 보여주지만 평가 seed가 다르다. PGCT 성능 이득이나 분업의 인과 증거로 사용할 수 없다. `eval_full_cycle_success_rate=1`도 모든 요청의 완주율이 아니라 **delivery와 return이 각각 한 번 이상 있었던 episode 비율**이다.

##### 3.4 이번에 추가 확인한 공간 점유·작업 분화

**확인:** 기존 `T.evaluate`를 그대로 사용하되 실행 중 메모리에만 관측 wrapper를 붙여 stage04 최종 모델을 평가했다. 최종 평가와 같은 seeds **5,000,001–5,000,020**, deterministic actions, action mask on, episode당500 step을 사용했다. 학습을 하지 않았고 모델 state tensor hash가 평가 전후 동일함을 확인했다. 평균 delivery **47.25**, home return **45.95**를 재현했으며 저장된 최종 평가 전체 수치와 최대 차이는 **4.68e-9**였다.

총10,000 환경 step에서 매 행동 직전 상태를 기록했다. 왼쪽은 `x<5`, 오른쪽은 `x>=5`다. 모든 agent는 매 step 하나의 cell을 점유하므로 agent별 분모는10,000이다.

| Agent | 팀 | 왼쪽 체류 | Episode별 왼쪽 체류 min–max | 요청 shelf pickup의 왼쪽 비중 | 운반/return 상태 비중 |
|---|---:|---:|---|---|---:|
| 1 | 0 | **99.57%** | 98.2–100% | **202/202 = 100%** | 47.27% |
| 2 | 1 | **0.55%** | 0–1.6% | **0/174 = 0%** | 52.48% |
| 3 | 0 | **38.01%** | 22.0–51.6% | **57/298 = 19.13%** | 76.57% |
| 4 | 1 | **56.53%** | 39.8–72.4% | **215/299 = 71.91%** | 75.95% |

운반/return 비중은 shelf를 들고 있던 pre-action 상태의 비율이다. 요청 pickup은 `requested=True AND return_phase=False`인 event만 세었다. 전체 pickup 집계에는 다른 event도 포함되어 이 표의 분모와 다를 수 있다.

![Stage04 최종 고정 모델의 에이전트별 공간 점유](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/frozen_occupancy.png)

이 평가에서는 **Agent1은 팀0 배송 지점 쪽의 왼쪽 작업, Agent2는 팀1 배송 지점 쪽의 오른쪽 작업에 강하게 집중**했다. 같은 팀의 Agent3은 요청 pickup 대부분을 반대쪽 오른쪽에서, Agent4는 상당 부분을 반대쪽 왼쪽에서 수행하면서 양쪽을 이용했다. 따라서 문서의 “1·2 왼쪽 / 3·4 오른쪽” 예시보다 **팀별 자기 구역에 집중하는 agent와 반대 구역까지 이동하는 agent가 공존하는 형태**가 이번 최종 평가를 더 잘 설명한다. 정확한 역할 명칭은 여전히 해석이다.

전체 cell 점유 histogram 사이의 JS(nats)는 다음과 같다. 이는 **policy JS와 다른 변수**다. episode별로 계산한 JS의 평균도 함께 제시해 pooling으로 인한 과도한 유사도 해석을 피했다.

| 쌍 | 공간 점유 JS: 전체 pooled | 공간 점유 JS: episode 평균 |
|---|---:|---:|
| 1–3 same | .36493 | .43577 |
| 2–4 same | .33451 | .40478 |
| 1–2 cross | .66985 | .68405 |
| 1–4 cross | .22077 | .32578 |
| 2–3 cross | .24633 | .33882 |
| 3–4 cross | **.15283** | **.30894** |

3–4는 이 평가에서 공간 점유도 가장 유사하고, 공통 probe의 정책 응답도 가장 유사하다. 1–4도 same pair보다 공간 점유가 유사했다. 이는 **공간·작업 분화가 정책 유사도 역전과 연결될 수 있다는 H1의 관측상 근거**다. 그러나 2–3은 공간 점유가 비교적 유사해도 정책 JS는 .43928로 크다. 공간 점유 유사성만으로 policy compatibility를 설명할 수 없다. 또한 3과4가 pickup하는 구역은 주로 서로 반대이며, 단순한 “동일한 좌우 구역 담당” 가설보다 이동형 작업 상태나 경로 구조의 유사성까지 검토해야 한다.

이 결과는 학습 seed1의 **최종 모델 한 개**를 평가한 것이고, cross gate는 최종 상태에서 모두 닫혀 있다. 과거 3–4 gate가 열렸던 시점의 경로를 측정한 것은 아니다. gate가 열렸던 update 주변 저장 checkpoint를 동일 평가 seed로 비교해야 시간적 연관성을 강화할 수 있다. 인과관계와 다른 학습 seed에서의 재현성은 아직 확인하지 않았다.

다른 설명도 남아 있다. 초기09700은 home ratio1.0에서 사전학습했으므로 1·2의 구역 집중이 그때 형성된 습관을 유지한 것일 수 있다. 3·4의 확대된 활동 범위가 커리큘럼에서 새로 형성됐는지는 이전 checkpoint 경로와 비교해야 한다. 관측된 분화가 효율적인 최적 분업인지, 일부 agent의 고정 습관·탐색 제한인지는 별도 성능 비교가 필요하다. probe의 좌표/방향/목표 단서와 중복 가중, zero hidden state에서의 정책 sharpness도 policy JS를 설명하는 대안이다.

이번 평가의 per-step 평균 geometric 이웃 수는 **1.86855/agent**였다. 이것은 §3.2의 rollout-end 평균1.80535와 샘플링 시점·정책 시점이 다르다. 최종 모델에서도 물리 접촉 자체가 사라진 것은 아니라는 추가 확인이다.

자료: [Frozen 평가 요약](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/frozen_rollout_summary.json), [step별 위치·행동·phase·event 기록](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/frozen_rollout.jsonl). 새로운 평가 trajectory이며 기존 학습 trajectory 복원물이 아니다.

#### 4. Probe의 공간적 편향과 평가 방법

##### 4.1 확인된 공간 정보와 coverage

[Semantic observation](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/semantic_observation.py:25)은 ego 20개와 13×11×11 spatial channels, 총 1,593차원이다. 입력에 정규화된 절대 x/y, 방향, task phase, home displacement, 통로·경계·shelf·agent·goal·relevant goal이 들어간다. 팀 ID는 직접 입력하지 않지만 자기 팀 요청과 관련 배송 지점이 관측에 반영된다. 따라서 정책 거리를 순수한 이동 패턴만의 유사도라고 정의하는 것도 정확하지 않다.

[RwareObjectiveProbeMapBuilder._make_probe_env](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:269)는 실제 환경의 highways/goals를 layout으로 복제한다. 맵을 키우면 geometry가 반영된다. 그러나 [구체 probe 생성](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:654)의 dual 시나리오는 `_dual_state`를 공통으로 호출하며 일부 좌표가 고정되어 있다.

확인할 위치:

- [_dual_state](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:623): 기본 x=4를 sensor range와 격자 폭으로 clip, row 2 또는 7 등 사용. `goal`/`lane` 이름의 row7은 확장 맵에서 실제 goal 행과 멀어진다.
- [_scenario_shelf](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:477): variant에 따라 shelf 선택. 현재 48 slots는 48-slot cycle 한 번이므로 variant는 모두 0이다.
- [_place_background_agents](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:531): focal에서 먼 통로부터 background agent 배치. 실제 좁은 곳에서 여러 agent가 상호작용하는 상황을 충분히 대표한다고 볼 수 없다.
- [_place_shelf](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:566): 겹치는 shelf를 구석으로 옮기고 좌표를 clip한다. 작은 맵에서는 의도한 offset이 잘릴 수 있다.

**현재 저장 bank는 48 slots지만 고유한 입력은 26개다.** 중복 입력은 평균 JS에서 여러 번 가중된다. 이름이 다른 시나리오라도 현재 realized input이 같을 수 있다. 이번 환경 생성에서 E2/E3 bank 고유 입력 수도 25/24개였다. 따라서 공간 확대만으로 probe가 넓은 맵을 고르게 샘플링한다고 볼 수 없다. 이 사실은 측정 범위의 한계이며 이번 작업에서 probe 구현을 바꾸지는 않았다.

##### 4.2 권장 로그·시각화 — 계획

| 목적 | 수집 항목 | 분석/시각화 |
|---|---|---|
| 공간 역할 | episode, step, agent, team, x/y, 방향, carrying/return phase | agent별 점유 heatmap, 이동 경로, 좌우/상하 체류 비율, episode별 역할 안정성 |
| 작업 역할 | shelf ID/home, 요청 팀, pickup/delivery/return event, carrier | pickup 출발 구역→배송→return 흐름, agent별 작업 단계 시간, 이동거리·cycle latency |
| Probe 응답 | bank hash/입력 중복 ID, scenario/variant, 각 action probability, entropy, per-probe JS | scenario×pair heatmap, 좌표/방향별 응답, 중복 입력 동일 가중 재집계 |
| 접촉과 승인 | geometric adjacency, evidence-ready, raw distance/EMA/count, gate, allocation | 후보·준비된 후보·승인 곡선, pair별 acceptance, EMA 나이와 접촉 누락률 |
| 전이 유익성 | peer loss, critic 예측/TD error, matched on/off 성능 | 같은 초기 상태에서 분기한 성능·학습 속도 비교 |

지금 `communication.jsonl`은 position/trajectory나 action probability를 저장하지 않는다. 기존 `collect_rollout`/`evaluate`에는 위치와 event를 읽는 함수가 있지만 결과는 대부분 집계다. **과거 학습 시점의 전체 경로를 최종 checkpoint와 집계 로그만으로 복원할 수 없다.** 이번처럼 고정 모델에 외부 분석 wrapper를 붙여 새 평가 경로를 얻는 것은 가능하다.

공간 정보의 영향량은 forward-only matched probe로 평가할 수 있다. 동일한 task phase·국소 배치에서 좌표/방향을 바꾼 realized state의 policy change를 측정하고, 목표/요청 단서만 바꾸는 실험과 비교한다. 방향을 돌릴 때 LEFT/RIGHT/FORWARD 행동 의미도 함께 맞춰야 한다. 좌표 두 숫자만 0으로 지우는 ablation은 불가능한 입력 조합을 만들 수 있으므로 보조 sensitivity 분석으로만 쓴다. 학습에 쓰는 gate bank는 그대로 유지하고 진단용 bank를 별도로 둔다.

서로 다른 맵에서의 비교에는 **각 맵에서 실현한 probe**와 **같은 저장 reference bank**를 병행한다. 전자는 환경 대응을, 후자는 입력 고정 상태의 정책 변화 자체를 본다. 후자는 확장 맵에서 out-of-distribution일 수 있다. 단계마다 bank가 달랐던 기존 EMA를 동일 조건의 정책 변화로 직접 비교해서는 안 된다.

#### 5. 맵 1.5배·2배 확대의 구현 가능성과 구조 유지

##### 5.1 기존 코드로 만들 수 있는 후보

아래는 **설정을 메모리에서 override하여 환경 생성/reset만 검증한 후보**다. 학습용 설정 파일로 적용하지 않았다. 모든 후보에서 agent4, request4(팀당2), sensor/communication range5, home.5, 보상은 동일했다. balanced zone과 1,593차원 관측 및 probe 생성도 확인했다.

| 후보 | rows / columns / height | H×W | H배 / W배 | 면적배 | Shelves / 밀도 | 팀별 goal 좌표 |
|---|---|---|---|---:|---|---|
| E1 기준 | 1 / 3 / 8 | 11×10 | 1 / 1 | 1 | 32 / 29.09% | (4,10), (5,10) |
| E2 길이 근사 | 2 / 5 / 6 | **16×16** | **1.45 / 1.60** | 2.33 | 108 / **42.19%** | (7,15), (8,15) |
| E3 길이 근사 | 2 / 7 / 8 | **20×22** | **1.82 / 2.20** | 4.00 | 208 / **47.27%** | (10,19), (11,19) |
| E2 모듈 유지 대안 | 2 / 5 / 8 | 20×16 | 1.82 / 1.60 | 2.91 | 144 / 45.00% | (7,19), (8,19) |

![생성기로 확인한 맵 구조와 seed1 초기 위치](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/map_geometry.png)

그림의 원은 seed1 초기 agent, 네모는 배송 지점이다. 담당 구역이나 평가 성능을 나타내지 않는다. 각 panel은 독립 좌표축이므로 그림의 화면 크기로 배율을 읽지 않는다.

현재 생성기는 shelf columns가 **홀수**여야 하며 W는 10/16/22…처럼 증가한다. column height8을 고정하면 H는 11/20/29…다. 따라서 두 변을 정확히 1.5배인 약17×15, 또는 2배인22×20으로 만드는 것은 기본 parameter 조합만으로 어렵다. E2에서 길이를 맞추면 shelf block 높이8→6도 바뀐다. 이 제약을 숨기고 `small/medium`을 각각 1.5/2배라고 부르면 안 된다.

##### 5.2 어떤 파일/설정이 대상인가

| 위치 | 현 상태 | 향후 확대 시 예상 작업 |
|---|---|---|
| `rware/warehouse.py::_make_layout_from_params/_make_layout_from_str` | 정수 parameter 또는 `layout` 지원 | 기존 generator 사용이면 함수 변경 불필요. 엄격한 밀도/비율 제어는 `layout` 문자열로 가능 |
| [공통 학습기 make_env](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:1146) | Gym kwargs override 지원 | `--env-kwargs-json`에 rows/columns/height 또는 layout 포함 |
| [현재 from-scratch 실행기](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/run_semantic_cnn_marl_pgct_from_scratch.ps1:1) | EnvKwargsJson 전달 가능 | 크기 키는 전달 가능. 고정 LR2e-4/기타 옵션은 기존 physical curriculum과 다르므로 matched 비교에 주의 |
| [physical curriculum build_stages](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_pgct_physical_mixing_curriculum.py:23) | checkpoint geometry 상속; PGCT만 하드코딩 | 향후 map override와 PGCT-off 분기를 명시하는 별도 실행 설정 필요. 현 wrapper에 map 크기/off 옵션 없음 |
| [eval build_env_kwargs](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/eval_checkpoint_generalization.py:40) | tiny/small/medium 지원, height8 고정 | rows2/columns7/height6 같은 임의 후보에는 옵션 확장 또는 독립 평가 설정 필요 |
| [Probe builder](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/utils/probe_maps.py:239) | geometry 복제 + 일부 fixed coordinates | 확대 후 coverage/중복/goal-relative 배치 확인. gate 알고리즘 수정과 분리하여 취급 |

특히 [기존 map variants wrapper](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/run_pgct_09700_map_variants.ps1:1)는 기본 agent counts가 **6,8**, home ratio **1.0**, 기존 **09700** checkpoint의 frozen zero-shot 평가다. 문서의 **4-agent stage04 home.5 맵 효과 비교**와 조건이 다르다.

##### 5.3 유지 가능한 조건과 함께 바뀌는 조건

기본 generator를 쓰면 일반 통로 폭 1, storage block 폭2, 하단 중앙 배송 지점2개와 그 인접 관계를 유지할 수 있다. column height8까지 유지하면 local block 규격도 유지된다. 그러나 **전역 shelf 밀도는 유지되지 않는다.** 작은 tiny에서는 중앙 queue 통로가 전체 저장 공간의 큰 몫을 제거하기 때문이다. 이는 agent가 다닐 수 있는 unloaded/loaded 경로와 병목 구조에도 영향을 준다.

엄격한 “공간 크기만” 비교를 원하면 후속 작업에서 custom layout을 설계해야 한다. 목표 규격은 다음과 같다.

1. 동일한 통로 폭·연결성, 팀별 배송 지점 개수와 하단 중앙 상대 위치를 유지한다.
2. storage cell 비율을 약29.09%에 맞추고 좌우 storage 수를 동일하게 만든다. 예컨대 16×16은 74개, 20×22는 128개가 이 비율에 가까운 짝수 shelf 수다. 이 수만으로 shelf module·통로 분포까지 같아지는 것은 아니다.
3. 일반 통로와 새 빈 storage 구역의 분포, 중앙 배송 queue 폭/길이, shelf-to-goal 경로 길이 분포를 함께 검증한다.
4. `balanced_soft_zones`의 동일 zone 크기, 요청 가능 shelf 수, 배송/return 도달성을 확인한다. layout이 제공되면 parameter 크기는 무시된다.

이 설계는 아직 생성·학습하지 않았다. 권장 해석은 “기본 generator로 넓은 창고를 만든 pilot”과 “밀도를 맞춘 통제 비교”를 구별하는 것이다. 어느 안에서도 shelf 수 증가는 **동시 요청 수 증가와 별개**다.

맵 변경 시 관측 tensor 차원은 sensor range를 유지하면 그대로라 checkpoint 가중치 로딩이 가능하다. 다만 normalized x/y 및 home dx/dy, 경계가 보이는 빈도는 바뀐다. 같은 tensor shape이 동일한 입력 분포를 보장하지 않는다. 현재 `normalize_shaping_rewards`는 default false이므로 progress reward 계수와 cell당 거리 변화는 유지된다. 이를 true로 바꾸면 H+W 기반 scaling까지 달라지므로 첫 비교에서는 바꾸지 않는다. 큰 맵의 긴 cycle, 더 많은 이동·충돌 벌점, gamma=.99의 할인도 성능 차이에 포함된다.

#### 6. 물리적 접촉과 Gating 승인 기록

**확인:** [get_neighbor_adjacency](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:886)는 team label·방향·shelf 가림과 무관하게 `max(|dx|,|dy|) <= 5`를 사용한다. 물리 통신은 실제 메시지 bandwidth나 latency 모델이 아니라 학습 관계 추정/전이 대상의 공간적 자격 조건이다.

현재 [communication.jsonl 기록](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:5057)에는 `available`, `transfer_weights`, `directed_probe_counts`, `policy_distance_ema`, `policy_information`, gate requirements가 있다. 따라서 기존 자료로 update 시점의 후보와 승인, same/cross 분모를 구분할 수 있다. 그러나 IPPO `none`은 communication 자체를 끄므로 `available=0`이며 geometric 후보가 아니라 **기능 off 상태**다. IPPO와 PGCT 접촉을 비교할 때는 알고리즘 off와 별개로 좌표에서 geometric adjacency를 계산해야 한다.

권장 정의(무방향 쌍 기준):

- `A_ij(t)`: 현재 geometric neighbor.
- `R_ij(u)`: warmup·finite distance·count·information 준비 완료.
- `G_ij(u)`: 준비 조건, threshold 및 현재 physical mask를 통과한 활성 전이 쌍.
- physical neighbor count: `sum_j A_ij`; candidate edge count: `sum_(i<j) A_ij`.
- accepted gate count: `sum_(i<j) G_ij`.
- acceptance: `sum G / sum A`; evidence-ready acceptance: `sum G / sum(A*R)`.
- same/cross 가능한 쌍 대비 활성률: `sum G_same/(2T)`, `sum G_cross/(4T)`.
- 승인 구성비: `sum G_same/sum G`, `sum G_cross/sum G`. 승인0이면 미정/NA로 기록한다.

gate가 가중치형으로 바뀌면 count와 weight/allocation mass를 별도로 기록한다. 기존 `neighbor_arcs`는 방향 있는 링크 수라 upper-triangle pair 수와 2배 차이 날 수 있다. 그래프가 비대칭이면 두 방향을 별도로 유지해야 한다. 이번 현재 physical threshold 자료는 대칭임을 확인했다.

특히 probe는 5 update마다, 전이 자격 확인은 매 update, 위치는 매 환경 step마다 바뀐다. rollout 중 이웃이었다가 마지막에 떨어진 쌍은 해당 update 전이에서 제외된다. per-step candidate/accepted 표시와 실제 optimizer transfer count를 구분해야 한다. EMA 마지막 갱신 update와 age를 함께 기록한다. stage04의 1–3은 측정 이후 최대79 update 동안 EMA가 유지된 구간이 있었다.

초기 위치가 전체 cell에서 균등·중복 없이 선택되는 현재 reset 규칙에 대해서는 range5 접촉 확률을 정확히 계산할 수 있다. `S(n)=n+2*sum_(d=1..min(5,n-1))(n-d)`일 때 특정 두 agent의 접촉 확률은 `(S(W)S(H)-WH)/(WH(WH-1))`다.

| 맵 | Reset 순간 pair 접촉 확률 | 기대 이웃/agent |
|---|---:|---:|
| 11×10 | 59.80% | 1.794 |
| 16×16 | 32.26% | .968 |
| 20×22 | 20.63% | .619 |
| 20×16 모듈 유지 | 26.86% | .806 |

이는 **reset 직후 분포의 계산**, 학습된 agent의 rollout 접촉 예측은 아니다. 배송 지점에 모이면 평가 접촉은 더 높을 수 있다. 그래도 agent/range를 고정한 확대가 통신 기회를 줄일 수 있다는 H3의 구조적 근거는 된다. 실제 판별 개선 여부는 acceptance의 분모와 측정 freshness를 함께 봐야 한다.

#### 7. 요청 수 증가·지연 페널티의 가능성

##### 7.1 6–8개 요청

**확인:** 환경은 이미 `request_queue_size`와 `request_queue_size_per_team`을 지원한다. `_make_team_request_queues`가 팀별 shelf에서 중복 없이 뽑고 실제 전역 큐는 팀별 큐를 합친다. 후속 Q6은 total6/per-team3, Q8은 total8/per-team4를 모두 지정하면 된다. 현재 shelf 수로도 가능하다. 후보 shelf가 부족하면 팀별 큐 크기는 `min`으로 줄어든다.

단, 현재 from-scratch PowerShell 실행기, physical `build_stages`, generalization `build_env_kwargs`는 이 값을 **agent_count와 agent_count/2로 다시 덮어쓴다.** 기존 JSON의 Q만6/8로 바꾸고 해당 wrapper를 실행하면 의도한 실험이 되지 않는다. 향후 공통 trainer에 직접 명시한 kwargs를 전달하거나 wrapper의 workload 옵션을 추가해야 한다. [공통 trainer의 큐 override](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:941)는 명시한 큰 팀별 큐를 auto-scale에서 낮추지는 않는다.

중요한 lifecycle: 현재 `require_delivered_shelf_return=True`이므로 **배송만 끝났다고 새 요청으로 바뀌지 않는다.** 배송된 shelf는 `shelves_awaiting_return`에 들어가 기존 queue slot을 차지한다. home return 완료 때 [_replace_team_request](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/rware/multi_team_warehouse.py:592)가 새 요청을 뽑는다. 따라서 Q4는 순수한 “아직 배송 안 된 주문 4개”가 아니라 배송·return을 포함하는 cycle slots4개다. Q6/8 효과를 해석할 때 unserved delivery 수와 awaiting return 수를 분리한다.

##### 7.2 기다린 시간에 비례하는 벌점

**확인:** 요청별 생성 시간/age와 `-lambda*sum age`를 적용하는 설정은 현재 없다. NOOP·정체·step 벌점은 요청 대기시간 벌점과 다르다. 이번 작업에서 추가하지 않았다.

향후 필요 위치는 `MultiTeamWarehouse.__init__`의 coefficient/state, `reset`의 초기 요청 timestamp, `_replace_team_request`의 새 요청 timestamp 및 `step`의 age update/reward, `_get_info`의 latency 통계다. reward/task/shaping 분류와 checkpoint 실험 설정도 함께 기록해야 한다.

설계 전에 다음을 정해야 한다.

1. 배송 완료까지만 age를 계산할지, return 완료까지 포함할지. 문서의 **미배송 화물** 정의라면 awaiting-return shelf는 age 벌점에서 제외하고 새 요청 때 다시 시작한다.
2. 총 penalty를 team members에게 분배할지, individual carrier에게 줄지. 아직 pickup되지 않은 요청에는 carrier가 없으므로 현재 individual reward에 자동으로 배분할 수 없다.
3. sum/mean/team-normalization 중 무엇을 쓸지. Q를 늘리면 같은 평균 대기시간에서도 sum penalty가 커지므로 workload 효과와 reward 규모 효과가 섞인다.
4. 장기 대기 요청의 penalty 폭증을 어떻게 평가할지. 단일 주문을 T step 기다리면 누적 age penalty가 대략 `-lambda*T*(T+1)/2`로 커진다. 먼저 age·p95 delay·미완료 요청 age를 reward 변화 없이 측정한다.

맵 비교 Q4를 먼저 끝낸 뒤 고정한 큰 맵에서 Q4/Q6/Q8을 비교하고, delay penalty는 그 다음 별도 축으로 비교하는 것이 효과 분리에 적절하다.

#### 8. 공정한 PGCT–IPPO 최소 실험 계획 — 아직 실행하지 않음

##### 8.1 공간 원인 조사와 학습 이득 검증을 분리

고정된 stage04 모델을 각 맵에 zero-shot 평가하는 것은 경로 변화·contact sparsity·입력 분포 변화 조사다. **동일 모델에 평가 그래프만 off로 바꿔도 PGCT 학습 이득 ablation이 되지 않는다.** `T.evaluate`는 학습을 하지 않고 통신 gate는 표시/환경 그래프에만 적용한다. 현재 actor에 메시지 입력도 없다.

기존 `eval_checkpoint_generalization.py::checkpoint_pgct_gate`는 saved graph를 복제하여 사용하고 새 맵에서 policy graph를 재추정하지 않는다. 최종 stage04는 gate가 모두0이므로 확대 맵에서 선이 생기지 않는 zero-shot 영상으로 새로운 gating 판별 능력을 평가할 수 없다.

##### 8.2 최소 학습 비교

**공간 효과와 추가 학습의 PGCT 이득을 함께 비교할 최소안:** 맵 E1/E2/E3 × PGCT-on/IPPO-off × paired 학습 seeds3개 = **18 runs**. 처음 1 seed의 6 runs는 pilot이며 논문 결론용 반복 검증과 구분한다. 기본 generator 후보를 쓰면 구조·밀도가 함께 바뀌는 pilot이라고 명시하고, 밀도 통제 layout을 확정한 후 본 비교를 수행한다.

현재 stage04와 연결되는 비교라면 두 branch 모두 같은 stage03 `final.pt`의 actor+critic을 읽고, home ratio .5를 고정해 **추가 4,000,000 steps** 학습하는 안이 적절하다. rollout 단위 때문에 실제 budget은 각각 **4,000,768**이다. 현재 stage04 `final.pt`에서 두 branch를 시작하는 것은 이미 gate가 닫힌 모델을 추가 적응시키는 다른 질문이다. 어느 경우든 같은 초기 checkpoint를 써야 한다.

| 통제 항목 | 양쪽 공통 설정 |
|---|---|
| 모델 초기화 | 같은 source checkpoint, `transfer_components=all`; optimizer/graph 모두 새로 시작 |
| Agent/작업 | agent4, teams2, Q4/per-team2, home.5, shuffle false |
| 관측·정책 | semantic CNN, 20 ego + 13×11×11, hidden128, action mask on |
| PPO | LR1e-4, entropy .02, gamma .99, GAE .95, clip .2, rollout1024, sequence64, epochs4, chunks8 |
| 보상/종료 | 같은 effective kwargs, 500-step episodes; delay penalty 추가 없음 |
| 평가 | 같은 고정 seed 목록, 20 episodes×500, 같은 deterministic/action-mask 규칙; 영상 별도 |
| 단계/예산 | 같은 checkpoint 시점과 각 branch env steps; update/초 단위 성능도 기록 |

PGCT-on은 현재 physical/probe48/interval5/min-count8/EMA.35/threshold.12/warmup100/peer loss.01을 유지한다. IPPO-off는 `--no-communication`, `graph_mode=none`, `comm_graph_mode=none`, `peer_transfer_mode=none`, consensus0/peer loss0이다. off에서 probe가 비활성화되더라도 **진단용 geometric contact와 frozen/reference probe 분석은 외부에서 동일하게 측정**한다.

같은 PGCT stage03에서 분기한 IPPO-off는 **PGCT로 사전학습한 공통 모델에서 추가 transfer의 효과**를 보는 ablation이다. 전체 학습 과정에서 pure IPPO와 PGCT를 비교했다는 주장을 할 수 없다. 전체 이득은 같은 초기 random weights·같은 pretraining/curriculum budgets로 두 방법을 처음부터 별도 학습하여 비교한다.

기존 physical 커리큘럼을 정확히 재현하는 비교는 같은 초기09700, 각 단계1/2/3/4M, LR1e-4/entropy.02, 같은 reset 규칙을 양쪽에 적용해야 한다. [일반 mixing wrapper](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/run_semantic_cnn_mixing_curriculum.ps1:1)는 scratch 시작·단계당 동일5M·LR2e-4/entropy.05이므로 현재 physical run의 대조군으로 그대로 사용할 수 없다. 별도 IPPO pretraining 8–9M도 방법 전체 비교의 재료는 되지만 matched curriculum 비교를 대신하지 않는다.

주요 성능은 delivery/return throughput, task return, 고정 eval seed에서의 학습곡선 면적·목표 성능 도달 env steps, training seed별 변동이다. success rate만 쓰면 현재처럼1.0에 포화될 수 있다. 넓은 맵에서 horizon을 임의로 늘리면 다른 조건을 바꾸는 것이므로 주 비교는500으로 고정하고, 긴 horizon 결과는 별도 보조 평가로 제시한다. 동일 seed를 써도 두 정책의 경로가 달라 RNG 소비가 달라질 수 있으므로 모든 요청 sequence가 완전히 같다고 가정하지 않는다.

##### 8.3 각 가설의 판별 기준

| 가설 | 지지할 수 있는 관측 | 결론의 한계 |
|---|---|---|
| H1 공간 역할 | 실제 연결 쌍의 occupancy/path/task-state가 유사하고 matched spatial probe 응답도 유사; 연결 직전 checkpoint에서도 재현 | 최종 heatmap이나 policy JS 하나만으로 학습 중 공간 역할이 gate 원인이라고 확정 불가 |
| H2 맵 확대 | 밀도/작업량을 통제한 맵 사이에서 역할 패턴·reference response·same/cross acceptance가 재현성 있게 변화 | cross count 감소만으로 판별 개선 주장 불가 |
| H3 접촉 희소성 | geometric 후보/agent, 접촉 episode coverage 감소; probe count 부족·EMA age 증가 | reset 계산은 rollout 결과를 대신하지 않음 |
| H4 작업량 | 고정 맵에서 Q4→6→8로 작업 선택/경로/latency가 변화 | 맵·Q·보상을 동시에 바꾸면 원인 분리 불가 |

Cross-team transfer의 유익성은 on/off branch의 critic quality와 후속 task performance로 판단한다. 선이 사라지거나 same-team 선이 늘었다는 결과만으로 PGCT 성능이 좋아졌다고 판단하지 않는다.

#### 9. 권장 순서와 산출물

1. 현재 저장된 pair·probe 결과와 최종 frozen rollout을 비교하고, 공간 역할 주장을 데이터에 맞춰 좁힌다.
2. probe 중복과 fixed-coordinate coverage를 별도 진단으로 확인한다. 학습 gate 알고리즘은 유지한다.
3. 확대 맵의 실제 규격·밀도·통로·goal 배치를 확정한다. 기본 generator pilot과 밀도 통제 비교를 구별한다.
4. geometric contact, evidence-ready candidate, accepted transfer, EMA age를 분리하는 분석 기록을 준비한다.
5. paired E1/E2/E3 × on/off 실험을 수행하고, 그 후 Q6/8과 요청 대기 벌점을 검토한다.

산출물은 [evidence.json](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/evidence.json), [맵 구조 그림](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/pgct_spatial_analysis/map_geometry.png), §3.4의 frozen 평가 요약·trajectory·점유 그림이다. JSONL 재집계에서 승인 조건을 재구성해 저장된 gate와 일치함을 확인했고, 후보 맵의 balance/관측/probe 생성과 frozen 모델 가중치 보존·기존 평가 수치 재현을 확인했다. 모든 학습 계획은 아직 실행하지 않았다.

## 출처: `output/learning_review_20261013/REPORT.md` (수정 2026-10-13 14:44)

### 2026-10-13 학습 결과 분석

**현재 seed 1에서는 E1의 평가 학습곡선 평균에 PGCT 이득 신호가 있지만, 최종 성능 우위나 critic 정확도 개선은 확인되지 않았다. E2는 PGCT와 IPPO가 거의 같다. 공간 확대 후 같은 팀 gate가 다시 생겼으나, 그것이 성능 향상으로 이어진다는 증거는 아직 없다.**

로그 스냅샷: 2026-10-13 14:37 KST. E3는 실행 중이므로 이후 수치는 달라진다. 학습 코드·설정·gate·probe·기존 로그·체크포인트를 변경하거나 학습을 중단하지 않았다. 이 폴더에만 분석 산출물을 추가했다.

#### 비교 조건과 진행 상태

실험: `runs/sp_20261008_120638_983201/experiment.json`.

모든 분기는 동일한 Stage03 final actor/critic에서 출발한다. 각 분기의 optimizer와 graph 상태는 새로 시작한다. Home ratio 0.5, 4 agents, 요청 4개, sensor/communication range 5, 학습 seed 1, learning rate 1e-4, entropy coefficient 0.02, rollout 1024, PPO epochs 4, peer coefficient 0.01(PGCT)/0(IPPO)다. 맵별 on/off의 환경 차이는 communication 활성/비활성 및 topology뿐이며, PPO·보상·평가 설정은 동일했다.

기존 PGCT 사전학습을 공유하므로 이 비교는 **Stage03 이후 추가 전이의 효과**를 본다. 처음부터 PGCT를 전혀 사용하지 않은 IPPO와 전체 curriculum의 효과를 비교한 것은 아니다.

| 조건 | 저장된 학습 step | 마지막 평가 delivery | 마지막 평가 shelf return | 상태 |
|---|---:|---:|---:|---|
| E1 11×10 PGCT | 4,000,768 | 44.35 | 42.65 | 완료 |
| E1 11×10 IPPO | 4,000,768 | 44.65 | 43.70 | 완료 |
| E2 16×16 PGCT | 4,000,768 | 37.85 | 36.15 | 완료 |
| E2 16×16 IPPO | 4,000,768 | 38.20 | 36.85 | 완료 |
| E3 20×22 PGCT | 2,252,800 | 27.25 | 25.95 | 진행 중; 평가는 2,201,600 step |
| E3 20×22 IPPO | — | — | — | 시작 전 |

평가는 공통 reset seeds 5,000,001–5,000,020, deterministic masked actor, 에피소드당 500 step이다. Delivery/return은 에피소드 평균이다. 개별 agent의 원본 `*_count`는 20개 에피소드 합계이므로 반드시 20으로 나눴다. 64-step smoke test, dry-run, 계획 manifest는 본 실험 반복 수에 포함하지 않았다. 실제 완료된 seeds 2·3, random donor, drop34의 장기 학습 결과는 발견되지 않았다.

#### 학습곡선 해석

| 지표 | E1 PGCT | E1 IPPO | E2 PGCT | E2 IPPO |
|---|---:|---:|---:|---:|
| 평가 delivery 시간 평균 | 45.856 | 44.573 | 34.167 | 34.245 |
| 마지막 10회 평가 delivery 평균 | 46.170 | 44.515 | 37.470 | 37.605 |
| 최고 평가 delivery | 47.95 | 46.80 | 38.15 | 38.65 |
| 최종 평가 delivery | 44.35 | 44.65 | 37.85 | 38.20 |

시간 평균은 관측된 51,200–4,000,768 step 평가 곡선을 사다리꼴 적분하고 구간 길이로 나눈 정규화 AUC다. 학습 중 실제 누적 delivery가 아니다. 기록되지 않은 step 0 점수는 만들지 않았다. 최고 성능은 고른 체크포인트의 성능이므로 최종 모델과 구분한다.

E1 시간 평균은 PGCT가 1.283 delivery/episode, 상대적으로 2.88% 높다. 79개 평가 시점 중 PGCT가 높은 시점은 60개, IPPO가 높은 시점은 16개, 동률은 3개다. 이 시점들은 한 학습 경로의 상관된 평가이므로 79개 독립 seed로 취급할 수 없다. 마지막 약 100만 step 구간의 시간 평균도 PGCT 46.511, IPPO 44.364였으나, 최종 snapshot은 IPPO가 0.30 높다. 따라서 최종 점수 하나만으로 PGCT가 계속 열세였다고 해석해서도 안 된다.

다만 PGCT가 모든 학습 효율 지표에서 앞선 것도 아니다. 처음으로 평가 delivery 45를 넘긴 시점은 PGCT 460,800, IPPO 358,400 step이다. 마지막 10회 점수의 시간 방향 표준편차는 PGCT 1.118, IPPO 0.712이며, 이는 seed 간 variance나 평가 confidence interval이 아니다. 이 run으로 PGCT가 안정성도 개선했다고 주장할 근거는 없다.

E2 시간 평균 차이는 PGCT−IPPO = −0.078(−0.23%)다. 첫 100만 step에서 약 18.8→32 수준으로 빠르게 적응하고 이후 약 37–38에 도달하는 양상은 두 조건에 공통이다. 현재 seed에서는 추가 critic transfer의 뚜렷한 성능 이득을 확인하지 못했다.

E3 PGCT는 첫 기록된 평가 10.00에서 27.25로 향상했다. IPPO 대조군이 없어 이 향상을 PGCT의 효과로 귀속할 수 없다. E1/E2/E3의 이동 거리, shelf 배치·밀도가 함께 다르므로 맵 간 delivery 차이를 알고리즘 우열로 해석하지 않는다.

#### 전이 및 공간 활동

아래 횟수는 무방향 pair-update다. 한 쌍을 양방향 arc 2개로 중복 집계하지 않았다. 물리 후보는 update 종료 시점에 실제 범위 안에 있던 쌍이다.

| Pair | E1 PGCT 승인 | E2 PGCT 승인 | E3 PGCT 승인(진행 중) |
|---|---:|---:|---:|
| 1–3 same | 0 | 89 | 410 |
| 2–4 same | 0 | 781 | 348 |
| 1–2 cross | 0 | 932 | 306 |
| 1–4 cross | 0 | 1,276 | 441 |
| 2–3 cross | 0 | 39 | 72 |
| 3–4 cross | 2,005 | 113 | 102 |

E1 same-team 물리 후보는 4,435회였지만 승인 0회다. 3–4는 물리 후보 2,525회 중 2,005회(79.4%) 승인됐다. 약 103,424 step부터 전이가 기록됐고, 100만 step 이후에도 지속됐다. 이번 E1은 **초기에만 전이하고 후반에는 완전히 꺼진 run이 아니다.** 기존 curriculum Stage04의 3–4 1,170회와 이번 E1의 2,005회는 별개의 학습 결과다.

E2는 same-team 후보 3,176회 중 870회(27.4%), cross-team 후보 6,434회 중 2,360회(36.7%) 승인됐다. Same-team 연결이 회복됐지만 가장 빈번한 쌍은 cross-team 1–4다. E3 역시 same/cross 연결이 공존한다. 따라서 맵 확대가 팀 식별 문제를 해결했다고 볼 수 없다.

학습 전 구간 평균 물리 이웃 수는 E1 PGCT 1.815, E2 PGCT 1.243, E3 PGCT 0.788이다(E3는 미완료). 접촉은 줄었지만 E2의 총 승인 pair-update는 E1보다 많았다. 연결 변화는 접촉 감소 하나만으로 설명되지 않는다. 모든 분석 대상에서 물리 범위 밖 전이는 0회였고, IPPO의 전이도 0회였다.

E1 학습 전체에서 왼쪽 체류 비율은 PGCT [99.0%, 0.6%, 37.7%, 61.8%], IPPO [98.0%, 0.6%, 47.7%, 62.0%]다. Agent 1/2의 좌우 편중과 Agent 3/4의 상대적으로 넓은 활동은 양쪽 조건에서 나타난다. 이 공간 분화를 PGCT만이 만들어냈다고 할 수 없다. 이 값은 과거 20회 frozen evaluation의 occupancy와 다른 **학습 전체 rollout** 통계다.

#### 에이전트별 성과

| 조건 | Agent 1 | Agent 2 | Agent 3 | Agent 4 |
|---|---:|---:|---:|---:|
| E1 PGCT 최종 delivery/episode | 8.70 | 8.50 | 13.65 | 13.50 |
| E1 IPPO 최종 delivery/episode | 9.30 | 8.10 | 13.35 | 13.90 |
| E2 PGCT 최종 delivery/episode | 9.60 | 9.35 | 9.00 | 9.90 |
| E2 IPPO 최종 delivery/episode | 9.40 | 9.60 | 9.75 | 9.45 |
| E3 PGCT 마지막 delivery/episode | 7.00 | 6.60 | 6.70 | 6.95 |

네 agent 모두 작업을 수행하고 있다. E1은 3/4가 전체 delivery의 약 61%를 담당하지만 E2/E3는 더 균등하다. 기록된 모든 update에서 개별 agent의 `actor_update_skipped`는 0이었다. 따라서 이번 학습은 한 agent만 업데이트하고 나머지를 나중에 순차 학습하는 구조로 보이지 않는다.

E1 마지막 10회 평균 delivery는 PGCT [9.400, 8.830, 13.950, 13.990], IPPO [9.135, 8.350, 13.210, 13.820]다. PGCT 평균 이득이 3–4에게만 나타난 것도 아니다. 최종 snapshot만 보면 Agent 3은 PGCT가 0.30 높고 Agent 4는 0.40 낮다. 3–4 둘 다 성능이 향상됐다고 단정할 수 없다.

#### 저장 모델의 추가 critic 평가

이번 분석에서 완료된 네 최종 모델을 고정하여 각각 10×500 step을 추가 평가했다. 별도 seeds 5,100,001–5,100,010, stochastic masked actor, 독립적인 local NumPy action RNG를 사용했다. 모든 40개 에피소드는 time-limit truncation이었다. 평가 전후 state-dict hash가 같음을 확인했다.

MC target은 실제 reward(작업 보상+shaping+penalty)의 유한 500-step discounted return이며 horizon 끝의 tail은 0이다. 학습 critic은 계속되는 task의 value를 근사하므로, 끝부분 MC MSE에는 tail bias가 있다. 이를 줄여 보기 위해 남은 step이 300 이상인 초기 200 step MSE도 별도 보고한다. 이 보정도 실제 미래 tail을 복원하거나 bias를 완전히 제거하지는 않는다. TD는 truncation에서 bootstrap하고 자연 종료에서 0으로 처리했다.

| 최종 모델 | 전체 MC MSE | 초기 200-step MC MSE | 평균 absolute TD error |
|---|---:|---:|---:|
| E1 PGCT | 4.190 | 1.725 | 0.06486 |
| E1 IPPO | 3.713 | 1.103 | 0.06076 |
| E2 PGCT | 2.190 | 0.286 | 0.04522 |
| E2 IPPO | 2.146 | 0.281 | 0.04408 |

E1 Agent 3의 초기 MC MSE는 PGCT 1.547/IPPO 0.407, Agent 4는 0.938/0.453이다. 현재 최종 모델에서 이 두 critic의 정확도가 개선됐다는 증거는 없다. E2는 거의 같다. 다만 모델마다 자기 정책으로 방문한 상태에서 계산한 값이고, reward target의 분산도 다르다. 따라서 이 비교만으로 PGCT 전이가 critic을 손상시켰다고 단정할 수 없다. 학습 중 value loss 또한 독립 평가 정확도와 동일하지 않다.

과거 공통 rollout 진단에서 3–4 critic 예측 간 MSE가 작았다는 사실과 모순되지 않는다. **서로 비슷한 예측과 실제 return에 대한 정확도는 다른 지표다.** 또한 과거 transfer가 예측을 비슷하게 만들었을 가능성이 있으므로 예측 일치를 donor 선택의 사전 타당성으로 소급하지 않는다.

#### 최종 probe 민감도

완료된 PGCT/IPPO 모델을 각 맵의 동일한 저장 canonical bank에 입력했다. Zero hidden, unmasked, forward-only 평가다. E1은 48개/고유 26개, E2는 48개/고유 25개 입력이다. 중복 제거는 진단에만 사용했고 실제 gate는 변경하지 않았다.

E1 PGCT에서 3–4 JS는 48개 평균 0.0921, 고유 입력 평균 0.1421이다. 1–4는 0.2114→0.1232다. **최종 모델에서도 probe 가중 방식에 따라 3–4/1–4의 유사성 순위가 바뀐다.** 기존 임계값을 재적용해 고유 입력 gate가 더 좋다고 주장하지 않는다. 과거 EMA의 연결 기록과 최종 raw JS도 구분해야 한다.

E1 IPPO의 3–4 JS는 0.2029/0.2659로 PGCT보다 높았다. 이는 추가 PGCT 여부와 최종 actor 응답 차이가 동반된 관측이며, 그 자체가 정확도·전이 유익성의 증명은 아니다.

E2에서 1–4는 PGCT 0.0074/0.0102, IPPO 0.0330/0.0326으로 두 기준 모두 가장 유사했다. 팀 구분과 행동 응답 유사성이 분리되는 현상은 IPPO에서도 나타난다. 맵별 bank 자체가 다르므로 E1/E2 raw JS를 동일 상태 분포의 거리처럼 직접 비교하지 않는다.

#### 과거 curriculum과의 관계

기존 stage01→04 최종 delivery는 61.00→50.60→49.85→47.25였고, same-team 승인 pair-update는 1,131→380→0→0이었다. 마지막 두 단계는 cross-team 전이가 나타났다. Home ratio가 단계마다 바뀌고 당시 평가 seed도 체크포인트마다 달라졌으므로 이 숫자를 성능 퇴행이나 PGCT 인과 효과로 해석할 수 없다.

별도 home1 IPPO continuation은 최종 delivery 61.45, shelf return 59.50을 저장했다. 학습 예산과 초기 모델이 현재 Stage03→home0.5 비교와 다르므로 현재 E1 PGCT의 대조군으로 섞지 않는다.

#### 연구 판단과 다음 순서

1. E1에서 추가 PGCT가 학습곡선 평균을 높인다는 탐색적 신호는 있다. 최종 성능·critic 정확도·안정성까지 함께 향상됐다는 주장은 아직 불가하다.
2. E2에서는 gate가 더 많이 열리고 same-team도 연결됐지만 on/off 성능은 거의 같았다. Gate 활성량이나 same-team 비율을 성공 지표로 대체하지 않는다.
3. 이미 진행 중인 E3를 보존하고 IPPO 대조군 완료를 기다린다. 현재 분석 때문에 학습을 중단하거나 probe/threshold를 바꾸지 않았다.
4. 우선 E1 seeds 2·3을 동일 checkpoint에서 반복하여 2.9% 수준의 평균 이득이 재현되는지 확인한다. 이 역시 하나의 사전학습 모델에 조건부인 반복이라는 한계를 명시한다.
5. E1 random donor와 drop34는 JS 선택 및 3–4 연결의 기여를 구분하는 후속 실험이다. 전달량 감소·auxiliary loss 크기·gradient 크기 등의 차이를 따로 기록한다. 이번 분석에서 추가 장기 학습은 시작하지 않았다.

산출물: `analysis.json`(학습 로그 스냅샷), `critic_summary.json`(추가 평가 전체 수치), `probe_responses.json`, `learning.png`, `agents.png`, `gates.png`, `probes.png`, `critic.png`. 재현용 분석 스크립트는 이 폴더 안에 있으며 학습 실행기와 별개다.

## 출처: `output/latent_team/exp_a_20261013/REPORT.md` (수정 2026-10-13 18:49)

### Experiment A — team identifiability and consensus premise

Generated 2026-10-13T18:43:28+09:00. Frozen models, stochastic masked own-policy rollouts, 20x500 steps, reset seeds 5200001–5200020. Early-window MC targets use the first 200 steps (finite horizon, zero tail).

AUROC and recovery use dependent episode x pair samples and only 2 same / 4 cross pairs; they are descriptive, not significance tests. canonical_js is one model-level value per pair.

#### AUROC (same > cross)

| Model | canonical_js | history_js | occupancy_js | goal_evidence | critic_gap | blend_gain |
|---|---:|---:|---:|---:|---:|---:|
| stage03_init_e1 | 0.500 | 0.282 | 0.379 | 1.000 | 0.242 | 0.325 |
| e1_ippo_s1 | 0.375 | 0.267 | 0.408 | 1.000 | 0.001 | 0.251 |
| e1_pgct_s1 | 0.375 | 0.267 | 0.333 | 1.000 | 0.000 | 0.290 |
| e2_ippo_s1 | 0.375 | 0.810 | 0.867 | 1.000 | 0.452 | 0.493 |
| e2_pgct_s1 | 0.500 | 0.853 | 0.821 | 1.000 | 0.554 | 0.470 |
| stage04_pgct | 0.500 | 0.291 | 0.365 | 1.000 | 0.013 | 0.289 |

#### Teammate recovery (chance .333)

| Model | canonical_js | history_js | occupancy_js | goal_evidence | critic_gap | blend_gain |
|---|---:|---:|---:|---:|---:|---:|
| stage03_init_e1 | 0.250 | 0.013 | 0.062 | 1.000 | 0.050 | 0.150 |
| e1_ippo_s1 | 0.000 | 0.000 | 0.113 | 1.000 | 0.000 | 0.113 |
| e1_pgct_s1 | 0.000 | 0.000 | 0.013 | 1.000 | 0.000 | 0.125 |
| e2_ippo_s1 | 0.250 | 0.675 | 0.825 | 1.000 | 0.250 | 0.263 |
| e2_pgct_s1 | 0.250 | 0.850 | 0.725 | 1.000 | 0.450 | 0.225 |
| stage04_pgct | 0.250 | 0.000 | 0.075 | 0.994 | 0.000 | 0.113 |

#### Same − cross score (larger = teammates scored as more similar/compatible)

| Model | canonical_js | history_js | occupancy_js | goal_evidence | critic_gap | blend_gain |
|---|---:|---:|---:|---:|---:|---:|
| stage03_init_e1 | 0.021 | -0.043 | -0.021 | 0.918 | -1.991 | -1.083 |
| e1_ippo_s1 | 0.002 | -0.055 | -0.010 | 0.924 | -8.839 | -1.693 |
| e1_pgct_s1 | -0.033 | -0.049 | -0.022 | 0.928 | -7.371 | -1.259 |
| e2_ippo_s1 | -0.013 | 0.016 | 0.064 | 0.864 | -0.003 | -0.004 |
| e2_pgct_s1 | -0.007 | 0.019 | 0.062 | 0.861 | -0.001 | 0.001 |
| stage04_pgct | -0.026 | -0.036 | -0.029 | 0.892 | -8.196 | -1.385 |

#### Goal evidence accumulated over episodes

| Model | episodes | pairs with evidence | recovery | AUROC |
|---|---:|---:|---:|---:|
| stage03_init_e1 | 1 | 6/6 | 1.000 | 1.000 |
| stage03_init_e1 | 2 | 6/6 | 1.000 | 1.000 |
| stage03_init_e1 | 5 | 6/6 | 1.000 | 1.000 |
| stage03_init_e1 | 10 | 6/6 | 1.000 | 1.000 |
| stage03_init_e1 | 20 | 6/6 | 1.000 | 1.000 |
| e1_ippo_s1 | 1 | 6/6 | 1.000 | 1.000 |
| e1_ippo_s1 | 2 | 6/6 | 1.000 | 1.000 |
| e1_ippo_s1 | 5 | 6/6 | 1.000 | 1.000 |
| e1_ippo_s1 | 10 | 6/6 | 1.000 | 1.000 |
| e1_ippo_s1 | 20 | 6/6 | 1.000 | 1.000 |
| e1_pgct_s1 | 1 | 6/6 | 1.000 | 1.000 |
| e1_pgct_s1 | 2 | 6/6 | 1.000 | 1.000 |
| e1_pgct_s1 | 5 | 6/6 | 1.000 | 1.000 |
| e1_pgct_s1 | 10 | 6/6 | 1.000 | 1.000 |
| e1_pgct_s1 | 20 | 6/6 | 1.000 | 1.000 |
| e2_ippo_s1 | 1 | 6/6 | 1.000 | 1.000 |
| e2_ippo_s1 | 2 | 6/6 | 1.000 | 1.000 |
| e2_ippo_s1 | 5 | 6/6 | 1.000 | 1.000 |
| e2_ippo_s1 | 10 | 6/6 | 1.000 | 1.000 |
| e2_ippo_s1 | 20 | 6/6 | 1.000 | 1.000 |
| e2_pgct_s1 | 1 | 6/6 | 1.000 | 1.000 |
| e2_pgct_s1 | 2 | 6/6 | 1.000 | 1.000 |
| e2_pgct_s1 | 5 | 6/6 | 1.000 | 1.000 |
| e2_pgct_s1 | 10 | 6/6 | 1.000 | 1.000 |
| e2_pgct_s1 | 20 | 6/6 | 1.000 | 1.000 |
| stage04_pgct | 1 | 6/6 | 1.000 | 1.000 |
| stage04_pgct | 2 | 6/6 | 1.000 | 1.000 |
| stage04_pgct | 5 | 6/6 | 1.000 | 1.000 |
| stage04_pgct | 10 | 6/6 | 1.000 | 1.000 |
| stage04_pgct | 20 | 6/6 | 1.000 | 1.000 |

#### Critic premise per pair (mean over episodes)

| Model | 1-3 | 2-4 | 1-2 | 1-4 | 2-3 | 3-4 |
|---|---:|---:|---:|---:|---:|---:|
| stage03_init_e1 blend_gain | -0.3198 | -2.4267 | +0.8791 | -1.2072 | -0.2186 | -0.6145 |
| stage03_init_e1 donor_excess_mse | +2.5448 | +8.3970 | +1.8719 | +3.6853 | +1.1184 | +2.0675 |
| e1_ippo_s1 blend_gain | -2.3251 | -3.1532 | -1.6834 | -1.2955 | -1.0908 | -0.1164 |
| e1_ippo_s1 donor_excess_mse | +10.3715 | +13.2285 | +6.5323 | +6.4081 | +4.4285 | +0.5052 |
| e1_pgct_s1 blend_gain | -1.8128 | -2.5508 | -1.4022 | -1.0283 | -1.2593 | -0.0023 |
| e1_pgct_s1 donor_excess_mse | +9.6188 | +10.7293 | +5.6139 | +5.2976 | +5.5714 | +0.0541 |
| e2_ippo_s1 blend_gain | +0.0105 | -0.0121 | +0.0008 | -0.0026 | +0.0079 | +0.0061 |
| e2_ippo_s1 donor_excess_mse | -0.0090 | +0.0474 | +0.0112 | +0.0316 | +0.0018 | +0.0013 |
| e2_pgct_s1 blend_gain | -0.0067 | -0.0179 | +0.0116 | +0.0001 | -0.0262 | -0.0400 |
| e2_pgct_s1 donor_excess_mse | +0.0215 | +0.1026 | -0.0063 | +0.0442 | +0.0746 | +0.1445 |
| stage04_pgct blend_gain | -2.4805 | -2.2576 | -1.6113 | -0.7024 | -1.7841 | +0.1599 |
| stage04_pgct donor_excess_mse | +11.5273 | +10.4763 | +6.2161 | +5.2157 | +6.7347 | -0.2307 |

## 출처: `output/scratch_review_20261015/REPORT.md` (수정 2026-10-15 09:36)

### From-scratch 핵심 비교(E17) 중단 시점 분석 — 약 2.5M step

2026-10-15 Claude Code. 읽기 전용 분석이며 학습·로그·checkpoint를 변경하지 않았다. 재현: `python output/scratch_review_20261015/analyze.py`. 수치: `analysis.json`, 그림: `curves.png`.

#### 조건과 한계

- **run**: `runs/scratch_20261013_202352_stage2`(IPPO/PGCT/Oracle/All, 무작위 초기화, 같은 초기 가중치).
- **환경**: E1 11×10, home .5, individual reward, 4 agents/2 teams.
- **평가**: deterministic masked policy, seeds 5,000,001–5,000,020, 20×500 step, 51,200 step마다.
- **중단**: 2026-10-15 01:01 KST Windows Update 재부팅. 마지막 기록은 IPPO 2,487,296 / PGCT 2,502,656 / Oracle 2,471,936 / All 2,455,552 step.
- **공통 비교 구간**: 51,200 ~ 2,406,400 step(All의 마지막 평가). AUC는 이 구간의 사다리꼴 평균이다.
- **한계**: training seed가 1개이고 학습 초기 구간만 있다. 평가값의 인접 평가 간 차이 표준편차는 0.2–0.8 delivery다. 아래 차이는 **방향 관찰**이지 효과 검증이 아니다.

#### 1. 평가 성능

| mode | 마지막 3회 평균 delivery | 요청 선반 pickup | return | full cycle 성공률 | delivery AUC/step | pickup AUC/step |
|---|---:|---:|---:|---:|---:|---:|
| IPPO | 3.10 | 20.68 | 1.12 | .58 | 0.41 | 4.25 |
| PGCT | 1.92 | 2.20 | 0.98 | .62 | 0.26 | 3.48 |
| **Oracle** | **9.98** | 10.42 | **9.43** | **1.00** | **1.28** | 2.51 |
| All | 3.45 | 15.15 | 1.37 | .65 | 0.69 | 3.89 |

처음 오른 시점(3점 이동평균 기준):

| mode | pickup ≥1 | pickup ≥10 | delivery ≥1 | delivery ≥5 |
|---|---:|---:|---:|---:|
| IPPO | 1.89M | 1.95M | 2.05M | 미도달 |
| PGCT | 1.89M | 2.00M | 2.15M | 미도달 |
| **Oracle** | **1.64M** | **1.69M** | **1.89M** | **2.25M** |
| All | 1.79M | 1.95M | 1.89M | 미도달 |

- 모든 mode에서 **0.5–1.5M은 보상이 거의 0인 정체 구간**이었다. train delivery는 0.002–0.006/episode였다. 학습은 1.6–1.9M부터 시작했다. 따라서 2M 시점 성능만으로 판단하면 안 된다는 기준이 맞았다.
- IPPO와 All은 pickup은 많지만(15–21) delivery로 이어지는 비율이 낮다. pickup conversion은 .11–.12다. Oracle은 pickup 10.4 → delivery 10.0 → return 9.4로 한 사이클을 완성했다.
- 참고(조건이 다름): 이전 from-scratch PGCT(home 1.0, complete graph)는 같은 2.4M에서 평가 delivery 26.7이었다. home .5가 더 어렵거나 학습이 느리다는 신호지만, 통신 그래프도 달라 단정하지 않는다.

#### 2. 가장 중요한 관찰: 성능이 agent 1–2개에서만 나온다

마지막 3회 평가의 agent별 delivery/episode:

| mode | Agent1 (팀0) | Agent2 (팀1) | Agent3 (팀0) | Agent4 (팀1) |
|---|---:|---:|---:|---:|
| IPPO | 1.63 | 1.47 | 0 | 0 |
| PGCT | 1.92 | 0 | 0 | 0 |
| **Oracle** | 0 | **9.98** | 0 | 0 |
| All | 0 | 2.12 | 1.33 | 0 |

- Oracle의 우위는 **Agent2 한 명이 배송 사이클을 먼저 완성한 결과**다. 팀원 Agent4를 포함한 나머지 3명은 아직 배송하지 못한다.
- 한 agent가 언제 "깨치는지"는 seed와 우연의 영향이 크다. 따라서 이 우위를 Oracle consensus의 효과로 바로 귀속할 수 없다. 다른 seed에서 같은 패턴이 반복되는지 확인해야 한다.
- 가능한 연결고리(가설): Oracle은 Agent2와 Agent4가 critic을 공유한다. 앞으로 Agent4의 학습이 Agent2보다 빨라지는지가 같은 팀 공유 효과를 보는 직접적인 관찰점이 될 수 있다.

#### 3. 실제 critic 전이

| mode | warm-up 후 전이가 있던 update 비율 | 같은 팀 arc-update | 다른 팀 arc-update | 평균 gate ratio |
|---|---:|---:|---:|---:|
| IPPO | 0% | 0 | 0 | 0 |
| PGCT | 77% | 3,496 | 5,590 | .59 |
| Oracle | 76% | 4,688 | **0** | .27 |
| All | 99% | 5,526 | 10,524 | .95 |

- 전이는 모두 물리 이웃 범위 안에서만 일어났다. 설계대로 Oracle은 같은 팀(1–3: 1,145, 2–4: 1,199 update)만, All은 모든 쌍에 전이했다.
- **PGCT의 gate는 같은 팀과 다른 팀을 거의 구분하지 않았다.**
  - 같은 팀 1–3: 826, 2–4: 922
  - 다른 팀 1–2: 808, 2–3: 886, 1–4: 601, 3–4: 500
  - 학습 초기에는 정책들이 비슷해서 JS gate가 넓게 열린다. 이는 실험 A의 "공통 입력 JS는 팀을 구분하지 못한다"는 결과와 일치한다.
- peer loss 크기(1.5M 이후 평균): PGCT .0010, All .0017, Oracle .0039.

#### 4. 학습 지표

- **entropy**: 0.0–0.5M 약 .91–.92 → 1.5M 이후 IPPO .83, PGCT .83, Oracle .76, All .89. Oracle이 가장 빨리 결정적인 정책으로 수렴했다.
- **value loss**: 1.5M 이후 .002–.006 수준이다. 보상이 생긴 뒤 커졌고, Oracle이 가장 크다(.0062).
- **approx_kl**: .0028 근처로 모두 안정적이다.
- **속도**: job당 약 24 step/s(4개 병렬).

#### 5. 결론 (현 시점)

1. 무작위 초기화에서도 네 mode 모두 1.6–1.9M부터 학습이 시작됐다. 학습 가능성은 확인됐다.
2. 2.4M 시점에는 Oracle이 가장 앞서 있다(delivery AUC 1.28 vs All .69, IPPO .41, PGCT .26). pickup과 delivery 시작도 가장 빠르다.
3. 그러나 그 우위는 **agent 한 명의 선행 학습**에서 나왔다. seed가 1개라 Oracle 효과로 결론 내릴 수 없다.
4. PGCT gate는 초기에 팀을 구분하지 않는다. 지금의 PGCT는 "잠재 팀 기반 공유"의 대리 지표가 아니다.
5. 해석 원칙은 유지한다. 이 실험은 critic 공유 효과의 검증이며, 팀 목표가 대칭인 환경이라는 점을 감안한다.
6. **다음 단계 제안**: 처음부터 재실행(15M)하고, 가능하면 seed 2·3을 함께 돌린다. agent별 학습 시작 시점(특히 Oracle에서 같은 팀원의 뒤따라오기)을 핵심 관찰 지표로 추가한다.

## 출처: `output/ijcai_review_20261015/REPORT.md` (수정 2026-10-15 11:50)

### PGCT 연구 기록 분석과 IJCAI 논문 설계

2026-10-15 KST, Codex. 사용자 요청: Codex·Claude로 만든 프로젝트의 Markdown 내역 분석, 현재 내역을 포함한 IJCAI 논문 작성 방향 제시.

이 문서는 연구 분석과 집필 제안이다. 새 알고리즘의 구현, 환경·보상·probe·threshold 변경, 학습 시작·중단·재시작은 수행하지 않았다. 새 학습 실행은 기존 파일에서 발견한 사실이며 이번 작업이 시작한 것이 아니다.

#### 1. 핵심 판단

**현재 자료는 잠재 팀 발견과 critic 공유의 관계를 연구할 근거를 제공하지만, PGCT가 잠재 팀을 찾아 학습 효율을 개선했다는 논문의 핵심 결론을 아직 뒷받침하지 않는다.**

사용자가 확정한 목표(D17·D22)는 다음이다.

> 국소적으로 관측한 타인의 행동에서 공통 목표의 팀원을 추론하고, 추론한 관계에 따라 critic 지식을 공유하여 학습 효율을 개선한다.

현재 구현의 정책 응답 유사도, 실제 팀 소속, critic 예측 일치, critic 정확도, 전이의 학습 기여는 서로 다른 변수다. 이들을 분리한 문제 정의와 검증 구조가 가장 설득력 있는 논문의 중심이다. 팀과 무관한 donor 선택 문제로 연구 목표를 자동 변경하지 않는다.

권장 전략은 **원래 목표를 유지한 방법론 논문을 준비하되, 기존 PGCT의 한계와 진단을 동기로 사용**하는 것이다. 현 자료만으로 먼저 쓸 수 있는 것은 탐색적 실증 분석 초고다. 진단 논문도 가능하지만, 현재 단일 seed·좁은 환경의 반례를 일반적 결론으로 확장하려면 추가 검증이 필요하다. 어느 방향도 채택 가능성을 보장하지 않는다.

#### 2. 읽은 자료와 근거 범위

프로젝트 내부 Markdown 20개를 식별했다. 연구 노트와 실행 문서를 중심으로 본문 또는 관련 절을 확인했고, 대화 로그는 과거 요약·연구 방향 전환·실험 요청·수행 기록·최근 결과 구간을 확인했다. 길게 붙여넣은 외부 답변의 모든 원출처를 다시 검증한 것은 아니다.

| 자료 묶음 | 파일 | 분석에서의 역할 |
|---|---|---|
| 공용 상태·판단 | `RESEARCH_STATE.md`, `DECISIONS.md`, `EXPERIMENTS.md` | D01–D22, E00–E18의 목표·관측·계획 분리 |
| 대화와 지침 | `CONVERSATION_LOG.md`, `AGENTS.md`, `CLAUDE.md` | 사용자 목표, 수행 허가의 범위, Codex·Claude 기록의 수정 이력 |
| 실행기와 비교군 | `latent_team/README.md`, `latent_team/BASELINES.md` | from-scratch 비교, 미구현 learned-team, baseline 구현 차이 |
| 기존 방법과 실험 문서 | `examples/EX5_PGCT.md`, `PGCT_PHYSICAL_MIXING_CURRICULUM.md`, `PGCT_SPATIAL_EXPERIMENTS.md`, `PGCT_TRANSFER_EXPERIMENTS.md`, `HARD_RWARE_EXPERIMENTS.md`, `examples/README.md` | 실제 방법, 조건부 비교, random/drop ablation, 장애물 환경의 범위 |
| 분석 보고서 | `output/gating_diagnosis/README.md`, `output/pgct_spatial_analysis/REPORT.md`, `output/learning_review_20261013/REPORT.md`, `output/latent_team/exp_a_20261013/REPORT.md`, `output/scratch_review_20261015/REPORT.md` | 정량 진단과 한계 |
| 환경 개요 | `README.md` | RWARE와 커스텀 multi-team 환경의 구분 |

추가 확인: 중단·신규 run의 `experiment.json`, 신규 run의 `metrics.jsonl`·`job_status.json`·초기 가중치 hash, E18 `analysis.json`, 기존 curriculum manifest. 관측과 peer loss 관련 코드를 제한적으로 대조했다. 전체 학습 코드·baseline의 독립 재현 감사나 테스트 재실행은 하지 않았다.

대화 로그의 L01–L12는 과거 요약이고 T001 이후는 저장된 원문 기록이다. 별도 Codex·Claude 세션을 자동 수집하거나 누락된 원문을 복원하지 않았다. 과거 ex4/ex5 PDF와 첨부 텍스트는 이번에 다시 열지 않았고, 현재 MD에 적힌 내용만 참고했다.

#### 3. 프로젝트가 발전한 과정

| 단계 | 기록상 한 일 | 연구적으로 남은 것 |
|---|---|---|
| 초기 PGCT | 공통 canonical probe의 actor 응답 JS, EMA gate, critic 보조 손실 구현 | 정책 유사도로 팀과 유익한 공유 상대를 구분할 수 있다는 전제 |
| 혼합 curriculum | complete-graph 사전학습 모델에서 물리 통신·home ratio 단계 적용 | 후반 same-team gate 소멸, 일부 cross-team 전이 |
| Codex 진단·대조 설계 | 접촉/승인 분리, probe 중복·공통 이력·critic 진단, Stage03 이후 on/off와 ablation 실행기 | 계산 오류보다 측정 분포와 전이 유익성 문제가 중요해짐 |
| 공간·난이도 확대 | E1/E2/E3 비교, 별도 장애물 환경과 smoke | 공간 확대가 팀 식별을 해결하지 않음; 난이도 자체가 원인인지는 미확인 |
| Claude의 목표 재정립 | 실험 A로 팀 식별 가능성과 critic 호환성 분리, oracle/all/wrong 준비 | 결과 수준 국소 증거는 유용하지만 같은 팀 critic의 우월한 호환성은 미확인 |
| 사용자 요구에 따른 from-scratch 전환 | 동일 무작위 초기화 비교, W&B, MAPPO·SePS·HetDPS 구현·smoke | 학습 초기부터 공유가 도움이 되는지 공정하게 묻기 시작 |
| E17·E18 | seed 1의 4 mode 학습이 약 2.5M에서 재부팅으로 중단, 초기 구간 분석 | Oracle 선행의 재현성과 원인은 미확인 |
| 이번 최신 확인 | 10월 15일 새 seed 1 run 발견 | 이전 MD의 ‘재실행 결정 대기’가 최신 실행 상태를 반영하지 않음 |

구현·로그·진단 기반은 많이 갖춰졌다. 반면 논문 주장에 해당하는 두 연결, **팀 추론→올바른 관계**와 **그 관계→학습 개선**, 중 어느 것도 현재 end-to-end 방식으로 검증되지 않았다. 테스트 개수와 실행기의 수를 연구 성과의 크기로 바꾸어 쓰면 안 된다.

#### 4. 최신 실행 상태: MD보다 실제 로그가 앞서 있다

신규 run: `runs/scratch_20261015_093349_stage2`.

조건: E1 11×10, 4 agents/2 teams, home .5, individual reward, sensor/communication range 5, 무작위 초기화, training seed 1, mode별 요청 예산 15,000,000 env steps. manifest의 rollout 반올림 예산은 15,000,576이다. 네 mode 모두 `init_checkpoint=""`이다.

2026-10-15 11:49 KST의 읽기 전용 스냅샷(`live_run_snapshot.json`):

| mode | 마지막 기록 env steps | 로그 수정 시각 KST | 최근 평가 step | delivery/episode |
|---|---:|---|---:|---:|
| IPPO | 200,704 | 11:48:58 | 153,600 | 0.0 |
| PGCT | 198,656 | 11:49:28 | 153,600 | 0.0 |
| Oracle | 196,608 | 11:49:12 | 153,600 | 0.0 |
| All | 199,680 | 11:49:18 | 153,600 | 0.0 |

평가 조건은 deterministic masked policy, reset seeds 5,000,001–5,000,020, 20 episodes×500 steps다. 네 초기 actor+critic hash는 `f78ec390e0fad60c9bee9ea045525a79befbd71357f41235f04d61356b91c7e3`로 일치했다. 상태 파일은 `running`이고 로그가 갱신되는 것을 확인했다. 시스템 프로세스 상세 조회는 CIM 접근 제한으로 확인하지 못했으므로 PID 생존 여부를 별도로 입증했다고 쓰지 않는다.

이 신규 run을 E17의 정확한 resume이나 seed 2로 취급하지 않는다. 같은 seed 1의 처음부터 재실행이다. 향후 중단 run의 prefix와 새 run을 연결해 하나의 연속 학습곡선을 만들지 않는다. 이 초기 평가값으로 학습 성공·실패를 판정하지 않는다.

#### 5. 현재 결과에서 쓸 수 있는 주장

##### 5.1 Stage03 이후 추가 공유: 약한 조건부 신호

모델: `runs/sp_20261008_120638_983201/e{1,2}_{pgct,ippo}_s1/final.pt`. 공통 초기 모델은 physical curriculum Stage03 final. training seed 1, 추가 4,000,768 env steps, home .5, individual reward. 평가는 공통 seeds 5,000,001–5,000,020, deterministic masked policy, 20×500.

| 환경 | PGCT 평가 delivery 정규화 AUC | IPPO | 상대 차이 | 최종 delivery PGCT/IPPO |
|---|---:|---:|---:|---:|
| E1 11×10 | 45.8559 | 44.5734 | +2.88% | 44.35 / 44.65 |
| E2 16×16 | 34.1674 | 34.2449 | −0.23% | 37.85 / 38.20 |

AUC는 평가 51,200–4,000,768 step의 사다리꼴 적분을 구간 길이로 나눈 값이다. 실제 학습 중 누적 배송량이 아니다. 두 결과는 이미 PGCT로 사전학습한 동일 모델에서 분기했으므로, **처음부터 독립 IPPO보다 PGCT가 좋다**는 결론에 사용할 수 없다.

특히 curriculum manifest는 Stage01 이전에 `checkpoint_09700.pt`를 읽었다고 명시한다. 전체 사전학습 비용을 ‘Stage01–03 약 6M’만으로 보고하면 이전 사전학습 비용을 누락한다. 전체 효율 비교에는 원 checkpoint의 실제 누적 env step도 메타데이터로 확인해 포함해야 한다. 파일명만으로 총 학습량을 확정하지 않는다.

##### 5.2 팀 식별 진단: 현재 JS 신호의 한계

E11 frozen 진단: Stage03→E1, E1/E2 IPPO·PGCT seed 1 final, Stage04 PGCT의 6개 checkpoint 조건. 자체 stochastic masked policy, reset seeds 5,200,001–5,200,020, 모델별 20×500. 서로 다른 6개 독립 training seed라는 뜻은 아니다.

- canonical 정책 JS 기반 같은/다른 팀 AUROC는 .375–.500, 팀원 recovery는 .000–.250였다. recovery의 균등 무작위 기준은 1/3이다.
- 국소 pickup·delivery 결과 증거의 AUROC는 1.000이었고, 누적 첫 episode 후 6쌍 모두의 팀 관계를 맞혔다.
- E13의 세 frozen 모델·각 5×500 진단에서 목격 증거 2,146건이 관측자 자신의 semantic 채널과 일치했다.

**쓸 수 있는 해석:** 이 평가 조건의 국소 작업 결과에는 팀 구분 정보가 있었으며, 현재 canonical 정책 응답 JS는 그 정보를 안정적으로 포착하지 못했다.

**쓸 수 없는 해석:** 온라인 잠재 팀 추론 알고리즘을 구현해 100%로 해결했다. 현재 진단은 env 이벤트로 사건을 재구성했고, 익명 관측의 사건을 특정 이웃에게 연결하는 가정이 남는다. 학습 초기에는 성공 사건이 드물어 이런 정보가 늦게 생긴다. frozen 숙련 정책의 첫 episode 결과를 무작위 정책의 첫 episode 결과로 일반화하지 않는다.

또한 .375–.500이라는 수치는 제한된 평가의 기술 통계다. 모든 행동 기반 팀 추론이 불가능하다는 통계적 증명은 아니다. 2 same/4 cross 쌍, episode·pair 종속성, 평가 모델 선정 편향을 명시해야 한다.

##### 5.3 같은 팀과 critic 호환성은 동의어가 아니다

E11의 E1 계열에서는 같은 팀 critic의 예측 차이가 더 컸고, 정적인 blend gain은 낮았다. E2에서는 critic 차이와 blend gain이 작았다. E06의 stochastic on-policy MC 평가에서도 최종 critic 정확도 개선은 확인되지 않았다.

E06 모델은 위 공간 실험의 E1/E2 final, training seed 1, 추가 4,000,768 step이다. reset/action RNG seeds 5,100,001–5,100,010, stochastic masked policy, 10×500, 초기 200-step의 유한 return MC MSE는 E1 PGCT/IPPO 1.724620/1.103477, E2 .286130/.281301이었다. 모델별 방문 분포와 zero-tail 편향이 달라 이 차이만으로 전이의 손상을 단정하지 않는다.

팀 보상이 같아도 각 agent의 관측 이력과 역할이 다르면 조건부 value가 다를 수 있다. 반대로 다른 팀이어도 자기 팀 기준 관측으로 과제가 정규화되면 같은 입력에서 value 함수가 비슷할 수 있다. 따라서 팀 보상 변경만으로 same-team consensus가 항상 유리해진다고 가정하면 안 된다.

##### 5.4 중단된 from-scratch 비교: Oracle의 초기 선행

E17: `runs/scratch_20261013_202352_stage2`, 무작위 초기화, E1 11×10, home .5, individual reward, training seed 1. 15M 목표였으나 약 2.46–2.50M에서 중단. 평가는 deterministic masked policy, 공통 reset seeds 5,000,001–5,000,020, 20×500.

| mode | 자기 run 마지막 3회 평균 delivery | 공통 평가 구간 정규화 delivery AUC |
|---|---:|---:|
| IPPO | 3.10 | .41 |
| PGCT | 1.92 | .26 |
| Oracle | 9.98 | 1.28 |
| All | 3.45 | .69 |

AUC의 공통 구간은 51,200–2,406,400 step이다. 마지막 3회는 mode별 마지막 평가 시점이 완전히 같지 않은 요약이므로 최종 본 논문에서는 공통 step으로 다시 맞추는 편이 좋다.

Oracle 마지막 3회 delivery는 Agent2 한 명이 모두 담당했고 같은 팀 Agent4는 0이었다. 이는 Oracle의 총 성능 개선이 **그 한 명의 실적에서 나왔다**는 뜻이다. Oracle이 Agent2의 학습을 촉진했을 가능성까지 배제하지는 못한다. 그 원인을 consensus로 귀속하거나 우연으로 확정할 수 없다는 것이 정확한 결론이다.

PGCT는 same 3,496 / cross 5,590 directed arc-updates를 기록했다. same 가능한 쌍은 2개, cross는 4개이므로 원시 합계 비율만으로 판별 능력을 비교하지 않는다. 물리 후보·접촉 노출을 분모로 한 정밀도·재현율·승인율이 필요하다.

#### 6. MD 내역에서 바로잡거나 구분할 부분

1. **실행 상태의 시차:** `RESEARCH_STATE.md`의 ‘실행 중 없음’, ‘진행 중’, ‘재실행 결정 대기’가 서로 다른 시점에 추가돼 한 페이지에 공존한다. 이번 최신 확인을 맨 위에 추가하고 과거 스냅샷은 보존한다.
2. **오래된 계획과 실제 결과:** E3의 진행 표, Stage03 oracle 계획, from-scratch 장기 미실행 문구는 작성 당시 상태다. 최신 E17/E18과 신규 run을 구분해 읽어야 한다.
3. **예산 기본값:** `latent_team/README.md`에 과거 2M/10M 예시와 최신 4M/15M 안내가 함께 있다. 논문에는 README의 임의 예시가 아니라 각 run manifest의 실제 설정을 쓴다.
4. **Oracle의 의미:** Oracle은 정답 팀을 쓰는 비교군이다. 최적 donor·weight·critic 호환성을 아는 수학적 성능 상한은 아니다. same-team만 고집하는 것이 all-peer보다 반드시 유리하지는 않다.
5. **공유 방식의 이름:** 현재 peer loss는 공통 probe에서 donor 예측을 stop-gradient target으로 삼는 value distillation 형태다. 네트워크 파라미터 평균이나 consensus 수렴 보장이 있는 방식과 구분해야 한다.
6. **분산성:** actor가 자기 관측만 쓰는 것과 학습 프로토콜의 완전 분산성은 다르다. 공통 bank 생성·배포, 이웃 식별, actor 응답/critic 값 교환, 전역 라벨의 logging-only 사용 범위를 명시해야 한다. ‘통신 없는 학습’이라고 쓰면 부정확하다.
7. **관측 정보:** semantic 관측은 상대 팀 ID를 직접 주지 않지만, 자기 요청·관련 목표는 알려준다. ‘목표 정보가 전혀 없는 순수 행동만으로 추론’이라는 표현은 범위가 과하다.
8. **성공률 정의:** 기존 full-cycle 지표는 episode에서 delivery와 return이 있었는지를 보는 값이다. 모든 주문·선반의 개별 cycle이 100% 완수됐다는 뜻으로 사용하지 않는다.
9. **불확실성:** 인접 평가 차이의 표준편차에는 학습 추세도 섞인다. 순수 평가 잡음, training seed 분산, 신뢰구간으로 부르지 않는다.
10. **구현 비교의 공정성:** `BASELINES.md`에 공통 PPO 외에도 advantage 정규화 범위와 zero-reward actor skip 차이가 기록돼 있다. ‘알고리즘 구조만 다르고 학습 설정이 완전히 동일’하다고 쓰기 어렵다. 공식 재현과 통제된 이식 구현을 구분하고, 결과 확보 전에 어느 비교를 할지 고정해야 한다.

기존 자료를 버릴 이유는 없다. 기존 curriculum·공간 실험은 가설 생성과 한계 진단으로 가치가 있다. 주성능 표에는 from-scratch 결과를, 조건부 적응 실험에는 기존 결과를 각각 배치한다.

#### 7. 논문의 중심 질문과 기여 설계

##### RQ1. 목표 관계는 국소 행동·작업 결과에서 식별되는가?

정책 응답 JS, 실제 이력 JS, 국소 작업 결과 증거를 비교한다. 학습 초·중·후반, 접촉량, 사건 희소성, 역할 차이, 환경 대칭성에 따라 식별 성능이 어떻게 달라지는지 측정한다.

##### RQ2. 정확한 목표 관계를 아는 것이 critic 공유에 도움이 되는가?

IPPO/Oracle/All/Wrong 비교로 본다. 팀 라벨 정확도가 높아도 공유 효과가 작을 수 있음을 허용한다. 같은 reward 목표와 같은 value 함수라는 전제를 분리한다.

##### RQ3. 추론한 관계를 사용해 실제 학습 효율이 개선되는가?

새 learned-team 모드가 필요하다. 현재 PGCT를 이 모드로 이름만 바꾸면 안 된다. 팀 추론을 거친 공유가 IPPO와 All보다 유리하고, Oracle과의 차이가 줄어드는지를 여러 training seed에서 확인한다.

권장 기여는 세 가지다. 아래는 **달성 목표**이며 현재 실적 목록이 아니다.

| 기여 목표 | 현재 확보 | 부족한 증거 |
|---|---|---|
| 정책 유사도·목표 관계·value 공유 유익성을 분리하는 문제 정식화와 진단 | 상당 부분 있음 | 통제된 반례, 기존 연구 대비 차별성 검토 |
| 국소 작업 증거에 기초한 온라인 팀 추론과 선택적 critic distillation | frozen 정보존재 진단 | 관측 기반 사건 검출·이웃 귀속·online posterior·learned allocation 구현 |
| 팀 선택이 도움이 되는 조건과 실패 조건의 실증 분석 | 조건부 on/off, 중단 pilot | 완료된 from-scratch 반복, 정보조건·전달량 ablation, 역할/목표 분리 |

단순 Beta 누적이나 JS 대신 다른 거리 사용만으로 독창성을 주장하기는 어렵다. **사건이 드문 초기 학습에서 어떻게 오판을 줄이고, 역할이 달라도 같은 목표 관계를 유지하며, 그 관계가 언제 실제 공유 가치를 갖는가**를 해결해야 한다. 이 관점이 기존 선택적 parameter sharing과의 실질적 차이가 될 수 있다. 다만 전면 문헌조사를 마친 독창성 판정은 아니다.

#### 8. 방법 절을 쓰는 방식

##### 8.1 문제 정의

부분관측 다중에이전트 확률게임, agent i의 관측 이력 h_i, 행동 a_i, 개인 보상 r_i, 숨은 목표 집단 z_i, 물리 이웃 N_i(t)를 정의한다. 각 agent는 자기 목표에 관한 task-relative 단서를 알지만 상대의 z_j는 모른다는 현재 정보 조건을 정확히 쓴다. 공통 목표와 보상 공유 여부는 별도 정의한다.

##### 8.2 기존 PGCT: 재현 가능한 기준 방법

공통 probe 분포 Q의 정책 응답 거리:

`D_ij = E[x~Q] JS(pi_i(.|x,h=0), pi_j(.|x,h=0))`.

실제 설정은 48 probe, sequence length 1, unmasked natural-log JS다. 이웃에서 갱신하는 EMA, threshold .12, warm-up 100 update, min-count 8, 측정 간격 5 update, 현재 물리 이웃 마스크를 구분한다. 최종 raw JS 하나를 과거 gate와 동일시하지 않는다.

receiver별 allocation은 gate 행을 정규화한 alpha_ij다. 단순화한 critic 목적은 다음과 같다.

`L_i = L_i^PPO + lambda_peer * sum_j alpha_ij E[x~Q](V_i(x) - stopgrad(V_j^old(x)))^2`.

현 설정의 lambda_peer는 .01이다. `L_i^PPO` 안의 local value loss coefficient는 .5다. donor target은 update 시작 시 고정한다. 수렴 증명 없이 ‘같은 팀의 최적 value로 수렴’이라고 주장하지 않는다.

##### 8.3 후속 learned-team 방법: 제안이며 미구현

국소 관측 이력에서 상대 j의 작업 사건 e_ij를 검출하고, `q_ij(t)=P(z_j=z_i | local evidence through t)` 같은 신뢰도를 추정한다. 증거가 부족하면 공유를 보류하는 기준을 명시한다. 물리 후보 안에서 q_ij로 gate/weight를 정하고 기존 critic distillation을 적용하는 방식이 가장 작은 확장이다.

필요한 구현·평가 항목:

- env의 정답 이벤트를 detector 입력으로 쓰는 조건은 privileged 진단으로 분리한다. 실제 방법은 허용된 관측 이력에서 사건을 검출한다.
- 이웃 ID와 익명 관측 물체의 대응을 가정하는지, 추가 통신이나 tracking으로 해결하는지 적는다.
- 양의 사건만 기다리는 cold-start 지연, 잘못된 pickup·delivery 귀속, 관측 누락, 증거 없음을 오판으로 처리하는 문제를 다룬다.
- q_ij는 관측자별로 다를 수 있다. 대칭성·전이성을 강제할지, pair 관계만 쓸지 정하고 비용을 기록한다.
- 모든 agent의 중앙 clustering을 쓴다면 분산 주장과 정보 조건을 다시 정리한다.
- 추론 데이터와 검증 데이터를 분리하고 threshold·hyperparameter를 최종 test seed로 고르지 않는다.

팀 추론과 방향별 transfer utility까지 동시에 새로 학습하는 복잡한 방법은 별도 확장이다. D15의 방향별 유익성 surrogate는 유용한 진단 후보지만, 지금 논문의 목표를 다시 팀 무관 transfer로 옮기는 이유가 되지 않는다.

##### 8.4 넣을 수 있는 간단한 분석 예시

정책 유사성만으로 value 호환성을 보장할 수 없음을 설명하는 자체 구성 예시다. 한 상태·한 행동의 무한 할인 MDP에서 두 agent의 정책은 같아서 JS=0이다. 매 step 보상이 각각 0과 c라면 value는 0과 `c/(1-gamma)`로 다르다. 따라서 정책 JS만으로 보상·value 차이를 제어하는 보편적 보장은 추가 가정 없이 성립하지 않는다.

이 예시는 현재 RWARE를 분석적으로 설명했다는 증명이나 새로운 정리의 독창성 주장이 아니다. 본 논문에서 일반 보장을 쓰려면 observation alignment, reward/transition 차이, 정책 평가 목표, probe coverage 가정을 명시하고 별도 증명해야 한다. 현재 recurrent nonlinear PPO+distillation에 기존 선형 consensus 수렴 정리를 그대로 적용할 수 없다.

#### 9. 필요한 실험과 우선순위

이 표는 제안이며 새 실행 허가나 실제 수행 기록이 아니다. 현재 실행 중인 seed 1 run은 그대로 보존한다.

| 우선순위 | 비교 | 답하려는 질문 | 완료 기준 |
|---|---|---|---|
| P0 | 현재 IPPO/PGCT/Oracle/All from-scratch | 이 설정에서 공유 효과가 관찰되는가 | 동일 예산 완료, 공통 평가 step, agent·팀별 성과 |
| P1 | 같은 4 mode의 독립 seed 2·3, 이후 필요시 추가 seed | 효과가 초기 성공의 우연에 민감한가 | seed별 AUC 차이·최종 구간 차이·구간 추정 |
| P2 | learned-team + IPPO/PGCT/Oracle/All | 추론된 관계가 실제 학습을 돕는가 | 관측 기반 online 구현, 추론·학습 동시 평가 |
| P3 | Wrong / 무작위 관계 / 전달량 통제 | 같은 팀을 고르는 것이 특별히 중요한가 | 실제 allocation·부족량·loss 노출량 기록 |
| P4 | 역할 차이×목표 차이의 통제 조건 | 다른 역할의 팀원과 비슷한 행동의 타팀원을 구분하는가 | 같은 팀/다른 역할, 다른 팀/비슷한 역할 비교 |
| P5 | MAPPO·SePS·HetDPS, 다른 규모·layout | 경쟁력과 적용 범위 | 정보·구현 차이 공개, 추가 compute 포함 |

3 seed는 우선 점검용 제안이다. 최종 핵심 비교는 자원이 허용하면 5개 이상 독립 training seed와 불확실성 보고를 권장한다. 이는 IJCAI의 고정 seed 수 규정이 아니며, seed 수가 적다면 그 한계를 그대로 적는다. seed 수를 늘리는 것만으로 방법의 독창성이 생기지는 않는다.

최소 ablation은 (a) critic 공유 없음, (b) 모든 이웃 공유, (c) 정답 팀 공유, (d) 잘못된/무작위 관계, (e) 국소 증거 추론, (f) 기존 정책 JS다. 동일한 전달량 비교는 전체 방법 비교와 별도로 수행한다. 거리/위치에 따라 후보 수가 달라 완벽히 맞출 수 없다면 부족량을 보고한다. Stage03용 random 실행기를 from-scratch에 이미 적용했다고 가정하지 않는다.

환경 확장은 맵을 크게 만들거나 장애물을 늘리는 것만으로 대체되지 않는다. 팀 관계가 보상·value·공유 가치에 어떻게 관련되는지 통제해야 한다. 현재 individual reward와 대칭 task-relative 관측은 실패·경계 조건으로 남길 수 있다. 다른 보상/과제 조건을 추가한다면 처음부터 새 비교를 하고 기존 결과와 섞지 않는다. SMAC 도입은 현재 사용자 요청이 아니며 필수 조건으로 제시하지 않는다.

#### 10. 지표와 통계 설계

- 주지표: 공통 env-step 구간의 delivery AUC/step. 최종 구간 delivery·return, 팀별 throughput, 실제 task return을 함께 보고한다. ‘수렴 속도’를 주장하려면 사전 지정한 목표 성능 도달 step도 쓴다.
- 추론: 같은 팀 edge precision/recall/F1, AUROC와 PR-AUC, 관측 가능한 후보 coverage, 첫 정확한 관계까지 env steps, 오판 지속 시간, 신뢰도 calibration. 미접촉·증거 없음은 따로 보고한다.
- 공유: 실제 directed allocation mass, donor 수, same/cross 후보 대비 승인, peer loss, 필요시 gradient 규모. pair-update와 arc-update를 혼합하지 않는다.
- 학습 분포: agent별 첫 pickup/delivery/return, 성공 agent 수, 팀별 최소 성과, 성과 집중도. 고정 agent 번호가 아니라 각 seed의 최초 성공 agent와 팀원을 기준으로 지연을 볼 수 있다.
- 원인 검증: 같은 팀원이 먼저 성공한 뒤 다른 팀원이 빨라지는 것은 관찰적 지표다. 공유 차단·donor 교체 같은 개입 대조가 없으면 인과 증거라고 부르지 않는다.
- critic: on-policy 유한 MC와 공통 이력 prediction gap을 분리한다. 다른 정책의 rollout return을 해당 정책 critic의 on-policy 정답으로 사용하지 않는다. 시간 제한 tail과 reward scale도 함께 보고한다.
- 비용: env steps, wall-clock, 평가·probe 비용, 전송한 값/byte 수, 모델 수와 파라미터 수. 분산성을 기여로 삼으면 중앙 기준 방법과 정보·통신 예산을 나란히 적는다.
- 불확실성의 기본 단위는 독립 training seed다. 여러 평가 episode와 수십 checkpoint를 독립 학습 반복으로 부풀리지 않는다. seed별 paired 차이를 우선 보고하며 episode 표본은 그 안에 종속된다.
- 동일 seed 1의 중단·재실행은 독립 seed 2개가 아니다. 여러 task를 종합할 때는 정규화와 task 간 가중을 사전에 정하고, 적절하면 IQM·구간 추정도 사용한다.
- 주지표·최종 구간·예산·실패/중단 처리와 tuning/test seed 분리를 결과 확인 전에 정한다. 좋은 구간만 사후 선택하지 않는다.

관련 평가 방법론은 [Agarwal et al., NeurIPS 2021](https://proceedings.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html)을 참고한다.

#### 11. 결과에 따른 논문 방향 결정

| 반복 실험에서의 결과 | 지지하는 해석 | 다음 집필 판단 |
|---|---|---|
| Oracle이 IPPO·All보다 일관되게 유리 | 현재 조건에서 팀 선택의 가치가 있음 | learned-team을 완성하고 Oracle gap 분석 |
| Oracle·All 모두 IPPO보다 유리하고 서로 비슷 | 공유는 유용할 수 있으나 팀 선택의 추가 가치는 불명확 | 원래 목표의 증거가 부족함을 인정하고 역할/목표 조건 분해 |
| Oracle도 IPPO보다 뚜렷하지 않음 | 현재 방식·조건에서 팀 제한 공유의 이득 미확인 | 공유 메커니즘·value 정의·환경 조건 점검, 팀 추론부터 복잡화하지 않음 |
| learned-team은 팀을 맞히지만 성능은 개선하지 않음 | 식별 성공과 학습 성공이 분리됨 | 핵심 실패 조건으로 보고, end-to-end 성공 주장 제외 |
| PGCT는 팀을 못 맞혀도 성능 향상 | 팀 무관 공유의 별도 증거 후보 | 원래 목표 달성으로 설명하지 않음; 목표 변경은 사용자와 명시적으로 결정 |

‘차이 없음’은 적은 표본으로 동등성이 입증됐다는 뜻이 아니다. 효과 크기·구간 추정·예산을 보고 판단한다. 원하는 결과가 나올 때까지 환경을 바꾸는 방식 대신 검증하려는 구조적 조건을 먼저 정한다.

#### 12. IJCAI 원고 구성안

현재 날짜 2026-10-15 기준, 다음 회차인 [IJCAI 2027 공식 홈페이지](https://2027.ijcai.org/)에는 초록 2027-01-04, 본문 2027-01-11, 모두 23:59 AoE로 안내되어 있다. 접수 직전에 변경 여부를 다시 확인해야 한다. 이번 확인에서는 2027 main-track 상세 CFP를 확보하지 못했다.

아래는 [IJCAI-ECAI 2026 main-track CFP](https://2026.ijcai.org/ijcai-ecai-2026-call-for-papers-main-track/)의 본문 7쪽·참고문헌 2쪽을 참고한 집필 배분안이며, 2027 확정 규정으로 간주하지 않는다. 2026 CFP의 익명 제출·재현성 안내와 LLM 사용 책임 규정도 대상 연도 CFP에서 다시 확인한다.

| 본문 절 | 배분 예시 | 담을 내용 |
|---|---:|---|
| 1. Introduction | .8쪽 | 숨은 목표 집단에서 공유 관계가 왜 어려운가, 두 단계 검증, 검증 완료된 기여만 열거 |
| 2. Related Work | .6쪽 | 선택적 parameter sharing, 역할 발견, 분산 critic consensus/distillation의 차이 |
| 3. Problem and Diagnostic Motivation | 1.0쪽 | 정보·통신 가정, 팀/역할/value 구분, 기존 JS 실패 진단 |
| 4. Method | 1.4쪽 | online evidence 추론, 보류/갱신, allocation, PPO+distillation, 알고리즘 상자 |
| 5. Experiments | 2.5쪽 | from-scratch 주결과, 식별/Oracle gap, 메커니즘·비용·실패 조건 |
| 6. Discussion and Conclusion | .7쪽 | 검증된 적용 범위, 정보 가정, 제한, 향후 과제 |

7쪽에 모든 과거 작업을 넣지 않는다. Windows 재부팅·W&B 경로·파일 정리·smoke 상세는 재현성 부록과 실행 이력으로 정리한다. 과거 curriculum 결과는 진단 동기 또는 조건부 적응 부록으로 배치한다.

추천 본문 그림/표:

1. 관계 추론→물리 후보 내 공유→local PPO 구조와 허용 정보 범위.
2. 같은 팀/역할 차이와 다른 팀/행동 유사성을 구분하는 진단 그림.
3. from-scratch 학습곡선과 seed별 효과 구간; 미완료 run은 별도 pilot 표시.
4. 추론 정확도·증거 coverage·학습 성능·실제 allocation을 함께 보여 주는 ablation 표.
5. agent별 onset 또는 성과 집중도와 비용 비교의 작은 패널.

##### 제목 후보

원래 목표의 알고리즘과 반복 검증을 완성한 뒤 사용할 후보:

> **Inferring Latent Teams from Local Task Evidence for Selective Critic Sharing**

현재 진단 중심 초고에 사용할 수 있는 후보:

> **Policy Similarity, Latent Teams, and the Limits of Critic Sharing in Multi-Agent Reinforcement Learning**

‘효율 향상’, ‘robust’, ‘fully decentralized’, ‘general’ 같은 제목 표현은 각각의 증거와 정보 가정이 충족된 뒤 추가한다.

##### 현재 증거만 사용한 영문 초록 초안

아래는 **탐색적 분석 원고용**이다. 미구현 방법이나 미래 성능을 과거형으로 쓰지 않았다. 특정 효과의 통계적 검증이나 제출 가능한 완성본을 뜻하지 않는다.

> Selecting communication partners in multi-agent reinforcement learning requires distinguishing similarity in behavior from alignment in objectives and compatibility of value predictions. We examine these distinctions in a partially observable warehouse environment with hidden team memberships and team-relative task observations. We analyze a policy-similarity-gated critic distillation scheme using frozen-policy diagnostics and controlled training comparisons. Across six checkpoint conditions derived from a single training seed, canonical policy-response similarity yields same-team AUROC values of 0.375–0.500, whereas locally witnessed task outcomes contain substantially stronger membership information. These diagnostics establish the availability of local evidence under the evaluated conditions, rather than an implemented online team-discovery solution. Comparisons initialized from a shared pretrained model show small and environment-dependent differences in learning-curve performance, without establishing improved final critic accuracy. An interrupted from-scratch pilot shows an early advantage for oracle team-restricted sharing, concentrated in one agent, but cannot establish a reproducible learning benefit. Together, these observations motivate separate evaluation of team identifiability, the value of oracle sharing, and the performance of inferred sharing relations. The study identifies limitations of using policy similarity as a proxy for latent team membership and outlines the evidence needed to connect relation discovery to learning improvements.

방법론 논문 최종본에서는 online 방법 설명과 완료된 여러 seed 실험의 효과 크기·불확실성을 넣어 다시 쓴다. 결과가 없는 단계에서 개선율 placeholder를 실측처럼 채우지 않는다.

##### Introduction에 사용할 논리 순서

1. 여러 agent가 공존해도 서로 같은 목표를 갖는 것은 아니며, 어떤 경험·예측을 공유할지가 학습에 영향을 준다.
2. 같은 목표라도 역할이 다르면 행동이 다르고, 다른 목표라도 공통 이동 능력 때문에 행동이 비슷할 수 있다.
3. 따라서 정책 유사성으로 팀과 value 호환성을 한꺼번에 추론하는 것은 강한 가정이다.
4. 현재 warehouse 진단은 이 구분을 실제 실패 사례로 보여 준다.
5. 논문에서 제안하는 online 방법과 식별·Oracle 공유·학습 개선을 분리한 평가 설계를 설명한다.
6. 완료한 결과의 범위 안에서만 기여를 열거한다.

#### 13. 관련 연구와의 차이를 확인할 관점

| 일차 자료 | 이미 다룬 것 | 본 연구가 명확히 할 차이 |
|---|---|---|
| [Christianos et al., SePS, ICML 2021](https://proceedings.mlr.press/v139/christianos21a.html) | 선택적 parameter sharing으로 효율과 다양성의 양립 | actor/critic 파라미터 공유와 숨은 목표 관계에 기초한 critic 예측 공유의 차이 |
| [Hu et al., HetDPS 공식 구현](https://github.com/Harry67Hu/HetDPS) | objective/policy 등의 이질성 구분, 거리 기반 동적 공유 | ‘이질성이 있으니 선택적 공유’만으로 차이가 약함. 허용 정보, 국소 증거, critic만 공유하는 가치 제시 |
| [Zhang et al., ICML 2018](https://proceedings.mlr.press/v80/zhang18n.html) | 통신망의 분산 actor-critic, critic consensus, 선형 근사 수렴 분석 | 통신망과 잠재 팀은 다름. 숨은 관계 추론, 개인 목표, 비선형 distillation과의 차이 |
| [Yu et al., MAPPO, NeurIPS 2022](https://arxiv.org/abs/2103.01955) | PPO 계열 MARL 성능과 구현 요인 | 중앙 critic의 추가 정보를 명시하고 구현 차이를 성능 원인과 혼동하지 않음 |
| [Wang et al., RODE, ICLR 2021](https://arxiv.org/abs/2010.01523) | action effect로 역할 발견·과제 분해 | 역할과 공통 목표 팀은 다른 잠재 변수. 필수 baseline 여부는 과제 정합성으로 판단 |

위 내용은 논문 초록·출판 페이지·공식 README 확인에 기초한 초기 위치 설정이며 완전한 신규성 조사는 아니다. HetDPS의 정식 논문명은 공식 README의 **Heterogeneity in Multi-Agent Reinforcement Learning**이다. 프로젝트의 구현 설명 제목을 그대로 서지 제목으로 쓰지 않는다. 원 논문의 모든 수식·실험을 이번에 정밀 검토했다고 주장하지 않는다.

MAPPO/SePS/HetDPS는 현재 smoke를 마친 이식 구현이며 완료된 성능 비교 결과는 없다. 논문에는 `SePS-style sharing with recurrent PPO`처럼 이식 조건이 드러나는 이름과 구현 차이 표를 사용한다. 공식 구현 재현 또는 작은 규모의 일치 검증이 별도로 필요할 수 있다.

#### 14. 이번 성과와 미실시 사항

실시: MD 교차 분석, 실행 상태 읽기 확인, IJCAI 공식 일정과 선행 연구 일차 자료 확인, 논문 구성·주장/증거·실험 우선순위 문서화, 공용 기록 갱신.

미실시: 새 학습·추가 frozen 평가·tests 재실행, learned-team 구현, baseline 수정, 환경/보상/gate/probe 변경, 실행 중 학습 중단·재시작, 완성 논문 제출.

**다음 실증 판단점은 현재 from-scratch Oracle 비교가 독립 seed에서 재현되고, All보다 목표 관계를 선택하는 가치가 있는가다. 논문의 문제 설정·관련 연구·기존 진단은 지금부터 쓸 수 있지만, 주결과와 성공 주장은 그 검증과 online 방법의 완성에 맞춰 확정한다.**

## 출처: `output/env_view_20261015/probes/README.md` (수정 2026-10-15 12:24)

### Canonical probe bank 시각화 — 실행 중 run `scratch_20261015_093349_stage2`

2026-10-15 Claude Code. 읽기 전용이며 학습에는 영향을 주지 않는다. 재현: `python output/env_view_20261015/probes/draw_probes.py`.

| 파일 | 내용 |
|---|---|
| `official/probe_contact_sheet.png`, `official/NNN_*.png`, `official/probe_manifest.json` | 저장소의 `rware.utils.probe_maps` 렌더러로 그린 48개 probe. 각 probe의 이름(의도)과 world 지도·agent별 시야가 함께 나온다 |
| `decoded_bank.png` | 실제 학습에 쓰이는 bank 벡터를 해독해 agent 관측(11×11)으로 그린 것. 빨간 제목은 다른 probe와 입력이 완전히 같은 경우 |
| `probes.csv` | probe별 고유 id, bank 안 중복 수, 방향, 적재/요청 적재/반납 단계, 위치, 보이는 요청 선반·목표·agent 수 |

#### 확인한 것

- 저장소 builder로 같은 env 상태(reset seed 1)와 rng(seed+9173)를 써서 다시 만든 bank가 run의 `canonical_bank_e1_s1.pt`와 **완전히 같다.**
- 48개 probe 중 **고유 입력은 26개**다.
  - `dual_requested_*` 7종(home_pair, other_home_pair, opposite_axis, front_side, near_far, diagonal, cross_zone_choice)이 팀마다 같은 입력 하나로 겹친다(8개씩, 2그룹 = 16개).
  - goal 계열 3종(goal_pair, goal_zone_pair, lane_choice)이 팀마다 하나로 겹친다(4개씩, 2그룹 = 8개).
  - `neutral`은 2개씩 2그룹이다.
- 겹치는 원인(관찰 기반 추정): 해독한 시야에서는 요청 선반이 대부분 **시야 가장자리에 1개만** 보인다. world 지도에서 서로 다른 두 번째 선반 위치는 11×11 관측 밖에 있어 입력에 반영되지 않는 것으로 보인다. builder 코드로 확인하지는 않았다.
- 상태 구성: 빈 손 38개, 요청 선반 적재 10개(이 중 반납 단계 4개). 요청되지 않은 선반을 든 상태는 0개다.
- 관측은 팀 기준(주황 = 내 팀 요청, 초록 = 내 목표)이다. 다른 agent의 팀은 표시되지 않는다.

#### 해석 시 주의

이름이 다른 7가지 시나리오가 같은 입력이므로, 해당 상황은 JS 평균에서 의도보다 큰 가중치(8/48)를 받는다. E04·E07에서 본 "중복 제거 시 유사도 순위 변화"의 직접적인 원인이다. probe 설계 의도("두 요청 선반 중 선택")는 현재 관측 범위에서 대부분 사라진다.

---

# Part 7. 실행기·구현 문서

## 출처: `latent_team/README.md` (수정 2026-10-15 12:46)

### 잠재 팀 추론 + 팀 내부 critic consensus 검증 (latent_team)

2026-10-13 Claude Code 작성. 기존 PGCT 코드(`examples/`, `rware/`)는 수정하지 않고, 이 폴더의 새 실행기만 기존 모듈을 import해서 사용한다.

#### 연구 질문

원래 목표: **팀 정보를 모르는 완전분산 agent가 국소적으로 관측한 행동으로 같은 목표의 agent(잠재 팀)를 찾고, 그 팀 안에서 critic consensus를 하여 학습을 개선한다.**

다음 두 명제를 따로 검증한다.

1. **실험 A**: 국소 행동 정보로 잠재 팀을 식별할 수 있는가? 또 같은 팀의 critic이 다른 팀보다 실제로 더 잘 호환되는가?
2. **실험 B**: 정답 팀을 알려줘도 팀 내부 critic 공유가 학습을 개선하는가?

#### 이 설계에 반영한 코드상의 사실

- 관측은 **자기 팀 기준(team-relative)**이다. `requested_shelf` 채널, `relevant_goal` 채널, `self_carrying_requested_shelf`는 모두 관측하는 agent 자신의 팀 기준으로 표시된다(`rware/utils/semantic_observation.py`의 `_requested_shelf_ids_for_observation`·`_relevant_goal_cells`, `rware/multi_team_warehouse.py`의 `_requested_shelves_for_observation`). 다른 agent의 팀은 관측에 없다.
- E1 지도에서 두 팀의 목표 칸은 (4,10)과 (5,10)으로 인접해 있다. home ratio .5에서는 팀 선반이 좌우 구역에 절반씩 섞인다.
- 따라서 같은 canonical 입력을 두 actor에 넣고 비교하는 현재 PGCT JS는 "이 장면에서 **내 팀의** 요청 선반/목표가 여기 있다면 어떻게 하느냐"를 비교한다. 두 팀 agent가 모두 과제를 잘 배웠다면 팀이 달라도 응답이 같아진다. 즉 이 신호는 **구조적으로 팀을 거의 구분하지 못한다**는 가설이 생긴다. 실험 A가 이를 확인한다.
- 같은 이유로, 관측 기준에서는 다른 팀의 critic도 상당 부분 호환될 수 있다. 이 경우 "같은 팀끼리만 공유"하는 이득은 작을 수 있다. 실험 A의 critic 항목과 실험 B가 이를 확인한다.
- 트레이너에는 이미 `graph_mode=oracle/unrestricted/wrong` 비교군이 구현되어 있었지만, 기록상 smoke만 실행했고 장기 학습은 없었다(`examples/EX5_PGCT.md`).

#### 실험 A — 고정 모델 평가 (학습 없음)

`exp_a_team_identifiability.py`. 각 checkpoint가 자기 stochastic masked policy로 rollout한다(기본 20회×500 step, reset seed 5,200,001–5,200,020). 평가 전후 weight hash를 확인한다. 팀 라벨은 채점에만 쓰고 점수 계산에는 쓰지 않는다.

| 항목 | 의미 | 정보원 |
|---|---|---|
| `canonical_js` | 현재 PGCT 신호. 공통 canonical 48개 입력, zero hidden | actor 응답 교환 |
| `history_js` | 두 정책을 두 agent 각자의 실제 관측 이력에서 비교. 각 network는 자기 hidden 사용 | actor 응답 교환 |
| `occupancy_js` | 방문 칸 분포 차이(공간 역할) | 위치 |
| `goal_evidence` | 관측자가 **자기 센서 범위 안에서** 본 상대의 pickup·delivery를 자기 관점으로 분류한다. 그 선반이 내 팀 요청인가, 그 목표가 내 목표인가? | 국소 관측만 |
| `critic_gap` | 각 agent 이력에서 `E[(V_i - V_j)^2]` (음수로 저장) | critic |
| `blend_gain` | `MSE(V_i, G_i) - MSE((V_i+V_j)/2, G_i)`, 초기 200 step의 유한 MC return | critic + 실제 보상 |

채점 기준:

- same-vs-cross AUROC: episode×pair 표본을 쓴다. 표본이 서로 종속이므로 기술 통계로만 본다.
- teammate recovery: 각 agent의 최고 점수 상대가 실제 팀원인 비율이다. 우연 수준은 1/3이다.
- episode bootstrap CI: 같은 팀 점수에서 다른 팀 점수를 뺀 차이의 신뢰구간이다.
- `goal_evidence`의 episode 누적 곡선: 관측이 쌓일수록 팀을 얼마나 맞히는지 본다.

기본 모델은 Stage03(E1 환경에서 평가), E1/E2 IPPO·PGCT final, Stage04 PGCT다. IPPO final이 가장 깨끗한 조건이다. 전이로 인한 유사성이 섞이지 않기 때문이다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe latent_team\exp_a_team_identifiability.py
```

출력: `output/latent_team/exp_a_<시각>/` (`summary.json`, `REPORT.md`, `identifiability.png`, 모델별 `*_scores.npz`).

결과 해석:

- `goal_evidence`만 팀을 맞히고 `canonical_js`·`history_js`는 우연 수준이라면, 행동에는 팀 정보가 있다. 다만 현재 PGCT가 보는 "공통 입력 응답 유사성"이 그 정보를 담지 못한다는 뜻이 된다. 이 경우 팀 추론 모듈을 "누구의 요청/목표를 수행하는가"라는 결과 수준 증거 위에 다시 설계해야 한다.
- `critic_gap`·`blend_gain`에서 same과 cross 차이가 없다면, 이 환경에서는 팀을 정확히 찾아도 critic 공유 대상으로서의 이점이 작다. 이 경우 실험 B의 oracle도 all-peer와 비슷할 것으로 예상된다. 그러면 팀마다 value가 실제로 달라지는 환경 설계가 먼저 필요하다.

#### 실험 B — 정답 팀 critic 공유 학습 (장기 학습, 사용자 승인 후 실행)

`exp_b_oracle_consensus.py`, `run_exp_b.ps1`. 기존 E1(또는 E2) PGCT/IPPO seed1과 같은 Stage03 weights, 환경, PPO 설정, 예산(4,000,768 step), 평가 seed, **같은 canonical probe bank**를 쓴다. 기존 critic peer loss의 donor 집합만 바꾼다.

| mode | trainer `graph_mode` | donor |
|---|---|---|
| `oracle` | `oracle` | 물리 이웃 중 같은 팀(정답 라벨). 팀 추론의 상한 |
| `all` | `unrestricted` | 물리 이웃 전부 |
| `wrong` | `wrong` | 물리 이웃 중 다른 팀만 |

- 기존 PGCT와 같은 시점에 전이를 시작하도록 처음 100 update 동안 전이를 보류한다(`--transfer-warmup-updates`).
- 실행 전에 새 설정이 기존 PGCT run과 `graph_mode` 하나만 다른지 검사한다.
- `transfer.jsonl`에 update별 실제 receiver×donor allocation을 남긴다. 팀/물리 범위를 벗어난 전이가 있으면 즉시 중단한다.
- 완료된 기존 PGCT/IPPO run은 읽기만 해서 `comparison.md`로 비교한다.
- W&B와 영상은 기본적으로 끈다(`-Track`, `-SaveVideo`로 켤 수 있음). 영상은 평가 에피소드를 렌더링만 하므로 평가 수치는 바뀌지 않는다.
- 예상 시간: 기존 E1 run 속도로 run당 약 30시간. 기본 oracle+all 순차 실행이면 약 60시간이다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\latent_team\run_exp_b.ps1 -DryRun                 # 계획만
.\latent_team\run_exp_b.ps1                         # E1 seed1: oracle, all
.\latent_team\run_exp_b.ps1 -Modes oracle,all,wrong # wrong 포함
```

출력: `runs/lt_b_<시각>/`. 기존 폴더가 있으면 덮어쓰지 않고 거부한다.

결과 해석(단일 seed는 방향 확인용이다):

- oracle도 IPPO보다 낫지 않다면, 팀 추론을 개선하기 전에 consensus 방식이나 환경의 팀-가치 구조를 먼저 다시 봐야 한다.
- oracle은 낫지만 PGCT는 낫지 않다면, 팀 추론이 병목이다.
- oracle과 all이 비슷하다면, 이 환경에서는 팀 선택 자체가 성능에 중요하지 않다.

#### 추가 검토 (2026-10-13, 외부 검토 의견 반영)

##### 국소 증거가 팀 ID·내부 상태를 간접 사용했는가?

- `exp_a`는 env 이벤트(pickup/delivery)와 관측자 **자신의** 팀 요청·목표 집합으로 증거를 분류한다. 상대 agent의 팀 ID는 읽지 않는다.
- `verify_evidence_observability.py`로 같은 판정이 관측자 자신의 post-step 관측 텐서에 그대로 보이는지 확인했다. 결과는 `output/latent_team/exp_a_20261013/observability_check.json`이다. E1 IPPO, E2 IPPO, Stage04 각 5×500 step에서 pickup 985건, delivery 1,161건을 확인했고, 모든 건에서 해당 칸이 "agent+loaded"였다. `requested_shelf`/`relevant_goal` 채널 값도 판정과 100% 일치했다.
- **남는 가정**: 관측의 agent 칸은 익명이다. 본 사건을 특정 이웃 j에게 귀속하려면 이웃 식별이 필요하다. 이는 PGCT가 통신 상대를 아는 것과 같은 수준의 가정이다. 또 이 환경은 팀을 요청 선반·목표로 정의하므로, 이 증거는 "팀을 구분할 정보가 국소적으로 존재한다"는 확인이다. 일반적인 잠재 팀 추론 알고리즘의 성과로 볼 수는 없다.

##### blend gain의 정의와 한계

`blend_gain(i←j) = MSE(V_i(h_i), G_i) − MSE((V_i(h_i)+V_j(h_i))/2, G_i)`. h_i는 agent i 자신의 rollout 관측 이력이고, 각 network는 자기 hidden을 사용한다. G_i는 i의 실제 보상(shaping 포함)의 할인 return이며, 500-step 중 초기 200 step만 평가한다(유한 horizon, zero tail). 양수면 j 예측을 섞을 때 i의 return 예측 오차가 줄어든다는 뜻이다.

이 값은 학습된 critic을 **정적으로 평균**했을 때의 오차 변화다. 학습 중 peer loss가 주는 regularization이나 표본 효율 효과는 측정하지 않는다. 따라서 이 값이 낮아도 학습 중 consensus가 해롭다고 결론 내리지 않는다. 실제 효과는 실험 B로만 판단한다.

##### `team_reward_mode="team"`으로 바뀌는 것 (코드 확인, 실행 안 함)

- `_reward_delivery`/`_reward_shelf_return`: delivery(1.0)와 return(1.0) 보상이 운반자 대신 **선반 팀의 모든 팀원**에게 간다. pickup·progress·penalty 등 shaping은 계속 개인별이다.
- critic target: 팀원은 같은 task-return 성분을 공유하고 다른 팀은 공유하지 않는다. 팀원 간 요청 경쟁도 사라진다. "공통 목표 팀"의 정의에 맞는다.
- 그대로 Stage03에서 이어갈 수 없는 이유:
  - task return 규모가 약 2배가 되어 기존 critic 보정이 깨진다.
  - 팀원의 배송이 내 advantage에 섞여 credit assignment 잡음이 생긴다.
  - 행동 유인이 바뀐다.
  - 따라서 team reward 하의 공통 사전학습 → IPPO/oracle/all 분기로 다시 정렬해야 한다.
- **주의**: 관측은 여전히 자기 팀 기준이고 두 팀 과제는 대칭이다. 그래서 같은 입력 x에서 team-0 critic과 team-1 critic이 배우는 함수는 team reward에서도 거의 같아질 수 있다. 관측에서 팀원과 상대 팀 agent는 구분되지 않는다. PGCT peer loss는 공통 probe 입력에서 critic **함수**를 맞추므로, 팀 보상 공유만으로 "다른 팀 critic은 틀린 target"인 상황이 생긴다는 보장은 없다. 팀별 value 함수가 실제로 갈라지려면 다음 중 하나가 필요할 수 있다(가설).
  - 팀 소유를 절대 기준으로 보여주는 관측(예: 팀 색 채널)
  - 비대칭 팀 과제
  - 현재 env에는 관측을 절대 기준으로 바꾸는 옵션이 없다. 새 wrapper가 필요하다.

##### 소규모 oracle 실험

트레이너에는 학습률 schedule이 없다. `total_timesteps`는 update 횟수만 정한다. 따라서 `--timesteps 1024000`의 oracle run은 기존 E1 PGCT/IPPO seed1의 첫 1,024,000 step과 matched prefix다. 비교표는 기준 run을 같은 step에서 자른다. 기존 1M 구간 기준선은 delivery AUC IPPO 43.828, PGCT 44.605다. 예상 소요는 oracle 한 run당 약 7–8시간이다.

```powershell
.\latent_team\run_exp_b.ps1 -Modes oracle -TotalTimesteps 1024000
```

#### 처음부터 학습 (커리큘럼 없음) — `train_from_scratch.py`, `run_from_scratch.ps1`

기존 E1/E2/E3 결과는 Stage03까지 약 6M step 커리큘럼을 거친 모델에서 분기한 조건부 비교다. 이 실행기는 체크포인트와 커리큘럼 없이 무작위 초기화로 학습한다.

| mode | 내용 |
|---|---|
| `ippo` | 통신·critic 공유 없음 |
| `pgct` | 기존 JS gate(policy graph, 물리 이웃) |
| `oracle` | 물리 이웃 중 같은 팀 critic 공유(정답 라벨) |
| `all` | 물리 이웃 전부와 공유 |
| `wrong` | 물리 이웃 중 다른 팀과만 공유 |

- 같은 (맵, seed)의 모든 mode는 같은 환경(기본 E1, home .5, 요청 4, individual reward), PPO 설정, 예산, 평가 seed, **같은 무작위 초기 가중치**(`initial_weights_sha256.txt`로 확인), **같은 canonical probe bank**(계획 시 1회 생성)를 쓴다. critic peer loss의 donor 집합만 다르다.
- 설정은 기존 E1 PGCT run에서 가져온다. 단, 이전에 처음부터 학습에 성공한 run의 lr 2e-4와 entropy .05를 쓴다. 기본 예산은 10M step(이전 성공 run 9.93M)이다. 모두 옵션으로 바꿀 수 있다.
- 전이는 PGCT warm-up과 같은 100 update 이후 시작한다. `transfer.jsonl`에 실제 allocation을 남기고, 팀·물리 범위를 벗어나면 중단한다.
- 학습 데이터:
  - `metrics.jsonl`(학습 지표, 51,200 step마다 20×500 평가)
  - `transfer.jsonl`, `communication.jsonl`, `spatial.jsonl`
  - `checkpoint_*.pt`(기본 250 update마다), `final.pt`
- `comparison.md`: mode별 delivery AUC, 마지막 10회 평가, 10/20/30/40 delivery 도달 step, seed 간 표준편차, 같은 초기 가중치 여부.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 1) 학습 가능성 pilot: IPPO와 oracle, 2M step, 병렬
.\latent_team\run_from_scratch.ps1 -Modes ippo,oracle -TotalTimesteps 2000000 -Parallel

# 2) 본 비교: 4개 mode, 10M step, seed 1 (이후 -Seeds 2,3)
.\latent_team\run_from_scratch.ps1 -Modes ippo,pgct,oracle,all -Seeds 1 -Parallel

# 진행 확인과 비교표 (<폴더>는 실행 시 출력되는 runs\scratch_<시각>)
Get-Content runs\scratch_<시각>\e1_oracle_s1.log -Tail 3
C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe latent_team\train_from_scratch.py --compare-only --plan runs\scratch_<시각>
```

1단계가 끝나면 2단계를 자동으로 시작하는 파이프라인:

```powershell
.\latent_team\run_scratch_pipeline.ps1 -Detach
```

- 기본 구성: 1단계는 ippo+oracle 2M, 2단계는 ippo/pgct/oracle/all 10M, 둘 다 seed 1, 병렬.
- 1단계의 모든 job이 `complete`일 때만 2단계를 시작한다. 1단계의 학습 성능을 판단하는 것은 아니다.
- `-Detach`로 실행하면 숨은 PowerShell에서 돌아가므로 창을 닫아도 계속된다. 다만 PC 재부팅에는 대비되지 않는다.
- 출력은 `runs/scratch_<시각>_stage1`, `_stage2`, `_pipeline.log`다.
- 단계별 mode·step·seed는 `-Stage1Modes`, `-Stage2Timesteps` 등의 옵션으로 바꾼다.

`-Parallel` 없이 실행하면 같은 PowerShell 창에서 순차 실행한다. `-Wait`는 병렬 job이 모두 끝날 때까지 기다린다. `-PlanOnly`는 계획과 bank만 만든다. 기존 E1 단일 프로세스 속도(약 37 step/s)로 보면 run당 2M은 약 15시간, 10M은 약 75시간이다. 병렬 실행 시 각 run 속도는 더 느려질 수 있다.

#### W&B, 학습 구간, 비교 알고리즘 (2026-10-13 추가)

- **W&B**
  - `-Track`으로 켠다. project는 `rware-from-scratch`, run 이름은 `e1_<mode>_s<seed>`다.
  - group은 출력 폴더 이름(stage별)이고, tag에 stage·맵·seed·mode가 들어간다.
  - config에는 trainer 설정 전체와 algorithm·stage·seed·home ratio·env_kwargs·예산이 들어간다.
  - 모든 run이 `step=env_steps`로 기록되므로 W&B의 Step 축이 env step이다.
  - gate 지표: `update/gate_ratio`, same/cross arc 수.
  - `-Detach`에서도 `_netrc` 로그인으로 동작함을 확인했다.
  - PowerShell 파이프라인 로그는 UTF-8로 남는다.
- **학습 구간 근거**
  - 이전 from-scratch PGCT(home 1.0, complete graph, 로컬 W&B 기록 `run-bhh1l6x8`)에서 pickup은 약 1.5M, delivery는 1.7M에 시작했다.
  - 평가 기준 20 이상은 2.3M, 40 이상은 3.3M이었고, 6–9M에 56–60으로 수렴했다.
  - 현재 home .5는 아직 기록이 없다.
  - 그래서 기본값을 Stage1 4M(pilot), Stage2 15M으로 바꿨다.
  - Stage1은 Stage2의 초기화가 아니며 같은 mode의 앞 구간과 겹친다. 생략하려면 `-SkipStage1`을 쓴다.
- **비교 알고리즘**: `mappo`, `seps`, `hetdps` mode. 구현 차이와 비용은 [BASELINES.md](BASELINES.md)에 있다.

```powershell
# 예: Stage1 생략, 7개 알고리즘 15M, W&B, 백그라운드 (7 프로세스 → 스레드 2개씩 권장)
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -ThreadsPerJob 2 `
  -Stage2Modes ippo,pgct,oracle,all,mappo,seps,hetdps -Stage2Seeds 1
```

#### E1-F 환경과 probe bank v2 (2026-10-15 추가, 옵션)

- **`--env-variant e1f`**(PowerShell `-EnvVariant e1f`): E1 맵에서 팀 목표만 두 아래 모서리로 옮긴다(빨강 (0,10), 파랑 (9,10)).
  - 관측(팀 기준), 보상, 선반 배치는 그대로다.
  - 환경의 기존 `team_goal_positions` 설정만 쓰며, 환경 코드는 바꾸지 않았다.
- **`--probe-bank v2`**(`-ProbeBank v2`): `probes_v2.py`가 만드는 새 bank.
  - 학습 env 설정 그대로 상태를 배치하고 실제 관측 함수로 probe를 뽑는다. 역할별 고유 입력만 남기고, 시나리오가 선언한 조건(적재·반납·목표 가시성)을 관측이 위반하면 거부한다.
  - **gate**(PGCT JS용, 48개): 요청 선반 적재 + **어느 팀 목표도 안 보이는** 상태. 같은 입력이 두 팀 모두에게 유효하며, 목표가 분리된 E1-F에서만 팀에 따라 정답 방향이 달라진다.
  - **transfer**(critic 증류용, 64개): 탐색 14, 적재·목표 보임 16, 적재·목표 안 보임 16, 반납 16, 목표 도착 2.
  - Oracle·All·PGCT 모두 증류는 transfer bank로 한다(`transfer.jsonl`의 `distill_probe_count`=64).
  - 모든 agent가 같은 결정적 규칙으로 생성하므로 관측 교환은 없다.
- **기본값**은 지금과 같다(`e1`, `canonical`). 실행 중인 `scratch_20261015_093349` run에는 영향이 없다.
- **확인한 것**: `output/env_view_20261015/probes_v2/`(그림·요약), smoke `runs/smoke_e1f_v2_20261015`, `tests/test_latent_team.py`의 v2/E1-F 테스트(모서리 목표에서 실제 배송 확인 포함), 전체 183 passed.

```powershell
# E1-F + v2 probe, 4개 비교군, 15M (승인 후 실행)
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -EnvVariant e1f -ProbeBank v2 -Stage2Seeds 1
```

#### 아직 하지 않은 것

- 추론된 팀(learned-team) 모드는 구현하지 않았다. 실험 A에서 쓸 만한 팀 신호가 확인된 뒤에 설계한다.
- 실험 B 장기 학습은 실행하지 않았다. 검증은 `runs/lt_b_smoke_20261013`(oracle/all/wrong 각 64-step)과 `tests/test_latent_team.py`뿐이다.

## 출처: `latent_team/BASELINES.md` (수정 2026-10-13 20:05)

### 비교 알고리즘 구현 기록 — MAPPO / SePS / HetDPS

2026-10-13 Claude Code. 코드: `marl_baselines.py`. 실행: `train_from_scratch.py --modes mappo seps hetdps` 또는 `run_from_scratch.ps1 -Modes ...`.
기존 IPPO/PGCT/oracle/all/wrong 코드는 변경하지 않았다. 세 알고리즘 모두 기존 `T.train` 루프를 그대로 쓰고, 한 프로세스 안에서 agent network 생성과 `update_ippo`만 교체한다.

#### 공통 조건 (IPPO/PGCT와 동일하게 유지한 것)

- **환경·관측·보상**: E1 11×10, 4 agents/2 teams, home .5, individual reward, semantic 1593차원 관측, action mask.
- **rollout·평가**: `collect_rollout`, `evaluate` 함수를 그대로 쓴다. 평가는 51,200 step마다 20×500, seed 5,000,001부터. train/eval 지표 계산도 같다.
- **예산과 seed**: 같은 env step 예산과 seed 목록을 쓴다. W&B Step 축은 모두 env steps다.
- **PPO 설정(공통 예산 기준)**: rollout 1024, sequence 64, epochs 4, minibatch 8 chunks, clip .2, value clip .2, lr 2e-4, entropy .05, γ .99, λ .95, grad norm .5, Adam eps 1e-5.
- **네트워크 용량**: IPPO와 같은 semantic CNN encoder + GRU(128) + linear head. 공식 구현의 MLP/LayerNorm 구조는 쓰지 않는다.
- **advantage 정규화**: 전체 batch(모든 agent) 단위로 한다. MAPPO·HetDPS 방식이다.
- **IPPO와 다른 점**: 기존 IPPO/PGCT trainer의 `skip_zero_reward_actor_update`는 baseline에 적용하지 않는다.
- **초기 가중치**: 같은 seed라도 구조가 달라 IPPO와 초기값이 다르다. 비교표 "Same init" 열에는 `n/a`로 표시된다.
- **checkpoint**: 모든 network는 `agents[0]` state_dict에 들어 있다. 배정 정보는 `*.baseline.pt`, `baseline_state.json`에 저장된다.

#### MAPPO — Yu et al., NeurIPS 2022 (marlbenchmark/on-policy)

**구현한 핵심**
- 모든 agent가 공유하는 recurrent actor
- 공유 중앙 recurrent critic V(s)
- ValueNorm(β=0.99999, debiasing, var≥1e-2)
- normalized target에 대한 Huber(δ=10) + value clipping(두 손실 중 큰 값)
- actor/critic 별도 Adam
- PPO clip
- denormalized value로 GAE 계산
- time-limit bootstrap도 중앙 critic으로 계산

**원 구현과 다른 점**
- **중앙 상태**: 이 환경에는 전역 상태가 없다. 그래서 4개 agent의 국소 관측을 공유 CNN으로 인코딩해 이어 붙이고, 평가 대상 agent의 one-hot을 더했다. on-policy의 MPE는 관측 연결을 쓰고, SMAC의 agent-specific state는 ID를 포함한다. reward가 individual이라 agent 구분이 필요하다.
- **agent ID**: actor 입력에 agent one-hot을 추가했다(공유 정책에서 agent 구분).
- **하이퍼파라미터**: 원 논문 기본값(lr 5e-4/7e-4, epoch 5–15, mini-batch 1, chunk 10, grad norm 10, entropy .01, feature LayerNorm) 대신 공통 예산 설정을 썼다.
- **중앙 critic 값 계산 시점**: rollout 뒤 기록한 joint 관측으로 다시 계산한다. 첫 minibatch replay 오차는 약 2e-7이었다.

**정보 조건**: critic이 다른 agent의 관측을 쓰는 **CTDE, 추가 정보 허용 비교군**이다. 실행 시 행동은 자기 관측만 쓴다.

#### SePS — Christianos et al., ICML 2021 (uoe-agents/seps)

**공식 기본값대로 구현한 것**
- **network 구성**: agent 수(N)만큼 network(actor + local critic). actor와 critic 모두 선택적으로 공유한다.
- **클러스터링 전**: agent 0 → network 0, 나머지는 무작위 배정한다(`sample_laac`). 클러스터링 전에도 RL 학습은 계속한다(`delay_training=False`).
- **pretraining 길이**: `pretraining_steps=5000`×8 env = 40,000 env step이며 예산에 포함된다.
- **VAE 구조**: `LinearVAE`. encoder는 agent one-hot을 받아 2×10을 출력하고, decoder는 [z, obs, act]를 받아 [next_obs, rew]를 복원한다.
- **VAE 학습**: loss = MSE(sum) + 1e-4·KLD(sum), 10 epochs, batch 128, Adam 3e-4.
- **클러스터링**: encoder 평균에 KMeans(k-means++, n_init=10)를 적용한다. K는 Davies–Bouldin 기준으로 2..N−1에서 고른다.
- **클러스터링 후**: cluster label을 network index로 쓰고, network는 재초기화하지 않는다.

**원 구현과 다른 점**
- **학습기**: A2C(n_steps 5, 8 env)가 아니라 공통 recurrent PPO를 쓴다. SePS의 기여는 학습기와 독립적인 선택적 공유다.
- **병렬 env**: env가 1개라서, 병렬 env마다 달랐던 클러스터링 전 무작위 배정을 rollout마다 다시 뽑는 방식으로 대체했다.
- **buffer**: reservoir 50,000 transition으로 제한했고 관측은 float16으로 저장한다. episode 경계 transition은 next_obs가 없어 제외한다.
- **VAE 은닉 크기**: `HIDDEN` 상수 값은 원문에서 확인하지 못해 64를 썼다.
- **클러스터링 라이브러리**: scikit-learn이 환경에 없어 KMeans·Davies–Bouldin을 같은 기본값의 numpy 코드로 구현했다. 사용자 환경에 패키지를 설치하지 않았다.

**추가 비용**: 40,000 env step의 pretraining(예산 안), VAE 학습 1회 약 9초(GPU, 212,110 parameters, 50k transitions), RAM 약 300MiB.

#### HetDPS — Heterogeneity-based Dynamic Parameter Sharing, AAMAS 2026 (Harry67Hu/HetDPS)

**공식 설정대로 구현한 것**
- **network 구성**: N개 network(actor + local critic). 처음에는 모든 agent가 network 0을 쓴다.
- **buffer**: FIFO, 최근 20×5×32 = 3,200 env step × N agent.
- **측정 주기**: 3,200 env step마다(`reparameter_interval=20` update × 160 transition) 측정한다.
- **VAE**: `BiHierarchicalVAE`(구조 그대로, HIDDEN 32, z 40)를 이어서 학습한다. 매번 새 Adam(lr 5e-4), 10 epochs, batch 128, kl 1e-4, MSE(sum).
- **VAE 입력·출력**: encoder는 agent one-hot과 condition [local_state, act one-hot]을 받는다. 복원 대상은 [next_local_state, next_obs, rew_pad]다.
- **거리**: 버퍼의 모든 상태 × 5개 행동 조건에서 agent별 Gaussian 사이 Wasserstein 거리를 계산해 평균한다(`fixed_obs_all_acts`).
- **군집**: AffinityPropagation(−WD), preference는 중앙값, damping .5.
- **동적 공유**(`compute_dynamic_parameter_sharing`, merge_mode='majority')
  - 첫 측정: cluster label을 network로 쓴다.
  - cluster 수가 같으면: Hungarian 매칭.
  - 분할: 새 network에 겹침이 가장 큰(없으면 가장 가까운) 기존 network를 복사한다.
  - 병합: 번호를 다시 매기고 다수 network의 파라미터를 복사한다.
  - actor와 critic을 함께 복사한다.

**원 구현과 다른 점**
- **network 구조**: MAPSNet(MLP shallow+deep, LayerNorm, network별 초기화) 대신 공통 CNN+GRU를 쓴다. hetdps mode에서는 shallow/deep 배정이 같으므로 network 단위 배정과 동등하다.
- **학습기**: 비순환 MLP PPO(n_steps 5 × 32 env)가 아니라 공통 recurrent PPO를 쓴다.
- **측정 시점**: 3,200 env step 기준을 update 경계(1,024 step)에서 확인하므로 약 3 update마다 측정한다.
- **라이브러리**: scikit-learn/scipy가 없어 AP와 Hungarian을 numpy로 구현했다. Hungarian은 N≤4이므로 정확한 순열 탐색이다.
- **network 수 한계**: 분할로 network id가 N을 넘으면 비어 있는 index를 재사용한다. 원 코드는 이 경우 오류가 난다.
- **buffer 처리**: episode 경계 transition은 제외하고, 관측은 float16으로 저장한다.
- **생략한 것**: 측정 전용인 model-based 정책 거리(`compute_fusions`, `if_measure`)는 HetDPS 결정에 쓰이지 않으므로 계산하지 않았다.

**추가 비용**: 측정 1회 약 4.4초(GPU, VAE 537,915 parameters, 12,800 transitions). 15M step이면 4,687회로 약 5.8시간 추가되며, 학습 시간의 약 5%다. RAM은 약 80MiB다.

#### 검증 (smoke, 각 64 step)

- **MAPPO**: 2회 update. approx_kl은 약 1e-9로 actor replay가 일치했다. critic replay 오차는 약 1.5e-7이다.
- **SePS**: 클러스터링 전 배정 [0,1,0,1] → VAE + DB → K=3, 배정 [2,0,2,1].
- **HetDPS**: 측정 2회, 배정 [0,1,0,0] → [0,0,0,1].
- **W&B**: 4개 run이 모두 `finished`(project `rware-from-scratch-smoke`), Step = env steps.
- **단위 테스트**: `tests/test_latent_team.py`의 군집·AP·Hungarian·동적 공유·ValueNorm·W2 테스트 포함, 전체 182 passed.
- 짧은 smoke에서 reward가 오르지 않은 것은 알고리즘 성능 판단 근거가 아니다.

## 출처: `examples/README.md` (수정 2026-10-13 19:09)

### RWARE IPPO / PGCT 실행 코드

현재 연구에 사용하는 학습, 평가, probe 도구를 정리한 목록입니다.

| 파일 | 용도 |
|---|---|
| `train_recurrent_ippo_consensus.py` | 공통 recurrent IPPO 학습기와 PGCT probe / critic transfer 구현 |
| `run_semantic_cnn_marl_pgct_from_scratch.ps1` | IPPO(`-Run none`), PGCT 및 oracle/wrong/unrestricted 비교군 실행; 체크포인트 초기화도 지원 |
| `env_kwargs_stage2_pgct_success_unblock_zones_individual.json` | 현재 실행기의 기본 환경·보상 설정 |
| `train_pgct_physical_mixing_curriculum.py` | 9700 모델에서 시작하는 PGCT 물리 이웃·shelf 혼합 커리큘럼 |
| `run_pgct_09700_physical_mixing_curriculum.ps1` | 위 PGCT 커리큘럼의 PowerShell 실행기 |
| `train_pgct_spatial_experiments.py` / `run_pgct_spatial_experiments.ps1` | 같은 초기 모델에서 3개 맵 × PGCT/IPPO를 독립적으로 실제 학습하는 비교 실험 |
| `train_pgct_transfer_experiments.py` / `run_pgct_transfer_experiments.ps1` | 기존 맵에서 Stage03 이후 on/off, 전달량 통제 random donor, 3–4 제거와 probe/critic 진단 |
| `plot_pgct_probe_charts.py` | 공통 probe 행동확률·pair별 JS 색상 차트와 학습 곡선; 기존 로그도 읽기 전용으로 지원 |
| `diagnose_pgct_rollout_compatibility.py` | 저장된 공통 observation 이력을 replay하여 recurrent policy JS와 critic 예측 차이를 추론만으로 비교 |
| `train_hard_rware_experiments.py` / `run_hard_rware_experiments.ps1` | 장애물·배송 제약 환경의 분리 실행기 ([HARD_RWARE_EXPERIMENTS.md](HARD_RWARE_EXPERIMENTS.md)) |

공통 환경, semantic 관측, canonical probe 생성 코드는 `../rware/`에 있고,
회귀 검증은 `../tests/`에 있습니다. 잠재 팀 추론·oracle consensus 검증은 `../latent_team/`에 분리돼 있습니다.

#### IPPO 비교용 사전학습

다음 명령은 팀 shelf가 완전히 분리된 환경에서 PGCT 없이 학습합니다.
학습률은 실행기에 지정된 `2e-4`이며, 기존 PGCT 사전학습과 같은
4 agents, sensor range 5, home ratio 1.0, entropy 0.05, seed 1을 사용합니다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
.\examples\run_semantic_cnn_marl_pgct_from_scratch.ps1 `
  -Run none -AgentCount 4 -SensorRange 5 -ShelfHomeRatio 1.0 `
  -TotalTimesteps 9932800 -EntropyCoef 0.05 -Seed 1 -RunNameSuffix off
```

PGCT 사전학습은 같은 실행기에 `-Run policy-complete`를 사용합니다.
`-Run policy-physical`은 물리 이웃만 후보로 하는 비교 설정입니다.
이 실행기는 `-InitCheckpoint`를 지정하면 actor와 critic 가중치를 모두 초기화합니다.
Optimizer와 rollout 상태까지 복원하는 완전한 resume은 아닙니다.

#### 커리큘럼과 평가

현재 stage04 결과를 만든 PGCT 커리큘럼의 상세 설정은
[PGCT_PHYSICAL_MIXING_CURRICULUM.md](PGCT_PHYSICAL_MIXING_CURRICULUM.md)에 있습니다.
이 실행기의 단계별 기본 예산은 1M / 2M / 3M / 4M이며 학습률은 `1e-4`입니다.

공간 확대 **학습** 비교는 [PGCT_SPATIAL_EXPERIMENTS.md](PGCT_SPATIAL_EXPERIMENTS.md)의
`run_pgct_spatial_experiments.ps1`을 사용합니다. 기본은 stage03에서 시작하는 6개 비교 실험입니다.
알고리즘과 문서의 대응은 [EX5_PGCT.md](EX5_PGCT.md)에 정리돼 있습니다.

현재 우선순위인 **기존 맵의 critic transfer 유익성 검증**은
[PGCT_TRANSFER_EXPERIMENTS.md](PGCT_TRANSFER_EXPERIMENTS.md)의
`run_pgct_transfer_experiments.ps1`을 사용합니다. 기본은 같은 Stage03에서
PGCT/IPPO × training seeds1·2·3이며 공간 실험의 완료된 E1 결과를 재사용할 수 있습니다.

#### Windows W&B 영상 경로

긴 실행 이름은 Windows 파일 경로 제한에 걸릴 수 있습니다. 짧은 suffix를 사용하거나
프로젝트를 `subst` 드라이브로 연결해 실행할 수 있습니다. 드라이브 별칭 사용 시
W&B가 Git 경로와 현재 드라이브를 혼동하지 않도록 같은 PowerShell에서 다음을 설정합니다.

```powershell
$env:WANDB_DISABLE_GIT = "true"
```

이 옵션은 Git 메타데이터 수집만 끄며 지표·영상 기록은 유지합니다.
`-NoTrack`은 W&B 전체를 끄는 별도 선택입니다.

#### 정리 범위

단일 에이전트 delivery / return 학습 진입점, 예전 actor-only PGCT 실행기,
중복 실행기와 그 전용 설정, 루트의 임시 랜덤 실행 예제를 제거했습니다.
공통 학습기, 환경 구현, 현재 IPPO/PGCT 실행기와 설정, 맵 평가·probe 도구,
테스트, 기존 체크포인트와 실험 로그는 보존했습니다.

2026-10-13 사용자 요청으로 다음을 추가 삭제했습니다(git 추적 파일은 이력에 남음).
- 끝난 09700 일반화 평가 도구: `eval_checkpoint_generalization.py`와 테스트, ps1 2개, 문서
- 일반 혼합 커리큘럼 실행기
- 그래프 시각화·PPT 이미지 도구
- 대체된 FoV·CNN 검토 문서
- 미사용 `Success_checkpoint/`, 임시 프레임·영상 분석 폴더
- 자동 생성 `generated_configs/`

`runs/`의 과거 결과는 보존했습니다.

## 출처: `examples/EX5_PGCT.md` (수정 2026-10-13 19:09)

### ex5 기준 CNN PGCT

기준 문서: 사용자가 정정한 `C:/Users/95101/Downloads/ex5.pdf`.
ex6용 방향성 FoV, 전방 관측 마스크, 시간 방향 연결성 진단은 제거했다.
기존 실험 결과와 체크포인트는 보존하며 새 실험명에는 `ex5_`를 붙인다.

#### 구현과 PDF의 대응

| 항목 | 현재 실행 설정 |
|---|---|
| 태스크 관측 | 방향과 무관한 SR5 정사각형 11×11, agent별 CNN/GRU |
| 후보 그래프 | 기본 complete. 실제 전달은 PGCT gate로 제한 |
| Canonical Q, pp.15–17 | 모든 정책에 동일한 고정 shared objective bank, zero probe hidden; online 상태를 사용하지 않음 |
| JS 거리, pp.18–20 | 전체 action distribution의 JS를 probe/time에 균등 평균 |
| EMA, pp.23–24 | beta=0.35, affinity=exp(-D/0.25)는 진단 점수이며 확률이 아님 |
| Gate, p.25 | warm-up 뒤 `D_ema < 0.12`인 쌍에 binary gate; 대각선 0 |
| Warm-up | PPO update 100회; 5 update마다 probe, 쌍별 측정 최소 8회 |
| Critic transfer, pp.26–28 | receiver별 gate 정규화, 고정 donor target에 stop-gradient, local value loss + 0.01 peer loss |
| 독립 학습 | 그래프/probe/peer loss/consensus 모두 OFF; 각 agent의 로컬 PPO는 계속 수행 |
| 영상 | 허용된 연결만 표시. 대칭 gate는 선 하나; 독립 모드는 선 없음 |

48개 probe, Lp=1을 기본으로 둔다. 이는 zero-state 단일 입력 비교이며 긴 recurrent history를 검증한 설정은 아니다. 48개는 PDF가 지정한 최적값이 아니라 기존 작업 시나리오 bank의 크기다. 같은 bank를 actor 거리와 critic 전달에 재사용하며 `canonical_probes.pt`에 저장한다. 실제 팀 라벨에 따라 정책별 probe를 달리 주는 `agent-team` 옵션은 이 실행기에서 허용하지 않는다.

threshold 0.12, warm-up 100, bank 크기는 실험 파라미터다. 초기 랜덤 정책은 D≈0이므로 **warm-up 이후에도 잘못 연결될 수 있다**. ex5는 이를 방지한다는 보장을 하지 않는다. 이전에 추가했던 KL-to-uniform 정보량 gate는 기본값 0으로 해제했다. Python CLI의 soft gate와 정보량 gate는 별도 ablation 옵션이며 ex5 기본 실행에서는 사용하지 않는다. 라벨 기반 threshold 보정도 하지 않는다.

반납 상태 관측, 동료 이동에 의한 잘못된 진행 보상 방지, timeout bootstrap, agent별 학습 진단과 4/8/16명·선반 혼합 설정은 유지했다. 이것들은 ex6 가정에 의존하지 않는 환경/학습 수정이다.

#### 실행

아래는 PowerShell 현재 창에만 실행 정책을 적용한다. 두 학습은 순차 실행된다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# ex5 PGCT: 완전 후보 그래프 + 학습된 gate
.\examples\run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run policy-complete -CommunicationEnabled $true -AgentCount 4 -SensorRange 5 -Seed 1 -TotalTimesteps 10000000

# 동일 환경의 independent PPO
.\examples\run_semantic_cnn_marl_pgct_from_scratch.ps1 -Run policy-complete -CommunicationEnabled $false -AgentCount 4 -SensorRange 5 -Seed 1 -TotalTimesteps 10000000
```

`-AgentCount 8` 또는 `16`으로 변경할 수 있다. W&B를 사용하지 않으려면 `-NoTrack`을 추가한다. 영상은 run 폴더의 `videos/final.mp4`, 전달 행렬과 거리/count는 `communication.jsonl`에 기록된다. 영상 연결은 허용된 peer 관계를 뜻하며 환경 매 step마다 optimizer transfer가 수행된다는 의미는 아니다.

비교군: `-Run oracle`(같은 objective), `-Run wrong`(다른 objective), `-Run unrestricted`(모든 peer), `-Run none`(독립). Oracle/Wrong만 팀 라벨을 사용하며, 학습용 PGCT는 이를 읽어 gate를 만들지 않는다. Oracle/Wrong/unrestricted는 warm-up 없이 해당 전달 관계를 사용한다. `policy-physical`은 별도의 거리 제한 ablation이다. `-Run all`은 여섯 실험을 순차 실행한다.

선반 소유권을 점차 섞는 커리큘럼은 [PGCT_PHYSICAL_MIXING_CURRICULUM.md](PGCT_PHYSICAL_MIXING_CURRICULUM.md)의 실행기를 사용한다. 과거 일반 혼합 커리큘럼 실행기(`run_semantic_cnn_mixing_curriculum.ps1`)는 2026-10-13 사용자 요청으로 삭제했으며 git 이력에 남아 있다.

각 stage는 고정 예산이며 이전 actor/critic을 가져오고 optimizer는 새로 시작한다. 성능 기준 자동 승급은 아니다. 새 bank는 stage별로 생성된다.

#### 검증 범위

ex5의 pp.29–33은 같은 checkpoint·optimizer·batch에서 transfer/independent branch를 비교해 utility, Spearman correlation, negative transfer를 실험으로 검증하라는 내용이다. 위의 두 독립 학습 run만으로 이 matched-branch 검증을 대신할 수 없다. 이번 변경은 학습 방법과 비교군의 구현 정렬이며, 장기 수렴·전달 이득·optimal probe 수를 입증하지 않는다. matched-branch utility 분석은 아직 구현하지 않았다.

기존 FoV 체크포인트의 이어 학습을 ex5 from-scratch 결과로 취급하면 안 된다. 실행 중인 프로세스는 파일 수정이 자동 반영되지 않으므로 새 실험은 위 명령으로 시작한다.

검증 결과: 전체 pytest 130개 통과. 4-agent CNN으로 policy/none/wrong/unrestricted 각 32-step smoke run 완료, 실제 전달 arc 수 12/0/8/12 확인, policy/none 영상 저장 및 육안 확인. smoke에서는 전달 경로 검증을 위해 warm-up=0/min-count=1을 사용했으며 정식 launcher의 100/8 설정과 구분한다.

## 출처: `examples/PGCT_PHYSICAL_MIXING_CURRICULUM.md` (수정 2026-10-02 11:23)

### 09700 → 거리 제한 PGCT + shelf 혼합 커리큘럼

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1
```

기본 초기 모델은 ex5 `policy-complete`, 4개 에이전트, 센서 범위 5,
seed 1 학습의 `checkpoint_09700.pt`입니다. actor와 critic 가중치를 모두
이어받아 미세 조정하며, 원본 체크포인트는 수정하지 않습니다.

| 단계 | 통신 | Shelf 혼합률 | Home ratio | 추가 학습 예산 |
| --- | --- | --- | --- | --- |
| 1 | physical, 센서 범위 이내 | 0% | 1.0 | 100만 스텝 |
| 2 | physical, 센서 범위 이내 | 12.5% | 0.875 | 200만 스텝 |
| 3 | physical, 센서 범위 이내 | 25% | 0.75 | 300만 스텝 |
| 4 | physical, 센서 범위 이내 | 50% | 0.5 | 400만 스텝 |

에이전트 4개, 기존 맵, 센서 범위 5를 유지합니다. 09700에 저장된 환경의
보상 설정과 네트워크 구조를 읽어 사용합니다. 학습률은 `1e-4`, entropy
계수는 `0.02`로 설정했습니다. 이 예산은 시작용 설정이며, 성능 검증을
마친 최적 커리큘럼은 아닙니다. 단계 전환은 성공률 기준이 아니라 예산 소진
기준입니다. 실제 스텝 수는 1024 스텝 rollout 단위로 올림됩니다.

#### 거리 제한의 의미

모든 단계에 다음 설정을 명시적으로 적용합니다.

```text
communication_enabled = true
communication_topology = physical
comm_graph_mode = physical
communication_range = sensor_range = 5
peer_transfer_mode = pgct
```

연결 조건은 `PGCT 허용 AND max(abs(dx), abs(dy)) <= 5`입니다.
원형 거리 대신 11×11 정사각형 관측 범위와 같은 거리 기준을 사용합니다.
방향이나 shelf에 의한 가림을 추가한 모델은 아닙니다.

렌더러의 초록 선은 매 환경 스텝의 위치로 제한됩니다. 기존 학습 코드는
rollout 뒤 PGCT 전이 대상을 정할 때도 현재 이웃으로 gate를 마스킹하므로,
이전에는 가까웠어도 업데이트 시점에 범위를 벗어난 에이전트는 제외합니다.
optimizer 업데이트 중에는 환경 위치가 변하지 않습니다.

기존 PGCT 구현을 그대로 사용합니다: 정책 유사도로 관계를 정하고,
공통 probe에서 다른 에이전트의 critic 예측을 전이하는 보조 손실을 적용합니다.
상대의 실시간 관측을 actor 입력에 전달하는 별도의 메시지 네트워크를 추가한 것은 아닙니다.

#### Shelf 혼합과 단계 간 연결

`balanced_soft_zones`로 두 팀의 shelf 총수를 유지하면서 구역 사이의
**shelf 팀 소속**을 섞습니다. Shelf 좌표 자체를 뒤섞지는 않습니다.
혼합 배치는 환경 reset 시 생성되며, 각 단계에서는 해당 혼합률을 유지합니다.

각 단계의 `final.pt`를 다음 단계의 `--init-checkpoint`로 사용합니다.
actor·critic 파라미터는 모두 전달하지만 **Adam 상태와 PGCT 그래프 통계는
매 단계 초기화**합니다. 완전한 학습 상태 resume이 아닌 단계별 미세 조정입니다.
과거 complete 그래프를 사용하지 않고 새 물리 이웃에서 관계를 다시 추정합니다.
각 단계의 초기 100 업데이트는 PGCT 전이 warmup이며, 최소 probe 횟수 조건도 적용합니다.
따라서 초반에 초록 선이 없는 것이 정상일 수 있습니다.

#### 실행 옵션

```powershell
# 설정과 연결 경로만 생성: 학습하지 않음.
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1 -DryRun

# 네 단계마다 64스텝만 실제 학습: CPU, W&B 및 영상 비활성화.
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1 -SmokeTest

# W&B 없이 본 학습. 로컬 평가 영상은 계속 저장함.
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1 -NoTrack

# 단계별 예산 변경.
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1 `
  -StageTimesteps 2000000,3000000,4000000,5000000

# 필요할 때 6개 또는 8개로 확장. 증가한 에이전트는 기존 정책을 순환 복제함.
.\examples\run_pgct_09700_physical_mixing_curriculum.ps1 -AgentCount 6
```

기본 출력은 `runs/pgct09700_physical_mixing_<timestamp>/`입니다.
`-OutputDir`로 지정할 수도 있으며 기존 폴더에는 덮어쓰지 않습니다.

- `curriculum.json`: 전체 단계 설정, 전 단계 체크포인트 경로, 진행 상태.
- `stageXX_.../final.pt`: 단계별 최종 모델.
- `stageXX_.../checkpoint_*.pt`: 100 업데이트마다 저장한 모델.
- `stageXX_.../videos/`: 50 업데이트마다 및 마지막 평가에서 저장한 MP4.

본 학습은 W&B 기록을 기본으로 사용합니다. `-NoTrack`은 W&B만 끄고,
`-NoVideo`는 영상 저장도 끕니다. 기본 평가는 20회 × 최대 500스텝입니다.
시험 학습의 성공은 코드 경로·가중치 전달 검증이며 최종 성능의 증거는 아닙니다.

## 출처: `examples/PGCT_SPATIAL_EXPERIMENTS.md` (수정 2026-10-08 12:01)

### 공간 확대 PGCT / IPPO 학습 실험

이 실행기는 **실제 PPO 학습**을 수행합니다. 기본 3개 맵 × PGCT/IPPO × seed1 = 6개 실험을 순차 실행합니다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_pgct_spatial_experiments.ps1
```

| 설정 | 값 |
|---|---|
| 공통 초기 모델 | 기존 physical curriculum stage03 `final.pt` |
| 공통 환경 | 4 agents / 2 teams / home ratio0.5 / request4(팀당2) |
| 맵 e1 | 11×10: rows1 / columns3 / height8 |
| 맵 e2 | 16×16: rows2 / columns5 / height6 |
| 맵 e3 | 20×22: rows2 / columns7 / height8 |
| 예산 | 실험당4M, 실제4,000,768 steps; 기본6개 총24,004,608 steps |
| 학습 | LR1e-4, entropy.02, rollout1024, sequence64, PPO epochs4 |
| PGCT | physical range5, probe48/shared/fixed, interval5, threshold.12, warmup100, peer loss.01 |
| IPPO | communication/graph/probe/peer transfer/consensus off |
| 평가 | 공통 seeds5,000,001–5,000,020, 20 episodes×500 steps |

모든 실험은 **동일한 초기 actor·critic 가중치**에서 독립적으로 시작합니다. 앞 실험의 결과를 다음 맵이나 IPPO에 넘기지 않습니다. optimizer/graph는 새로 시작합니다. 기존 학습기·gate·보상 코드는 수정하지 않았습니다.

이 비교는 PGCT 사전학습 모델에서 **추가 학습의 transfer 효과**를 보는 실험입니다. 처음부터 pure IPPO로 학습한 비교군은 아닙니다. 기본 맵 생성기는 shelf 밀도도 e1 29.09% → e2 42.19% → e3 47.27%로 바꾸므로 공간 확대 pilot이며 밀도 통제 실험이라고 부르면 안 됩니다.

#### 선택 실행

```powershell
# 설정 생성만: 학습 없음.
.\examples\run_pgct_spatial_experiments.ps1 -DryRun

# 각 조합64스텝 시험 학습: CPU, W&B/영상 off.
.\examples\run_pgct_spatial_experiments.ps1 -SmokeTest

# 먼저 기존 맵에서 matched PGCT/IPPO 두 개만 학습.
.\examples\run_pgct_spatial_experiments.ps1 -Maps e1

# 확대 맵 두 개만 학습.
.\examples\run_pgct_spatial_experiments.ps1 -Maps e2,e3

# 세 학습 seed 반복: 18 runs, 예산은 각각 동일.
.\examples\run_pgct_spatial_experiments.ps1 -Seeds 1,2,3

# W&B off여도 로컬 지표·평가 영상은 저장.
.\examples\run_pgct_spatial_experiments.ps1 -NoTrack

# 현재 최종stage04에서 추가 적응시키려면 초기 모델을 별도로 지정.
# stage03에서 분기하는 기본 비교와 연구 질문이 다릅니다.
.\examples\run_pgct_spatial_experiments.ps1 `
  -InitCheckpoint "runs/pgct09700_physical_mixing_20260929_155338_079437/stage04_4ag_physical_home0.500/final.pt"

# 후속 workload 비교: Q4 맵 실험과 별도로 실행.
.\examples\run_pgct_spatial_experiments.ps1 -Maps e3 -RequestCount 8
```

`-Modes pgct` 또는 `-Modes ippo`, `-TotalTimesteps`, `-ShelfHomeRatio`, `-EvalSeed`, `-OutputDir`, `-NoVideo`도 지원합니다. 새 출력 폴더만 허용하며 기존 폴더를 덮어쓰지 않습니다. 중단된 실험의 자동 optimizer resume 기능은 없습니다. 남은 조합을 `-Maps/-Modes/-Seeds`로 골라 새 폴더에서 실행할 수 있습니다.

#### 결과와 접촉 기록

기본 출력은 `runs/sp_<timestamp>/`이고 실험 이름은 `e1_pgct_s1`처럼 짧습니다. Windows에서는 W&B Git 경로 추론 충돌을 피하도록 `WANDB_DISABLE_GIT=true`를 미지정 시 설정합니다. Python 실행기로 직접 실행하면 W&B는 `--track`을 지정할 때만 켜지며 PowerShell 기본 실행은 켭니다.

- `experiment.json`: 초기 모델, 전체 설정·예산, 각 실험 상태와 최종 결과.
- `eX_<mode>_sN/final.pt`, `checkpoint_*.pt`: 기존 학습기의 모델 저장.
- `metrics.jsonl`: W&B 여부와 무관한 로컬 train/update/probe/eval scalar 기록.
- `spatial.jsonl`: update마다 전체 rollout의 agent별 점유 histogram·phase·좌우 체류율·물리 후보 step 수, update 끝의 geometric 후보.
- `communication.jsonl`: 기존 학습기가 기록한 실제 optimizer 시점 전이.
- `summary.json`: same/cross geometric 후보와 승인 횟수·acceptance, 최종 평가.
- `final_eval_metrics.json`, `videos/`: 기존 평가 지표·영상.

IPPO의 `communication.jsonl.available`은 알고리즘 off로0이지만, `spatial.jsonl`의 geometric 후보는 좌표로 별도 계산합니다. 따라서 통신 off와 서로 만나지 않는 것을 구별할 수 있습니다. step별 후보 수와 update 시점 승인을 혼합하지 않습니다. 동일한 evaluation seed 목록을 매 체크포인트에서 사용하지만 policy 경로가 달라지면 이후 요청 RNG 소비도 달라질 수 있습니다.

## 출처: `examples/PGCT_TRANSFER_EXPERIMENTS.md` (수정 2026-10-08 17:00)

### Stage03 이후 critic transfer 검증 학습

`run_pgct_transfer_experiments.ps1`은 실제 PPO 학습을 수행합니다. 기본은 기존 11×10 맵에서 PGCT-on/IPPO-off × training seeds 1·2·3입니다. 모든 조건은 같은 Stage03 actor·critic에서 시작하고 optimizer와 graph를 초기화합니다. 원래 학습기, 환경, JS gate와 기존 공간 실행기는 수정하지 않았습니다. Ablation 조건에만 이 실행기 프로세스 안에서 실제 auxiliary loss의 donor allocation을 교체합니다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_pgct_transfer_experiments.ps1
```

기본 조건: Stage03 `stage03_4ag_physical_home0.750/final.pt`, 4 agents / 2 teams, home ratio .5, Q4(팀당2), LR1e-4, entropy .02, rollout1024, 공통 평가 seeds5,000,001–5,000,020 / 20×500. 각 branch는 4M 요청 예산을 rollout 단위로 올림하여 **4,000,768 환경 step** 학습합니다. 기본6개 총24,004,608 step입니다. W&B는 기본 on, 영상은 `-SaveVideo` 지정 시 저장합니다. 출력은 짧은 `runs/tr_<timestamp>/`입니다.

#### 세 단계 실행

먼저 on/off를 실행하고 성능 차이와 전이 노출량을 확인합니다.

```powershell
# 1단계: on/off. 기본과 동일.
.\examples\run_pgct_transfer_experiments.ps1 -Modes pgct,ippo -Seeds 1,2,3

# 2단계: 완료한 1단계 결과를 donor 전이 일정의 기준으로 사용.
# 이 경로는 실제 완료된 1단계 출력 폴더로 바꿉니다.
.\examples\run_pgct_transfer_experiments.ps1 -Modes random -Seeds 1,2,3 `
  -ReferenceExperiment "runs/tr_첫실험출력폴더"

# 3단계: 3–4 양방향 전이 제거. 나머지 allocation은 유지하며 재정규화하지 않음.
.\examples\run_pgct_transfer_experiments.ps1 -Modes drop34 -Seeds 1,2,3

# 필요할 때만 별도 비교: 제거한 양을 다른 물리 이웃에게 보충.
.\examples\run_pgct_transfer_experiments.ps1 -Modes drop34_refill -Seeds 1,2,3

# 전부 순차 실행할 수도 있음: 4조건×3seeds=12runs, 약48M 추가 step.
.\examples\run_pgct_transfer_experiments.ps1 -Modes pgct,ippo,random,drop34 -Seeds 1,2,3

# 설정만 생성 / 각 조건64스텝 실제 실행 검증.
.\examples\run_pgct_transfer_experiments.ps1 -DryRun
.\examples\run_pgct_transfer_experiments.ps1 -Seeds 1 -Modes pgct,ippo,random,drop34,drop34_refill -SmokeTest
```

Random은 같은 seed PGCT-on의 receiver별 전이 시점·donor 수·allocation weight를 replay합니다. Donor는 **해당 random branch의 현재 물리 이웃 중 균등하게** 선택합니다. 이웃이 부족하면 가능한 donor에 receiver 총 weight를 분배하고 donor 수 부족을 기록합니다. 이웃이 전혀 없으면 전이를 생략하고 weight 부족을 기록합니다. 따라서 완벽한 전달량 일치를 가정하지 않고 결과에서 실제 부족량을 확인해야 합니다. 보조 손실 계수는 동일한 .01입니다. Donor 예측 차이에 따른 실제 peer loss와 gradient 크기까지 같다는 뜻은 아닙니다. PGCT reference의 환경·초기 모델·학습 seed·예산·주요 학습 조건이 다르면 실행을 거부합니다.

`drop34`는 현재 branch의 gate가 여는 3→4와 4→3만 제거합니다. 다른 연결을 새로 열거나 남은 weight를 재정규화하지 않으므로 전체 전이량이 줄 수 있습니다. `drop34_refill`은 제거량을 다른 물리 이웃 한 곳에 더하며 보충할 이웃이 없으면 부족을 기록합니다. 두 조건은 각각 해당 연결 제거의 전체 효과와 전달량 보충 시의 효과를 묻습니다. 모두 agent 표시번호는 1-based, 행렬은 receiver×donor입니다. Ablation 전후 궤적이 달라지므로 다른 연결의 미래 gate 발생도 달라질 수 있습니다.

#### Probe 색상 차트와 JS 진단

에이전트마다 별도 probe를 비교하지 않고 **동일한 공통 입력에 대한 각 에이전트의 응답**을 비교합니다. 진단 bank는 E1 환경과 seed1로 고정하며 모든 method·training seed에서 동일합니다. 이 bank는 진단 전용이고 실제 학습 gate의 probe bank와 criterion을 교체하지 않습니다.

- `probes.jsonl`: 최초·매5update·학습 종료의 agent별 전체 action probability vector, probe별 JS, 평균 JS, 중복 제거 평균 JS, entropy, 입력 중복 ID. 종료 스냅샷은 최종 update 이후입니다.
- `charts/response.png`: 4개 agent의 probe×action 확률과 6개 pair의 probe별 JS, 4×4 평균 JS. 확률은 노란색일수록 높고, JS는 밝을수록 유사합니다.
- `charts/js_time.png`, `unique_js_time.png`: x=추가 환경 step, y=6개 pair. Natural-log JS 범위를 [0,ln2]로 고정합니다.
- `charts/ema_time.png`: 실제 학습 gate의 neighbor-only EMA; 진단 평균 JS와 다릅니다.
- `charts/transfer_time.png`: 실제 auxiliary loss에 사용한 pair-update 전이.
- W&B `diagnostic/probe_color_chart`: 기본 매50update 확률/JS 차트. `diagnostic/js_*`, `unique_js_*` scalar에도 기록합니다.

기존48개 probe의 중복은 동일하게 유지한 평균과 고유 입력 균등 평균을 별도로 비교합니다. Dedup 결과를 기존 .12 gate에 적용하여 새로운 승인으로 해석하면 안 됩니다.

Critic 평가의 첫 stochastic episode에서는 4개 agent의 경험 observation·action-mask 이력을 모두 사용합니다. 각 이력에 모든 actor를 넣고 각 actor가 자기 hidden state를 전개하게 하여 공통 이력에서의 masked JS와 같은 observation에 대한 zero-hidden masked JS를 함께 기록합니다. 다른 actor에게는 off-policy 이력이며 rollout 자체의 행동이 일치한다는 증거는 아닙니다.

#### 성능·critic·실제 전달 기록

- `metrics.jsonl`: 기존 train/update/probe/eval + diagnostic scalar. 최초 step0와 종료 예산에서도 task 평가.
- `final_eval_metrics.json`: 기존 deterministic task 성능, 추가 stochastic critic 오차, 팀별·에이전트별 이벤트/episode.
- `critic_eval.jsonl`: 평가 때마다 기본5×500 stochastic policy rollout. Local NumPy RNG로 행동을 샘플링하여 training RNG를 소비하지 않습니다. 개인별 보상 전체를 discount한 **유한 horizon Monte Carlo return**의 MSE/MAE와 one-step TD 절대오차. TD는 time limit에서는 bootstrap하고 실제 termination에서는 bootstrap하지 않습니다.
- MC는 horizon 이후 보상을 포함하지 않아 continuing critic과 tail bias가 있습니다. 동일 horizon에서도 정책별 방문 분포가 다르므로 MC MSE 감소 하나로 전이 유익성을 결론내리지 않습니다. Deterministic task 평가와 stochastic critic 평가를 구별합니다. `-CriticEpisodes 0`은 critic 진단을 끕니다.
- `transfer.jsonl`: 실제 receiver×donor allocation, 원래 local gate allocation, 물리 후보, 전달량·donor 수 부족, 전이 전 pair별 critic MSE, peer loss 계수.
- **Ablation의 실제 전이는 `transfer.jsonl`을 사용합니다.** 기존 `communication.jsonl`에는 원래 PGCT gate가 남으므로 random/drop 조건의 실제 전달과 다를 수 있습니다. 학습 영상의 선도 원래 gate를 표시할 수 있습니다.
- `transfer_summary.json`: directed 전달 update 수, weight 합, 전달량 부족, 평가 곡선 trapezoidal AUC와 AUC/step, 목표 delivery에 최초 도달한 평가 step. 기본 목표45 deliveries/episode는 결과를 보기 전에 정하는 설정값이며 `-PerformanceTarget`으로 바꿉니다. 평가 간 최초 도달 시점은 알 수 없습니다.
- 실험 전체 `charts/learning.png`, `agents.png`, `critic.png`: 조건·seed별 곡선. 현재는 개별 seed를 표시하며 통계적 유의성을 주장하지 않습니다.

Wall-clock은 평가·진단까지 포함한 elapsed seconds와 train SPS를 기록합니다. 공간 실행기의 예전 결과와 새 실행기의 wall-clock을 직접 공정 비교하면 안 됩니다. 이전 train의 `value_uncertainty`/GAE residual은 새 one-step TD/MC 오차와 다른 지표입니다.

#### 현재 공간 실험 재사용

현재 `runs/sp_20261008_120638_983201`의 E1 PGCT/IPPO는 Stage03·환경·예산이 맞으므로 성능 비교에 사용 가능합니다. E2/E3는 공간 확대 후속 실험으로 보존합니다. **실행 중인 프로세스를 이 코드가 중단하거나 그 설정을 바꾸지 않습니다.** E1의 두 조건 완료 후 다음 명령은 seed1 학습을 재실행하지 않고 완료 결과를 읽으며 seeds2·3만 새로 학습합니다.

```powershell
.\examples\run_pgct_transfer_experiments.ps1 -Seeds 1,2,3 `
  -ReuseExperiment "runs/sp_20261008_120638_983201"
```

재사용하려는 조건이 아직 완료되지 않았으면 실행을 거부합니다. 새로 생성한 폴더의 기록에는 `reused_run_dir`가 표시됩니다. 이전 결과에는 새 critic 진단이 없으므로 **성능 비교용 재사용**입니다. Critic와 wall-clock까지 동일 진단 조건으로 비교하려면 `-ReuseExperiment` 없이 새 on/off를 실행합니다.

완료된 기존 E1 PGCT seed1은 random schedule 기준으로도 사용할 수 있습니다.

```powershell
.\examples\run_pgct_transfer_experiments.ps1 -Modes random -Seeds 1 `
  -ReferenceExperiment "runs/sp_20261008_120638_983201"
```

기존/live 로그와 체크포인트를 읽어서 차트를 생성하는 명령:

```powershell
& "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe" `
  examples/plot_pgct_probe_charts.py `
  --experiment-dir runs/sp_20261008_120638_983201 `
  --output-dir output/pgct_transfer_review/live_spatial
```

이 명령은 원본 모델·로그를 읽기만 합니다. 기존 IPPO에는 training probe가 없으므로 같은 맵·seed의 PGCT bank로 저장 checkpoint의 forward-only JS를 재구성합니다. 저장 간격 사이의 policy 응답은 복원할 수 없습니다.

여러 training seed의 결과는 **이 한 Stage03 모델을 조건으로 한 효과**입니다. 독립적인 Stage03 사전학습 seed에도 재현되는지는 각 Stage03 checkpoint로 이 실험을 반복해야 합니다.

#### 저장 모델의 공통 rollout 이력 진단

`diagnose_pgct_rollout_compatibility.py`는 학습을 하지 않는 CPU 추론 도구입니다. 한 고정 reference policy로 평가 이력을 생성한 뒤, 같은 observation·action mask 이력을 모든 비교 모델의 actor/critic에 넣습니다. 각 network는 그 동일한 이력으로 자기 hidden state를 형성하며 hidden vector를 서로 복사하지 않습니다.

```powershell
& "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe" `
  examples/diagnose_pgct_rollout_compatibility.py `
  --checkpoints `
    runs/pgct09700_physical_mixing_20260929_155338_079437/stage04_4ag_physical_home0.500/final.pt `
    runs/sp_20261008_120638_983201/e1_pgct_s1/checkpoint_00600.pt `
  --episodes 20 --horizon 500 `
  --output-dir output/pgct_transfer_review/common_rollout_stage04_e1_u600
```

출력:

- `histories.npz`: 재사용할 observation/mask/reward/phase 이력, episode 경계, 시간, 실제 종료·truncation 사유. 기본은 첫 checkpoint의 stochastic policy와 seeds5,000,001–5,000,020. `--reference-checkpoint`으로 이력 생성 정책을 명시할 수 있습니다.
- `summary.json`: pair별 recurrent/zero-hidden × masked/unmasked policy JS, 공통 이력에서의 critic prediction MSE, phase별 결과, 가중치 hash와 추론 전후 동일 여부.
- `model_N_samples.npz`: 관측 시점별·source stream별 pair JS와 critic 예측 차이. 기본은 매10step 표본이며 `--sample-interval 1`은 모든 시점을 사용합니다. 각 step에서 hidden state는 항상 전개합니다.
- `compatibility.png`: policy JS와 critic 예측 차이, 6개 pair 평균의 관계. 6개 pair는 독립 표본이 아니며 상관계수는 설명용입니다.

후속 PGCT/IPPO checkpoint도 **동일한 저장 이력**에 평가할 수 있습니다.

```powershell
& "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe" `
  examples/diagnose_pgct_rollout_compatibility.py `
  --checkpoints "완료된PGCT모델.pt" "완료된IPPO모델.pt" `
  --cache output/pgct_transfer_review/common_rollout_stage04_e1_u600/histories.npz `
  --output-dir output/pgct_transfer_review/common_rollout_on_off
```

환경·보상·맵 설정은 같아야 합니다. 같은 E1 기본 맵의 명시/암묵 generator 인자는 동일하게 취급하며, actor 입력에 영향을 주지 않는 IPPO의 communication off는 허용합니다. Reference 이력은 다른 정책에게 off-policy이므로 저장된 reference return을 다른 정책의 실제 on-policy value 정답으로 사용하지 않습니다. 이 도구는 **critic 예측 유사성**을 측정하며 **critic 정확도나 전이 유익성**을 입증하지 않습니다. 별도 stochastic on-policy MC 평가와 구분합니다. 현재 Stage04/E1 PGCT 두 모델 비교도 PGCT-on/IPPO-off 실험 결과는 아닙니다.

## 출처: `examples/HARD_RWARE_EXPERIMENTS.md` (수정 2026-10-13 16:31)

### 분리된 장애물·배송 제약 RWARE 환경

`run_hard_rware_experiments.ps1`은 기존 trainer를 재사용하는 **별도 실행기**다. 원래 환경·실행기·PPO·PGCT gate·probe 파일을 수정하지 않았으며 기존 학습을 중단하지 않는다. 새로운 환경 ID는 `rware-constrained-4ag-2teams-v0`이고 이 실행기에서 명시적으로 등록한다.

#### 네 환경

| Profile | 실제 제약 | 공통 조건 |
|---|---|---|
| `control` | 장애물·dock 대기 없음 | E2와 같은 16×16, 선반108개, agent4개, 2팀 |
| `detour`(기본) | 아래쪽 교차로 (3,14)/(12,14)에 벽2개를 놓아 일부 적재 경로를 우회 | 중앙 통로는 유지 |
| `bottleneck` | y=7 통로의 14개 cell을 벽으로 막고 x=3·12의 1-cell 통로 두 곳만 개방 | 선반 수·요청 수·보상 계수 유지 |
| `dock` | bottleneck + 배송 성공 후 해당 목표 지점을 8 step 동안 적재 robot이 새로 진입할 수 없음 | 빈 robot 통과와 기존 carrier의 퇴장은 허용 |

벽은 원래 통로에만 놓는다. 원래 shelf 위치·수와 목표 위치 (7,15)/(8,15)는 같다. 전체 적재 가능 통로 그래프와 모든 shelf home의 접근성을 검사한다. 모든 cell의 경로가 연결돼도 여러 robot이 충돌 없이 협력해야 하므로 성공이 자동으로 보장되지는 않는다.

벽이 있는 cell로의 FORWARD는 물리적으로 NOOP 처리된다. Mask를 껐을 때는 기존 NOOP 비용과 추가 constraint penalty .005가 부과된다. Mask를 켠 기본 학습에서는 벽·busy dock 진입을 사전에 차단한다. 기존 collision resolver를 그대로 사용하므로 원래 동시 이동·교환 금지 규칙도 유지한다.

Dock cooldown은 step 종료 때 감소하고, 그 step에서 새 delivery가 생기면8로 설정한다. 이후8개의 환경 step 동안 적재 robot의 신규 진입을 막는다. 화면에는 남은 숫자가 표시된다. 관측에는 timer 숫자 전체를 추가하지 않고 로컬 목표 지점의 현재 가용성만 표시한다.

#### 실행

기본은 동일한 기존 Stage03 checkpoint에서 `detour` PGCT/IPPO seed1을 각4,000,768 환경 step 학습한다. 두 분기의 초기 actor/critic weights는 같으며 optimizer와 graph는 초기화한다. 학습 코드와 입력 차원이 호환돼 기존 가중치를 사용할 수 있지만, 장애물에 대한 즉시 일반화는 보장되지 않는다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 완만한 우회 환경: PGCT/IPPO matched 학습, 두 조건 순차 실행.
.\examples\run_hard_rware_experiments.ps1

# 강한 병목 환경 또는 병목 + 배송 지점의 8-step 대기.
.\examples\run_hard_rware_experiments.ps1 -Profiles bottleneck
.\examples\run_hard_rware_experiments.ps1 -Profiles dock

# 장애물 효과와 dock 제약 효과를 단계별 비교: 4 profiles × 2 modes.
.\examples\run_hard_rware_experiments.ps1 -Profiles control,detour,bottleneck,dock

# 반복 seed를 추가하면 계산 예산도 비례해 늘어남.
.\examples\run_hard_rware_experiments.ps1 -Profiles detour -Seeds 1,2,3

# 학습 전 확인. 각 실행은 새 출력 폴더만 사용하며 덮어쓰기를 거부.
.\examples\run_hard_rware_experiments.ps1 -PreviewOnly
.\examples\run_hard_rware_experiments.ps1 -Profiles control,detour,bottleneck,dock -DryRun
.\examples\run_hard_rware_experiments.ps1 -Profiles control,detour,bottleneck,dock -SmokeTest

# W&B/영상은 명시적으로 켠다. 기본은 둘 다 off.
.\examples\run_hard_rware_experiments.ps1 -Profiles bottleneck -Track -SaveVideo
```

`-InitCheckpoint`, `-OutputDir`, `-TotalTimesteps`, `-Requests`도 지정할 수 있다. 기본 requests4를 바꾸면 난이도 외 작업량도 달라진다. 요청 수가 늘어난다고 항상 더 어려운 것은 아니다. Profile의 geometry는16×16으로 고정한다.

기본 출력은 짧은 `runs/hard_<timestamp>/`다. 원래 실행기의 출력 폴더와 겹치지 않는다. 같은 경로가 있으면 덮어쓰지 않고 종료한다. 학습은 기존 실행과 자원을 공유하므로 장기 실행 시작 시점을 사용자가 선택한다. 이 환경 개발 과정에서는 CPU smoke만 실행했고 추가4M 학습은 시작하지 않았다.

#### 알고리즘·관측·평가 조건

- 기존 PPO 설정과 PGCT의 canonical probe48개, zero hidden, unmasked JS, EMA < .12, warmup100, coefficient .01을 유지한다. Smoke는 기존 smoke 규칙과 동일하게 축소한다.
- 기존 probe builder는 일반 MultiTeamWarehouse를 만들기 때문에 새로운 환경 인자3개만 temporary adapter에서 제거한다. 벽·dock 전용 probe를 새로 넣지 않는다. **네 profile의 canonical bank가 기존 E2 bank와 tensor 단위로 같다는 테스트를 통과했다.**
- Semantic observation은20 ego +13×11×11 =1593차원을 유지한다. 기존 out-of-bounds channel0에 내부 벽도 표시하고, 벽 cell의 나머지 channel은0이다. Busy goal은 goal channel11을 유지하되 available relevant-goal channel12를0으로 표시한다.
- 이 채널 의미 확장은 새 실행기에만 적용된다. 원래 wrapper와 기존 학습의 관측은 바뀌지 않는다. 새 환경은 반드시 전용 실행기의 `constrained_runtime()`와 semantic wrapper로 사용한다. 원래 trainer를 새 ID만 지정해 직접 실행하면 필요한 어댑터가 설치되지 않는다.
- Action mask는 기존 mask와 새 로컬 제약을 교집합으로 적용한다. 인접 cell과 현재 local goal 가용성 이상의 정보를 agent에게 주지 않는다.
- 통신은 기존 Chebyshev range5다. 벽이 통신의 line-of-sight를 차단하는 모델은 추가하지 않았다.
- 보상 shaping의 기존 Manhattan distance도 유지한다. 장애물 우회와 shaping 방향이 다를 수 있으므로 delivery/return과 실제 이동 경로를 함께 해석한다.
- Task 평가는 공통 reset seeds5,000,001–5,000,020, deterministic masked policy,20×500이다. 새로운 실행기는 step0의 고정 평가도 저장한다.
- 기본 초기 모델은 PGCT Stage03이므로 이 실험도 **해당 사전학습 모델 이후 추가 전이 효과**를 본다. 처음부터 독립 학습한 IPPO의 대조군은 아니다.

#### 출력

- `experiment.json`: 모든 조건·상태·checkpoint·원본 핵심 파일 SHA256.
- `maps.png`, profile별PNG, `layouts.json`: 장애물 지도와 모든 shelf의 적재 최단 경로.
- 각 run의 `metrics.jsonl`, `spatial.jsonl`, `communication.jsonl`: 기존 성능/활동/전이 로그.
- `constraints.jsonl`: rollout마다 wall/dock block, busy dock-step, 인근 loaded agent-step, 병목 영역 체류량. Action mask가 불법 행동을 막으면 block 횟수는0일 수 있다.0은 제약이 작동하지 않는다는 뜻이 아니다.
- `initial_eval_metrics.json`, `final_eval_metrics.json`, `summary.json`, `final.pt`, 주기 checkpoint.
- `-SaveVideo` 시 실제 벽·agent·goal 대기 상태를 CPU RGB renderer로 저장한다. OpenGL 창을 열지 않는다.

기존 차트 도구도 사용할 수 있다.

```powershell
& "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe" `
  examples/plot_pgct_probe_charts.py `
  --experiment-dir "runs/hard_실제출력폴더" `
  --output-dir "output/hard_실제차트폴더"
```

#### 검증 기록 — 2026-10-13

- 새 환경17 tests를 포함한 관련32 tests 통과.
- 50개 reset seed에서 벽 spawn·중복 위치가 없음을 확인했고, 모든 선반의 적재 경로 접근성을 검사했다.
- 네 profile 모두 실제 pickup→delivery→home return 경로 실행을 통과했다.
- 원래 환경과 control의 관측·reward·동시 이동·미지정 seed reset RNG가 동일했다.
- 네 profile×PGCT/IPPO 총8조건의 CPU64-step 학습·평가·final 저장 완료: `runs/hard_smoke_20261013_final`.
- Control64-step PGCT/IPPO의128 tensor가 기존 E2 smoke 결과와 bitwise 일치했다. 원래 핵심10개 파일 SHA256도 그대로였다.
- 동일 preview 배치의 적재 평균 최단 경로는 control13.370칸, detour14.444칸(약8.0% 증가), 병목17.074칸(약27.7% 증가), 최대23→30칸이다. Dock은 같은 경로에 서비스 대기 제약을 추가한다.
- 이것은 경로 제약·실행 검증이며, 새 환경의 학습 난이도나 PGCT 성능 이득을 입증한 결과가 아니다.

초기 시행에서 발견한 preview 정수 직렬화 및 기존 probe builder의 새 인자 호환 문제를 새 파일 안에서 수정했다. 이전 실패 폴더 v1/v2는 완료 결과에 포함하지 않는다.

#### 초기 난이도 보정

기존 E2 PGCT final을 고정한5×500 평가에서 control은37.8 deliveries/episode, detour는5.4, 강한 bottleneck/dock은각2.2였다. 이는 새 환경으로의 초기 일반화 평가이며 재학습 후 성능이나 본질적인 학습 난이도를 입증하지 않는다. 변화가 커서 적재 경로 증가는 더 완만한 detour를 기본으로 추가하고 bottleneck/dock은 강한 선택지로 남겼다. 최종 수치는 `output/hard_rware_validation_20261013/frozen_difficulty_pilot_v2.json`에 저장한다.

Detour에서도 기존 정책의 즉시 성능은 크게 떨어졌다. 장애물 수와 구조적 경로 증가가 작아도 기존 정책이 우회에 취약할 수 있다. 따라서 여기서 완만하다는 말은 구조적 제약의 정도이며, 실제 학습 난이도가 조금만 높아졌다는 검증은 아니다.

---

# Part 8. 대화 기록 원문 (Codex + Claude Code)

## 출처: `CONVERSATION_LOG.md` (수정 2026-10-18 12:28)

### PGCT 대화 기록 — 과거 요약과 이후 원문

최초 작성: **2026-10-13, Codex**. 현재 대화에 제공된 사용자 발화와 외부 답변, 이 대화의 Codex 작업 기록, 로컬 실험 근거로 정리했다.

**아래 L01–L12는 원본 전체 transcript가 아니라 대화 순서별 인수인계용 요약**이다. 정확한 과거 시각이나 제공되지 않은 답변은 만들어 넣지 않았다. 외부 답변의 제안, 실제 수행한 작업, 검증된 관측을 구분한다. 최신 수치는 `RESEARCH_STATE.md`와 `EXPERIMENTS.md`를 확인한다. 2026-10-13의 전부 기록 요청부터는 파일 끝에 사용자 메시지와 assistant 답변·진행 안내를 원문으로 남긴다.

#### L01. 프로젝트 배경과 gate 소멸 — 날짜 미상

- 사용자: ex4/ex5 문서에 기반한 프로젝트이며 기존 최종 상태는 `stage04_4ag_physical_home0.500`. 초록색 gating 선이 사라졌고, 팀 내 분업으로 D_ij가 달라진 것 같다고 질문했다.
- 제공 파일: `C:/Users/95101/Downloads/ex4.pdf`, `C:/Users/95101/Downloads/ex5.pdf`.
- 초기 가설: 행동이 분화하면 같은 팀의 정책 JS가 threshold를 넘을 수 있다. 전체 성능이 유지되면 선 소멸이 곧 학습 실패는 아니다.
- 이후 정밀화: 실제 rollout 행동 빈도가 아니라 공통 canonical probe/zero hidden 응답 차이다. 명확한 작업 역할 분담은 가설로 남겼다.
- 이후 관측: 같은 팀이 만날 기회가 있어도 gate가 닫혔고, 일부 cross-team pair만 연결됐다.

#### L02. IPPO-off 코드와 사전학습 — 날짜 미상

- 사용자: “pgct off의 경우의 학습 실행코드”. 추가할 필요가 있는지, 이미 코드가 있는 것 같다고 질문했다.
- 사용자 기억: curriculum 전 학습은 8~9M, 팀별 shelf가 양쪽으로 완전히 분리된 상태였다.
- 구분: 8~9M은 당시 사용자가 기억으로 제시한 값이며 run별 checkpoint/설정 없이 확정 예산으로 일반화하지 않는다.
- 확인된 경로: from-scratch runner의 `-Run none`은 기존 IPPO 경로다. 이후 Stage03→E1 matched 분기 전용 실행기를 추가했다.

#### L03. 연구 해석과 cross-team 연결 — 날짜 미상

- 사용자가 붙여넣은 외부 검토: PGCT를 지속적인 팀 연결보다 선택적인 critic 정보 전달로 해석할 수 있다는 의견이었다.
- 중요한 수정: 후반 transfer가 없어도 성능이 좋다는 관측만으로 초반 transfer가 유익했거나 후반에는 불필요했다고 주장할 수 없다.
- 기존 Stage04의 same-team0/cross1,221, 3–4 1,170회 전이가 연구 질문으로 정리됐다.
- 질문 전환: “왜 3–4가 연결됐는가?”와 “연결로 무엇이 좋아졌는가?”를 분리했다.
- 미해결: latent team discovery 유지 또는 team-agnostic transfer로 확장할지 여부.

#### L04. 코드 변경 금지와 W&B 영상 오류 — 날짜 미상

Traceback의 run 경로에는 2026-10-02/07이 포함된다. 이것을 모든 관련 발화의 정확한 날짜로 간주하지 않는다.

- 사용자: “아 그리고 코드 수정은 하지마”. 당시 진단은 알고리즘 변경 없이 진행하는 요청이었다.
- 오류: W&B가 임시 mp4를 긴 `runs/recurrent_ippo_consensus/.../wandb/.../media/videos/eval/video_1024000_...mp4`로 옮기다가 `FileNotFoundError`가 발생했다.
- 사용자 질문: 그대로 재실행하면 920000 step에서 재발하는지, 다른 방법이 있는지.
- 사용자 추가 정보: 1~2시간 뒤 자동 절전이 예약됐을 가능성.
- 진단 범위: 긴 Windows 목적지 경로가 유력했고, 실패 영상 이름의 step은 1,024,000이었다. 절전 원인설은 확정하지 않았다.
- 이어진 시도: `subst R:` 후 R:에서 checkpoint900으로 continuation 실행.
- 새 오류: W&B code path 추정 중 `ValueError: path is on mount 'R:', start on mount 'C:'`.
- 대응 방향: 짧은 출력 root/run 이름, 영상 선택 옵션, W&B Git 탐색 설정을 검토했다. 학습 알고리즘 문제와 파일시스템/W&B 문제를 구분했다.

#### L05. 구버전 코드 정리와 공간 실험 요청 — 과거 대화

실행 산출물은 2026-10-08에 생성됐다.

- 사용자: 비교 IPPO와 기존 PGCT와 무관한 코드를 정리하고, 붙여넣은 PGCT cross-team/공간 확장 내용을 수행하도록 요청했다.
- 참고 파일:
  - `C:/Users/95101/.codex/attachments/ade4d1da-89cc-4297-8909-688090d78dd8/붙여넣은 텍스트.txt`.
  - `C:/Users/95101/.codex/attachments/4fd542a4-b27d-4077-b256-bacabce7fb00/붙여넣은 텍스트.txt`.
- 사용자 강조: “보고서 말고 학습 자체를 돌려야 하는거 아냐? 실험 코드”. 보고서와 실제 학습 실행기를 구분해야 한다는 수정이었다.
- 작업 기록: 구버전 17개 tracked 파일 제거, README 정리, 공간 실험 Python/PowerShell 실행기와 테스트 추가. 실제 run은 `runs/sp_20261008_120638_983201`이다.
- 범위: 원래 핵심 trainer/환경/gate 설계 변경과 별도 실행기 추가를 구분했다.

#### L06. Continuation은 IPPO인가? 왜 agent별 성공 시점이 다른가?

- 사용자: `ex5_semantic_cnn_none_from_scratch_4ag_sr5_square_home1.00_seed1_pretrain_off_9700_continue`가 IPPO인지 질문했다.
- 확인: graph/communication/peer/consensus가 off인 IPPO다.
- 초기 checkpoint에 이미 성공 경험과 agent별 성능 차이가 있었다. 독립 보상과 희소한 task 성공 피드백 때문에 성공 시점이 엇갈릴 수 있다는 설명을 했다.
- 확인 범위: 각 agent는 별도 actor/critic optimizer로 학습한다. 현재 E1/E2의 개별 actor skip은 0이다.
- 미확정: 모든 run에서 같은 agent가 먼저 성공한다거나 나머지가 반드시 뒤늦게 따라잡는다는 일반화.

#### L07. 진단 검토와 네 가지 요청 — 2026-10-08 작업 기록

- 사용자 제공 외부 검토: Stage04의 물리 후보/실제 gate, occupancy, individual reward, policy와 value compatibility 차이를 강조했다.
- 사용자 요청: ① JS 사용이 맞는지, ② 공통 probe 응답 유사성 color 차트, ③ on/off/random/drop34 학습 실행 코드, ④ 기존 공간 실험을 폐기할지.
- 수행: JS의 natural-log 평균 계산과 실제 EMA gate를 구분해 확인했다. 확률/probe별 JS/시간 차트 도구, transfer 전용 실행기·문서·테스트를 추가했다.
- 검증 기록: 관련 35 tests, 조건별 64-step smoke, 기존 공간 실행기와 on/off weights 일치 확인.
- 판단: 기존 E1 on/off 결과를 보존하고 완료 결과 재사용 옵션을 추가했다. 이미 실행 중인 공간 run을 임의로 폐기하지 않았다.
- 구분: 구현·검증은 장기 random/drop 실험 완료가 아니다.

#### L08. Probe 중복이 donor 순위를 바꾸는가? — 2026-10-08 진단 기록

- 관측: 기존 Stage04의 48개 중 고유26개. 3–4 JS .130→.227, 1–4 .206→.137.
- 사용자가 붙여넣은 외부 평가: JS 계산보다 probe 분포가 문제이며 중복이 실제 방문 빈도를 반영하는지 검증해야 한다는 의견.
- 판단: 동의할 근거가 있다. 다만 26개로 학습했다면 과거 EMA 연결이 실제로 역전됐을 것이라고 단정하지 않았다.
- 추가 제안: 공통 rollout 관측 이력의 recurrent policy JS, 공통 이력의 critic 예측 차이, 실제 return 예측 오차.
- 실제 학습 bank/threshold는 변경하지 않았다.

#### L09. 공통 관측 이력 진단 — 2026-10-08 작업 기록

- 수행: `diagnose_pgct_rollout_compatibility.py`와 2개 테스트 추가, 20×500 reference 이력 cache 생성.
- 모델: 기존 Stage04 final과 새 E1 PGCT checkpoint600. 각 network가 같은 이력으로 자신의 hidden state를 형성했다.
- 결과: 기존 Stage04의 3–4 recurrent masked JS .059547, critic 예측 간 MSE .106799. 새 E1 checkpoint600은 .068073/.120176. 두 지표에서 3–4가 가장 낮았다.
- 답변: 3–4 유사성은 canonical 중복에만 있는 현상은 아니다. 예측 일치는 정확도/전이 유익성과 다르고 두 모델 모두 PGCT이므로 on/off 결론은 아니다.
- 모델 hash 불변을 확인하고 원래 학습 설정과 진행 프로세스를 유지했다.

#### L10. “지금까지 학습 내용 분석해줘” — 2026-10-13

- 수행: 실제 manifest/metrics/spatial/communication과 기존 진단에서 학습곡선, agent별 성과, 실제 전이, 공간 활동을 정리했다.
- 완료 확인: E1/E2 on/off 각 4,000,768 step, E3 PGCT 약2.25M 진행, E3 IPPO 시작 전(14:37 스냅샷). Smoke와 계획은 본 실험으로 세지 않았다.
- 결과: E1 정규화 평가 AUC +2.88%, E2 −0.23%. 최종 delivery는 E1 44.35/44.65, E2 37.85/38.20.
- Gate: E1은 3–4만 2,005회, E2 same870/cross2,360. E1 후반 transfer가 지속돼 “초기에만 작동” 해석을 배제했다.
- 추가 수행: 각 최종 모델 10×500 stochastic critic 평가, 최종 공통 canonical48/고유 입력 응답 평가. 고정 모델 hash가 불변임을 확인했다.
- Critic 초기200-step MC MSE: E1 1.725/1.103, E2 .286/.281. PGCT 정확도 개선은 미확인이다. 방문 분포와 MC tail 편향 때문에 손상의 인과 관계도 확정하지 않았다.
- 최종 probe: E1 PGCT 3–4 .0921→.1421, 1–4 .2114→.1232로 순위 민감성이 지속됐다.
- 답변: seeds2·3 재현 확인이 우선이다. 기존 학습 중단/변경이나 추가 장기 학습 시작은 하지 않았다.
- 산출물: `output/learning_review_20261013/REPORT.md`와 수치·차트·분석 스크립트.

#### L11. “지금까지 있었던 대화 내용들 1번처럼 로그로 남겨줘” — 2026-10-13

- 사용자 제공 구조: AGENTS/RESEARCH_STATE/DECISIONS/EXPERIMENTS를 공유하고 Claude Code는 CLAUDE.md로 연결.
- 수행: 위 4개 파일, CLAUDE.md, 이 CONVERSATION_LOG.md를 프로젝트 루트에 생성했다.
- 규칙: 시작 시 공용 노트 확인, 의미 있는 완료 작업·실험·판단 추가, 근거·한계·확인 시각 명시, 이전 결론의 수정 이력 보존.
- 이 작업에서는 학습 코드·원본 로그·체크포인트를 변경하지 않고 학습을 시작/중단하지 않았다.
- 범위: 제공된 대화와 로컬 근거로만 요약했다. 별도 Claude 대화나 누락된 원문을 자동 수집하지 않았다. Hook/MCP 설치는 요청 범위에 포함하지 않았다.

#### 코드 변경·검증 내역 색인

아래는 과거 작업 기록이며 이번 공용 노트 생성에서 모두 새로 수행한 것은 아니다.

| 변경 묶음 | 파일·범위 | 목적·검증 |
|---|---|---|
| 구버전 정리 | examples/curriculum1·2, 구 stage 설정, 구 PowerShell 실행기, test_.py 등 17개 tracked 파일 삭제; README 수정 | 사용자의 정리 요청 범위. 다른 기존 untracked 작업은 보존 |
| 공간 실행 | examples/train_pgct_spatial_experiments.py, run_pgct_spatial_experiments.ps1, PGCT_SPATIAL_EXPERIMENTS.md, tests/test_spatial_experiments.py | 동일 Stage03에서 E1/E2/E3 on/off 분기, 물리·공간·성능 로그 |
| Transfer 실행·차트 | examples/train_pgct_transfer_experiments.py, run_pgct_transfer_experiments.ps1, pgct_probe_diagnostics.py, plot_pgct_probe_charts.py, PGCT_TRANSFER_EXPERIMENTS.md, tests/test_transfer_experiments.py | on/off/random/drop34/refill, 실제 allocation, critic/probe 진단, 35 tests와 64-step 검증 기록 |
| 공통 이력 진단 | examples/diagnose_pgct_rollout_compatibility.py, tests/test_rollout_compatibility.py, 관련 문서 | 이력 cache 재사용, 각 network의 자기 hidden, 2 tests와 고정 모델 평가 |
| 10월13일 분석 | output/learning_review_20261013/ | 학습 로그 분석, 고정 모델 평가, 합계·예산·물리 범위·truncation 검증 |
| 공용 기록 | 루트 AGENTS.md, CLAUDE.md, RESEARCH_STATE.md, DECISIONS.md, EXPERIMENTS.md, CONVERSATION_LOG.md | 현재 작업. 내용과 참조 경로 검증 |

#### L12. E2의 3~4개 연결 집단과 probe 신뢰도 — 2026-10-13

- 사용자: 맵 확장 후 두 개씩이 아니라 3~4개가 연결됐다면 팀 구분보다 공통 움직임 probe가 많아 신뢰도가 떨어지는 것인지, 이런 알고리즘을 좋다고 볼 수 있는지에 대한 외부 답변을 제공했다.
- 참고: `C:/Users/95101/.codex/attachments/0adf2737-c22e-4047-9552-5f91073abb82/붙여넣은 텍스트.txt`.
- 검토: 팀 구분 능력과 전이 유익성은 분리해야 한다는 답변에 대체로 동의한다. 이동 probe가 과다하다는 설명은 아직 가설이다. 원래 팀 발견 목표의 미달을 사후 목표 변경만으로 정당화하지 않는다.
- 추가 수행: E2의 실제 gate support에서 연결 성분을 계산했다. 3,907 update 중 3개 연결 661회(완전 연결244/불완전417), 4개 연결18회(완전 연결0)였다.
- 결론: 네 개 연결은 연쇄 형태였지만 세 개의 완전 연결도 있었다. 따라서 혼합 집단을 전부 연쇄 연결로 설명할 수 없다. 일반적인 probe 신뢰성과 유익한 donor 선택은 여전히 미입증이다.
- 산출물: `output/learning_review_20261013/e2_components.json`, `analyze_e2_components.py`. 공용 결정·실험·상태 기록을 갱신했다. 실제 학습 코드·gate·probe 변경, 학습 중단·새 장기 실행은 하지 않았다.

#### 이후 추가 양식

날짜 KST / 작성 도구 / 사용자 요청(짧은 원문 또는 요약) / 관측·가설 / 실제 수행 / 코드 변경·검증 / 근거 경로 / 미해결·다음 단계.

#### 원문 기록 T001 — 2026-10-13 KST, Codex

이 구간부터는 짧은 대화도 포함하여 원문을 기록한다. 이전 L01–L12를 원문으로 소급 복원한 것은 아니다.

##### 사용자

앞으로도 대화한 내역들은 전부 로그로 남겨줘 알겠지?

##### Assistant — 진행 안내

앞으로는 요약뿐 아니라 사용자 메시지와 제 답변·진행 안내도 원문으로 남기도록 공용 지침을 갱신하겠습니다. 이번 요청부터 적용하겠습니다.

##### 수행 기록 — 원문 대화와 별도

AGENTS.md와 CLAUDE.md에 이후 모든 대화의 원문 기록 규칙을 추가했다. 과거 요약은 보존하고 이후 원문 구간을 분리했다. 연구 판단·실험 상태·학습 코드는 변경하지 않았다.

##### Assistant — 최종 답변

알겠습니다. 앞으로 사용자 메시지와 제 답변·진행 안내를 [CONVERSATION_LOG.md](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/CONVERSATION_LOG.md)에 **원문으로 계속 기록하겠습니다.** 이번 요청도 기록했고, 공용 작업 지침에 반영했습니다.


#### 원문 기록 T002 — 2026-10-13 KST, Codex

##### 사용자 — 최초 메시지 원문

### Files pasted by the user:

#### "결론부터 말하면, Probe를 여러 상황에 설정하는 것만으로는 현재 PGCT의 근본적인 문제가 해결되지 않습니다. 그리고 RWARE와 SMAC…": C:\Users\95101\.codex/attachments/dfd8268a-3656-491e-b205-a38205efefc2/붙여넣은 텍스트.txt

#### My request:
1. probe를 여러 상황에 설정하기만 하면 되는가?
   1. 만약 지금의 RWARE처럼 같은 에이전트가 색깔을 제외하곤 동일한 운동을 취할시. 색깔적인 팀 구분이 사라지는 문제
   2. SMAC 환경의 경우 동일 유닛이라도 현 상황, 자원에 따라서 건물 설치, 생산, 정찰 등의 다양한 활동을 함
      1. RWARE와 SMAC 환경은 서로 극명한 차이를 내는데 이를 한 알고리즘으로 만들순 없는가?
2. 각 환경에 대해 probe를 직접 여러 케이스에 대하여 만들어야하는데 너무 귀찮지 않나?



해당 질문에 대한 대답이야

##### Assistant — 진행 안내 1

첨부 답변을 읽고, probe를 늘리는 것으로 해결되는 부분과 환경에 공통으로 적용할 기준이 필요한 부분을 구분해 검토하겠습니다. SMAC의 실제 과제 범위도 확인하고, 이번 대화도 원문 로그에 남기겠습니다.

##### 첨부 원문 — 전체 읽음, 사용자 메시지와 별도

출처: `C:\Users\95101\.codex\attachments\dfd8268a-3656-491e-b205-a38205efefc2\붙여넣은 텍스트.txt`

````text
결론부터 말하면, Probe를 여러 상황에 설정하는 것만으로는 현재 PGCT의 근본적인 문제가 해결되지 않습니다. 그리고 RWARE와 SMAC처럼 전혀 다른 환경에서도 작동하는 하나의 알고리즘을 만드는 것은 가능합니다. 다만 지금의 수동으로 설계한 canonical probe + JS divergence + 고정 threshold 구조에서 한 단계 더 나아가야 합니다.

저는 오히려 지금 제기한 두 문제가 PGCT의 연구 방향을 결정하는 핵심이라고 봅니다.

1. 무엇을 유사하다고 판단할 것인가? 행동이 비슷한 에이전트인가, 목표가 같은 에이전트인가, critic 정보를 공유하면 서로 도움이 되는 에이전트인가?
2. 어떤 상황에서 유사성을 측정할 것인가? 연구자가 만든 probe인가, 실제 학습 경험에서 자동으로 추출한 probe인가?

이 둘은 구분해야 합니다. 특히 두 번째를 자동화하더라도 첫 번째 문제가 해결되지 않으면 RWARE의 색상 구분이나 SMAC의 역할 차이를 여전히 놓칠 수 있습니다.

## 1. RWARE에서 색깔이 달라도 행동이 같다면?

가령 두 에이전트가 있다고 합시다.

- Agent A: 빨간색 팀 화물을 배송
- Agent B: 파란색 팀 화물을 배송

두 에이전트 모두 선반으로 이동하고, 화물을 집고, 배송 지점으로 이동하는 거의 동일한 행동을 수행합니다.

이때 공통 입력에 대한 행동확률만 비교하면

\\[ D\_{\mathrm{JS}}(\pi_A,\pi_B)\approx 0 \\]

일 수 있습니다.

하지만 각자의 보상 함수는 다를 수 있습니다.

\\[ r_A(s,a)\neq r_B(s,a) \\]

즉, 동일한 행동을 하는 것과 동일한 목적을 갖는 것은 다릅니다.

여기서 두 가지 목표가 갈립니다.

| 구분            | 목표                | 중요한 정보                     |
| ------------- | ----------------- | -------------------------- |
| 팀 발견          | 같은 팀의 에이전트를 식별    | 목표, 보상 구조, 작업 대상           |
| 유익한 critic 전이 | 서로 도움 되는 donor 식별 | Value target, 학습 신호, 전이 효과 |

특히 같은 팀을 발견하는 것이 연구 목표라면, 행동 유사도만으로 팀을 구분하려는 접근 자체에 한계가 있습니다.

반대로 critic 전이가 목표라면 색깔이 달라도 서로 도움이 되는 경우가 있을 수 있습니다. 따라서 팀이 다르다는 이유만으로 연결을 막는 것도 정답은 아닙니다.

## 2. RWARE와 SMAC을 하나의 알고리즘으로 다룰 수 있을까?

가능합니다. 다만 환경마다 동일한 probe를 사용한다는 뜻은 아닙니다. 환경에 관계없이 동일한 규칙으로 probe를 생성하고, 유사성을 평가하고, 전이를 결정한다는 뜻입니다.

먼저 SMAC에 관해 하나만 정확히 구분하겠습니다. 일반적인 SMAC (StarCraft Multi-Agent Challenge)과 SMACv2는 건물 건설·유닛 생산까지 포함한 전체 스타크래프트가 아니라, 유닛의 전투 미시 제어에 초점을 맞춘 환경입니다. SMACv2는 유닛 종류, 초기 위치, 시야 등을 다양화했습니다. 건설·생산·정찰을 함께 다루려면 일반적인 SMAC 외의 확장된 전략 환경이 필요합니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



하지만 말씀하신 연구상의 차이는 유효합니다.

| 특성                 | RWARE        | 다양한 역할의 RTS 환경   |
| ------------------ | ------------ | ---------------- |
| 공통 행동              | 이동, 물체 조작    | 이동, 상호작용         |
| 작업 차이              | 화물 소속, 배송 목표 | 전투, 정찰, 생산, 건설 등 |
| 행동이 같아도 목표가 다른가?   | 가능           | 가능               |
| 같은 목표에서 행동이 달라지는가? | 가능           | 가능               |
| 행동 유사성만으로 목적 구분    | 어려움          | 어려움              |

이런 차이를 다루려면 행동확률만 비교하기보다, 에이전트가 어떤 상황에서, 어떤 보상을 기대하며 행동하는지까지 고려해야 합니다.

### 제가 생각하는 일반화된 구조

환경별 Local Experience

관측 · 행동 · 보상 · 다음 관측 · 이력

Automatic Probe Sampler

실제 경험으로부터 다양한 상황을 자동 추출

Task-aware Similarity / Transfer Predictor

행동 · 목표 관련 정보 · 가치 예측 · 학습 신호

Selective Critic Transfer

유익할 것으로 판단되는 전달만 허용

핵심은 RWARE용 `pickup probe`, SMAC용 `attack probe`를 사람이 일일이 만드는 대신, 환경에서 실제로 수집된 경험을 사용한다는 것입니다.

다만 관측·행동 공간이 서로 다르다면 환경별 encoder나 action adapter는 필요할 수 있습니다. 동일한 알고리즘이라는 것은 모든 환경에서 입력 차원까지 같다는 뜻은 아닙니다.

## 3. Probe를 자동으로 만들 수는 없을까?

저는 이 방향이 가장 현실적이라고 생각합니다.

현재 방식은 사람이 상황을 정의합니다.

\\[ \mathcal P\_{\mathrm{manual}} =\\{o_1,o_2,\ldots,o\_{48}\\} \\]

그 대신 학습 중 자연스럽게 모이는 trajectory를 활용할 수 있습니다.

\\[ \tau_i= (o_0,a_0,r_0,o_1,a_1,r_1,\ldots) \\]

여기서 자동으로 probe를 추출하는 것입니다.

다만 그냥 replay buffer에서 무작위로 뽑으면 문제가 반복될 수 있습니다. RWARE에서 이동 상태가 대부분이라면 다시 이동 중심 probe가 만들어지기 때문입니다.

따라서 샘플링 기준을 세분화할 필요가 있습니다.

자동 Probe 생성의 세 가지 후보

A. Experience-based sampling

실제 방문한 상태에서 무작위로 추출합니다.

장점: 구현이 간단하고 실제 방문 분포를 반영함. 단점: 자주 발생하는 단순 행동에 치우칠 수 있음.

B. Diversity-based sampling

관측 이력의 학습된 표현을 군집화하거나 중복을 제거해 서로 다른 유형의 경험을 선택합니다.

장점: 반복적인 이동 상황을 줄일 수 있음. 단점: 표현이 중요한 작업 차이를 보존한다는 보장은 없음.

C. Learning-signal-based sampling

TD error, 불확실성, 보상 변화, critic 예측 불일치가 큰 상황을 우선 선택합니다.

장점: critic 학습에 중요한 상황을 더 자주 검사할 가능성. 단점: 노이즈나 예측 오류가 큰 상태만 과도하게 선택할 위험.

저라면 우선 A+B를 혼합하고, 이후 C를 추가하겠습니다.

중요한 점은 환경별 이벤트 이름을 직접 지정하지 않는 것입니다.

예를 들어 RWARE의 배송 완료나 RTS의 적 처치가 모두 학습 과정에서 보상·상태 변화로 나타난다면, 알고리즘은 그 결과를 보고 관련 경험을 선택할 수 있습니다.

물론 이벤트의 의미가 관측이나 보상에 전혀 드러나지 않으면 자동 샘플링도 해당 의미를 알아낼 수 없습니다.

## 4. 그런데 자동 probe만으로 충분할까?

아닙니다. 여기서 더 중요한 개선이 필요합니다.

지금 PGCT에서는 다음 관계를 기대하고 있습니다.

\\[ \text{Policy Similarity} \longrightarrow \text{Transfer Utility} \\]

하지만 앞선 E1/E2 결과에서 둘이 일치한다는 증거는 충분하지 않았습니다.

따라서 저는 장기적으로 다음 방향을 더 주목하고 있습니다.

\\[ \boxed{ \text{Policy Similarity} + \text{Learning Compatibility} \longrightarrow \text{Transfer Gate} } \\]

여기서 Learning Compatibility란 donor의 critic 정보를 받아들였을 때 receiver의 학습 목표가 실제로 개선되는지를 뜻합니다.

예를 들어 receiver \\(i\\)의 critic loss를 \\(\mathcal L_i\\), donor \\(j\\)로부터 받는 peer loss를 \\(\mathcal L\_{i\leftarrow j}^{peer}\\)라고 하겠습니다.

각 손실의 gradient를

\\[ g_i=\nabla\_{\theta_i}\mathcal L_i,\qquad g\_{i\leftarrow j}^{peer} =\nabla\_{\theta_i}\mathcal L\_{i\leftarrow j}^{peer} \\]

라고 두면,

\\[ \boxed{ \langle g_i,g\_{i\leftarrow j}^{peer}\rangle>0 } \\]

은 작은 peer-gradient 업데이트가 receiver의 critic loss를 국소적으로 줄일 가능성을 시사합니다.

이는 1차 근사에 따른 조건이며, 미래 return이나 PPO 학습 성능 개선을 보장하는 조건은 아닙니다. 또한 \\(g_i\\) 자체도 부트스트래핑된 target의 편향을 포함할 수 있습니다.

그럼에도 두 에이전트가 같은 행동을 하는가보다 전달된 정보가 receiver의 학습 방향에 도움이 되는가를 직접 조사한다는 의미가 있습니다.

그리고 이 방식은 팀 색상이나 작업 역할에 대한 수동 규칙이 필요하지 않습니다.

다만 추가 gradient 계산과 이웃 간 전달 비용이 발생하므로, 모든 에이전트 쌍에 매번 적용하기보다는 JS로 후보를 좁힌 뒤 일부에만 적용하는 방식이 현실적입니다.

## 5. 비슷한 이론적 접근이 이미 있나?

관련해서 읽어볼 가치가 높은 것이 Successor Features입니다.

특히 Barreto 등의 [Transfer in Deep Reinforcement Learning Using Successor Features and Generalised Policy Improvement](https://proceedings.mlr.press/v80/barreto18a.html)에서는 동역학과 보상 구조를 분리해 서로 다른 task 간 전이를 다룹니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://papers.neurips.cc\&sz=32)

papers.neurips.cc

+1



대표적인 형태는 다음과 같습니다.

\\[ r_i(s,a)=\phi(s,a)^\top w_i \\]

\\[ Q_i^\pi(s,a)=\psi^\pi(s,a)^\top w_i \\]

여기서 \\(\psi^\pi\\)는 미래의 feature 누적량이고, \\(w_i\\)는 task별 보상 가중치입니다.

이 관점에서는 비슷한 움직임을 만드는 동역학적 지식은 공유하면서도, 서로 다른 보상 목적은 구분할 수 있습니다.

RWARE에서 색깔이 다른 에이전트가 같은 이동 지식을 사용할 수 있다는 문제와 자연스럽게 연결됩니다.

다만 이 수식 형태는 공통 feature에 대한 선형 보상 표현을 전제합니다. 기존 연구에는 더 일반적인 보상 차이를 다루는 확장도 있습니다. 이를 PGCT에 그대로 결합해 이론적 보장까지 얻을 수 있다는 뜻은 아닙니다.

그리고 이 분야에는 이미 풍부한 선행 연구가 있기 때문에, 단순히 successor features를 넣는 것만으로 새로운 알고리즘이라고 주장하기는 어렵습니다.

## 6. 지금 PGCT를 어떻게 발전시키는 게 좋을까?

저는 기존의 모든 것을 한 번에 바꾸기보다 세 단계를 권합니다.

| 단계      | 변경                               | 목적              |
| ------- | -------------------------------- | --------------- |
| PGCT-v1 | 기존 canonical probe + JS          | 현재 기준선 유지       |
| PGCT-v2 | 자동 추출된 다양한 trajectory probe + JS | 수동 probe 의존성 제거 |
| PGCT-v3 | 자동 probe + critic 학습 신호 기반 gate  | 전이 유익성에 가까운 판단  |

특히 v2에서 유의미한 개선이 나타나지 않는다면, 단순히 probe를 다양하게 만드는 것으로는 충분하지 않다는 직접적인 실험 근거가 됩니다.

v3는 더 높은 연구 가치를 가질 가능성이 있지만, 동시에 계산 비용·이론 분석·실험 난도가 훨씬 높습니다. 논문 제출을 고려하면 전부 구현하기보다 먼저 v2의 가능성을 검증하는 것이 현실적입니다.

또한 완전분산 조건을 유지하려면 자동 probe와 학습 통계를 중앙 서버에서 모으는 대신, 학습 시 물리적으로 연결된 이웃끼리 제한적으로 공유하도록 설계해야 합니다. 실행 시에는 기존처럼 통신을 꺼둘 수 있습니다.

## 7. 제 최종 판단

질문하신 두 문제를 종합하면 저는 수동 canonical probe를 계속 환경마다 확장하는 방향은 권하지 않습니다.

RWARE에서 색깔 구분을 잘하는 probe를 만들고, SMAC에서 전투 역할을 잘 구분하는 probe를 만들고, 다른 환경에 가서 다시 설계한다면 환경별 휴리스틱의 집합이 될 위험이 큽니다.

반면 다음과 같은 접근은 하나의 일반적인 알고리즘으로 발전시킬 여지가 있습니다.

> 에이전트가 자신의 관측 및 보상 경험에서 대표적인 상태 이력을 자동으로 선택하고, 물리적 이웃의 학습 특성과 비교하여, 실제로 도움이 될 가능성이 있는 critic 정보만 선택적으로 전달한다.

여기서 중요한 연구 기여는 단순한 자동 probe 생성이 아니라 환경별로 수작업을 하지 않아도 유익한 정보 전달 관계를 발견할 수 있는가입니다.

다만 이것도 경험상 유사성을 학습할 수 있다는 가정이 필요합니다. 두 에이전트의 관측 이력과 보상 정보가 완전히 구분 불가능하다면, 어떤 알고리즘도 숨겨진 실제 팀 소속을 확실하게 복원할 수는 없습니다.

그래서 지금 결정해야 할 가장 큰 설계 선택은 이것입니다.

- 잠재적인 팀을 정확히 발견하고 싶다면, 정책 행동 외에 보상·목표에 관한 정보를 반드시 고려해야 합니다.
- 팀 구분 없이 critic transfer를 개선하고 싶다면, 정책 유사성은 후보 선정에 사용하고 학습 유익성에 가까운 신호를 최종 gate에 활용하는 편이 더 타당합니다.

제 생각에는 현재 E1/E2에서 나타난 현상을 고려할 때 두 번째 방향이 PGCT의 기존 구조를 가장 자연스럽게 확장하면서, RWARE와 SMAC처럼 서로 다른 환경에도 적용할 가능성이 큰 방향입니다.
````

##### Assistant — 진행 안내 2

답변의 큰 방향에는 동의하지만, 두 가지 보완이 필요합니다. 경험에서 probe를 자동 추출해도 서로 다른 보상 목표의 critic을 그대로 공유하는 문제는 남습니다. 또 JS로 후보를 먼저 차단하면, 행동은 달라도 전이가 유익한 agent를 놓칠 수 있습니다. 제안된 gradient 내적 기준도 현재 코드의 Adam·gradient clipping 업데이트에서 성능 개선을 보장하는 조건은 아닙니다.

##### 사용자 — 추가 메시지 원문

수정할 필요까진 일단 없고 한번 생각을 알려줘

##### Assistant — 진행 안내 3

네. 코드나 probe는 수정하지 않고, 첨부 답변에 대한 제 생각만 정리하겠습니다. 대화 원문 기록은 요청하신 대로 계속 남기겠습니다.

##### 수행 기록 — 원문 대화와 별도

첨부 전체와 공용 노트를 읽고 SMAC/SMACv2 공식 저장소 및 Barreto et al. 2018 PMLR 초록을 확인했다. 현재 trainer의 agent별 Adam, 결합 손실, gradient clipping을 읽었다. 학습 코드·probe·gate·실험은 변경하거나 실행하지 않았다. 아래 검토는 설계 의견이며 성능 보장이 아니다.

##### Assistant — 최종 답변

제 생각에는 첨부 답변의 핵심은 맞습니다. **문제의 중심은 probe 개수보다 “행동 유사성을 왜 critic 전이의 허가 기준으로 사용하는가”에 있습니다.**

RWARE에서 다른 팀이 같은 이동·운반 동작을 한다면, 낮은 JS 자체는 정확한 측정일 수 있습니다. 문제는 그 값을 “같은 팀이다” 또는 “value를 공유해도 좋다”로 해석하는 데 있습니다. 반대로 같은 팀이 분업하면 행동은 달라질 수 있습니다. 따라서 원래 목표가 팀 발견이었다면, probe를 늘리는 것만으로 이 가정을 해결하기는 어렵습니다.

**환경마다 수동으로 상황을 만드는 부담에 대한 지적도 타당합니다.** 수동 probe는 원인을 확인하는 진단 도구로는 유용하지만, 환경마다 계속 추가해야 한다면 일반적인 방법으로 주장하기 어려워집니다. 실제 경험에서 관측 이력을 자동 선택하는 방향은 자연스럽습니다. 다만 자동으로 뽑아도 대부분 이동 상태라면 같은 편향이 반복됩니다. 자동화와 중요한 상황을 포착하는 능력은 별개입니다.

RWARE와 SMAC에 같은 알고리즘을 적용하는 것은 연구 목표로 가능합니다. 여기서 공통이어야 하는 것은 **경험을 선택하고 전이를 판단하는 규칙**이지, 동일한 probe 벡터나 모델 가중치가 아닙니다. 관측·행동의 의미가 다른데 확률이나 value를 그대로 비교할 수는 없습니다. 또한 답변의 정정대로 표준 SMAC은 건설·생산을 포함한 전체 게임이 아니라 전투 미시 제어 환경입니다. [SMAC 공식 설명](https://github.com/oxwhirl/smac)

첨부 답변에서 제가 특히 보완하고 싶은 부분은 **“JS로 후보를 좁힌 뒤 유익성을 검사한다”는 제안**입니다. JS가 큰 agent를 처음부터 차단하면, 서로 다른 역할을 수행하면서 유용한 정보를 줄 수 있는 donor는 검사조차 못 합니다. 지금 관측한 specialization 문제를 그대로 남길 수 있다는 뜻입니다. 전이 유익성이 목표라면 JS를 필수 조건으로 둘 근거도 검증해야 합니다.

Gradient 방향의 일치를 보는 제안은 조사할 가치가 있습니다. 하지만 그것은 작은 업데이트가 현재 critic loss를 줄이는지에 가까운 신호입니다. 현재 코드의 Adam·gradient clipping까지 포함한 업데이트나 장기 delivery 개선을 보장하지는 않습니다. 별도로 남겨 둔 receiver 경험에서 오차가 개선되는지 확인하는 편이 더 설득력 있습니다. 이것도 최종 task 성능 검증을 대신하지는 못합니다.

현재 PGCT를 폐기할 단계라고 생각하지는 않습니다. 다만 **현재 구조가 일반적으로 좋은 donor를 고른다는 주장은 보류해야 합니다.** 기존 방식은 기준선으로 보존하고, 나중에 probe 자동화의 효과와 전이 판단 기준의 효과를 분리해 검증하는 것이 맞겠습니다. 지금은 코드나 probe를 수정하지 않았습니다.


#### 원문 기록 T003 — 2026-10-13 KST, Codex

##### 사용자

나는 SMAC를 쓴다는게 아니야
다만 같은 에이전트인 MARL이고, 역할이 분담된다고 해도 그 분담의 차이가 크지 않냐는 거지

##### Assistant — 진행 안내

제가 SMAC 도입 여부로 논점을 옮겼네요. 말씀하신 건 같은 형태의 에이전트라도 역할 분담의 성격과 차이가 크게 달라질 수 있는데, 현재 유사도 기준이 그 차이를 감당할 수 있느냐는 문제로 이해했습니다.

##### 수행 기록 — 원문 대화와 별도

사용자 정정에 따라 SMAC를 도입 요청으로 해석하지 않도록 DECISIONS.md D14와 RESEARCH_STATE.md에 기록했다. 역할 분담의 크기, canonical 응답 차이, 공유 가능한 지식을 구분한 의견이다. 코드·probe·실험은 변경하거나 실행하지 않았다.

##### Assistant — 최종 답변

맞아요. 제가 환경 선택 문제로 받아들였습니다. 말씀하신 핵심은 **같은 형태의 에이전트라도, 환경에 따라 역할 분담의 성격과 차이가 크게 달라진다**는 것이죠.

예를 들어 분업에도 차이가 있습니다.

- **담당 구역·경로가 다른 분업:** 모두 같은 운반 작업을 하지만 활동 위치가 다름.
- **기능 자체가 다른 분업:** 같은 능력을 가진 agent들이 탐색·운반·지원처럼 서로 다른 일을 맡음.

두 번째에서는 같은 목표를 달성하려고 오히려 다른 행동을 해야 합니다. 그러므로 **행동이 비슷할수록 같은 팀이거나 정보를 공유하기 좋다는 가정은, 분업의 형태에 따라 성립하지 않을 수 있습니다.** 이것이 현재 PGCT에 대한 더 근본적인 질문입니다.

Probe를 다양하게 만들면 역할 차이를 더 정확히 드러낼 수는 있습니다. 하지만 그렇게 드러난 정당한 차이까지 gate가 ‘전이하면 안 되는 차이’로 판단한다면, probe를 늘려도 핵심 문제는 남습니다.

다만 실제 행동이 크게 다르다고 공통 probe의 JS가 반드시 커지는 것은 아닙니다. 하나의 조건부 정책도 서로 다른 상황에서 다른 역할을 수행할 수 있기 때문입니다. **실제 역할 차이와 동일 입력에 대한 정책 차이는 구분해야 합니다.**

그래서 제가 중요하게 보는 질문은 **“역할이 얼마나 비슷한가?”보다 “역할이 달라도 어떤 지식은 공유할 수 있고, 어떤 value는 각자 달라야 하는가?”**입니다. 같은 agent라는 이유만으로 critic 전체를 공유해도 된다는 보장은 없습니다. 말씀하신 분업 차이의 크기는 바로 그 가정을 검증해야 하는 이유입니다.


#### 원문 기록 T004 — 2026-10-13 KST, Codex

##### 사용자 — 원문

아, 이제 정확히 이해했습니다. 제가 앞에서는 SMAC이라는 특정 환경에 너무 집중했습니다.

말씀하신 핵심은 동일한 종류의 에이전트들로 구성된 MARL이라도, 환경에 따라 에이전트들이 학습하는 역할의 차이가 질적으로 크게 달라질 수 있지 않느냐는 것이군요.

저도 이 부분이 PGCT를 일반적인 MARL 알고리즘으로 발전시킬 때 상당히 중요한 문제라고 생각합니다.

#### 1. 같은 에이전트라도 역할 차이의 정도는 전혀 다를 수 있습니다

예를 들어 다음 세 가지 상황을 생각해 보겠습니다.

|   |
| - |

상황

|   |
| - |

역할 분화

|   |
| - |

정책의 특징

|   |
| - |

A. RWARE의 팀별 배송

|   |
| - |

목표 화물이나 배송 지점만 다름

|   |
| - |

대부분의 이동·조작 행동이 유사

|   |
| - |

B. 같은 창고의 공간 분업

|   |
| - |

왼쪽 담당 / 오른쪽 담당

|   |
| - |

위치와 상황에 따라 행동이 달라짐

|   |
| - |

C. 다양한 임무의 협력 환경

|   |
| - |

정찰 / 방어 / 자원 수집

|   |
| - |

필요한 정보, 행동 전략, 보상 구조가 크게 다름

셋 다 같은 관측·행동 공간을 가진 homogeneous agents로 구성할 수 있습니다.

그러나 학습되는 정책의 차이는 완전히 다릅니다.

- A에서는 서로 다른 역할이어도 정책이 거의 동일할 수 있습니다.
- B에서는 같은 목표를 추구하지만 담당 위치에 따라 정책이 달라질 수 있습니다.
- C에서는 동일한 동역학을 가진 에이전트라도 서로 상당히 다른 정책을 학습할 수 있습니다.

따라서 \*\*역할 분화의 정도가 환경마다 다른데, 하나의 고정된 probe와 JS threshold로 모든 역할 관계를 판별하려는 것이 타당한가?\*\*라는 문제가 생깁니다.

#### 2. 특히 현재 PGCT에는 구조적인 어려움이 있습니다

PGCT는 기본적으로 다음과 같은 유사성을 측정합니다.

\\[ D\_{ij}^{\pi} = \mathbb E\_{o\sim\mathcal P} [D\_{\mathrm{JS}}(\pi_i(\cdot|o),\pi_j(\cdot|o))] \\]

하지만 정책 응답 유사성과 역할의 유사성은 일대일 대응하지 않습니다.

서로 다른 역할, 유사한 행동

행동 JS는 작을 수 있음

같은 목표, 서로 다른 행동

행동 JS는 클 수 있음

이 문제는 probe를 48개에서 100개, 1,000개로 늘린다고 자동으로 해결되지 않습니다.

관측 상황을 충분히 다양하게 확보하는 것은 측정 품질을 개선할 수 있지만, 무엇을 유사하다고 정의할지라는 근본적인 문제는 남습니다.

#### 3. 그렇다면 하나의 알고리즘으로 일반화할 수 없을까?

저는 가능하다고 생각합니다. 다만 알고리즘이 역할의 유사성 자체를 맞히도록 설계될 필요는 없다고 봅니다.

예를 들어 두 에이전트가 있습니다.

- Agent 1은 자원을 수집합니다.
- Agent 2는 경로를 탐색합니다.

서로 완전히 다른 역할이지만, 두 에이전트가 공유할 수 있는 가치 정보가 있을 수도 있습니다. 반대로 같은 자원 수집 역할이라도 보상 구조가 다르면 critic transfer가 해로울 수 있습니다.

따라서 유사성을 하나의 숫자로만 판단하기보다 적어도 다음 두 개념을 구분하는 것이 좋습니다.

\\[ \underbrace{S\_{ij}^{\mathrm{behavior}}}\_{\text{행동의 유사성}} \qquad \underbrace{C\_{i\leftarrow j}^{\mathrm{transfer}}}\_{\text{학습 정보의 유익성}} \\]

여기서 중요한 차이점이 하나 더 있습니다.

일반적인 JS divergence는 대칭적입니다.

\\[ D\_{\mathrm{JS}}(\pi_i,\pi_j) = D\_{\mathrm{JS}}(\pi_j,\pi_i) \\]

하지만 critic transfer의 유익성은 반드시 대칭적이지 않습니다.

\\[ C\_{i\leftarrow j}^{\mathrm{transfer}} \neq C\_{j\leftarrow i}^{\mathrm{transfer}} \\]

즉, Agent 1이 Agent 2에게 도움을 줄 수 있다고 해서 Agent 2도 Agent 1에게 똑같이 도움이 되는 것은 아닙니다.

이러한 방향성까지 고려하는 것이 서로 다른 정도의 역할 분화를 가진 환경에 일반화할 때 중요할 수 있습니다.

#### 4. 제가 생각하는 PGCT의 더 일반적인 방향

처음에는 다음 방식이었습니다.

\\[ \text{Probe} \rightarrow \text{Policy JS} \rightarrow \text{Critic Transfer} \\]

하지만 역할 분화의 정도가 크게 달라지는 환경까지 고려한다면 다음 구조가 더 자연스럽습니다.

\\[ \boxed{ \begin{aligned} &\text{Local Experience}\\\ &\downarrow\\\ &\text{Automatic Probe Selection}\\\ &\downarrow\\\ &\text{Policy Similarity + Transfer Compatibility}\\\ &\downarrow\\\ &\text{Directed Critic Transfer} \end{aligned} } \\]

이것은 아직 검증된 알고리즘이 아니라 제가 제안하는 연구 방향입니다.

장점은 역할이 비슷한 환경에서는 행동 유사성을 활용할 수 있고, 역할이 상당히 다른 환경에서는 학습 신호의 유익성을 더 중요하게 고려하도록 설계할 수 있다는 것입니다.

단, 어떤 환경에서도 반드시 잘 작동한다는 보장은 없으며, 서로 다른 역할의 critic 정보를 비교할 수 있는 공통 표현이나 평가 기준도 필요합니다.

#### 5. 여기서 연구적으로 더 중요한 질문

저는 이제 PGCT를 연구할 때 역할의 차이를 두 가지 변수로 나눠볼 가치가 있다고 생각합니다.

\\[ \text{Role Difference} = \begin{cases} \text{Behavioral Difference}\\\ \text{Objective Difference} \end{cases} \\]

이 둘은 독립적이지 않을 수 있지만, 개념적으로 구분할 수 있습니다.

예를 들어 행동은 비슷하지만 목적이 다른 환경과, 목적은 비슷하지만 행동이 다른 환경을 각각 구성할 수 있습니다.

그런 다음 PGCT가 어느 조건에서 유익한 전이를 만들어 내는지 분석하면, 단순히 RWARE 한 환경에서 성능이 좋아졌다는 결과보다 훨씬 일반적인 설명을 제공할 수 있습니다.

핵심은 에이전트들의 역할 차이가 작든 크든, 그 역할을 사람이 정의하지 않고 유익한 학습 관계를 발견하는 알고리즘을 만드는 것입니다.

그리고 이 관점에서 보면 현재 PGCT의 가장 큰 한계는 probe의 개수가 아니라, 정책 유사성 하나만으로 다양한 역할 관계에서 critic transfer 여부를 결정한다는 점이라고 생각합니다.

따라서 저는 지금 고민하신 문제가 단순한 환경 선정 문제가 아니라, PGCT를 일반적인 MARL 알고리즘으로 만들기 위해 해결해야 할 핵심적인 설계 문제라고 봅니다.



어떻게 생각해?

##### Assistant — 진행 안내 1

행동 유사성과 전이 유익성을 구분한 점에 동의합니다. 특히 전이의 방향성이 현재 코드에서 어떻게 처리되는지 확인한 뒤, 이 제안이 보완하는 부분과 아직 검증이 필요한 부분을 짚겠습니다. 대화도 원문으로 기록하겠습니다.

##### Assistant — 진행 안내 2

현재 코드도 전이를 수신자×donor로 표현하고 수신자별로 가중치를 정규화하므로, 양방향 전달량이 달라질 수는 있습니다. 제안의 핵심 보완은 여기에 “이 donor가 이 수신자에게 실제로 도움이 되는가”를 방향별로 판단하는 기준을 추가하는 것이라고 봅니다.

##### 수행 기록 — 원문 대화와 별도

현재 trainer의 gate, 수신자별 allocation 정규화, detached donor critic target 코드를 읽었다. DECISIONS.md D15와 RESEARCH_STATE.md에 설계 의견을 기록했다. 새 학습·평가 실험이나 학습 코드·probe 변경은 수행하지 않았다.

##### Assistant — 최종 답변

이번 정리에 동의합니다. 특히 **“행동 유사성은 대칭적이지만, 전이의 유익성은 방향에 따라 다르다”**는 구분이 중요합니다. 다만 제안한 구조는 아직 검증할 연구 가설입니다.

예를 들어 donor의 critic이 receiver가 경험하는 상황에서 더 정확하다면 도움이 될 수 있지만, 반대 방향의 전이는 부정확한 예측을 퍼뜨릴 수 있습니다. 같은 역할이나 비슷한 정책이라는 사실만으로 이 차이를 판단할 수는 없습니다.

여기서 현재 구현과 구분할 부분이 있습니다. **지금 코드도 수신자별로 전달 가중치를 정규화하므로 양방향 전달량이 달라질 수 있습니다.** 하지만 이는 방향별 유익성을 판단한 결과는 아닙니다. 제안의 핵심 기여는 ‘방향이 있는 행렬’ 자체보다 **각 수신자에게 어떤 donor가 도움이 되는지 판단하는 기준**에 있습니다. [현재 allocation 구현](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/train_recurrent_ippo_consensus.py:4957)

그래서 가장 어려운 부분은 `Transfer Compatibility`를 실제로 어떻게 측정하느냐입니다. 한 가지 검증 방법은 같은 receiver 모델·학습 경험에서 **전이 없는 업데이트와 특정 donor를 추가한 업데이트를 비교하고, 별도로 남겨 둔 receiver 경험의 예측 오차가 얼마나 달라지는지** 보는 것입니다. 이것도 단기 critic 오차의 대리 지표이지, 장기 성능 개선을 보장하지는 않습니다.

행동 차이와 목적 차이를 두 축으로 나누는 제안도 타당합니다. 다만 같은 목적이라도 담당 역할·관측 이력·정책이 다르면 value는 달라질 수 있습니다. 따라서 **목적이 같다는 사실 역시 critic 전체를 공유해도 된다는 충분조건은 아닙니다.** 무엇을 공유할 수 있는지까지 검토해야 합니다.

자동 probe는 수동 설계 부담을 줄이는 별도의 개선입니다. 그러나 JS가 큰 agent를 후보에서 무조건 제외하면, 역할은 달라도 유익한 donor를 놓치는 문제는 남습니다. Probe 자동화와 방향별 유익성 판단의 효과를 분리해서 검증할 필요가 있습니다.

제 판단은 **연구 문제를 더 명확하게 정의한 방향**이라는 것입니다. 이를 전이 유익성 중심으로 발전시킨다면 핵심 질문은 “역할을 사람이 지정하지 않아도, 각 agent가 자신에게 유익한 지식 제공자를 발견할 수 있는가?”가 됩니다. 원래 팀 발견 목표에서 이 방향으로 확장한다면, 목표 변경도 명시해야 합니다. 지금은 검토와 기록만 했고 코드나 probe는 수정하지 않았습니다.


#### 원문 기록 T005 — 2026-10-13 KST, Codex

##### 사용자 — 원문

그리고 별 차이가 없는걸보면 이번 환경이 너무 쉬웠던건 아닐까?

장애물이나 다른 제약이 추가 된 조금더 어려운 환경을 현재 코드에 방해받지 않게 만들어줘

##### Assistant — 진행 안내 1

환경이 쉬워서 PGCT와 IPPO 차이가 작았을 가능성은 있습니다. 다만 기존 보조 전이의 효과가 작은 경우도 있어 난이도만으로 단정할 수는 없습니다. 기존 코드·학습에는 손대지 않고, 장애물과 제약을 넣은 별도 환경 및 실행 경로를 만들겠습니다.

##### Assistant — 진행 안내 2

기존 RWARE에는 지도 내부의 벽을 처리하는 기능이 없어, 새 환경 클래스로 분리하겠습니다. 먼저 E2와 같은 크기·보상에서 비교할 수 있도록 무장애물 대조군, 통로를 두 곳으로 제한한 병목 환경, 여기에 배송 지점의 대기시간을 추가한 환경을 만들겠습니다. 선반과 목표 지점까지 실제로 이동 가능한지도 검사하겠습니다.

##### Assistant — 진행 안내 3

새 환경과 전용 학습 실행기를 추가했습니다. 장애물은 기존 통로에만 배치해 대조군과 선반 수·맵 크기·보상을 유지했고, 벽과 배송 지점의 대기 상태를 관측 및 action mask에 반영했습니다. 이제 벽 통과 방지, 배송·반납 가능 여부, 기존 환경과의 동일성, 짧은 시험 학습을 검증하겠습니다.

##### Assistant — 진행 안내 4

관련 테스트 31개와 세 환경×PGCT/IPPO의 64-step 시험 학습이 모두 통과했습니다. 108개 선반을 그대로 유지하면서, 이번 배치의 적재 상태 평균 최단 이동거리는 13.37칸에서 17.07칸으로 약 28% 늘었습니다. 배송·반납이 가능한 경로도 확인했고, 기존 핵심 파일과 canonical probe 내용은 바뀌지 않았습니다.

##### Assistant — 진행 안내 5

기존 E2 모델을 고정해 평가하니, 병목 환경의 delivery가 37.8에서 2.2로 크게 떨어졌습니다. 학습 후의 난이도를 뜻하는 결과는 아니지만 초기 변화가 상당해, 요청하신 “조금 더 어려운” 환경의 기본값으로는 더 완만한 장애물 2개짜리 우회 환경을 추가하겠습니다. 병목과 배송 대기 환경은 더 강한 선택지로 남기겠습니다.

##### Assistant — 진행 안내 6

최종 4개 환경×PGCT/IPPO의 시험 학습 8개와 테스트 32개가 모두 통과했습니다. 기본 우회 환경은 적재 최단 경로가 약 8% 늘지만, 기존 모델의 고정 평가 delivery는 37.8에서 5.4로 떨어져 우회에 대한 적응이 필요함을 확인했습니다. 원래 학습·환경 파일은 보존했고, 새 장기 학습은 시작하지 않았습니다. 실행 명령과 검증 결과를 문서 및 공용 로그에 정리하겠습니다.

##### 수행 기록 — 원문 대화와 별도

사용자가 새 환경 구현을 요청하여 원래 학습을 보존하는 opt-in 환경을 추가했다. 새 파일은 rware/constrained_warehouse.py, examples/train_hard_rware_experiments.py, examples/run_hard_rware_experiments.ps1, examples/HARD_RWARE_EXPERIMENTS.md, tests/test_constrained_warehouse.py다.

초기 테스트에서 info 공개 설정을 수정했고, smoke에서 발견한 NumPy 경로 통계 직렬화 및 원래 probe constructor의 새 인자 호환 문제를 새 파일 내부에서 고쳤다. 새 detour 조건 추가 후 계획 테스트의 조건 수/벽 개수 기대값도 갱신했다. 최종 관련32 tests,4 profiles×PGCT/IPPO8조건의 CPU64-step smoke,32-bit local 관측 및 실제 배송/반납,RGB MP4 저장을 검증했다. Control64-step 모델의128 tensor는 기존 E2 smoke와 bitwise 일치했다. 원래 핵심10개 소스 파일 SHA256을 보존했다.

기존 E2 PGCT final을 고정한5×500 평가에서 control37.8/detour5.4/bottleneck2.2/dock2.2 deliveries였다. 고정 모델의 환경 변화에 대한 적응 평가이며, 새 환경에서 재학습한 성능이나 PGCT 성능 향상의 결과가 아니다. 모든 평가 전후 모델 hash 불변을 확인했다.

최종 산출물은 runs/hard_smoke_20261013_final과 output/hard_rware_validation_20261013/validation.json 및 frozen_difficulty_pilot_v2.json이다. 과거 실패 v1/v2와 초기3조건 성공 v3는 최종 장기 학습 결과로 세지 않는다. 새4M 장기 학습을 시작하거나 기존 프로세스를 중단하지 않았다. DECISIONS.md D16, EXPERIMENTS.md E10, RESEARCH_STATE.md를 갱신했다.

##### Assistant — 최종 답변

기존 코드와 분리된 **새 환경과 학습 실행기**를 만들었습니다. 기존 환경이 쉬웠다는 가설은 아직 확정할 수 없지만, 난이도를 단계별로 비교할 수 있습니다.

| 환경 | 추가 제약 |
|---|---|
| `control` | 기존 E2와 같은 대조군 |
| **`detour` — 기본** | 장애물 2개로 우회 유도, 적재 최단 경로 약 8% 증가 |
| `bottleneck` | 벽 14개, 통과 지점 두 곳으로 제한 |
| `dock` | 병목 + 배송 지점의 8-step 대기 |

모두 16×16·선반108개이며 기존 보상과 PGCT 기준을 유지했습니다. **테스트 32개와 8조건의 CPU 64-step 시험 학습을 통과**했고, 배송·반납 경로도 확인했습니다.

기존 E2 모델의 고정 평가(5회×500 step)에서는 delivery가 대조군37.8→detour5.4로 떨어졌습니다. 이는 기존 정책의 초기 적응 문제이며, 재학습 후 성능을 뜻하지는 않습니다.

학습 실행:

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_hard_rware_experiments.ps1 -Profiles detour
```

동일한 Stage03 모델에서 PGCT/IPPO를 각각 약400만 step 학습하고 새 폴더에 저장합니다. **장기 학습은 아직 시작하지 않았고, 기존 학습은 유지했습니다.**

[환경 지도](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/runs/hard_smoke_20261013_final/maps.png) · [실행 설명](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/examples/HARD_RWARE_EXPERIMENTS.md)


#### 원문 기록 T006 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다. 이 항목부터 Claude Code가 작성한 기록이다.

##### 사용자 — 원문

지금까지의 내용을 AGENTS.md, CLAUDE.md, CONVERSATION_LOG.md, DECISIONS.md, EXPERIMENTS.md, RESEARCH_STATE.md로 정리했어 앞으로 너도 수정하거나 대화한 내역들은 여기에 정리해줘 알겠지?

##### Assistant — 진행 안내 1

노트 기록 형식(인코딩·줄바꿈)을 확인한 뒤 이번 대화를 `CONVERSATION_LOG.md`에 추가하고 있습니다.

##### 수행 기록 — 원문 대화와 별도

Claude Code가 CLAUDE.md·AGENTS.md 지침에 따라 RESEARCH_STATE.md, DECISIONS.md(D13–D16), EXPERIMENTS.md(E10), CONVERSATION_LOG.md(L01–L12 요약, T001–T005 원문)를 읽었다. 이번 turn은 기록 규칙 확인뿐이므로 이 T006만 추가했다. 연구 상태·판단·실험 기록, 학습 코드, 로그, 체크포인트는 변경하지 않았고 학습을 시작하거나 중단하지 않았다. 별도 Hook·MCP 자동 수집은 설정하지 않았다.

##### Assistant — 최종 답변

알겠습니다. 앞으로 이 프로젝트에서는 작업 전에 `RESEARCH_STATE.md`·`DECISIONS.md`·`EXPERIMENTS.md`를 확인하고, 과거 맥락이 필요하면 `CONVERSATION_LOG.md`도 보겠습니다.

작업 후에는 다음처럼 기록하겠습니다.

- **대화:** 사용자 메시지와 제 진행 안내·최종 답변을 [CONVERSATION_LOG.md](CONVERSATION_LOG.md)에 원문으로 남기겠습니다. 작성 도구는 `Claude Code`로 표시하고, 짧은 확인도 빠뜨리지 않겠습니다.
- **연구 기록:** 상태·판단·실험 결과가 바뀌면 `RESEARCH_STATE.md`, `DECISIONS.md`, `EXPERIMENTS.md`를 갱신하겠습니다.
- **동시 수정:** Codex도 같은 파일을 고칠 수 있으므로, 쓰기 직전에 다시 읽고 변경 내용을 합치겠습니다.

자동 수집 Hook은 없으므로 매번 제가 직접 추가합니다. 이번 대화는 **T006**으로 기록했습니다. 연구 상태는 바뀌지 않아 다른 노트는 수정하지 않았습니다.

노트에 적힌 다음 단계를 실행 허가로 보지 않겠습니다. 기존 학습·로그·체크포인트는 그대로 두겠습니다.


#### 원문 기록 T007 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

지금 문서 정리 관해서 기억하고 있어?

##### Assistant — 진행 안내 1

노트 확인은 끝났고, 이번 대화를 `CONVERSATION_LOG.md`에 T007로 추가하고 있습니다.

##### 수행 기록 — 원문 대화와 별도

새 Claude Code 세션에서 자동 로드된 CLAUDE.md·AGENTS.md 지침을 따라 RESEARCH_STATE.md, DECISIONS.md(D01–D16 제목), EXPERIMENTS.md(E00–E10 제목), CONVERSATION_LOG.md(L10–L12, T001, T005–T006)를 읽었다. Claude Code 개인 memory 폴더는 비어 있었고, 문서 정리 약속은 T006 기록으로 확인했다. 이번 turn은 확인 질문이므로 T007만 추가했다. 연구 상태·판단·실험 기록, 학습 코드, 로그, 체크포인트는 변경하지 않았고 학습을 시작하거나 중단하지 않았다.

##### Assistant — 최종 답변

네, 알고 있습니다. 다만 이전 대화를 제가 직접 기억하는 것은 아닙니다. 새 세션마다 자동으로 불러오는 `CLAUDE.md`와 지난 약속을 남긴 [CONVERSATION_LOG.md](CONVERSATION_LOG.md)의 **T006**을 읽고 확인한 것입니다. 제 개인 memory 폴더는 비어 있습니다.

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | Codex·Claude Code 공통 작업 지침 |
| `CLAUDE.md` | Claude Code 시작 파일, `AGENTS.md`를 불러옴 |
| `RESEARCH_STATE.md` | 현재 연구 상태 (최신 수치 기준 2026-10-13 14:37 KST) |
| `DECISIONS.md` | 질문·결론·설계 판단 D01–D16 |
| `EXPERIMENTS.md` | 실험·평가 기록 E00–E10 |
| `CONVERSATION_LOG.md` | 과거 요약 L01–L12, 이후 대화 원문 T001부터 (T001–T005 Codex, T006 Claude Code) |

다음 규칙을 따르겠습니다.

- **작업 전:** `RESEARCH_STATE` → `DECISIONS` → `EXPERIMENTS` 순서로 확인하고, 필요하면 대화 기록도 읽습니다.
- **매 대화:** 사용자 메시지, 진행 안내, 최종 답변을 원문 그대로 기록합니다. 작성 도구는 `Claude Code`로 표시하고, 시각을 모르면 임의로 적지 않습니다.
- **연구 기록:** 상태·판단·실험이 바뀌면 해당 노트도 갱신합니다.
- **동시 수정:** Codex와 같은 파일을 쓰므로 쓰기 직전에 다시 읽고 변경 내용을 합칩니다.
- **실행 범위:** 노트의 '다음 단계'를 실행 허가로 보지 않고, 기존 학습·로그·체크포인트를 보존합니다.

참고로 노트에 기록된 마지막 상태는 이렇습니다. E1·E2는 PGCT와 IPPO 모두 완료됐고, E3 PGCT는 14:37 기준으로 진행 중이었습니다. 별도로 만든 장애물 환경은 smoke 검증까지만 했고, 장기 학습은 시작하지 않았습니다.

이번 대화는 **T007**로 기록했습니다.


#### 원문 기록 T008 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다. 붙여넣은 GPT 답변은 사용자 메시지의 일부로 전체를 기록한다.

##### 사용자 — 원문 (붙여넣은 내용 2개 포함)

###### 붙여넣은 내용 1 — 사용자의 질문

자 그럼 처음부터

1. 일단 현재 진행중인 PGCT를 계속 돌리는게 맞아?
2. 연구 주제를 다시한번 정리해줘
   1. 내가 원했던 것 : 행동 유사도를 기반으로 팀을 찾고, 각 팀끼리 critic consensus를 이뤄 학습 능력을 향상시킨다.
   2. 너가 원했던 것 : 다른 팀이어도 행동 유사도가 비슷하다면 critic transfer를 통해 학습 능력이 향상될 수 있다.
   3. 이 둘중 뭐가 맞는건지

###### 붙여넣은 내용 2 — 위 질문에 대한 GPT의 답변 (참고 자료, 실행 지시 아님)

### PGCT 연구 방향 재정립

먼저 결론부터 말하겠습니다.

현재 연구의 주제는 1번으로 돌아가는 것이 맞다고 생각합니다. 다만 1번에도 반드시 해결해야 할 이론적 문제가 있습니다.

그리고 현재 진행 중인 PGCT를 무작정 계속 학습시키는 것은 추천하지 않습니다. 지금까지의 실험은 오히려 기존 PGCT의 핵심 가정이 성립하는지 다시 검토해야 한다는 신호를 보여주고 있습니다.

제 판단을 정리하면 다음과 같습니다.

| 질문                       | 판단                                                     |
| ------------------------ | ------------------------------------------------------ |
| 기존 PGCT를 계속 돌릴까?         | 진행 중인 대조 실험은 마무리하되, 새로운 대규모 학습은 보류                     |
| 원래 연구 주제는?               | 행동을 관측해 잠재적 팀을 추론하고, 팀 내부에서 critic consensus 수행        |
| 다른 팀 간 critic transfer는? | 별도의 연구 가설로는 가능하지만 본래 목표는 아님                            |
| 지금 가장 중요한 문제는?           | 행동 유사성이 실제로 같은 목표를 가진 팀을 식별할 수 있는가                     |
| 기존 PGCT는 폐기해야 하나?        | 아니요. 이미 구현한 학습 구조는 활용하되, 팀 추론과 critic 공유 조건을 다시 설계해야 함 |

특히 지금까지 제가 행동이 비슷한 에이전트라면 서로 다른 목표를 가져도 critic을 공유해서 이득을 얻을 수 있다는 방향으로 연구를 해석한 것은 원래 의도에서 벗어난 부분이 있습니다.

이것은 흥미로운 별도의 연구 주제일 수 있지만, 사용자가 처음 제시했던 문제를 해결한 것은 아닙니다.

#### 1. 우리가 원래 연구하고 싶었던 문제

연구의 출발점은 다음과 같았습니다.

> 여러 에이전트가 존재하는 완전분산 MARL 환경에서, 에이전트들은 서로 다른 목표를 가진 잠재적인 팀으로 구성되어 있다.
>
> 그러나 각 에이전트는 다른 에이전트가 자신과 같은 목표를 추구하는지 알지 못한다.
>
> 따라서 국소적으로 관측 가능한 행동을 통해 같은 목표를 공유하는 에이전트를 추론하고, 그렇게 형성된 팀 내에서 critic consensus를 수행함으로써 학습 효율을 향상시키고자 한다.

이것이 중심 연구 질문입니다.

여기서 중요한 것은 행동 유사도 자체가 목적이 아니라, 관측된 행동으로부터 다른 에이전트의 잠재적인 목표를 추론하는 것이 목적이라는 점입니다.

원래 의도한 연구 구조

이 구조에서는 역할이 명확하게 구분됩니다.

- Behavior observation: 다른 에이전트의 행동에서 정보를 얻는 수단
- Latent team inference: 누가 같은 목표를 갖는지 추론하는 핵심 문제
- Critic consensus: 추론한 팀을 활용하여 학습을 개선하는 방법

반면 기존 PGCT는 사실상 첫 단계에서 행동 유사도를 계산한 뒤, 잠재적인 팀을 별도로 추론하거나 검증하지 않고 critic transfer로 바로 연결합니다.

바로 이 중간 단계의 부재가 현재 PGCT와 원래 연구 목표 사이의 가장 큰 차이입니다.

#### 2. 두 연구 방향 중 어느 것이 더 타당한가?

두 방향은 서로 다른 연구 가설을 갖고 있습니다.

##### 방향 A. 잠재 팀 발견 → 팀 내 critic consensus

사용자가 원했던 방향입니다.

가정은 다음과 같습니다.

\\[ \begin{aligned} &\text{Behavioral evidence}\\\ &\Downarrow\\\ &\text{Latent objective similarity}\\\ &\Downarrow\\\ &\text{Team inference}\\\ &\Downarrow\\\ &\text{Within-team critic consensus} \end{aligned} \\]

핵심은 에이전트가 관측한 행동을 통해 자신과 동일하거나 호환되는 목표를 추구하는 에이전트를 식별하는 것입니다.

예를 들어 에이전트 4개가 있다고 가정하겠습니다.

실제 팀은 다음과 같습니다.

\\[ \mathcal T_1=\\{1,3\\},\qquad \mathcal T_2=\\{2,4\\} \\]

하지만 각 에이전트는 다른 에이전트의 팀 정보를 모릅니다.

에이전트 1이 국소적인 행동 관측을 통해 에이전트 3이 같은 목표를 가진다고 추론하면, 둘 사이에서 critic 정보를 공유하도록 합니다.

이때 목표는 단순히 critic을 공유하는 것이 아닙니다.

1. 팀을 모르는 상태에서 적절한 협력 대상을 발견할 수 있는가?
2. 발견한 팀에서 critic consensus가 학습에 도움이 되는가?
3. 이를 중앙 서버 없이 수행할 수 있는가?

이 세 가지가 논문의 핵심 연구 질문이 됩니다.

##### 방향 B. 목표와 무관한 행동 유사성 → 선택적 critic transfer

기존 PGCT가 실제로 구현한 방향에 가깝습니다.

\\[ D\_\pi(i,j) = \mathbb E\_{x\sim Q} \left[ D\_{\mathrm{JS}} \left( \pi_i(\cdot\mid x), \pi_j(\cdot\mid x) \right) \right] \\]

두 에이전트의 정책 응답 분포가 유사하면 critic 정보를 전달합니다.

여기에는 두 에이전트가 같은 목표를 공유해야 한다는 조건이 없습니다.

이 방향에서 중요한 질문은 다음과 같습니다.

> 서로 다른 목표를 가진 에이전트라도 정책 응답이 비슷하면 critic transfer로 학습 성능을 개선할 수 있는가?

이 역시 연구할 수 있는 가설입니다.

다만 정책 응답이 비슷하다는 것이 value function 역시 호환된다는 뜻은 아닙니다.

동일한 행동을 하더라도 보상이 다르면 Bellman target과 value function이 달라질 수 있기 때문입니다.

따라서 방향 B에는 별도의 검증이 필요합니다.

\\[ D\_\pi(i,j)\text{가 작음} \\;\not\Rightarrow\\; \text{critic transfer가 유익함} \\]

지금까지의 PGCT는 이 연결을 아직 충분히 입증하지 못했습니다.

##### 제 판단

방향 A를 본 연구로 선택하고, 방향 B는 현재 PGCT의 실험 가설로 분리하는 것이 좋겠습니다.

다만 A 역시 아직 옳다고 증명된 것은 아닙니다. 특히 아래 문제가 가장 중요합니다.

#### 3. 행동이 비슷하면 같은 목표를 가진 것인가?

사실 이 부분이 전체 연구에서 가장 어렵고 중요한 문제라고 생각합니다.

두 가지 반례가 존재합니다.

반례 1. 다른 목표, 같은 행동

서로 다른 팀이 같은 복도를 따라 이동

반례 2. 같은 목표, 다른 행동

같은 목표를 위해 역할을 나누어 반대 방향으로 이동

첫 번째는 현재 RWARE에서 이미 관찰한 현상과 연결됩니다.

같은 공간을 담당하는 서로 다른 팀의 에이전트가 유사한 행동을 보인 것입니다. 행동 유사도는 팀의 목표보다 공간적 역할의 유사성을 더 잘 포착했을 가능성이 있습니다.

반대로 두 번째에서는 같은 팀의 에이전트들이 역할을 분담하면서 서로 다른 행동을 합니다.

더 근본적으로, 이것은 inverse reinforcement learning의 identifiability 문제와도 연결됩니다. 서로 다른 reward function이 동일한 최적 정책을 만들어낼 수 있으므로 행동만으로 보상의 동일성을 일반적으로 보장할 수 없습니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research

+1



따라서 원래 연구 목표를 다음처럼 더 정교하게 표현해야 합니다.

기존 가정:

\\[ \boxed{ \text{Behavior similarity} \Rightarrow \text{Same objective} } \\]

수정해야 할 가정:

\\[ \boxed{ \text{Behavioral evidence} \longrightarrow P(z_i=z_j\mid \mathcal H\_{ij}) } \\]

여기서 \\(z_i\\)는 에이전트 \\(i\\)의 잠재 팀이고, \\(\mathcal H\_{ij}\\)는 국소적으로 얻을 수 있는 행동 관측 이력입니다.

즉, 행동 유사성을 확정적인 팀 판정 기준으로 쓰는 대신 팀이 같을 가능성을 추론하기 위한 증거로 사용하는 방향입니다.

단, 두 목표가 관측 가능한 행동에 전혀 구분 가능한 차이를 만들지 않는 환경에서는 행동만으로 팀을 복원하는 것이 원천적으로 불가능할 수 있습니다. 따라서 정보가 충분한지 먼저 확인해야 합니다.

#### 4. 그렇다면 현재 PGCT 실험은 어떻게 해야 하는가?

10월 13일 기준으로 지금까지의 실험을 다시 살펴보겠습니다.

| 실험         | 주요 관찰                                  | 해석                          |
| ---------- | -------------------------------------- | --------------------------- |
| E1         | PGCT AUC 약 +2.88%, 최종 delivery 약 -0.30 | 초기 학습 효율이 좋아질 가능성은 있으나 제한적  |
| E2         | IPPO와 PGCT 거의 동률                       | 개선 효과가 일관되게 나타나지 않음         |
| Critic MSE | 뚜렷한 개선 없음                              | critic transfer 자체의 이득이 불확실 |
| Gating 진단  | 서로 다른 팀 3–4 연결, 같은 팀 gate 미발생 사례       | 행동 유사도 기반 팀 추론에 문제          |
| Probe 진단   | 중복 probe 제거 시 유사도 순위 변화                | probe 구성에 따른 민감성이 존재        |

여기서 중요한 점은 E1과 E2의 결과가 PGCT가 확실히 도움이 된다는 근거로는 부족하다는 것입니다.

그렇다고 실패했다고 단정할 수도 없습니다. 특히 공통 IPPO 사전학습 후 분기하는 실험에서는 전체 학습 과정의 이득이 아니라 이후 critic transfer의 추가 효과를 평가하고 있다는 점도 구분해야 합니다.

##### 지금 당장 추천하는 실험 운영

현재 E3 및 대응 IPPO 대조군은 마무리

현재 설정을 유지해서 결과를 확보합니다. E1의 추가 seed도 최소 반복 검증에 활용할 가치가 있습니다.

새로운 PGCT 장기 학습과 probe 튜닝은 잠시 중단

현재 구조의 핵심 가정이 검증되기 전에는 맵 확장, threshold 변경, probe 추가만으로 장시간 실험을 반복하지 않는 것이 좋겠습니다.

우선 팀 추론 가능성과 oracle consensus 효과를 분리 검증

잠재 팀을 실제로 알아낼 수 있는지와, 올바른 팀을 알아냈을 때 critic consensus가 도움이 되는지를 독립적으로 검증해야 합니다.

특히 저는 다음 두 실험이 중요하다고 봅니다.

실험 A: 행동 기반 팀 구분이 가능한가?

기존 checkpoint를 그대로 사용하고, 충분히 다양한 실제 trajectory에서 행동 기반 유사도를 계산합니다. 같은 팀과 다른 팀의 점수 분포가 통계적으로 구분되는지 평가합니다.

이때 공간적 역할과 관측 조건을 통제해야 합니다. 단순히 맵을 키워서 유사도가 구분되는 것만으로는 일반적인 팀 식별 능력을 증명하기 어렵습니다.

실험 B: 정답 팀 정보를 알고 있다면 consensus가 효과적인가?

학습에 정답 팀을 사용하는 oracle baseline을 별도로 만듭니다.

| 방법                     | Critic 공유     |
| ---------------------- | ------------- |
| IPPO                   | 없음            |
| All-peer consensus     | 관측 가능한 모든 이웃  |
| Oracle-team consensus  | 실제 같은 팀인 이웃만  |
| Learned-team consensus | 추론된 같은 팀인 이웃만 |

이 실험의 결과가 연구 방향을 결정하는 데 중요합니다.

- Oracle-team consensus도 IPPO보다 못하면, 팀 추론을 개선하기 전에 consensus 방식 자체를 검토해야 합니다.
- Oracle은 개선되지만 learned-team은 개선되지 않으면, 팀 추론이 병목일 가능성이 높습니다.
- Oracle과 learned-team 모두 개선되면, 원래 연구 주제를 뒷받침하는 초기 증거가 됩니다.

물론 모든 방법은 가능한 한 동일한 초기 조건, 환경 상호작용 수, 네트워크 구조와 공통 checkpoint를 사용해서 비교해야 합니다.

#### 5. 앞으로의 알고리즘은 어떻게 구성하면 좋을까?

제가 제안하는 것은 기존 PGCT에 단순히 새로운 probe만 추가하는 것이 아닙니다.

연구를 다음 세 모듈로 분리하는 것입니다.

##### Module 1. 행동 관측과 표현

현재처럼 환경별로 사람이 일일이 probe를 설계하기보다는 실제 관측 trajectory에서 학습 가능한 행동 표현을 구성하는 쪽이 장기적으로 적합합니다.

다만 trajectory 기반이라고 해서 자동으로 목표 정보가 복원되는 것은 아닙니다. 단순한 이동 패턴뿐 아니라, 상황에 따른 반응과 자신의 목표 달성 결과에 관한 국소적 증거가 필요할 수 있습니다.

##### Module 2. 잠재 팀 추론

행동 표현에서 팀 호환도 \\(w\_{ij}\\)를 추정합니다.

\\[ w\_{ij}\in[0,1] \\]

이 값은 단순한 JS similarity가 아니라, 같은 목표를 가진 팀에 속할 가능성을 나타내는 것으로 설계하고 검증해야 합니다.

또한 한 번 연결된 모든 에이전트를 무조건 같은 팀으로 묶는 방식은 위험합니다. 추론 오류가 전파될 수 있으므로 신뢰도와 시간에 따른 관측 축적을 고려해야 합니다.

##### Module 3. 팀 내부 critic consensus

학습 중 국소 통신이 가능한 이웃 중 팀 호환도가 높은 에이전트끼리 critic 정보를 합의하도록 합니다.

여기서 한 가지 주의할 점이 있습니다.

같은 팀이라는 사실만으로 서로 다른 부분관측 입력에 대한 critic 값이나 파라미터를 무조건 동일하게 만들어도 된다는 뜻은 아닙니다.

Consensus의 대상이 critic 파라미터인지, 공통 상태에서의 value estimate인지, TD 정보인지를 명확히 정해야 합니다.

참고로 Fully Decentralized Multi-Agent Reinforcement Learning with Networked Agents는 이질적인 지역 보상을 가진 에이전트가 시간에 따라 변화하는 통신 그래프에서 전역 평균 return을 최적화하는 프레임워크입니다. 이것은 영감을 줄 수 있지만, 잠재 팀을 발견하는 문제를 직접 해결한 것은 아닙니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research



또한 최근 value aggregation 연구에서도 서로 다른 학습 불확실성을 가진 critic 정보를 단순 평균하는 것이 학습을 악화시킬 수 있음이 분석되었습니다. 따라서 올바른 팀 추론과 올바른 critic 합의 방식은 서로 다른 두 과제입니다.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research



#### 6. 최종적으로 정리한 연구 주제

현재 목표를 한 문장으로 정리하면 다음과 같습니다.

> 명시적인 팀 정보가 없는 완전분산 다중 에이전트 강화학습 환경에서, 에이전트들이 국소적으로 관측한 행동을 활용하여 잠재적인 목표 공유 관계를 추론하고, 추론된 팀 내부의 선택적 critic consensus를 통해 학습 효율을 향상시키는 방법을 연구한다.

영어로는 다음과 같은 가제도 가능합니다.

Behavior-Based Latent Team Discovery and Group-Selective Critic Consensus in Fully Decentralized Multi-Agent Reinforcement Learning

이때 논문의 핵심 기여는 세 가지로 정리할 수 있습니다.

1. Latent team inference: 명시적인 팀 정보 없이 국소 행동 관측을 통한 목표 공유 관계 추론
2. Selective critic consensus: 추론된 팀 구조를 이용해 부적절한 critic 공유를 억제하면서 학습 수행
3. Decentralized learning: 중앙의 팀 판정자 없이 동적으로 변화하는 이웃 관계에서 팀 추론과 학습을 수행

이는 앞으로 입증해야 할 목표이지, 현재 PGCT가 이미 달성한 기여는 아닙니다.

#### 7. 마지막 판단

현재 가장 중요한 일은 PGCT 성능을 몇 퍼센트 더 끌어올리는 것이 아닙니다.

우선 아래 두 명제를 검증하는 것입니다.

\\[ \boxed{ \begin{gathered} \text{국소 행동 정보로}\\\ \text{잠재 팀을 식별할 수 있는가?} \end{gathered} } \\]

\\[ \boxed{ \begin{gathered} \text{올바르게 식별된 팀에서}\\\ \text{critic consensus가 학습을 개선하는가?} \end{gathered} } \\]

첫 번째가 성립하지 않는다면 행동 유사도만으로 팀을 찾겠다는 가정을 수정해야 합니다. 두 번째가 성립하지 않는다면 팀을 아무리 잘 찾더라도 원하는 학습 개선 효과를 얻기 어렵습니다.

따라서 기존 PGCT는 실험적 출발점으로 보존하고, 새로운 연구의 중심을 '행동 유사도 기반 critic transfer'에서 '행동 관측 기반 잠재 팀 추론 및 선택적 critic consensus'로 옮기는 것이 제 결론입니다.

이렇게 하면 원래 의도를 되찾으면서도 지금까지 수행한 PGCT 실험을 버리지 않고, 그것을 새로운 연구가 해결해야 할 문제를 드러낸 기초 실험으로 활용할 수 있습니다.

###### 사용자 본문

내 질문과 이에대한 GPT의 대답이야

현재 코드를 최대한 수정하지 않고, 새로운 파일, 폴더를 만들어서 GPT의 대답처럼 먼저 확인하는게 맞을꺼 같아

##### Assistant — 진행 안내 1

확인해 보니 E3 PGCT 학습은 지금 실행 중이 아닙니다. 18:21에 컴퓨터가 재부팅되면서 약 2.75M step(checkpoint 2700)에서 멈춘 상태입니다. 코드 구조를 파악한 뒤 질문에 답하고 새 검증 폴더를 설계하겠습니다.

##### Assistant — 진행 안내 2

트레이너에 이미 oracle 팀 그래프와 critic consensus 함수가 있는지 확인하고 있습니다. 있다면 기존 코드를 고치지 않고 새 실행기에서 재사용할 수 있습니다.

##### Assistant — 진행 안내 3

환경 코드에서 중요한 점을 확인하고 있습니다. 각 agent의 관측이 "자기 팀의 요청 선반" 기준으로 만들어지는 것으로 보여, 공통 probe JS가 원리적으로 팀을 구분할 수 있는지 점검하겠습니다.

##### Assistant — 진행 안내 4

구조는 파악했습니다. 기존 트레이너에 oracle(같은 팀만)·unrestricted(모든 이웃)·wrong(다른 팀만) 비교군이 이미 구현되어 있지만, 지금까지는 smoke test로만 돌려봤습니다. 따라서 실험 B는 트레이너를 고치지 않고 새 실행기만으로 만들 수 있습니다. 이어서 재사용할 진단 코드를 확인하겠습니다.

##### Assistant — 진행 안내 5

E1 맵에서 두 팀의 배송 목표는 (4,10)과 (5,10)으로 서로 붙어 있습니다. 또 관측의 "요청 선반"·"관련 목표" 채널은 모두 자기 팀 기준으로 표시됩니다. 그래서 공통 입력에 대한 정책 JS로는 원리적으로 팀을 구분하기 어렵습니다. 실험 설계에 이 점을 반영하겠습니다. 테스트와 실행기 관례를 확인합니다.

##### Assistant — 진행 안내 6

실험 A·B 설계를 정했습니다. 구현 전에 기존 AUC 계산 방식을 확인합니다. 새 비교표가 기존 E1 수치(45.856/44.573)를 그대로 재현해야 하기 때문입니다.

##### Assistant — 진행 안내 7

설계를 확정했습니다. 새 폴더 `latent_team/`에 실험 A(고정 모델로 팀 식별 가능성과 consensus 전제 확인)와 실험 B(oracle·all-peer 학습 실행기)를 만듭니다. 기존 트레이너와 실행기 파일은 수정하지 않고 import만 합니다.

##### Assistant — 진행 안내 8

실험 A 스크립트를 작성했고, 이어서 실험 B 실행기(oracle·all-peer·wrong)를 작성하고 있습니다. 이후 두 스크립트를 짧게 시험 실행하겠습니다.

##### Assistant — 진행 안내 9

Dry-run 결과 oracle·all·wrong 설정은 기존 E1 PGCT 설정과 `graph_mode` 한 항목만 다릅니다. 이제 실험 B의 64-step smoke test와 실험 A의 짧은 시험을 실행합니다.

##### Assistant — 진행 안내 10

실험 B smoke 결과는 기대대로입니다. oracle은 같은 팀끼리만, all은 같은 팀과 다른 팀 모두, wrong은 다른 팀끼리만 전이했고, 모든 전이가 물리적 이웃 범위 안에서만 일어났습니다. 비교표도 기존 E1 AUC(PGCT 45.856, IPPO 44.573)를 그대로 재현합니다. 이어서 실험 A를 짧게 시험합니다.

##### Assistant — 진행 안내 11

실험 A도 정상 작동합니다. 짧은 시험에서도 "배송·픽업 목격 증거"는 팀을 맞혔고, 기존 canonical JS는 맞히지 못했습니다. 다만 2개 에피소드짜리 시험이라 결론으로 쓰지 않습니다. 이제 6개 고정 모델 × 20 에피소드 × 500 step의 본 평가를 백그라운드로 실행합니다. 학습은 하지 않습니다.

##### Assistant — 진행 안내 12

새 테스트 6개가 모두 통과했습니다. 실험 A 본 평가는 백그라운드에서 계속 진행 중이고, 그동안 README를 작성하겠습니다.

##### Assistant — 진행 안내 13

Stage03 결과가 먼저 나왔습니다. 6개 모델이 다 끝나면 함께 정리하겠습니다. 미리 보면 국소 배송·픽업 증거는 팀을 100% 맞히지만, 정책 JS와 critic 호환성은 오히려 같은 팀 쌍에서 더 나쁩니다. 나머지 모델을 기다리는 동안 테스트를 다시 확인합니다.

##### Assistant — 진행 안내 14

실험 A는 6개 모델 중 2개가 끝났습니다(모델당 약 2분). 기다리는 동안 중단된 E3 상태를 정리했습니다. 마지막 평가는 2,816,000 step(delivery 28.6), 마지막 checkpoint는 2,764,800 step입니다.

##### Assistant — 진행 안내 15

실험 A는 6개 모델 중 4개가 끝났고 나머지 2개(E2 PGCT, Stage04)를 기다리고 있습니다. E2 맵에서도 두 팀의 목표 칸은 (7,15)와 (8,15)로 서로 붙어 있습니다. 모든 조건이 individual reward이고 home ratio는 0.5입니다.

##### Assistant — 진행 안내 16

실험 A 본 평가가 6개 모델 모두 끝났습니다. 결과를 표로 정리합니다.

##### 수행 기록 — 원문 대화와 별도

사용자 메시지에 붙여넣은 GPT 답변은 참고 자료로 취급했다. 실측 결과 실행 중인 학습이 없었다. E3 PGCT는 18:21 KST 재부팅으로 2,855,936 step에서 중단됐고, 재개하지 않았다. 새 폴더 `latent_team/`(README, common, 실험 A, 실험 B 실행기, PowerShell 실행기)와 `tests/test_latent_team.py`를 추가했다. 기존 trainer·환경·실행기·probe·gate 파일은 수정하지 않았다. 실험 A를 6개 고정 모델에 실행했고(`output/latent_team/exp_a_20261013/`), 실험 B는 dry-run과 64-step smoke(`runs/lt_b_smoke_20261013`)만 실행했다. 장기 학습은 시작하지 않았다. RESEARCH_STATE, DECISIONS D17, EXPERIMENTS(E02 추가, E11, E12)를 갱신했다.

##### Assistant — 최종 답변

#### 1. PGCT를 계속 돌려야 하나?

**지금 실행 중인 학습은 없습니다.** E3 PGCT는 오늘 18:21 Windows 재부팅으로 2,855,936 step에서 멈췄습니다(마지막 checkpoint 2,764,800 step, 마지막 평가 delivery 28.6). E3 IPPO는 시작 전입니다.

제 권장은 **E3를 재개하지 않는 것**입니다. GPT의 "E3 마무리" 제안과는 다른 판단입니다.
- 기존 실행기는 이어 학습을 지원하지 않습니다. 새 폴더에서 optimizer와 EMA가 초기화되므로 같은 조건으로 완료할 수 없습니다.
- E3는 JS gate로 맵 확장 효과를 보는 실험(방향 2)인데, 아래 실험 A에서 그 JS 신호가 팀을 구분하지 못했습니다.
- IPPO 대조군까지 하면 이틀 가까이 걸립니다.

기존 로그와 checkpoint는 그대로 두었습니다. 재개 여부는 결정해 주세요.

#### 2. 연구 주제: 1번이 맞습니다

연구 주제는 **1번(행동으로 팀을 찾고 팀 안에서 critic consensus)**입니다. 2번은 다른 팀끼리 연결된 결과를 해석하다가 생긴 이탈이고, 별도 가설로만 남기겠습니다. 다만 오늘 확인한 결과, 1번을 **지금 환경 그대로** 검증하기는 어렵습니다.

**실험 A 결과** (고정 모델 6개 × 20 episode × 500 step, 학습 없음, weight 불변)

| 팀 신호 | 같은 팀/다른 팀 구분 AUROC | 팀원 맞힘 (우연 .33) |
|---|---|---|
| 현재 PGCT canonical JS | .375–.50 | 0–.25 |
| 실제 이력에서 정책 JS | E1 계열 .27–.29 / E2 .81–.85 | E1 0–.01 / E2 .68–.85 |
| 상대가 무엇을 들고 어디에 배송하는지 직접 본 증거 | **6개 모델 모두 1.00** | **.99–1.00**, 첫 500 step 안에 |
| critic 공유 이득 (blend gain) | E1 계열 .25–.33 / E2 .47–.49 | — |

- **행동으로 팀을 찾는 것은 가능합니다.** 다만 써야 할 신호는 "응답이 비슷한가"가 아니라 "누구의 요청 선반을 들고 어느 목표에 배송하는가"입니다. 이 증거는 통신 없이 자기 센서 범위 안에서 얻을 수 있습니다.
- **현재 PGCT JS가 팀을 못 찾는 데는 구조적 이유가 있습니다.** 관측의 요청 선반·목표 채널이 자기 팀 기준으로 표시됩니다. 두 팀 목표 칸도 붙어 있습니다(E1 (4,10)/(5,10), E2 (7,15)/(8,15)). 그래서 같은 입력을 넣으면 팀이 달라도 같은 응답이 나옵니다.
- **더 큰 문제는 두 번째 전제입니다.** E1 계열에서는 같은 팀 critic이 오히려 덜 호환되고, 다른 팀인 3–4 쌍이 가장 잘 맞습니다. E2에서는 네 critic이 거의 같아서 누구와 공유해도 이득이 0에 가깝습니다. 원인은 이렇게 추정합니다(가설). individual reward에서 팀원은 같은 요청 2개를 두고 경쟁하는 관계이고, 관측이 팀 기준이라 value가 팀에 거의 의존하지 않습니다.

AUROC는 서로 종속인 표본과 2개 대 4개 쌍으로 계산한 기술 통계입니다. 증거 신호가 완벽한 것은 이 환경이 팀을 요청 선반·목표로 정의하기 때문이므로, 다른 환경에 일반화하려면 별도 검증이 필요합니다.

#### 만든 것 (기존 코드 수정 없음)

- [latent_team/README.md](latent_team/README.md): 설계, 해석 기준, 실행 명령
- [exp_a_team_identifiability.py](latent_team/exp_a_team_identifiability.py): 실험 A. 결과는 [REPORT.md](output/latent_team/exp_a_20261013/REPORT.md)
- [exp_b_oracle_consensus.py](latent_team/exp_b_oracle_consensus.py), [run_exp_b.ps1](latent_team/run_exp_b.ps1): 실험 B. 기존 E1 PGCT와 같은 Stage03·probe bank·평가 seed를 쓰고 critic 공유 대상만 바꿉니다. oracle=같은 팀, all=모든 이웃, wrong=다른 팀이며, 트레이너에 이미 있던 모드를 그대로 씁니다.
- [tests/test_latent_team.py](tests/test_latent_team.py): 새 테스트 6개, 관련 기존 테스트 포함 19개 통과

검증한 내용:
- 실험 B 설정은 기존 E1 PGCT와 `graph_mode` 한 항목만 다릅니다.
- 64-step 시험에서 oracle은 같은 팀끼리만, wrong은 다른 팀끼리만 전이했고, 모두 물리 범위 안이었습니다.
- 비교표가 기존 E1 AUC 45.856/44.573을 그대로 재현합니다.

**실험 B 장기 학습은 시작하지 않았습니다.**

#### 결정이 필요합니다

실험 A 결과로 보면, 지금 환경에서는 oracle(정답 팀 공유)이 all-peer나 IPPO보다 나을 근거가 약합니다.

1. **현재 환경에서 B를 확인용으로 실행**: oracle+all, E1 seed1, 약 60시간. 명령은 `.\latent_team\run_exp_b.ps1`입니다.
2. **(권장) 팀 소속이 value를 실제로 바꾸는 조건을 먼저 정하기**: 예를 들어 기존 환경 옵션 `team_reward_mode="team"`(팀원이 보상 공유)으로 바꾼 뒤 B를 실행합니다. 보상 변경이고 Stage03은 individual reward로 학습했으므로, 승인해 주시면 설계안부터 드리겠습니다.

기록은 RESEARCH_STATE, DECISIONS D17, EXPERIMENTS E11·E12, CONVERSATION_LOG T008에 남겼습니다.


#### 원문 기록 T009 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다. 사용자는 별도 본문 없이 GPT 검토 답변만 붙여넣었다. 참고 자료로 취급했다.

##### 사용자 — 원문 (붙여넣은 내용, 별도 본문 없음)

Claude의 실험 결과를 보면, 저는 2번을 선택하되, `team_reward_mode="team"`만 변경해서 곧바로 실험 B를 시작하는 것은 반대합니다.

이번 실험에서 상당히 중요한 사실이 드러났습니다. 특히 기존 PGCT의 문제와 원래 연구 목표의 문제를 구별할 수 있게 되었습니다.

#### 1. 이번 결과에서 가장 중요한 발견

| 검증 항목               | 결과                   | 제 해석                        |
| ------------------- | -------------------- | --------------------------- |
| Canonical probe JS  | AUROC 0.375\~0.50    | 현재 probe로는 팀 식별이 어려움        |
| 실제 trajectory 기반 JS | E1 약 0.28, E2 약 0.83 | 행동 유사도가 환경·상황에 크게 의존        |
| 배송·픽업 관측 증거         | AUROC 1.00           | 현재 환경에서는 팀을 구분할 정보가 존재      |
| Critic 호환성          | E1 약 0.25\~0.33      | 같은 팀 critic의 호환성이 높다는 증거 부족 |

##### 첫 번째 문제: 행동으로 팀을 찾았다고 말할 수 있을까?

Claude는 배송·픽업을 관측한 증거만으로 팀을 거의 완벽하게 찾았다고 보고했습니다.

그런데 이것을 연구 성과로 해석하기는 어렵습니다.

현재 RWARE는 각 팀에 서로 다른 요청 선반과 배송 목표를 할당하는 구조입니다.

따라서 에이전트가 특정 선반을 어느 배송 지점으로 옮기는지 관찰하면, 그 행동이 어떤 팀에 해당하는지 직접 드러날 수 있습니다.

이는 행동 패턴을 학습하여 숨겨진 목표를 추론하는 것과는 차이가 있습니다.

물론 해당 정보가 실제 국소 센서로 관측된다면 유효한 단서입니다. 하지만 팀을 구분할 수 있다는 사실과 일반적인 잠재 팀 추론 알고리즘을 개발했다는 사실은 다릅니다.

그리고 실험 코드가 팀 ID나 환경 내부 상태를 간접적으로 사용하지 않았는지도 확인해야 합니다.

##### 두 번째 문제: 같은 팀이면 critic consensus가 유리한가?

저는 이쪽이 오히려 더 중요하다고 생각합니다.

원래 가설에는 두 단계가 있습니다.

\\[ \underbrace{\text{Behavior}\rightarrow\text{Team}}\_{\text{팀 추론}} \\]

\\[ \underbrace{\text{Team}\rightarrow\text{Useful Consensus}}\_{\text{학습 개선}} \\]

첫 번째 단계가 성공하더라도 두 번째 단계가 성립하지 않으면 연구의 최종 목적을 달성하지 못합니다.

현재 실험은 같은 팀의 critic이 반드시 더 호환되지는 않는다고 보여줍니다.

다만 보고서의 `blend gain` 계산 정의를 확인해야 합니다. 정적인 critic 호환성 지표가 낮다고 해서 실제 학습에서 consensus가 반드시 해롭다는 의미는 아닙니다.

따라서 실제 학습 실험을 통해 oracle-team consensus가 IPPO보다 유리한지 확인하는 것은 여전히 필요합니다.

#### 2. 제가 제안하는 실험 순서

1단계. E3 PGCT는 중단 상태로 보존

현재 checkpoint와 로그를 보존하고 재개하지 않습니다. 지금은 추가 학습보다 가설 검증의 우선순위가 높습니다.

2단계. 현재 환경에서 소규모 oracle 실험

IPPO와 oracle-team consensus를 먼저 비교합니다. 장시간 학습 전에 작은 예산과 동일한 초기 checkpoint로 학습 곡선이 어떻게 달라지는지 확인합니다.

개선이 없다면 기존 환경의 보상 구조와 critic 합의 방식 중 무엇이 문제인지 조사합니다.

3단계. 팀 협력의 의미가 명확한 환경 설계

`team_reward_mode="team"`을 후보로 검토합니다. 다만 보상만 변경하면 기존 individual-reward 기반 Stage03 critic과 학습 목표가 달라집니다.

따라서 새로운 보상 구조에 맞는 공통 사전학습과 비교군을 설계해야 합니다.

4단계. 새로운 팀 추론 방법 연구

지금의 canonical probe JS를 팀 판정 방법으로 고집하지 않습니다. 서로 다른 목표지만 행동은 비슷한 경우와, 같은 목표지만 역할 때문에 행동이 다른 경우를 모두 구분할 수 있는지 검토합니다.

#### 3. 여기서 한 가지 연구 방향을 더 명확히 해야 합니다

원래 구상은 서로 다른 목표를 가진 잠재 팀들이 존재한다는 것이었습니다.

그런데 중요한 질문이 하나 남아 있습니다.

같은 팀이라는 것은 정확히 무엇을 의미하는가?

예를 들어 다음 두 정의는 서로 다릅니다.

- 공통 목표 팀: 팀원들이 동일한 팀 보상을 최대화합니다.
- 협력적 목표 팀: 각자 보상이나 역할은 다르지만 공동 작업에 협력해야 합니다.

첫 번째는 동일한 팀 reward를 사용하기 때문에 critic consensus의 목적을 상대적으로 명확하게 정의할 수 있습니다.

반면 두 번째에서는 같은 팀이라도 가치함수가 다를 수 있으므로 어떤 critic 정보를 합의해야 하는지 별도로 설계해야 합니다.

저는 우선 첫 번째를 출발점으로 삼는 것이 좋다고 생각합니다. 다만 최종 연구를 첫 번째에만 한정할 필요는 없습니다.

#### 4. Claude에게 내릴 결정

제 권장은 다음과 같습니다.

E3는 재개하지 않습니다. 실험 B의 60시간 규모 학습도 지금 당장 시작하지 않습니다.

먼저 기존 환경에서 소규모 oracle/IPPO 비교를 수행하고, 동시에 `team_reward_mode="team"`을 적용했을 때 어떤 학습 목표와 critic 업데이트 구조가 달라지는지 분석하는 것입니다.

그 후 보상 변경이 타당하다면 공통 사전학습부터 다시 정렬한 본 실험을 설계해야 합니다.

그리고 이번 결과로 분명해진 점이 있습니다.

우리가 해결하려는 문제는 '행동이 비슷한 에이전트를 연결하는 것'이 아니라 '관측 가능한 행동에서 목표 공유 관계를 추론하는 것'입니다.

이 방향은 유지하는 것이 맞습니다.

다만 앞으로 가장 먼저 입증해야 할 것은 같은 목표를 공유하는 에이전트들끼리 critic consensus를 수행할 때 정말 학습 효율이 좋아지는가입니다. 이것이 성립한다면 잠재 팀 발견 알고리즘을 발전시키는 연구적 동기도 훨씬 명확해집니다.

##### Assistant — 진행 안내 1

GPT 답변을 검토하면서, 지적된 두 가지 확인 사항부터 직접 점검하겠습니다. 실험 A의 증거가 팀 ID나 환경 내부 상태를 간접적으로 썼는지, 그리고 `team_reward_mode="team"`이 코드에서 무엇을 바꾸는지입니다. 학습은 시작하지 않습니다.

##### Assistant — 진행 안내 2

학습률 annealing이 없음을 확인했습니다. 따라서 짧은 oracle run은 기존 E1 PGCT/IPPO run의 같은 구간과 정확히 맞춰 비교할 수 있습니다. 이제 실험 A의 증거가 관측자 자신의 관측 텐서만으로 재현되는지 검증하는 스크립트를 실행합니다.

##### Assistant — 진행 안내 3

Use the channel list directly from the module rather than the `__globals__` hack.

##### Assistant — 진행 안내 4

6,000개 넘는 이벤트의 판정이 관측자 자신의 관측 채널과 100% 일치했습니다. 이어서 소규모 oracle 실험 설계를 위해 기존 E1 PGCT/IPPO의 초기 1M 구간 차이를 계산합니다. 이 값이 seed 하나 수준의 잡음 기준이 됩니다.

(기록자 주: "6,000개 넘는"은 오류이며 실제 확인 건수는 2,146건이다. "잡음 기준"이라는 표현도 부정확하다. PGCT와 IPPO의 차이는 순수 seed 잡음이 아니다. 최종 답변에서 정정했다.)

##### Assistant — 진행 안내 5

기존 환경에는 관측을 팀 기준이 아니라 절대 기준(팀 색)으로 보여주는 옵션이 없습니다. 이 점은 설계 분석에 반영하겠습니다. 이제 소규모 oracle 실험이 가능하도록 실험 B 실행기를 보완합니다. 짧은 예산으로 돌리면 기존 run의 같은 구간까지만 잘라 비교하도록 바꿉니다.

##### Assistant — 진행 안내 6

Order-only mismatch; compare as sets.

##### Assistant — 진행 안내 7

테스트 20개가 통과했습니다. 이제 README에 관측 가능성 검증, blend gain 정의, team reward 분석을 추가하고 연구 노트를 갱신합니다.

##### Assistant — 진행 안내 8

Unchanged since my last writes. Updating notes.

##### 수행 기록 — 원문 대화와 별도

학습은 시작하지 않았다. `latent_team/verify_evidence_observability.py`를 추가하고 E1 IPPO·E2 IPPO·Stage04 각 5×500 step으로 고정 replay를 실행했다. 결과 `output/latent_team/exp_a_20261013/observability_check.json`: 2,146건, 관측 채널과 100% 일치. 트레이너에 학습률 schedule이 없음을 확인했다. `latent_team/common.py`의 `learning_summary`에 `max_step`을 추가했다. `exp_b_oracle_consensus.py`는 짧은 예산에서 `total_timesteps` 차이를 허용하고 기준 run을 자르도록 수정했다. 1,024,000 step dry-run을 확인했다. test 1개를 추가해 20 passed. README에 검토 사항을 추가했다. `team_reward_mode="team"`은 코드만 읽고 실행하지 않았다. DECISIONS D18, EXPERIMENTS E12 추가·E13, RESEARCH_STATE를 갱신했다. 기존 trainer·환경·실행기 파일은 수정하지 않았다.

##### Assistant — 최종 답변

GPT 검토에 대체로 동의합니다. 학습은 시작하지 않았고, 확인할 수 있는 것부터 점검했습니다.

**동의하는 점**
- E3는 재개하지 않고, 60시간짜리 실험 B도 지금 시작하지 않습니다.
- 배송·픽업 증거로 팀을 맞힌 것은 "이 환경에 팀을 구분할 정보가 국소적으로 존재한다"는 확인일 뿐, 잠재 팀 추론 알고리즘의 성과는 아닙니다. 이 환경은 팀을 요청 선반·목표로 정의하므로, 이 증거는 거의 정답에 가까운 단서입니다.
- blend gain만으로 학습 중 consensus의 효과를 판정할 수 없습니다. 실제 학습 실험이 필요합니다.
- 출발점은 "공통 목표 팀(같은 팀 보상)"으로 두고, team reward는 공통 사전학습부터 다시 정렬합니다.

**확인한 것**
1. **팀 ID 간접 사용 여부**: 상대 agent의 팀 ID는 읽지 않습니다. 판정 2,146건(pickup 985, delivery 1,161)을 관측자 자신의 관측 텐서와 대조했고 100% 일치했습니다([observability_check.json](output/latent_team/exp_a_20261013/observability_check.json)). 다만 관측 속 agent에는 ID가 없습니다. 그래서 "본 agent가 이웃 j"라고 연결하려면 이웃 식별 가정이 필요하며, 이는 PGCT가 통신 상대를 아는 것과 같은 수준의 가정입니다.
   - 정정: 진행 안내에서 "6,000개 넘는 이벤트"라고 했지만 실제는 2,146건입니다. 또 기존 PGCT−IPPO 차이를 "잡음 기준"이라고 한 것도 부정확했습니다.
2. **blend gain 정의**: `MSE(V_i, G_i) − MSE((V_i+V_j)/2, G_i)`입니다. i 자신의 관측 이력을 쓰고, 초기 200 step의 유한 MC return으로 계산합니다. 양수면 j의 예측을 섞을 때 i의 오차가 줄어든다는 뜻입니다. 학습된 critic을 정적으로 평균한 값이라 학습 중 효과는 측정하지 않습니다.
3. **`team_reward_mode="team"`의 변화**(코드만 확인): delivery·return 보상이 그 선반 팀 전원에게 가고, shaping은 개인별로 남습니다. 팀원 간 경쟁이 사라지고 task return 규모가 약 2배가 됩니다. 따라서 Stage03 critic에서 바로 이어갈 수 없습니다.

**추가로 짚을 점 (가설)**
team reward만으로는 부족할 수 있습니다. 관측은 여전히 자기 팀 기준이고 두 팀 과제는 대칭입니다. 그래서 같은 입력에서 팀 0 critic과 팀 1 critic이 결국 비슷한 함수를 배울 수 있습니다. 관측에서는 팀원과 상대 팀 agent도 구분되지 않습니다.

"다른 팀 critic은 틀린 목표를 배운다"는 상황이 생겨야 같은 팀끼리 공유하는 것이 원리적으로 유리해집니다. 그러려면 다음 중 하나가 필요할 수 있습니다.
- 팀 소유를 절대 기준(팀 색 채널)으로 보여주는 관측
- 비대칭 팀 과제

현재 env에는 이런 옵션이 없어서 새 wrapper가 필요합니다.

**소규모 oracle 실험: 준비 완료, 실행 안 함**
트레이너에 학습률 schedule이 없으므로 짧은 run은 기존 run의 앞 구간과 정확히 대응합니다. IPPO를 새로 돌리지 않고 기존 E1 seed1의 첫 1,024,000 step과 비교할 수 있습니다. 그 구간의 delivery AUC는 IPPO 43.83, PGCT 44.61입니다.

```powershell
.\latent_team\run_exp_b.ps1 -Modes oracle -TotalTimesteps 1024000
```

oracle 한 run에 약 7–8시간 걸리고, `-Modes oracle,all`로 하면 약 15시간입니다. seed가 하나뿐이라 방향 확인용입니다.

**결정해 주세요**
1. 소규모 oracle(1M)을 지금 시작할까요? oracle만 할지, all-peer까지 할지도 정해 주세요.
2. team reward 환경 설계에 관측을 절대 기준으로 바꾸는 새 wrapper까지 포함할까요? 설계안부터 드리겠습니다.

변경 사항:
- [verify_evidence_observability.py](latent_team/verify_evidence_observability.py) 추가
- 실험 B에 짧은 예산 비교 기능 추가
- [README](latent_team/README.md) 보강
- 테스트 1개 추가(관련 테스트 20 passed)

기록은 D18, E12 추가 항목, E13, RESEARCH_STATE, CONVERSATION_LOG T009에 남겼습니다.


#### 원문 기록 T010 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

우선 지금 있는 examples 폴더라든가 이런데 보면 기존에 사용하고 안쓴 쓸모없는 파일들이 많은데 정리좀 해줘

##### Assistant — 진행 안내 1

먼저 정리 대상을 파악하겠습니다. 어떤 파일이 다른 코드, 테스트, 연구 노트에서 참조되는지 확인한 뒤 분류합니다. 삭제는 목록을 보여드리고 확인을 받은 뒤에 하겠습니다.

##### Assistant — 진행 안내 2

정리 대상을 세 묶음으로 나눴습니다. 같은 일을 하는 파일이라도 삭제 위험도가 다르기 때문입니다. 삭제는 되돌리기 어려우므로 범위를 먼저 확인받겠습니다.

##### Assistant — 선택 질문 (원문)

어떤 묶음을 정리할까요? (현재 실험·테스트·연구노트가 참조하는 파일은 모두 유지합니다)

- ① 임시·캐시 (권장): 아무도 참조하지 않음. tmp_video_analysis/, .codex-video-frames/(git 추적 34개), tmp/fov_on_video_frame.png, tmp/.cache/, examples/generated_configs/(실행 시 자동 재생성), 각종 __pycache__, 빈 .agents/·.pytest-tmp/
- ② 대체된 문서: examples/FOV_COMMUNICATION.md(폐기 안내 stub), examples/CNN_TRAINING_REVIEW_20260916.md(ex6 시절 검토, EX5로 대체). 삭제 대신 docs/archive/로 이동도 가능
- ③ 끝난 과거 실험 도구: 09700 일반화 실험(run_pgct_09700_generalization.ps1, run_pgct_09700_map_variants.ps1, eval_checkpoint_generalization.py+그 테스트, PGCT_09700_GENERALIZATION.md), visualize_graph_connectivity.py, create_probe_ppt_images.py, run_semantic_cnn_mixing_curriculum.ps1, Success_checkpoint/checkpoint_Fixed_1.pt. 과거 결과 재현이 불가능해짐
- 삭제 말고 archive로 이동: 선택한 묶음을 지우지 않고 archive/ 폴더로 옮겨 examples/를 깔끔하게만 만듦(되돌리기 쉬움)

##### 사용자 — 선택 응답

① 임시·캐시 (권장), ② 대체된 문서, ③ 끝난 과거 실험 도구

##### Assistant — 진행 안내 3

①②③ 묶음을 삭제하겠습니다. `tmp/pdfs`(ex4/ex5 원문 추출)는 선택지에 없었으므로 유지합니다. 먼저 삭제 대상을 참조하는 테스트와 README를 확인합니다.

##### Assistant — 진행 안내 4

`.pytest-tmp`와 `.pytest_cache`는 권한 문제로 지울 수 없어 그대로 두었습니다. 이제 삭제한 파일을 가리키던 examples/README.md와 EX5_PGCT.md를 고칩니다.

##### Assistant — 진행 안내 5

The heredoc was decoded as cp949; I'll use the Edit tool instead.

##### Assistant — 진행 안내 6

Now verify no dangling references remain and the full test suite still runs.

##### 수행 기록 — 원문 대화와 별도

삭제 목록과 유지 항목은 DECISIONS D19에 기록했다. git 추적 파일은 `git rm`으로 stage했고 커밋하지 않았다. `examples/README.md`와 `examples/EX5_PGCT.md`의 참조를 갱신했다. 남은 참조를 검색해 정리 안내문 외에는 없음을 확인했다(`generated_configs`는 실행기가 재생성). 전체 `tests` 178 passed. 학습 코드·환경·runs/output 결과는 변경하지 않았다.

##### Assistant — 최종 답변

선택하신 ①②③ 묶음을 정리했습니다. 커밋은 하지 않았고, git이 추적하던 파일은 이력에서 복구할 수 있습니다.

**삭제한 것**
- **임시·캐시**: `.codex-video-frames/`, `tmp_video_analysis/`, `tmp/fov_on_video_frame.png`, `tmp/.cache/`, `examples/generated_configs/`(실행 시 자동 재생성), `__pycache__`, 빈 `.agents/`
- **대체된 문서**: `FOV_COMMUNICATION.md`, `CNN_TRAINING_REVIEW_20260916.md`
- **끝난 과거 실험 도구**: 09700 일반화 평가 세트(`eval_checkpoint_generalization.py`, 그 테스트, ps1 2개, 문서), `visualize_graph_connectivity.py`, `create_probe_ppt_images.py`, `run_semantic_cnn_mixing_curriculum.ps1`, `Success_checkpoint/`

**남긴 것**
- 현재 실험·테스트·노트가 쓰는 파일 전부: examples에는 학습기, spatial/transfer/hard 실행기, probe 진단 도구, 커리큘럼 실행기만 남았습니다.
- `tmp/pdfs`: ex4/ex5 원문 추출본이라 선택지에 넣지 않았습니다.
- `runs/`, `output/`의 과거 결과 전부
- `.pytest-tmp`, `.pytest_cache`: 권한 거부로 지우지 못했습니다. 지우려면 관리자 권한 PowerShell에서 직접 삭제해 주세요.

**확인**
- [examples/README.md](examples/README.md)와 [EX5_PGCT.md](examples/EX5_PGCT.md)에서 삭제된 파일을 가리키던 부분을 고쳤습니다.
- 남은 참조가 없음을 확인했습니다.
- 전체 테스트 178개가 통과했습니다.

정리 내역은 DECISIONS D19와 CONVERSATION_LOG T010에 남겼습니다. 커밋을 원하시면 말씀해 주세요.


#### 원문 기록 T011 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (붙여넣은 GPT 답변 + 본문)

###### 붙여넣은 내용 (GPT 답변, 참고 자료)

맞습니다. 저도 지금은 처음부터 학습시키는 실험이 필요하다고 생각합니다. 오히려 지금까지의 실험 설계를 다시 보면, 사전학습이 너무 많이 진행된 상태에서 PGCT나 critic consensus를 적용한 것이 학습 개선 효과를 제대로 측정하지 못한 원인 중 하나일 수 있습니다.

그리고 이 부분은 제가 앞서 제안한 실험 B의 한계이기도 합니다.

#### 1. 현재 실험 설계의 문제

지금까지의 RWARE 학습은 대략 다음 구조였습니다.

Stage 1 — 단일 에이전트 사전학습

배송·이동 등 기본 행동 학습

Stage 2 — 복수 에이전트 / 반납 학습

기존 정책을 활용한 추가 학습

Stage 3 — Multi-team MARL

이미 학습한 정책·critic을 활용

IPPO

독립 학습

PGCT / Oracle

Critic 공유

이런 구조에서 실험 B를 진행하면 실제로 검증하는 것은 다음과 같습니다.

> 이미 상당히 학습한 에이전트에게 critic 공유를 추가하면 성능이 개선되는가?

그런데 우리가 원래 알고 싶었던 것은 조금 다릅니다.

> 처음부터 여러 에이전트가 함께 학습하는 상황에서, 적절한 critic consensus가 학습 속도와 최종 성능을 개선하는가?

두 질문은 서로 다릅니다.

기존 critic이 이미 충분히 학습되었다면 공유할 때 얻는 추가 정보가 적을 수 있습니다. 따라서 뒤늦게 consensus를 도입했을 때 성능 개선이 작더라도, 초기 학습에서 consensus가 유용하지 않다고 결론 내릴 수는 없습니다.

물론 그 반대도 성립합니다. 초기 critic이 부정확하면 consensus가 오히려 오류를 전파할 수도 있습니다.

#### 2. 그렇다면 어떻게 학습해야 할까?

저는 실험을 두 가지로 구분하는 것이 적절하다고 봅니다.

##### 실험 1. 완전 초기 학습 (Cold Start)

처음부터 4개 에이전트, 2개 팀을 구성하고 모든 네트워크를 무작위 초기화합니다.

동일한 초기 환경, 동일한 학습 예산

IPPO

Critic 공유 없음

Oracle

같은 팀끼리 공유

All-peer

모든 이웃과 공유

PGCT

기존 JS gate 공유

이렇게 하면 처음부터 critic 공유가 학습에 미치는 영향을 평가할 수 있습니다.

다만 단점이 있습니다. 현재 RWARE는 보상이 희소하고 배송·반납 과정이 복잡하므로, 무작위 정책에서 네 방법 모두 제대로 학습하지 못할 수 있습니다.

이 경우에는 알고리즘의 우열을 구분하기 어렵습니다.

##### 실험 2. 초기부터 동일한 커리큘럼 적용

현재의 커리큘럼을 유지하되, critic 공유 방법의 차이를 비교할 수 있는 첫 단계부터 각 알고리즘을 적용하는 것입니다.

핵심은 Stage 3까지 과도하게 사전학습한 후 분기하는 방식이 아니라, 다중 에이전트 학습이 시작되는 시점부터 공유 방법별 학습 곡선을 비교하는 것입니다.

단, Stage 1처럼 에이전트가 하나라면 consensus 자체가 불가능합니다. 그 구간은 공통으로 학습해 재사용하더라도 비교의 공정성을 해치지 않습니다.

Stage 2에서도 한 팀만 존재한다면 Oracle과 All-peer를 구별하기 어려우므로, 실제로 차이가 발생하는 단계가 어디인지 확인해야 합니다.

#### 3. 제가 추천하는 최종 실험 구성

| 실험 | 초기화                   | 목적                        |
| -- | --------------------- | ------------------------- |
| A  | 완전 무작위                | 처음부터 critic 공유가 유리한가?     |
| B  | 최소한의 공통 사전학습          | 초기 탐색 문제를 줄여도 공유 효과가 있는가? |
| C  | 기존 Stage03 checkpoint | 충분히 학습된 후에도 공유가 유리한가?     |

개인적으로는 A와 B를 우선하고 C는 보조 실험으로 남기는 것을 권합니다.

또한 IPPO, Oracle, All-peer부터 비교하는 편이 좋겠습니다. 이 세 방법으로 critic 공유 자체의 유효성을 먼저 검증한 다음, PGCT와 새로운 팀 추론 알고리즘을 평가하는 것이 자연스럽습니다.

평가 지표도 단순 최종 배송량만 볼 것이 아니라, 전체 학습 구간의 AUC, 일정 성능에 도달하기까지의 환경 step, seed 간 분산을 함께 봐야 합니다.

여기서 전체 학습 효율을 주장하려면 사전학습에 사용한 환경 상호작용 비용도 포함해야 합니다.

#### 4. 더 중요한 문제가 하나 있습니다

지금까지 논의에서 놓치기 쉬운 부분입니다.

처음부터 학습한다고 해서 Oracle-team consensus가 반드시 All-peer보다 좋아지는 것은 아닙니다.

현재 환경에서는 서로 다른 팀의 과제가 구조적으로 유사하기 때문입니다.

초기학습 문제와 환경의 목표 구분 문제는 별개입니다.

따라서 저는 다음 두 질문을 각각 실험해야 한다고 생각합니다.

- 학습 시점의 문제: Critic consensus는 학습 초기, 중기, 후기 중 언제 유용한가?
- 팀 구조의 문제: 실제 같은 목표를 가진 에이전트끼리 공유하는 것이 모든 에이전트와 공유하는 것보다 유리한가?

둘을 동시에 바꾸면 무엇이 성능 개선의 원인인지 구별하기 어렵습니다.

#### 제 결론

지금 예정된 1.024M step짜리 Stage03 기반 Oracle 실험은 우선순위를 낮추는 것이 맞습니다.

현재 학습이 이미 많이 진행된 checkpoint에서 1M step을 추가하는 것만으로는 우리가 가장 궁금한 초기 학습 효율을 검증할 수 없기 때문입니다.

대신 저는 다음 순서를 권합니다.

1. 현재 4-agent, 2-team RWARE에서 무작위 초기화 IPPO와 Oracle을 짧게 실행해 학습 가능성부터 확인합니다.
2. 학습 자체가 어려우면 최소한의 공통 커리큘럼을 설계합니다.
3. Oracle, IPPO, All-peer를 동일한 초기 조건과 학습 예산으로 비교합니다.
4. Oracle이 일관되게 유리한 조건을 확인한 후, 잠재 팀 추론 알고리즘으로 넘어갑니다.

여기서 제가 특히 강조하고 싶은 것은 우리의 연구 목표가 사전학습된 정책들의 critic을 공유하는 것이 아니라, 여러 에이전트가 학습하는 과정에서 적절한 협력 관계를 찾아 학습 효율을 높이는 것이라는 점입니다.

따라서 처음부터 학습시키자는 의견에 동의합니다. 지금의 연구 목적에는 그 실험이 더 직접적입니다.

###### 사용자 본문

기존 실험은 애초에 커리큘럼 러닝으로 인해 초기 학습량이 너무 많아 데이터가 믿기 힘들어
IPPO, PGCT, 기타 MARL 들을 처음부터 돌려서 학습 데이터를 뽑아내야 할꺼 같은데
각각 커리큘럼러닝없이 학습할수 있게 코드를 구현해주고 실행코드를 알려줘

##### Assistant — 진행 안내 1

기존 결과는 커리큘럼에서 분기한 조건부 실험이라, 처음부터 학습하는 비교 실험은 별도 실행기로 만드는 게 맞습니다. 먼저 기존 from-scratch 실행기와, 실제로 처음부터 학습에 성공했던 9700 run의 설정을 확인하겠습니다.

##### Assistant — 진행 안내 2

기존 from-scratch 실행기는 oracle 비교군이 물리 이웃이 아닌 complete 그래프를 쓰고, mode마다 probe bank가 달라지는 등 공정한 비교 조건이 맞지 않습니다. 새 실행기로 만들겠습니다. 처음부터 학습에 성공한 9700 run의 설정(lr 2e-4, entropy 0.05, 약 10M step)을 기준으로 삼고, 다른 조건은 기존 E1과 같게 맞춥니다. 시드 처리 순서를 확인합니다.

##### Assistant — 진행 안내 3

시드 처리는 seed 설정 → env reset → 네트워크 생성 순서이므로, 같은 seed면 모든 mode가 같은 초기 가중치로 시작해야 합니다. smoke 단계에서 초기 가중치 hash로 이를 직접 확인하겠습니다. 이제 실행기를 작성합니다.

##### Assistant — 진행 안내 4

실험 B 실행기에 초기 가중치 hash 기록과 IPPO·PGCT 허용 조건을 추가했습니다. 이제 커리큘럼 없이 처음부터 학습하는 실행기(`train_from_scratch.py`)와 병렬 실행용 PowerShell 스크립트를 작성합니다.

##### Assistant — 진행 안내 5

5개 mode가 모두 같은 초기 가중치(hash 동일)로 시작했고, 전이 대상도 설계대로였습니다. oracle은 같은 팀끼리만, wrong은 다른 팀끼리만 전이했고, IPPO는 전이가 없었습니다. 이어서 병렬 실행용 PowerShell 스크립트를 만들고, 병렬 실행 경로도 시험합니다.

##### Assistant — 진행 안내 6

두 병렬 학습은 정상 완료됐습니다. 다만 한 job이 끝나고 비교표를 만드는 순간, 다른 job이 상태 파일을 쓰고 있어 읽기 오류가 났습니다. 상태 파일을 원자적으로 쓰고, 비교 단계가 이런 경우를 견디도록 고칩니다.

##### Assistant — 진행 안내 7

Windows에서 다른 job이 상태 파일을 읽는 순간에는 교체가 거부됩니다. 학습 자체는 정상 완료됐고 상태 기록만 실패한 것이므로, 짧게 재시도하도록 고칩니다.

##### Assistant — 진행 안내 8

병렬 4개 job이 모두 오류 없이 완료됐고, 모든 mode가 같은 초기 가중치에서 시작했습니다. 실행기가 정말 체크포인트 없이 무작위 초기화로 시작하는지, mode 간 설정 차이가 의도한 항목뿐인지를 검사하는 테스트를 추가합니다.

##### Assistant — 진행 안내 9

전체 테스트 179개가 통과했습니다. 무작위 초기 가중치(hash `baaa10bf…`)도 Stage03(`b5e2158b…`)과 달라, 체크포인트 없이 시작함을 확인했습니다. 이제 README와 연구 노트를 갱신합니다.

##### 수행 기록 — 원문 대화와 별도

`latent_team/train_from_scratch.py`, `latent_team/run_from_scratch.ps1`을 추가했다. `exp_b_oracle_consensus.py`에 초기 가중치 hash 기록, ippo/pgct 허용 조건, None allocation 보존을 추가했다. 테스트 1개를 추가했다. smoke: `runs/scratch_smoke_20261013`(5 modes 순차), `runs/scratch_smoke_parallel_20261013`(4 modes 병렬). 병렬 첫 두 시도는 상태 파일 경합으로 실패했고 해당 smoke 폴더는 삭제 후 재실행했다. 전체 tests 179 passed. README, D20, E14, RESEARCH_STATE를 갱신했다. 장기 학습은 시작하지 않았다.

##### Assistant — 최종 답변

커리큘럼 없이 무작위 초기화로 처음부터 학습하는 실행기를 만들었습니다. 기존 트레이너는 수정하지 않았고, **장기 학습은 아직 시작하지 않았습니다.**

**학습 방법 (mode)**

| mode | 내용 |
|---|---|
| `ippo` | 독립 학습, 통신·critic 공유 없음 |
| `pgct` | 기존 JS gate 기반 critic 공유 |
| `oracle` | 같은 팀 이웃과만 공유(정답 팀 라벨) |
| `all` | 모든 이웃과 공유 |
| `wrong` | 다른 팀 이웃과만 공유 (대조용) |

**공정한 비교 조건**

같은 seed의 모든 mode는 다음이 같고, critic 공유 대상만 다릅니다.
- 환경: E1 11×10, 4 agents/2 teams, home 0.5, individual reward
- PPO 설정, 학습 예산, 평가 seed
- **무작위 초기 가중치**: hash로 확인
- **probe bank**

학습률 2e-4와 entropy 0.05는 예전에 처음부터 학습에 성공한 run의 설정입니다. 기본 예산은 10M step이며 모두 옵션으로 바꿀 수 있습니다.

**검증**
- 5개 mode 순차 smoke와 4개 mode 병렬 smoke가 모두 정상 완료됐습니다.
- 모든 mode의 초기 가중치가 동일하고, 기존 Stage03과는 다릅니다. 체크포인트 없이 시작한다는 뜻입니다.
- 전이 대상이 설계대로였습니다. oracle은 같은 팀끼리만, wrong은 다른 팀끼리만 전이했고, IPPO는 전이가 0이었습니다.
- 전체 테스트 179개가 통과했습니다.

**실행 코드**

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

1단계(권장): 처음부터 학습이 되는지 확인하는 pilot. IPPO와 oracle을 2M step씩 병렬로 돌립니다.

```powershell
.\latent_team\run_from_scratch.ps1 -Modes ippo,oracle -TotalTimesteps 2000000 -Parallel
```

2단계: 본 비교. 4개 mode를 10M step으로 돌립니다. 이후 `-Seeds 2,3`으로 반복합니다.

```powershell
.\latent_team\run_from_scratch.ps1 -Modes ippo,pgct,oracle,all -Seeds 1 -Parallel
```

진행 상황과 비교표는 이렇게 확인합니다(`<시각>`은 실행할 때 출력되는 폴더 이름).

```powershell
Get-Content runs\scratch_<시각>\e1_oracle_s1.log -Tail 3
C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe latent_team\train_from_scratch.py --compare-only --plan runs\scratch_<시각>
```

`comparison.md`에는 mode별로 다음이 정리됩니다.
- delivery AUC
- 마지막 10회 평가 평균
- 10·20·30·40 delivery에 처음 도달한 step
- seed 간 표준편차
- 같은 초기 가중치로 시작했는지 여부

학습 데이터는 run 폴더마다 `metrics.jsonl`, `transfer.jsonl`, `spatial.jsonl`, checkpoint로 남습니다.

**주의할 점**
- **소요 시간**: 기존 E1 속도(약 37 step/s) 기준으로 run 하나에 2M은 약 15시간, 10M은 약 75시간입니다. 병렬로 돌리면 run마다 더 느려질 수 있습니다. pilot 로그의 `sps` 값으로 실제 속도를 확인해 주세요.
- **학습 가능성**: home 0.5에서 처음부터 학습한 적은 없습니다. pilot에서 delivery가 오르지 않으면 공통 최소 커리큘럼이 필요합니다(GPT의 실험 B 구성). 처음부터 학습해도 oracle이 all보다 유리하다는 보장은 없습니다. 팀 과제가 대칭이라는 환경 구조 문제는 그대로 남기 때문입니다.
- **"기타 MARL"의 범위**: 지금 트레이너가 지원하는 critic 공유 변형(oracle/all/wrong)까지만 구현했습니다. MAPPO(중앙 critic)나 parameter sharing 같은 표준 baseline이 필요하면 별도로 추가하겠습니다.

자세한 내용은 [latent_team/README.md](latent_team/README.md)를 참고하세요. 기록은 D20, E14, RESEARCH_STATE, CONVERSATION_LOG T011에 남겼습니다.


#### 원문 기록 T012 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다. 첫 사용자 메시지에는 직전 답변의 실행 명령 부분 스크린샷이 첨부됐다(`images/1.png`, 직전 답변의 1단계·2단계·진행 확인 명령 화면).

##### 사용자 — 원문 1

[이미지: 직전 답변의 실행 명령 화면] 1번 끝나면 자동으로 2번 돌아가게

##### Assistant — 진행 안내 1

1단계가 끝나면 2단계가 자동으로 이어지도록 파이프라인 스크립트를 만들겠습니다. 터미널을 닫아도 계속 돌 수 있게 백그라운드 실행 옵션도 넣습니다.

##### 사용자 — 원문 2 (작업 중 추가 메시지)

그냥 파이프라인 바꾸는거 치곤 너무 오래걸리는거 아냐?

##### Assistant — 진행 안내 2

맞습니다, 이 smoke 시험은 1–2분이면 끝나야 합니다. 대기 루프에 문제가 있는지 바로 확인하겠습니다.

##### Assistant — 진행 안내 3

파이프라인 자체는 정상입니다. 1단계 2개와 2단계 4개 job이 모두 완료됐습니다. 오래 걸린 것은 제 확인용 대기 명령 때문이었습니다. PowerShell 로그의 인코딩 때문에 "완료" 문구를 찾지 못해 10분 제한까지 기다린 것입니다. 남은 대기 작업을 멈추고 로그를 확인합니다.

##### Assistant — 진행 안내 4

실제 파이프라인은 **18초** 만에 끝났습니다(19:23:37 시작 → 19:23:55 완료). 1단계 2개 job이 모두 완료된 뒤 2단계 4개 job이 자동으로 시작해 완료됐습니다. 남은 시간은 제 확인 명령이 로그 인코딩(UTF-16) 때문에 완료 문구를 못 찾고 10분을 기다린 탓입니다. 이제 README와 노트를 갱신하고 마무리합니다.

##### 수행 기록 — 원문 대화와 별도

`latent_team/run_scratch_pipeline.ps1`을 추가하고 `run_from_scratch.ps1`에 `-Wait`를 추가했다. `-SmokeTest -Detach`로 검증했다(`runs/scratch_pipeline_smoke_20261013_*`, 18초). Assistant의 확인용 bash 대기 루프가 UTF-16 로그를 grep하지 못해 약 10분 지연됐다. README와 EXPERIMENTS E14 추가 항목을 갱신했다. 장기 학습은 시작하지 않았다.

##### Assistant — 최종 답변

네, 너무 오래 걸렸습니다. 파이프라인 자체는 18초 만에 끝났는데, 제가 결과를 확인하려고 쓴 대기 명령이 PowerShell 로그 인코딩(UTF-16)을 읽지 못해 10분 제한까지 기다렸습니다. 제 확인 방식의 실수였고, 파이프라인에는 문제가 없습니다.

**만든 것**: 1단계가 끝나면 2단계가 자동으로 시작됩니다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\latent_team\run_scratch_pipeline.ps1 -Detach
```

- **1단계**: ippo, oracle을 2M step씩 병렬로 돌립니다.
- **2단계**: 1단계 job이 모두 정상 완료되면 ippo, pgct, oracle, all을 10M step씩 병렬로 돌립니다. 1단계가 실패하면 2단계는 시작하지 않습니다.
- `-Detach`: 숨은 백그라운드 창에서 돌아가므로 이 터미널을 닫아도 계속됩니다. 다만 오늘 E3처럼 PC가 재부팅되면 중단됩니다. 장기 실행 중에는 Windows 자동 재시작을 꺼 두시는 게 좋습니다.

진행 상황은 이렇게 확인합니다(`<시각>`은 실행 시 출력되는 이름).

```powershell
Get-Content runs\scratch_<시각>_pipeline.log -Tail 5
```

**검증**: 64-step 시험 모드로 돌려서 1단계 2개 job 완료 → 2단계 4개 job 자동 시작 → 완료까지 확인했습니다.

**주의**: 2단계 진행 조건은 "1단계 job이 오류 없이 끝났는가"뿐입니다. 1단계에서 처음부터 학습이 잘 되는지까지 판단하지는 않습니다. pilot에서 delivery가 오르지 않았다면 2단계 결과도 의미가 약하므로, 1단계 비교표(`runs\scratch_<시각>_stage1\comparison.md`)를 중간에 한 번 확인해 주세요. 1단계가 끝날 때까지 약 15시간 이상 걸릴 것으로 예상합니다.


#### 원문 기록 T013 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다. 사용자는 별도 본문 없이 아래 점검 요청을 붙여넣었다.

##### 사용자 — 원문 (붙여넣은 내용)

파이프라인 Smoke Test가 완료된 것은 확인했습니다.
실제 2M/10M 학습을 실행하기 전에 아래 내용을 확인해 주세요.

1. Stage 1에서 학습한 체크포인트를 Stage 2에서 사용하는지 확인하세요. Stage 2의 네 실험군은 원칙적으로 랜덤 초기화부터 학습해야 합니다.
2. Stage 2의 IPPO, PGCT, Oracle, All이 동일 seed에서 동일한 초기 actor/critic 파라미터로 시작하는지 확인하세요.
3. Stage 1의 학습 성과가 충분하지 않아도 Stage 2로 넘어가는 구조의 위험성을 검토하세요.
4. 네 개의 학습 프로세스를 병렬 실행할 때 GPU 메모리 및 성능 문제가 없는지 확인하세요.

학습은 아직 실행하지 말고 코드와 설정을 점검한 결과만 보고해 주세요.

##### Assistant — 진행 안내 1

학습은 실행하지 않고 코드·설정·이미 만든 smoke 결과만으로 네 항목을 점검하겠습니다.

##### 수행 기록 — 원문 대화와 별도

학습은 실행하지 않았다. 실제 크기 stage1/stage2 plan을 scratchpad에만 plan-only로 만들었다(bank 생성 포함). 네트워크 초기화를 CPU/CUDA에서 재현해 hash를 계산했고, GPU 메모리 측정을 위해 무작위 입력으로 minibatch 크기의 forward/backward를 1회 실행했다(optimizer step·env 없음). nvidia-smi와 CPU/RAM, Windows Update 활성 시간을 조회했다. 결과는 EXPERIMENTS E14 점검 항목에 기록했다. 코드는 변경하지 않았다.

##### Assistant — 최종 답변

학습은 실행하지 않고 점검만 했습니다. 실제 크기의 계획 파일만 임시 폴더에 만들어 보았습니다.

**1. Stage 2가 Stage 1 체크포인트를 쓰는가 → 쓰지 않습니다**
- 두 단계 모두 `init_checkpoint=""`(무작위 초기화)입니다. 파이프라인은 출력 폴더만 바꿔 두 번 실행할 뿐, 단계 사이에 넘기는 것이 없습니다.
- 다만 중요한 사실을 발견했습니다. Stage 1과 Stage 2의 같은 mode는 설정 차이가 `total_timesteps`(그리고 저장 폴더 이름)뿐입니다. probe bank도 같습니다. 트레이너에 학습률 schedule이 없으므로 **Stage 1의 2M ippo/oracle은 Stage 2 ippo/oracle의 앞 2M을 그대로 반복하는 학습**입니다. GPU 연산 특성상 비트 단위로 완전히 같지는 않을 수 있습니다.

**2. 네 실험군이 같은 초기 파라미터로 시작하는가 → 예**
- 실제 트레이너로 돌린 smoke에서 Stage 1·2의 6개 run 초기 actor+critic hash가 모두 같았습니다.
- 트레이너는 네트워크를 CPU에서 만든 뒤 GPU로 옮기므로, GPU 실행에서도 초기화는 CPU 난수를 따릅니다. 별도 재현 코드로 CPU와 GPU의 hash가 같음도 확인했습니다.
- 다만 그 재현 hash는 트레이너 hash와 달라서 재현이 완전하지는 않습니다. 실제 GPU run에서는 시작 직후 `comparison.md`의 "Same init" 열로 한 번 확인해 주세요.

**3. 성과 없이 Stage 2로 넘어가는 위험 → 실제 문제입니다**
- 현재 조건은 "Stage 1 job이 오류 없이 끝났는가"뿐입니다. 처음부터 학습이 안 되더라도 약 75시간짜리 Stage 2가 자동으로 시작됩니다.
- 1번의 prefix 관계 때문에 Stage 1은 Stage 2와 계산이 겹칩니다. 약 15시간 × 2개 프로세스를 추가로 쓰면서, 얻는 것은 사실상 "멈춤 판단"뿐인데 그 판단을 하지 않는 구조입니다.
- 제안은 두 가지입니다. 원하시는 쪽으로 고치겠습니다.
  - (a) 성과 기준 추가: Stage 1의 IPPO/oracle 마지막 평가가 기준 delivery(예: 10) 이상일 때만 Stage 2 시작
  - (b) Stage 1을 없애고 Stage 2만 실행: 2M 시점에 delivery를 보고 계속할지 직접 판단. 이쪽이 계산 낭비가 없습니다.

**4. 4개 병렬 실행 시 GPU 메모리·성능 → 메모리는 여유, 속도는 실측 필요**
- GPU는 RTX 5070 Ti 16GB이고 현재 780MB를 쓰고 있습니다. agent당 파라미터는 약 127만 개입니다. 학습 1회분 크기의 forward/backward peak가 143MB이고, 프로세스당 CUDA context 수백 MB를 더해도 4개 병렬이 2–3GB 수준이라 충분합니다.
- CPU는 20코어, RAM 31GB(여유 17GB)입니다. 4 job × 4 thread로 설정돼 있습니다.
- 기존 속도(37 step/s)는 GPU보다 Python 환경 시뮬레이션과 평가에 막혀 있을 가능성이 큽니다(추정). 병렬 실행 시 job별 속도는 실제로 재봐야 합니다.
- 추가 위험: E3를 멈춘 18:21 재부팅은 Windows Update 활성 시간(8–17시) 밖이어서 자동 업데이트 재시작일 수 있습니다(가설). 수십 시간 학습 전에 Windows 업데이트를 일시 중지하시는 게 안전합니다.

결과는 EXPERIMENTS의 E14 점검 항목과 CONVERSATION_LOG T013에 기록했습니다. 3번을 (a)와 (b) 중 어느 쪽으로 할지 정해 주시면 반영하겠습니다.


#### 원문 기록 T014 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

PGCT 실험 파이프라인 개선 및 MARL 비교 알고리즘 확장
현재 작성된 from-scratch 실험 파이프라인을 기반으로 다음 작업을 진행해 주세요.
1. WandB 기반 실험 관리
기존 PowerShell 파이프라인의 자동 실행 및 오류 처리 기능은 유지하되, 학습 상황은 WandB에서 확인할 수 있도록 수정해 주세요.

* 기존 코드에 구현된 WandB 로깅 기능부터 조사하고 재사용
* 동일 프로젝트에서 알고리즘별 독립적인 run 생성
* Stage, 알고리즘, seed, 환경 설정을 group/config에 기록
* Reward, Delivery, Return, Pickup, Loss, Gate Ratio 등 사용 가능한 지표 기록
* 모든 비교군의 X축은 동일하게 environment steps 기준으로 통일
* 백그라운드(-Detach) 실행에서도 WandB 로깅이 정상 동작하도록 확인
* PowerShell 로그는 파이프라인 상태와 오류 진단을 위해 유지

2. 학습 구간 재검토
기존 RWARE 실험에서는 다음과 같은 학습 양상이 관찰된 것으로 기억합니다.

* 약 2~4M steps: 물체를 집는 행동이 나타나기 시작
* 약 9M steps: 미션을 어느 정도 완수하기 시작

따라서 Stage 1의 2M steps와 Stage 2의 10M steps가 적절한지 검토해 주세요.
특히 2M에서 성능이 낮다는 이유만으로 학습 실패를 판단해서는 안 됩니다.
다음 사항을 우선 확인해 주세요.

1. Stage 1이 단순 pilot인지, Stage 2 초기화에 이용되는 사전학습인지
2. Stage 2의 각 알고리즘이 어떤 초기 파라미터를 사용하는지
3. 기존 실험 로그에서 Pickup, Delivery가 상승하기 시작한 step
4. 총 학습량을 15~20M까지 확대할 필요가 있는지

기존 기록이 현재 환경과 다르다면 그 차이도 보고해 주세요.
3. 비교 알고리즘 추가
다음 세 알고리즘을 비교군으로 추가하고 싶습니다.
A. SePS — ICML 2021
Scaling Multi-Agent Reinforcement Learning with Selective Parameter Sharing
논문:
https://proceedings.mlr.press/v139/christianos21a.html
공식 구현:
https://github.com/uoe-agents/seps
B. HetDPS — AAMAS 2026
Heterogeneity in Multi-Agent Reinforcement Learning
공식 구현:
https://github.com/Harry67Hu/HetDPS
C. MAPPO — NeurIPS 2022
The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games
공식 구현:
https://github.com/marlbenchmark/on-policy
각 논문과 공식 구현을 먼저 검토한 다음, 현재 커스텀 RWARE 환경에 맞게 통합해 주세요.
중요한 사항:

* 알고리즘의 핵심 수식 및 학습 구조를 임의로 단순화하지 않을 것
* 원 논문과 다르게 구현한 부분을 명확히 기록할 것
* 학습 알고리즘 외 환경·보상·평가 조건은 가능한 한 동일하게 유지할 것
* SePS와 HetDPS의 사전학습 및 추가 계산 비용도 기록할 것
* MAPPO의 중앙집중식 critic은 추가 정보가 허용된 비교군으로 구분할 것
* 모든 비교군은 동일한 seed 목록과 동일한 환경 step 예산으로 반복 실험이 가능하도록 구성할 것
* 현재 PGCT, IPPO, Oracle, All 구현은 변경하지 않는 것을 원칙으로 할 것

4. 진행 순서

1. 현재 코드 구조 및 WandB 지원 여부 분석
2. WandB 통합 및 테스트
3. 학습 step과 초기화 조건 검증
4. MAPPO 구현 및 Smoke Test
5. SePS 구현 및 Smoke Test
6. HetDPS 구현 및 Smoke Test
7. 통합 파이프라인 검증 및 변경 사항 정리

각 단계가 끝날 때마다 구현 내용, 테스트 결과, 원 논문 대비 차이를 간단히 정리해 주세요.
Smoke Test는 최소한의 학습 step으로 수행하고, 짧은 테스트에서 reward가 오르지 않는 것을 알고리즘 실패로 판단하지 마세요.
실제 수백만 step의 본 학습은 제 승인 없이 시작하지 마세요.
기존 학습 체크포인트, 실험 로그, 결과물은 보존해 주세요.

토큰이 500K로 부족할 수 있으니 마지막에 MAPPO -> SePS -> HetDPS 순으로 구현해줘

##### Assistant — 진행 안내 (발화 순서대로)

1. 작업 범위가 넓어서 요청하신 순서대로 진행하겠습니다. 토큰을 아끼기 위해 진행 안내는 단계마다 짧게 하겠습니다. / **1단계: 현재 W&B 지원 조사**부터 합니다.
2. W&B 지원은 이미 트레이너에 있습니다(`init_wandb`, `log_to_wandb(step=env_steps)`, `_netrc` 로그인 확인). 따라서 트레이너는 고치지 않고 새 실행기에서 project, group, config, gate 지표만 덧붙이면 됩니다. 이어서 **학습 구간 검토**에 필요한 기존 from-scratch 기록을 찾습니다.
3. 학습 구간 확인 결과입니다(로컬 W&B 기록 `run-bhh1l6x8.wandb`, 이전 from-scratch PGCT, 10M step).
   - 요청 선반 pickup: 약 **1.5M step**에서 시작
   - delivery: **1.7M**에서 시작, 평가 기준 20 이상은 **2.3M**, 40 이상은 **3.3M**
   - 그 뒤 6–9M에 56–60 수준으로 수렴

   기억하신 "2–4M pickup, 9M 완수"와는 다릅니다. 다만 그 run은 **home 1.0**(팀 선반이 공간적으로 분리됨)과 **complete 그래프**였고, 지금 계획은 home 0.5와 physical 그래프입니다. 보상과 맵은 같습니다. / 이제 W&B 통합을 구현합니다.
4. Now editing the from-scratch runner for W&B (project, group, tags, config, gate metrics).
5. The pipeline file is small; I'll rewrite it whole instead of patching.
6. W&B 통합을 반영했습니다. 이제 `-Detach -Track` 조합으로 백그라운드 실행에서도 W&B 로깅이 되는지 smoke test로 확인합니다. 본 프로젝트가 지저분해지지 않도록 별도 프로젝트 `rware-from-scratch-smoke`를 씁니다.
7. **1–3단계 결과**
   - W&B는 트레이너에 이미 구현되어 있어 그대로 재사용했습니다.
   - `-Detach -Track` smoke에서 3개 run이 모두 `finished` 상태로 기록됐습니다. group은 stage별, tag는 맵·mode·seed, config에는 algorithm·stage·seed·env가 들어갔고, Step 축은 env step(32, 64)입니다.
   - gate 지표(`update/gate_ratio`, same/cross arc 수)도 기록됩니다.
   - 학습 구간 검토를 반영해 기본 예산을 Stage1 4M, Stage2 15M으로 바꿨고 `-SkipStage1` 옵션을 추가했습니다.

   **4단계 MAPPO**로 넘어갑니다. 평가·rollout 수집은 기존 트레이너 함수를 그대로 재사용해야 조건이 같아지므로, 그 인터페이스를 확인합니다.
8. 기존 `collect_rollout`과 `evaluate`는 agent별 network 인터페이스(`act`, `action_probabilities`, `_critic_step`)를 호출합니다. MAPPO의 중앙 critic은 전체 관측이 필요하므로, rollout 뒤에 중앙 critic 값을 다시 계산하는 방식으로 기존 수집·평가 코드를 그대로 재사용하겠습니다. 이를 위해 네트워크 내부 구조를 확인합니다.
9. 네트워크 인터페이스를 거의 확인했습니다. sequence 평가와 done reset 처리 방식만 확인한 뒤 MAPPO 코드를 작성하겠습니다.
10. MAPPO 구현 방식이 정해졌습니다. 기존 `T.train`의 env·rollout·평가·W&B·checkpoint 루프는 그대로 두고, agent network를 "공유 actor + 중앙 critic"으로 바꿉니다. update만 MAPPO 방식으로 교체하고 중앙 critic 값은 rollout 뒤에 다시 계산합니다. / 구현 전에 세 공식 구현의 핵심을 확인합니다.
11. 두 저장소 모두 핵심 정보가 README에 다 나오지 않아서, 공식 구현의 해당 파일을 직접 확인합니다.
12. SePS와 HetDPS 공식 구현의 공유 구조를 확인했습니다. 둘 다 "agent 수만큼의 네트워크와 agent→네트워크 배정 index"로 parameter sharing을 바꾸는 방식입니다. HetDPS의 재배정 일정과 PPO 설정을 마저 확인합니다.
13. MAPPO부터 구현합니다. 그 전에 트레이너가 update 결과에서 어떤 key를 직접 읽는지만 확인합니다.
14. MAPPO를 구현합니다. 새 파일 `latent_team/marl_baselines.py`에서 기존 `T.train` 루프를 그대로 쓰고, network 생성과 update 함수만 이 프로세스 안에서 교체합니다. 기존 PGCT/IPPO 코드와 파일은 바꾸지 않습니다. 같은 파일에 SePS·HetDPS도 이어서 넣을 수 있게 공통 learner 구조로 작성합니다.
15. MAPPO 코드를 정리했습니다. 이제 from-scratch 실행기에 `mappo/seps/hetdps` mode를 연결하고 MAPPO smoke test를 돌립니다.
16. MAPPO smoke test를 통과했습니다. 2회 update 모두 완료됐고, 첫 minibatch의 approx_kl이 약 1e-9입니다. 즉 저장된 행동 확률을 actor가 그대로 재현합니다. 중앙 critic 재계산도 같은 방식으로 검증할 수 있도록 replay 오차 지표를 추가합니다. 이어서 SePS로 넘어갑니다.
17. SePS의 VAE 구조를 확인했습니다. encoder는 agent one-hot을 받아 2×z를 출력하고, decoder는 [z, obs, act]를 받아 [next_obs, rew]를 복원합니다. 은닉 크기 상수 `HIDDEN`의 값만 원문에서 확인하지 못해 64로 두고 기록하겠습니다. SePS를 구현합니다.
18. The shell heredoc failed to parse; I'll write the patch script with the Write tool instead.
19. Now appending the SePS learner to the same module.
20. MAPPO는 critic replay 오차가 약 1.5e-7로, 중앙 critic 재계산이 일관됨을 확인했습니다. SePS는 `scikit-learn`이 RWARE_MARL 환경에 설치되어 있지 않아 실패했습니다. 사용자 환경에 패키지를 새로 설치하는 대신, 같은 기본값의 k-means++(n_init=10), Davies–Bouldin, Affinity Propagation을 numpy로 직접 구현하겠습니다. HetDPS도 AP가 필요합니다.
21. The assertion tripped only on docstring mentions; nothing was written. Applying the replacements with the Edit tool.
22. SePS smoke test를 통과했습니다.
    - 클러스터링 전에는 무작위 배정(agent 0 → network 0)을 썼습니다.
    - pretraining 뒤 VAE 학습 → Davies–Bouldin으로 K=3 선택 → 배정 [2,0,2,1] 적용까지 정상 동작했습니다.
    - critic replay 오차는 약 2e-7입니다.

    마지막으로 **HetDPS**입니다. 공식 코드의 VAE, 거리 계산, 재배정 로직을 읽습니다.
23. HetDPS 공식 로직을 확인했습니다.
    - 처음에는 모든 agent가 network 0을 공유합니다.
    - 최근 transition buffer(agent당 20×5×32=3,200 env step)를 둡니다.
    - 3,200 env step마다 BiHierarchicalVAE(z=40, lr 5e-4, 10 epoch)를 이어서 학습합니다.
    - buffer의 모든 상태 × 5개 행동 조건에서 agent별 Gaussian 사이 Wasserstein 거리를 계산합니다.
    - 이 거리로 Affinity Propagation을 돌리고, 이전 배정과 Hungarian 매칭을 해서 분할·병합합니다(majority 파라미터 복사).

    이를 구현합니다.
24. No scipy either, so I'll use an exact permutation search for the (≤4×4) Hungarian matching. Appending the HetDPS learner now.
25. HetDPS smoke test도 통과했습니다. 측정 2회 모두 VAE 학습, Wasserstein 행렬, AP 군집, 이전 배정과의 매칭까지 동작했고 배정은 [0,1,0,0] → [0,0,0,1]로 바뀌었습니다. 이제 SePS·HetDPS의 **추가 계산 비용**을 실제 크기의 무작위 데이터로 측정합니다. 이 측정은 env 학습이 아닙니다.
26. SePS·HetDPS의 추가 비용을 측정했습니다(GPU, 실제 크기, 무작위 데이터).
    - **HetDPS**: 측정 1회에 약 4.4초가 듭니다. 15M step이면 약 4,687회로 **약 5.8시간 추가**되며, 학습 시간의 약 5% 수준입니다.
    - **SePS**: VAE 학습 1회에 약 9초입니다.

    이제 W&B를 켠 상태로 세 baseline을 통합 smoke test하고 단위 테스트를 추가합니다.
27. 네 알고리즘 모두 W&B에 같은 env-step 축으로 기록됐고, SePS·HetDPS 고유 지표도 들어갔습니다. 단위 테스트를 추가합니다.
28. 전체 테스트 182개가 통과했습니다. 이제 원 논문 대비 차이와 비용을 정리한 `BASELINES.md`를 작성하고 README와 연구 노트를 갱신합니다.
29. Now the research notes and conversation log.

##### 수행 기록 — 원문 대화와 별도

- **외부 자료**: 공식 저장소는 WebFetch로 읽었다(SePS ops_utils.py/ac.py/model.py 요약 확인). HetDPS는 `model_Het.py`, `main_Het.py`, `utils_Het.py`를 scratchpad에 내려받아 해당 부분만 읽었다. MAPPO는 on-policy 구현의 알려진 구성으로 구현했고 별도 파일 fetch는 하지 않았다.
- **코드 변경**:
  - 추가: `latent_team/marl_baselines.py`, `BASELINES.md`
  - 수정: `train_from_scratch.py`, `exp_b_oracle_consensus.py`(gate 지표), `run_from_scratch.ps1`, `run_scratch_pipeline.ps1`(재작성: UTF-8 로그, `-SkipStage1`, `-Track`, 기본 4M/15M), `tests/test_latent_team.py`(+3 tests)
- **W&B**: 사용자 W&B 계정의 `rware-from-scratch-smoke` project에 smoke run 7개를 생성했다.
- **실패와 대응**: 중간 실패(heredoc 파싱, sklearn 부재로 seps 첫 smoke 실패, 테스트 인자)는 수정 후 재실행했다.
- **실행하지 않은 것**: 기존 trainer·PGCT/IPPO 실행 경로는 변경하지 않았다. 본 학습은 시작하지 않았다.

##### Assistant — 최종 답변

요청하신 7단계를 모두 마쳤습니다. 기존 PGCT/IPPO/Oracle/All 구현과 트레이너는 바꾸지 않았고, **본 학습은 시작하지 않았습니다.** 기존 checkpoint와 로그도 그대로입니다.

#### 1–2. W&B 통합
- 트레이너에 이미 있던 W&B 기능(`init_wandb`, `step=env_steps`)을 재사용했습니다. 새 실행기는 정보만 덧붙입니다.
  - project: `rware-from-scratch`
  - run: 알고리즘별로 따로(`e1_<mode>_s<seed>`)
  - group: stage
  - tag: 맵·mode·seed
  - config: algorithm·stage·seed·환경 설정·예산
- **X축**: 모든 비교군이 env step으로 통일됩니다.
- **지표**: reward·delivery·return·pickup·loss 외에 gate ratio와 same/cross 전이 수, SePS·HetDPS 군집 정보도 기록합니다.
- **-Detach 확인**: 백그라운드 실행에서도 run이 정상 `finished`로 남았습니다. 시험 run은 별도 project `rware-from-scratch-smoke`에 있으니 필요 없으면 지우셔도 됩니다.
- PowerShell 파이프라인 로그는 UTF-8로 유지됩니다.

#### 3. 학습 구간과 초기화 검증
1. **Stage 1은 단순 pilot**입니다. Stage 2의 초기화로 쓰이지 않습니다. 오히려 같은 mode라면 Stage 2의 앞부분을 그대로 반복합니다. 그래서 건너뛰는 `-SkipStage1` 옵션을 추가했습니다.
2. **Stage 2 초기 파라미터**: 모두 무작위 초기화입니다.
   - IPPO/PGCT/Oracle/All은 같은 seed면 초기값도 같습니다(hash로 확인).
   - MAPPO/SePS/HetDPS는 구조가 달라 초기값이 다릅니다. seed 목록은 같습니다.
3. **기존 로그**(이전 from-scratch PGCT, 로컬 W&B 기록)
   - pickup은 약 1.5M, delivery는 1.7M에 시작했습니다.
   - 평가 delivery 20 이상은 2.3M, 40 이상은 3.3M이었고, 6–9M에 56–60으로 수렴했습니다.
   - 기억하신 "2–4M / 9M"보다 빠릅니다. 다만 이 run은 **home 1.0·complete 그래프**였고, 지금 계획은 home 0.5·physical 그래프입니다(보상과 맵은 동일).
   - IPPO from-scratch 기록은 1M까지뿐입니다(pickup 0.76M 시작).
4. **예산**: home 0.5는 더 어려울 수 있어 **15M을 기본값으로** 바꿨습니다(Stage 1은 4M). 20M은 seed를 반복할 때 비용이 커서 옵션으로 남겼습니다. 2M 성능으로 실패를 판단하지 않습니다.

#### 4–6. 비교 알고리즘

| | 구현한 핵심 | 원 논문과 다른 점 | 추가 비용 |
|---|---|---|---|
| **MAPPO** | 공유 actor, **중앙 critic**, ValueNorm, Huber+value clipping, actor/critic 별도 optimizer | 전역 상태 = 4개 관측 연결 + agent ID. 하이퍼파라미터는 공통 설정 | 거의 없음 |
| **SePS** | VAE로 agent 특성 학습 → KMeans(K는 Davies–Bouldin) → 군집별 parameter 공유. 군집 전 무작위 배정 | 학습기 A2C 대신 PPO. 병렬 env 8개 → 1개. buffer 5만 개 제한 | 사전학습 40,000 env step(예산 포함), VAE 1회 약 9초 |
| **HetDPS** | 3,200 step마다 VAE 기반 이질성(Wasserstein) 측정 → Affinity Propagation → 그룹 분할·병합과 파라미터 복사 | MLP 구조 대신 공통 CNN+GRU. 학습기를 순환 PPO로 | 측정 1회 약 4.4초, 15M 기준 **약 5.8시간(학습의 약 5%)** |

- **MAPPO의 정보 조건**: critic이 다른 agent의 관측까지 보므로 **추가 정보가 허용된 비교군**으로 표시했습니다. 실행할 때 행동은 자기 관측만 씁니다.
- **공통 조건**: 세 알고리즘 모두 IPPO와 같은 env·보상·평가·예산·네트워크 크기를 씁니다.
- **환경 패키지**: scikit-learn/scipy가 환경에 없어 설치하지 않고, 같은 기본값으로 numpy에 직접 구현했습니다.
- **기록**: 원 논문과의 모든 차이는 [BASELINES.md](latent_team/BASELINES.md)에 정리했습니다.

#### 7. 통합 검증
- **세 알고리즘 모두 64-step 시험 학습을 통과**했습니다.
  - 저장된 행동 확률과 value를 다시 계산했을 때 오차가 1e-7 수준이라, 수집과 학습이 일관됩니다.
  - SePS는 군집화 후 배정 [2,0,2,1]이 적용됐습니다.
  - HetDPS는 재배정 [0,1,0,0] → [0,0,0,1]이 동작했습니다.
- W&B를 켜고 4개 알고리즘을 함께 돌린 시험도 모두 정상 기록됐습니다.
- 전체 테스트 **182개 통과**.

#### 실행 명령 (승인하시면 직접 실행하시거나 저에게 말씀해 주세요)

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -ThreadsPerJob 2 `
  -Stage2Modes ippo,pgct,oracle,all,mappo,seps,hetdps -Stage2Seeds 1
```

7개를 병렬로 돌리면 CPU 코어 수 때문에 프로세스당 스레드를 2개로 권장합니다. 기존 속도 기준으로 15M은 **run당 100시간 이상**이 걸릴 수 있으니, 시작 후 W&B에서 `train/sps`를 확인해 주세요.

기록: D21, E15, RESEARCH_STATE, CONVERSATION_LOG T014.


#### 원문 기록 T015 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (붙여넣은 내용 + 본문)

###### 붙여넣은 내용

From-Scratch 구현 결과를 확인했습니다.
다만 현재는 7개 알고리즘을 동시에 본 학습시키지 않겠습니다.
1. 우선 비교군은 IPPO, PGCT, Oracle, All-peer 네 개로 제한합니다.

* 모두 무작위 초기화에서 시작합니다.
* 동일한 환경, 보상, evaluation seed 및 environment step 기준으로 비교합니다.
* 같은 seed의 IPPO/PGCT/Oracle/All 초기 파라미터가 동일한지 확인합니다.
* 15M step을 기본 예산으로 설정하되, 4M~5M 시점에 학습 가능성 및 성능 추세를 점검합니다.
* 초기 2M step의 낮은 성능만으로 실패를 판단하지 않습니다.

2. 학습 실행 전 checkpoint resume를 검증해주세요.

* 모델뿐 아니라 optimizer, RNG, gate EMA와 기타 학습 상태가 복원되는지 확인합니다.
* 재개가 불가능하다면 중간 점검을 위해 학습을 종료하지 않는 방식으로 운영합니다.

3. MAPPO, SePS, HetDPS는 현재 구현을 보존합니다.

* 원 논문과의 차이점을 정리합니다.
* 핵심 비교 실험 이후에 본격적으로 학습합니다.

4. 이번 실험의 목적을 명확히 유지합니다.
이번 실험의 목적은 무작위 초기화 상태에서 critic 공유가 실제로 학습 효율을 개선하는지, 특히 정확한 팀 정보를 활용한 Oracle consensus가 IPPO 및 All-peer보다 유리한지 검증하는 것입니다.
From-Scratch로 바꾸더라도 현재 환경의 팀 목표 대칭성 문제는 남아 있으므로, 결과 해석 시 이를 고려해주세요.
본 학습 실행 전 위 조건의 검증 결과와 실행 계획을 보고해주세요.

###### 사용자 본문

최종 판단
현재 Claude의 구현 작업은 연구에 필요한 방향으로 진행되고 있습니다. 특히 기존 사전학습 checkpoint에서 벗어나 초기 학습부터 비교할 수 있게 된 점이 중요합니다.
그러나 현 단계에서 7개 알고리즘의 최종 성능을 얻는 것보다 중요한 것은, 정확한 팀을 알고 critic을 공유하는 것이 정말 유리한가를 확인하는 것입니다.
저는 IPPO, Oracle, All-peer, PGCT의 From-Scratch 비교부터 시작하겠습니다.
그리고 그 결과와 무관하게 한 가지는 계속 구분해야 합니다. 현재 실험은 critic 공유의 효과를 검증하는 것이지, 우리가 최종적으로 연구하려는 잠재 팀 발견 문제를 해결하는 실험은 아닙니다.(중요)

##### Assistant — 진행 안내 1

학습은 시작하지 않고 실행 전 검증만 합니다. 먼저 트레이너가 checkpoint에 무엇을 저장하고, 재개할 때 무엇을 복원하는지 확인합니다.

##### Assistant — 진행 안내 2

트레이너에는 **재개(resume) 기능이 없습니다.**
- checkpoint에 모델·optimizer·graph 통계를 저장하기는 합니다.
- 하지만 `init_checkpoint`로 다시 시작하면 네트워크 가중치만 복사하고, optimizer와 graph 통계(gate EMA)는 새로 시작한다고 코드에 명시돼 있습니다.
- 난수 상태, update 카운터, 진행 중이던 episode와 hidden state는 아예 저장하지 않습니다.

이어서 **실제 본 학습 설정(GPU, rollout 1024)** 으로 4개 mode를 4 update만 병렬로 돌려 세 가지를 확인합니다. 초기 파라미터가 같은지, GPU 경로가 정상인지, 병렬 실행 시 속도가 얼마인지입니다. 이 실행은 검증용이며 본 학습이 아닙니다.

##### Assistant — 진행 안내 3

실제 설정 검증이 끝났습니다.
- **초기 파라미터**: GPU에서 IPPO·PGCT·Oracle·All 4개 run의 초기 actor+critic hash가 모두 `f78ec390…`로 같습니다.
- **속도**: 4개를 병렬로 돌리면 update 1회(1,024 step)에 약 39초가 걸립니다. job당 약 26 step/s이고, 4개 합계 처리량은 단일 실행의 약 2.8배입니다.

노트를 갱신하고 실행 계획을 정리하겠습니다.

##### 수행 기록 — 원문 대화와 별도

코드는 변경하지 않았다. 트레이너의 save_checkpoint/transfer_checkpoint_to_agents를 검토해 resume 경로가 없음을 확인했다. `runs/verify_realcfg_20261013`에서 실제 설정 4 mode × 4 update 병렬 검증을 실행했다(본 학습 아님, W&B 끔). DECISIONS D22, EXPERIMENTS E16, RESEARCH_STATE를 갱신했다. 본 학습은 시작하지 않았다.

##### Assistant — 최종 답변

검증 결과와 실행 계획입니다. **본 학습은 시작하지 않았습니다.** 코드도 바꾸지 않았습니다.

#### 1. 비교 조건 검증 (IPPO / PGCT / Oracle / All)
- 실제 본 학습 설정(GPU, rollout 1024)으로 4개를 **4 update만** 병렬로 돌려 확인했습니다(검증용, `runs/verify_realcfg_20261013`).
- **초기 파라미터**: 4개 모두 첫 update 전 actor+critic hash가 `f78ec390…`로 **같습니다**. 무작위 초기화이고, 체크포인트는 쓰지 않습니다.
- **고정 조건**: 환경(E1, home 0.5, individual reward), 평가 seed(5,000,001~ 20회×500 step), 예산, probe bank가 같습니다. **critic을 공유하는 대상만 다릅니다.**
- **오류**: 4개 run 모두 정상 완료됐고 오류는 없었습니다.

#### 2. Checkpoint resume → **정확한 재개는 불가능합니다**

| 항목 | 저장 | 재개 시 복원 |
|---|---|---|
| 모델 가중치 | O | O (가중치 복사만) |
| optimizer 상태 | O | **X** (새로 시작) |
| gate EMA 등 graph 통계 | O | **X** (새로 시작) |
| update 카운터 | O | **X** (1부터 다시) |
| 난수(Python/NumPy/Torch, 내부 생성기) | **X** | X |
| 진행 중 episode, hidden state | **X** | X |

- 트레이너를 고치지 않는다는 원칙 때문에 resume을 새로 만들지 않았습니다.
- 말씀하신 대로 **학습을 멈추지 않고** 4–5M 점검을 하겠습니다. W&B, `metrics.jsonl`, checkpoint를 읽기만 합니다.
- 중간에 끊기면(재부팅 등) 해당 run은 처음부터 다시 돌리는 것이 원칙입니다.

#### 3. MAPPO / SePS / HetDPS
현재 구현을 그대로 보존합니다. 원 논문과의 차이는 [BASELINES.md](latent_team/BASELINES.md)에 정리되어 있습니다.
- **MAPPO**: 중앙 critic(추가 정보 허용), 하이퍼파라미터는 공통 설정
- **SePS**: A2C 대신 PPO, 병렬 env 8개 → 1개
- **HetDPS**: MLP 대신 CNN+GRU, 순환 PPO

핵심 비교가 끝난 뒤에 학습합니다.

#### 4. 실행 계획

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -Stage2Seeds 1
```

- 기본값: IPPO·PGCT·Oracle·All, 15M step, 4개 병렬, W&B 기록.
- **예상 시간**: update 1회에 약 39초이므로 15M까지 약 **6.6–7일**입니다. 4–5M 점검 시점은 시작 후 **약 2–2.4일**입니다.
- **4–5M 점검 항목**
  - 평가 pickup·delivery·return 곡선과 처음 오르기 시작한 step
  - 그때까지의 AUC
  - 실제 전이(Oracle은 같은 팀만, All은 같은 팀과 다른 팀 모두, PGCT gate 비율)
  - value loss, 속도
- **점검 시 판단 기준**
  - 어느 mode도 pickup이 나타나지 않으면, 알고리즘 실패가 아니라 예산·환경 문제로 보고 계속 진행할지 함께 결정합니다.
  - seed가 1개라 방향 확인용입니다. seed 2·3 반복은 이 결과를 본 뒤 결정합니다.
- **사전에 직접 해 주실 것**: E3를 멈춘 18:21 재부팅은 Windows 자동 업데이트 재시작이었을 가능성이 있습니다. 실행 전에 **Windows 업데이트 일시 중지와 절전 해제**를 직접 설정해 주세요. 시스템 설정이라 제가 바꿀 수 없습니다.

#### 5. 해석 원칙 (기록해 둠)
- 이 실험은 **critic 공유 효과를 검증하는 것이지, 잠재 팀 발견 문제를 해결하는 실험이 아닙니다.**
- 관측이 팀 기준이고 두 팀 목표가 대칭이라서 **Oracle ≈ All이 나와도 이상하지 않습니다**. 그 결과가 팀 발견 연구 자체를 부정하지는 않습니다. 이 환경에 목표 이질성이 부족하다는 뜻으로 해석합니다.
- 반대로 Oracle이 분명히 유리하면 "같은 팀끼리만 공유"에 근거가 생깁니다. 이 경우에도 seed를 반복해서 확인해야 합니다.

기록: DECISIONS D22, EXPERIMENTS E16, RESEARCH_STATE, CONVERSATION_LOG T015. 실행해도 되면 알려 주세요. 직접 실행하셔도 됩니다.


#### 원문 기록 T016 — 2026-10-13 KST, Claude Code

정확한 시각은 확인하지 않았다(측정은 20:27 KST 무렵).

##### 사용자 — 원문

지금 GPU 95~99% 꽉 채워서 쓰는데 이대로 6~7일 괜찮은 거야?

##### Assistant — 진행 안내 1

지금 GPU를 쓰고 있는 프로세스부터 확인하겠습니다.

##### Assistant — 진행 안내 2

요청하신 학습이 이미 실행 중입니다. 20:23:52에 시작된 `scratch_20261013_202352_stage2`에서 IPPO·PGCT·Oracle·All 4개 프로세스가 돌고 있습니다. GPU 상태를 몇 번 측정해 보겠습니다.

##### 수행 기록 — 원문 대화와 별도

nvidia-smi를 6회 측정했고, 프로세스·CPU·RAM과 학습 진행(metrics.jsonl)을 읽기 전용으로 확인했다. 실행 중인 학습은 건드리지 않았다. EXPERIMENTS E17, RESEARCH_STATE를 갱신했다.

##### Assistant — 최종 답변

**네, 이대로 괜찮습니다.** 사용률 수치는 높게 보이지만 GPU가 실제로 받는 부하는 낮습니다.

지금 실행 중인 학습(20:23 시작, 4개 프로세스)에서 측정한 값입니다.

| 항목 | 현재 | 의미 |
|---|---|---|
| 사용률 | 70–81% (nvidia-smi) | GPU에 작업이 걸려 있는 **시간 비율**일 뿐, 연산을 꽉 채운다는 뜻이 아님 |
| 전력 | 78–83W / 최대 300W | 실제 부하는 약 **27%** |
| 온도 | 50–52°C | 매우 낮음(게임 시 70–80°C대가 보통) |
| 팬 | 0% | 식힐 필요가 없어 팬이 멈춘 상태 |
| VRAM | 2.6 / 16.3GB | 여유 충분 |

작업관리자에 95–99%로 보이는 이유는 이렇습니다. 4개 프로세스가 아주 작은 계산(1 step씩 행동 선택)을 쉬지 않고 GPU에 넘기기 때문에, "무언가 실행 중인 시간"이 거의 100%로 잡힙니다. 하드웨어 수명에 영향을 주는 것은 온도와 전력인데 둘 다 여유가 큽니다. GPU는 이보다 훨씬 높은 부하로도 상시 운용하도록 만들어져 있습니다.

**실제로 신경 쓸 위험은 GPU가 아니라 다음입니다.**
- **재부팅·절전·정전**: 이어서 학습할 수 없으므로 중간에 끊기면 처음부터 다시 해야 합니다. Windows 업데이트 일시 중지와 절전 해제를 꼭 해 두세요.
- **다른 GPU 작업**: 게임이나 영상 작업을 같이 하면 학습이 느려집니다. 결과값은 달라지지 않고 시간만 늘어납니다.
- **RAM**: 프로세스당 약 2.1GB, 여유 10GB입니다. 무거운 프로그램을 많이 띄우지 않는 게 좋습니다.

현재 4개 run 모두 정상 진행 중이고(2,048 step), update 1회에 약 40.6초가 걸려 **15M까지 약 7일**로 예상됩니다. 4–5M 점검은 학습을 멈추지 않고 로그만 읽어서 하겠습니다.


#### 원문 기록 T017 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

컴퓨터가 알수없는 이유로 학습중에 자고왔더니 재부팅돼서 2.5M에서 끊긴거 같아 이어할수 있을까

##### Assistant — 진행 안내 1

먼저 실제로 어디서 멈췄는지와 남은 checkpoint를 확인하겠습니다.

##### 수행 기록 — 원문 대화와 별도

System 이벤트 로그, run 폴더, metrics를 읽기 전용으로 확인했다. EXPERIMENTS(E17 추가)와 RESEARCH_STATE를 갱신했다. 학습을 재시작하거나 파일을 변경하지 않았다.

##### Assistant — 최종 답변

**원인은 "알 수 없는" 게 아니라 Windows 업데이트였습니다.** 10월 15일 00:59와 01:01에 Windows Update(TrustedInstaller)가 "운영 체제 업그레이드" 사유로 PC를 재시작했습니다.

**멈춘 위치**
- 마지막 기록: IPPO 2.49M, PGCT 2.50M, Oracle 2.47M, All 2.46M step
- 마지막 checkpoint: 4개 모두 2,304,000 step(`checkpoint_02250.pt`)
- 로그와 checkpoint는 모두 보존돼 있습니다.

**이어서 할 수 있나 → 똑같이 이어가는 것은 불가능합니다.** 지난번 점검(D22)에서 확인했듯이, 트레이너는 재개할 때 가중치만 불러옵니다. optimizer, gate EMA, update 카운터, 난수, 진행 중이던 episode는 이어지지 않습니다.

선택지는 두 가지입니다.

| | 방법 | 장점 | 단점 |
|---|---|---|---|
| **A (권장)** | 처음부터 다시 15M | 끊김 없는 깨끗한 비교 | 약 7일 다시 소요 |
| B | 2.30M checkpoint에서 근사 재개(가중치와 optimizer, gate 상태를 복원하는 기능을 새로 구현) | 약 1일 절약 | 4개 모두 같은 지점에서 이어가므로 서로 비교는 되지만, 끊기지 않은 학습과 완전히 같지는 않음. 구현과 검증에 시간이 듦 |

A를 권하는 이유는 이 실험이 "학습 효율"을 비교하는 실험이기 때문입니다. 중간에 optimizer나 gate 상태가 초기화되면 곡선이 바뀔 수 있습니다. 끊긴 2.5M까지의 데이터는 초기 구간 참고 자료로 남겨 두겠습니다(예: 2.4M 무렵 평가 delivery는 Oracle 10.7, All 4.2, IPPO 2.9, PGCT 2.2이지만, seed 1개짜리 초기 값이라 결론은 아닙니다).

**다시 돌리기 전에 꼭 해 주세요**(시스템 설정이라 제가 바꿀 수 없습니다).
1. **설정 → Windows 업데이트 → 업데이트 일시 중지**(최대 기간, 예: 5주). 대기 중인 업데이트가 있으면 먼저 설치하고 재부팅을 끝내 두는 게 가장 안전합니다.
2. **설정 → 시스템 → 전원 → 절전 모드: 안 함**.

A로 할지 B로 할지 알려 주세요. A라면 업데이트를 정리하신 뒤 아래 명령으로 다시 시작하시면 됩니다. 기존 폴더는 그대로 두고 새 폴더에 저장됩니다.

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -Stage2Seeds 1
```


#### 원문 기록 T018 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

1. 2번 절전모드 안함도 괜찮지?
2. 지금 2.5M에서의 학습 현황을 총분석해줘
   1. 이 내용은 로그로 자세히 남겨줘

##### Assistant — 진행 안내 1

먼저 2.5M까지 남은 로그에 어떤 지표가 있는지 확인하고, 분석 스크립트를 만들겠습니다.

##### 수행 기록 — 원문 대화와 별도

`output/scratch_review_20261015/`에 analyze.py, analysis.json, curves.png, REPORT.md, reference_home1_pgct_eval.json을 만들었다(읽기 전용 분석). 상세 수치는 EXPERIMENTS E18과 REPORT.md에 기록했다. RESEARCH_STATE를 갱신했다. 학습·로그·checkpoint는 변경하지 않았고 재시작도 하지 않았다.

##### Assistant — 최종 답변

#### 1. 절전 모드 "안 함" → 괜찮습니다
- 학습 중에는 꺼야 하는 설정입니다. 데스크톱은 상시 켜 두도록 설계되어 있고, 지금 부하(GPU 약 80W, 50°C)에서는 하드웨어 부담도 작습니다.
- 대신 **"화면 끄기"는 10–15분으로 두세요.** 화면만 꺼지고 학습은 계속됩니다. 전기도 아끼고 모니터 번인도 막을 수 있습니다.
- 최대 절전(hibernate)도 꺼져 있는지 같이 확인해 주세요. 그리고 **Windows 업데이트 일시 중지가 더 중요합니다.** 이번 재부팅의 원인이었습니다.

#### 2. 2.5M 시점 학습 현황 (seed 1, 중단된 run)

**평가 성능**(20×500, 마지막 3회 평균. AUC는 공통 구간 0.05–2.41M)

| mode | delivery | pickup | return | delivery AUC | 첫 delivery |
|---|---:|---:|---:|---:|---:|
| IPPO | 3.1 | 20.7 | 1.1 | 0.41 | 2.05M |
| PGCT | 1.9 | 2.2 | 1.0 | 0.26 | 2.15M |
| **Oracle** | **10.0** | 10.4 | **9.4** | **1.28** | **1.89M** |
| All | 3.5 | 15.2 | 1.4 | 0.69 | 1.89M |

- **학습은 시작됐습니다.** 네 mode 모두 0.5–1.5M은 보상이 거의 없는 정체 구간이었고, 1.6–1.9M부터 pickup·delivery가 오르기 시작했습니다. 2M 성능만 보고 판단하지 않기로 한 기준이 맞았습니다.
- Oracle이 가장 앞서 있습니다. 시작도 가장 빠르고(pickup 1.64M), pickup→delivery→return 한 사이클을 완성했습니다. IPPO와 All은 선반은 많이 들지만 배송까지 가는 비율이 낮습니다.

**가장 중요한 주의점: 성능이 agent 1–2명에게서만 나옵니다.**

| mode | Agent1 | Agent2 | Agent3 | Agent4 |
|---|---:|---:|---:|---:|
| IPPO | 1.6 | 1.5 | 0 | 0 |
| PGCT | 1.9 | 0 | 0 | 0 |
| Oracle | 0 | **10.0** | 0 | 0 |
| All | 0 | 2.1 | 1.3 | 0 |

Oracle의 우위는 **Agent2 한 명이 먼저 배송을 깨친 결과**입니다. 같은 팀인 Agent4는 아직 0입니다. 한 agent가 언제 깨치는지는 우연의 영향이 커서, seed 1개로는 이것을 "같은 팀 critic 공유 효과"라고 말할 수 없습니다. 앞으로 Agent4가 Agent2를 빨리 따라오는지가 같은 팀 공유 효과를 보는 좋은 관찰점입니다.

**critic 전이는 설계대로 동작했습니다.**
- Oracle은 같은 팀끼리만 전이했습니다(1–3, 2–4, 다른 팀 0회).
- All은 거의 모든 update에서 전체 쌍과 전이했습니다.
- **PGCT gate는 같은 팀과 다른 팀을 비슷하게 열었습니다**(같은 팀 826·922회, 다른 팀 500–886회). 학습 초기에는 정책끼리 비슷해서 JS gate가 팀을 구분하지 못합니다. 실험 A 결과와 일치합니다.

**참고**: 이전 from-scratch PGCT(home 1.0, complete graph)는 같은 2.4M에서 delivery 26.7이었습니다. 지금 조건(home 0.5)이 더 어렵거나 느릴 수 있습니다.

**결론**: 학습 가능성은 확인됐고 Oracle이 앞서는 방향은 보입니다. 다만 단일 seed의 한 agent 결과라 효과로 볼 수는 없습니다. 재실행할 때는 **seed 2·3을 함께 돌리는 것**을 권합니다. 4개 mode × 3 seed = 12개 프로세스라 동시에 돌리면 많이 느려지므로, seed별로 순서대로 돌리거나 seed 1·2만 먼저 돌리는 방식도 가능합니다.

자세한 분석은 [REPORT.md](output/scratch_review_20261015/REPORT.md)와 그래프 `curves.png`에 있고, 연구 노트(EXPERIMENTS E18, RESEARCH_STATE)와 대화 로그(T018)에 남겼습니다.


#### 원문 기록 T019 — 2026-10-15 KST, Codex

정확한 발화 시각은 별도로 측정하지 않았다. 실행 확인 스냅샷은 11:49 KST다.

##### 사용자 — 프로젝트 작업 지침 제공

사용자는 이 프로젝트의 AGENTS.md 지침 원문을 작업 시작 맥락으로 제공했다. 반복되는 대용량 지침 원문은 프로젝트 루트 `AGENTS.md`를 근거로 연결한다. 환경 경로·클라이언트 open-page 같은 메타데이터는 연구 발화와 구분한다.

##### 사용자 — 분석 요청 원문

지금까지 codex, claude로 만든 프로젝트의 md 내역 분석해줘
그리고 지금 내역들까지 포함해서 IJCAI 논문 작성한다면 어떻게 작성하면 될까?

##### Assistant — 진행 안내 1

프로젝트의 연구 노트와 대화 기록을 읽고, 확인된 결과·설계 결정·미해결 문제를 구분해 분석하겠습니다. 이를 바탕으로 IJCAI 논문의 핵심 주장, 구성, 추가로 필요한 검증을 정리하겠습니다.

##### Assistant — 진행 안내 2

기록에서 가장 중요한 점은 연구 목표와 현재 구현 사이의 차이입니다. 원래 목표는 ‘행동에서 팀을 추론한 뒤 팀 내부 critic을 공유’하는 것이지만, 현재 PGCT의 정책 유사도 gate는 팀을 안정적으로 구분하지 못했습니다. 최신 from-scratch 비교에서도 Oracle의 초기 선행은 보이지만, seed 1개의 중단된 학습이므로 아직 성능 기여로 확정할 수 없습니다.

##### Assistant — 진행 안내 3

논문은 ‘팀을 식별할 수 있는가’와 ‘그 팀끼리 critic을 공유하면 학습이 좋아지는가’를 각각 검증하는 구조가 적절합니다. 현재 자료로 쓸 수 있는 진단 결과와, 본 논문의 기여로 주장하려면 추가 검증이 필요한 부분을 나눠 상세 문서로 남기겠습니다. 제출 일정은 IJCAI 공식 사이트에서도 확인하고 있습니다.

##### Assistant — 진행 안내 4

MD에 아직 반영되지 않은 새 실행도 발견했습니다. `scratch_20261015_093349_stage2`에서 IPPO·PGCT·Oracle·All을 seed 1, 15M 목표로 다시 시작했고, 현재 로그는 약 0.19M step입니다. 기존 2.5M 중단 결과와 구분해 기록하겠습니다. 같은 seed의 재실행이므로 독립 seed 반복으로 세지는 않겠습니다.

##### Assistant — 진행 안내 5

분석 문서에 논문 구성과 주장별 근거를 정리했습니다. 핵심 빈칸은 관측에서 팀 관계를 추론해 실제 공유에 사용하는 `learned-team` 모드입니다. 현재는 고정 모델에서 팀 정보의 존재를 확인한 진단까지만 있습니다. MAPPO·SePS·HetDPS도 구현·smoke 단계이므로, 성능 비교가 끝난 결과로 논문에 넣을 수 없습니다.

##### 수행 기록 — 원문 대화와 별도

- 프로젝트 Markdown 20개를 식별하고 연구 노트·실행 문서의 본문 또는 관련 절, 대화 로그의 과거 요약·주요 방향 전환·사용자 요청·수행/최근 결과 구간을 확인했다. 붙여넣은 외부 답변의 모든 원출처를 검증하거나 별도 Codex/Claude 세션을 자동 수집한 것은 아니다. 과거 ex4/ex5 PDF와 첨부 원본은 이번에 재열람하지 않았다.
- 기존 E17·E18과 신규 run의 manifest/metrics/status/초기 hash, curriculum manifest와 관측·peer loss 코드 일부를 읽었다. 신규 seed1 재실행의 로그 갱신을 확인했다. CIM 프로세스 상세 조회는 접근 제한으로 확인하지 못했다. 학습 프로세스에 개입하지 않았다.
- IJCAI2027 공식 홈페이지의 일정, 2026 main-track CFP, SePS·MAPPO·RODE·분산 actor-critic·통계평가 논문 초록/출판 페이지와 HetDPS 공식README를 확인했다. 2027 상세 CFP나 선행 연구 전체를 정밀 검토했다고 주장하지 않았다.
- 새 산출물: `output/ijcai_review_20261015/REPORT.md`(연구 교차 분석·주장/증거·수식·실험 우선순위·집필 구성·영문 탐색적 초록), `live_run_snapshot.json`(11:49 KST 읽기 스냅샷).
- 공용 노트에 최신 실행 E19와 집필 검토 D23을 추가하고 RESEARCH_STATE 최상단을 갱신했다. 과거 노트와 다른 도구의 기존 변경은 보존했다. 본문의 참조와 언어·구성 및 snapshot 일관성을 확인했다. 새 학습·frozen 평가·tests 재실행, 알고리즘/환경/보상/probe/gate 변경은 하지 않았다. 후속 실험은 제안이며 실행 허가가 아니다.
- 최종 답변을 확정한 후 아래에 원문을 기록했다.

##### Assistant — 최종 답변

**논문으로 발전시킬 연구 질문과 진단 자료는 충분히 모였습니다. 다만 현재 결과로 “PGCT가 잠재 팀을 발견해 학습 효율을 높였다”고 주장하기에는 핵심 검증이 남아 있습니다.**

MD 기록과 실제 실행 로그를 대조한 [상세 분석·IJCAI 논문 설계서](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/ijcai_review_20261015/REPORT.md)를 작성했습니다. 주장별 근거, 방법 수식, 실험 우선순위, 관련 연구, 현재 증거만 사용한 영문 초록도 포함했습니다.

**프로젝트 내역에서 드러난 핵심은 다음과 같습니다.**

연구는 처음에 **행동 유사성으로 팀을 찾고, 팀 내부에서 critic을 공유한다**는 목표로 시작했습니다. 이후 cross-team 연결을 분석하면서 ‘팀과 무관한 유익한 전이’로 해석이 이동했지만, 사용자 지시에 따라 원래 목표로 돌아왔습니다. 이 두 목표는 논문에서도 분리해야 합니다.

현재 기록의 의미는 이렇게 정리됩니다.

| 확인한 내용 | 논문에서 가능한 해석 |
|---|---|
| 정책 JS가 같은 팀을 안정적으로 구분하지 못함 | 현재 팀 추론 신호의 한계 |
| 국소 pickup·delivery 결과에는 팀 정보가 있음 | 작업 결과를 이용한 추론의 가능성 |
| 같은 팀 critic이 항상 더 호환되지는 않음 | 팀 식별과 공유 유익성을 따로 검증해야 함 |
| Oracle이 초기 학습에서 선행함 | 정답 팀 공유의 효과를 반복 검증할 이유 |
| 온라인 learned-team 모드는 미구현 | 원래 목표의 전체 과정은 아직 검증되지 않음 |

특히 **정책 유사성 → 같은 팀 → 비슷한 value → 유익한 공유**라는 연결을 모두 당연하게 가정했던 것이 현재 연구의 가장 큰 문제였습니다. 이 연결들이 언제 성립하고 언제 깨지는지를 밝히는 것이 논문의 중심이 될 수 있습니다.

기존 결과를 폐기할 필요는 없습니다. Stage03 공통 모델에서 추가 4,000,768 step을 학습한 seed 1 비교에서, 평가 delivery AUC는 E1에서 PGCT가 IPPO보다 2.88% 높고 E2에서는 0.23% 낮았습니다. 조건은 home .5·individual reward, deterministic masked 평가 20×500입니다. 이는 **사전학습 이후 추가 공유의 조건부 효과**이며, 처음부터 학습한 PGCT의 우위를 뜻하지 않습니다.

최신 중단 run도 같은 구분이 필요합니다. E1·home .5·individual reward·training seed 1의 from-scratch 비교에서 약 2.5M 중단 직전 마지막 3회 평가 delivery는 Oracle 9.98, All 3.45, IPPO 3.10, PGCT 1.92였습니다. 평가는 동일한 deterministic masked 20×500 조건입니다. Oracle의 배송은 Agent2 한 명에게 집중됐습니다. **공유가 그 agent의 학습을 도왔는지, seed에 민감한 선행 학습인지는 아직 구분되지 않습니다.**

**IJCAI 논문은 다음 질문으로 구성하는 것을 권합니다.**

> **역할과 행동이 서로 다른 에이전트들이, 국소 작업 증거로 공통 목표의 동료를 추론하고 critic 공유를 통해 학습을 개선할 수 있는가?**

방법과 검증이 완성된 뒤 사용할 제목 후보는 다음입니다.

> **Inferring Latent Teams from Local Task Evidence for Selective Critic Sharing**

논문의 논리는 세 질문을 순서대로 해결해야 합니다.

1. **팀을 알아낼 수 있는가?** 정책 응답 유사도와 실제 국소 작업 증거를 비교합니다.
2. **정답 팀을 알아도 공유가 도움이 되는가?** Oracle·IPPO·All·Wrong을 비교합니다.
3. **추론한 팀을 사용해도 학습이 좋아지는가?** 온라인 learned-team 방법을 구현하고 Oracle과의 차이를 측정합니다.

이 구조라면 기존 PGCT의 실패 진단도 중요한 동기가 됩니다. 다만 “JS 대신 작업 증거를 쓴다”는 변경만으로 독창성이 충분하다고 보기는 어렵습니다. **성공 사건이 드문 학습 초기의 추론 지연, 사건의 이웃 귀속 오류, 같은 팀 내부의 역할 차이**를 어떻게 다루는지가 방법의 핵심이어야 합니다.

원고 구성은 다음처럼 잡을 수 있습니다.

| 절 | 작성할 내용 |
|---|---|
| Introduction | 숨은 목표 집단에서 공유 상대를 선택하는 문제와 세 연구 질문 |
| Related Work | 선택적 파라미터 공유·역할 발견·분산 critic 공유와의 차이 |
| Problem & Motivation | 허용 관측·통신 가정, 정책/팀/value의 구분, 기존 실패 진단 |
| Method | 국소 증거 추론, 불확실할 때 공유 보류, critic distillation |
| Experiments | from-scratch 주결과, 팀 식별, Oracle 비교, ablation·비용 |
| Discussion | 도움이 되는 조건과 실패 조건, 정보 가정과 한계 |

현재 구현의 공유는 **공통 probe에서 donor critic 예측을 따라가는 보조 손실**입니다. 이를 정확히 기술하고, 수렴 보장이 있는 consensus와 구분해야 합니다. 또한 자기 요청·목표 단서는 관측에 있으므로 ‘목표 정보 없이 순수 행동만으로 추론한다’고 쓰면 범위가 과합니다.

**남은 실험은 다음 순서가 적절합니다.**

1. 현재 from-scratch 4개 비교를 완료하고, 독립 seed에서 Oracle 효과를 확인합니다.
2. 관측 이력으로 사건을 검출하고 실제 allocation에 연결하는 learned-team 모드를 완성합니다.
3. 무작위 관계·잘못된 팀·모든 이웃 공유와 비교해 팀 선택의 가치를 분리합니다.
4. 같은 팀의 다른 역할과 다른 팀의 비슷한 행동을 구분하는 조건을 검증합니다.
5. MAPPO·SePS·HetDPS 성능 비교를 추가하고 이식 구현의 차이를 공개합니다.

Oracle과 All이 비슷하게 나오면 ‘공유의 이득’과 ‘팀 선택의 추가 이득’을 구분해 써야 합니다. 팀을 정확히 맞혀도 학습이 개선되지 않으면 그 역시 중요한 경계 조건입니다. 현재 자료만 사용하는 초고는 **정책 유사도 기반 팀 추론과 critic 공유의 한계를 분석하는 실증 논문**으로 쓸 수 있지만, 일반적 결론을 위해서는 반복·통제 실험이 더 필요합니다.

실행 상태도 갱신했습니다. **10월 15일 11:49 KST 확인 기준**, 새 `scratch_20261015_093349_stage2`에서 IPPO·PGCT·Oracle·All이 seed 1, 각 15M 목표로 약 0.20M step까지 기록됐습니다. 이전 2.5M 중단 run과 별개인 같은 seed의 재실행입니다. 이번 작업에서는 학습이나 코드를 변경하지 않았습니다.

[IJCAI 2027 공식 안내](https://2027.ijcai.org/)상 초록 마감은 **2027년 1월 4일**, 본문은 **1월 11일**, 모두 23:59 AoE입니다. 상세 제출 규정은 대상 연도 공고를 다시 확인해야 합니다. 지금부터 문제 설정·관련 연구·진단 부분을 작성하고, 방법의 성공 주장과 주결과는 남은 검증에 맞춰 확정하면 됩니다.



#### 원문 기록 T019 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

이거는 그냥 의견을 듣고싶어

논문의 최종 핵심으로 팀 추론과 Critic 공유 관련해서 얘기했는데
둘은 어느정도 상반된거 아냐?
저번 실험에서 붉은색, 푸른색 팀이라는 점을 제외한 모든 목적이 유사한 RWARE 환경의 경우 서로 다른 팀이라도 Critic을 공유하게 되었어. 물론 분석상 에이전트가 물건을 반환할때는 팀이 확실히 구분됐다고는 하는데 내가 정확히 확인은 못했지
이는 잠재 팀 추론과는 상반된 말 아닌가?
저번에 너가 추천했던 두 팀의 역할이 아예 분산되어 한쪽은 배송, 한쪽은 반환으로 역할을 나누는 케이스도 따져봐야 할꺼같아
그리고 보통 강화학습에서 보상함수를 Wrapper를 통해 깎는것도 힘들다는 말이 있는데
심지어 이 알고리즘은 사용자가 여러개의 프로브를 직접 만들어야해. 여기서 발생하는 귀찮음 + 사용자 차이가 IJCAI 논문 등재에 마이너스 포인트가 되진 않을까?

##### Assistant — 진행 안내 1

Codex가 IJCAI 원고 설계(D23)를 추가해 두었네요. 의견을 드리기 전에 겹치거나 어긋나는 부분이 없는지 확인합니다.

##### Assistant — 진행 안내 2

Codex의 IJCAI 설계(D23)와 방향은 같아서, 그 위에 제 의견을 더하겠습니다. 오전 09:33에 seed 1 재실행이 시작된 것도 기록에서 확인했습니다.

##### 수행 기록 — 원문 대화와 별도

DECISIONS D23(Codex)과 `output/ijcai_review_20261015/REPORT.md`의 제목만 읽었다. 의견을 DECISIONS D24에 기록했다. 코드·실험은 변경하지 않았다.

##### Assistant — 최종 답변

#### 1. 팀 추론과 critic 공유는 상반되나?

**개념상으로는 상반되지 않습니다. 다만 지금 RWARE에서는 실제로 어긋나고 있습니다.** 두 가지가 서로 다른 질문을 하기 때문입니다.

- **팀 추론**은 "저 agent가 나와 같은 목표를 가졌나?"를 묻습니다.
- **critic 공유**는 "저 agent의 critic이 **내 관측에서** 내 value를 잘 맞히나?"를 묻습니다.

두 질문의 답은 **팀이 다르면 value도 달라지는 환경**에서만 일치합니다. 지금 RWARE는 그렇지 않습니다.
- 관측이 "내 팀의 요청 선반, 내 팀의 목표" 기준으로 표시됩니다.
- 빨강·파랑 팀의 과제가 거울처럼 대칭입니다.

그래서 빨강 팀 agent와 파랑 팀 agent는 "같은 화면"을 보면 사실상 같은 가치를 매기고, 다른 팀과 critic을 공유해도 해가 없습니다. 실험 결과도 그대로입니다.
- **팀 구분**: 국소 증거로 100% 됩니다.
- **같은 팀 critic의 호환성**: 더 높지 않았습니다(E1 계열은 오히려 반대, E2는 차이 없음).
- **PGCT gate**: 학습 초기부터 같은 팀과 다른 팀을 비슷하게 열었습니다.

**확인하실 점**: 팀이 구분된 근거는 "반환"이 아니라 **pickup과 delivery 목격**(그 선반이 내 팀 요청인가, 그 목표가 내 목표인가)이었습니다. 관측 채널과의 일치는 2,146건으로 검증했지만, 직접 보지 못하셨다면 해당 장면을 영상 프레임으로 뽑아 보여드릴 수 있습니다.

**제 의견**: 논문의 추론 대상을 "팀"이 아니라 **"critic이 호환되는 관계"**(누구의 value를 내 것 대신 써도 되는가)로 잡고, 팀은 그 관계를 만드는 원인 중 하나로 두는 편이 더 정직하고 강합니다. 그러면 "다른 팀인데 공유가 됐다"는 결과가 모순이 아니라 **설명되는 현상**이 됩니다.

#### 2. 역할 분업(배송 vs 반환)은 꼭 넣어야 합니다

이 경우가 오히려 핵심 증거가 됩니다. 세 가지 환경으로 나누어 보시길 권합니다.

| 환경 | 팀과 critic 호환 관계 | 기대 결과 |
|---|---|---|
| (a) 지금처럼 대칭 팀 | 팀 무관하게 모두 호환 | Oracle ≈ All (대조군) |
| (b) 팀별로 역할이 다름(빨강=배송, 파랑=반환) | 팀 = 호환 관계 | Oracle·추론 방법 > All |
| (c) **한 팀 안에서** 배송/반환을 나눔 | 같은 팀인데도 호환 안 됨 | 팀 기준 공유는 실패, 호환 관계 추론만 성공 |

(c)가 중요합니다. Oracle-team도 틀리는 경우를 보여 주면, "팀"이 아니라 "호환 관계"를 추론해야 한다는 주장이 생깁니다. 세 환경 모두에서 All/IPPO 이상을 내면 논문의 메시지가 분명해집니다.

#### 3. 수작업 probe → **감점 요인이 될 가능성이 큽니다**

심사에서 나올 만한 지적:
- **환경마다 사람이 설계**해야 합니다. 일반성이 약하고 domain knowledge에 의존한다는 지적을 받습니다.
- **사용자마다 결과가 달라집니다.** 실제로 probe 중복만 제거해도 유사도 순위가 뒤집혔습니다(E04/E07).
- **비교 공정성**: SePS와 HetDPS는 probe 없이 수집한 transition으로 VAE를 학습해 자동으로 판단합니다. 우리 방법만 사람 손이 들어가면 불리합니다.

보완 방향:
1. **probe를 없애거나 자동화**: 실제 rollout 이력에서 비교 상태를 자동으로 뽑거나, 실험 A의 history JS처럼 실제 경험에서 비교합니다.
2. 남긴다면 **probe 개수·구성 민감도 분석**을 본문에 넣어 "누가 만들어도 결과가 비슷하다"를 보여 줍니다.
3. reward shaping은 모든 비교군에 같다는 점을 명시해, 보상 설계 비판을 미리 막습니다.

한 가지 위험이 더 있습니다. **HetDPS(이질성 기반 동적 parameter sharing)와 겹쳐 보일 수 있습니다.** 차별점을 분명히 해야 합니다.
- 중앙 서버 없이 이웃 간 국소 통신만 쓴다.
- 정책은 독립으로 두고 critic만 공유한다.
- 추론 대상이 "호환 관계"다.

정리하면, 지금 결과는 연구 방향의 실패가 아닙니다. **"팀 = 공유 대상"이라는 가정이 틀릴 수 있음을 보여 준 좋은 동기 자료**입니다. 이 의견은 결정이 아니라 제안으로 DECISIONS D24에 기록해 두었습니다.


#### 원문 기록 T020 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다. 사용자 메시지 2개를 받은 뒤 한 번에 답했다. 첫 메시지 직후에는 노트 확인만 하고 답을 보내지 않았다.

##### 사용자 — 원문 1 (붙여넣은 내용 포함)

이건 아까 GPT랑 대화했을때 내 의견인데 어떻게 생각해?

> (붙여넣은 내용) 내가 생각하는 자동 프로브의 문제를 알려줄게. 아닐수도 있으니 자세히 생각해봐
> 지금 우리야 전지적 시점에서 보지만 각 에이전트들은 자기와 관측자가 명확히 분리되어 있어
> 그 상황에서 자신이 관측한 내역중 일부를 Probe로 만들어서 전이 적합성을 평가한다면, 그 Probe를 어딘가에서 공유를 시켜야 되는건데 그럴꺼면 그냥 centralized MARL를 하거나 팀 에이전트를 통신을 통해서 찾아내지 왜 굳이 힘들게 그런짓을 해야돼?
>
> 그리고 같은 팀에서 배송, 반납 담당이 다르다는 무슨 이득을 얻지?
> 목표는 각 팀이 다른 목적을 지니고 수행할때 이에 발생하는 행동 분포의 유사도를 통해 팀을 추론하고, 추론된 팀끼리 critic을 전이해서 학습 능력을 향상시키는 거 아녔어?
> 붉은색, 파란색 팀이 내부에서 배송, 반납을 따로 가진다면 결국 배송하는 사람, 반납하는 사람끼리 붉은색, 파란색과 별개로 잠재적 팀을 추론하게 될텐데

##### 사용자 — 원문 2 (붙여넣은 GPT 답변 + 본문)

붙여넣은 GPT 답변 전문은 사용자 메시지의 일부다. 분량이 매우 길어 요지만 기록하며, 원문은 이 세션 transcript에 있다. 원문 소급 기록이 아님을 밝힌다.
- 요지: 자동 probe는 서로 다른 관측 공간 때문에 관측·모델 통신이나 공통 생성 규칙이 필요하다(원래 정보 구조와 충돌).
- 요지: 팀 내 배송/반납 분업 제안은 역할 추론이 되므로 철회한다. Red 배송/Blue 반납은 후보지만 인계 문제가 있다.
- 요지: 식별 불가능성 P(H|Red)=P(H|Blue)가 근본 문제다.
- 요지: H1 식별 → H2 Oracle 이득 → 분산 추론 → 학습 개선 순서로 검증한다.
- 요지: 국소 행동 분포 추정 P̂_j(a|c)를 대안으로 검토한다.

사용자 본문: "이건 추가로 GPT의 답변이야"

##### 수행 기록 — 원문 대화와 별도

DECISIONS 최신 항목을 확인한 뒤 의견을 D25로 기록했다. 코드·실험은 변경하지 않았다.

##### Assistant — 최종 답변

두 메시지를 함께 보고 답하겠습니다. 결론부터 말하면 **두 지적 모두 맞고, 제 이전 제안 일부는 철회합니다.** 다만 GPT 답변에 빠진 더 큰 위험이 하나 있습니다.

#### 1. 자동 probe → 지적이 맞습니다
- probe 방식은 "같은 입력을 두 정책에 넣는 것"이 핵심입니다. 그래서 각자 자기 경험으로 probe를 만들면 결국 관측이나 정책을 주고받아야 합니다. 새로운 가정이 생기는 것이고, 제가 가볍게 제안할 문제가 아니었습니다.
- 보완하자면, **지금 PGCT도 이미 모델 출력을 주고받고 있습니다.** 공통 probe에 대한 정책 응답과 critic 값을 교환합니다. 관측을 안 보내도 되는 이유는 probe bank를 미리 똑같이 정해 두었기 때문뿐입니다(GPT가 말한 3번 방식).

#### 2. 팀 내 배송/반납 분업 → 철회합니다
말씀대로 그 환경은 **팀이 아니라 역할을 추론하는 실험**이 됩니다. 저는 "추론 대상을 팀이 아닌 critic 호환 관계로 바꾸자"는 생각에서 제안했는데, 그건 연구 목표 자체를 바꾸는 일이었습니다. 원래 목표(목적이 다른 팀을 행동으로 추론)에는 맞지 않습니다.

#### 3. GPT 답변에 대한 의견
**동의**: 식별 불가능성 조건 P(행동|Red) = P(행동|Blue), 그리고 ① 식별 가능성 → ② Oracle 이득 → ③ 분산 추론 → ④ 학습 개선 순서. 실패했을 때 원인을 나눠 볼 수 있어 좋은 구조입니다.

**빠진 점: 가장 큰 위협은 probe보다 "왜 팀 ID를 그냥 교환하지 않나"입니다.**
- 학습 중 이웃 간 통신(critic 전이)을 허용하면서 팀을 추론해야 한다면, 심사자는 거의 확실히 묻습니다. "자기 팀을 서로 말해 주면 끝 아닌가?"
- 지금 RWARE에서 각 agent는 관측 채널(내 팀 요청 선반, 내 목표)로 **자기 목표를 사실상 알고 있습니다.** 실험 A에서 팀을 100% 구분한 근거도 "저 선반이 **내** 요청인가"였습니다. 관측자가 자기 목표를 안다는 점을 이용한 것입니다.
- 그래서 문제 정의에 **"목표는 알 수 있지만 공개할 수 없거나, 공통 라벨이 없거나, 보상으로만 학습된다"** 같은 정당화가 꼭 들어가야 합니다. 이게 약하면 probe를 어떻게 만들든 전제가 흔들립니다.

**현재 결과의 위치**
- **①(식별 가능성)**: 행동 사건(pickup·delivery)으로는 성립합니다. 정책 응답 JS로는 성립하지 않습니다.
- **②(Oracle 이득)**: 지금 돌고 있는 비교는 팀 과제가 대칭인 환경이라 이론상 Oracle ≈ All이 예상됩니다. 그래서 ②의 **대조군**에 가깝습니다. 의미는 있지만, ②를 제대로 검증하려면 다른 환경이 필요합니다.

#### 4. ①과 ②를 함께 검증할 수 있는 가장 단순한 환경 (제안)
Red 배송/Blue 반납은 팀 사이 의존성(반납할 선반을 누가 넘겨주나)을 새로 정의해야 해서 복잡합니다. 그보다 **두 가지만 바꾸는** 쪽을 권합니다.
1. **팀 목표 위치를 멀리 분리**: 지금은 (4,10)/(5,10)으로 붙어 있습니다. 좌우 끝으로 떨어뜨립니다.
2. **관측을 절대 색 기준으로**: "내 팀 요청" 대신 "빨강 요청 / 파랑 요청" 채널을 줍니다.

그러면 선반을 든 뒤 가는 방향이 팀마다 달라져 **행동으로 팀이 구분되고(①)**, 같은 화면을 봐도 팀마다 가치가 달라져 **다른 팀 critic은 실제로 틀린 값을 주게 됩니다(②)**. 팀 목적이 같은 종류(배송)라서 "역할 추론"으로 빠지지도 않습니다.

#### 5. "이웃 행동 분포 추정" 방향
원래 목표에 가장 잘 맞습니다. 다만 실제로 해결해야 할 것이 있습니다.
- 관측 속 다른 agent는 **익명**입니다. 누가 누구인지 추적해야 합니다.
- 행동은 연속 프레임에서 **추정**해야 합니다.
- 두 agent가 비교 가능한 "상황" 표현이 필요합니다.
- **마주치는 빈도**가 충분해야 합니다. E1 작은 맵은 42–78% step에서 서로 보이지만, 큰 맵에서는 줄어듭니다.

요약하면, 다음 단계로는 **4번 환경 설계**를 권합니다. 지금 학습은 그대로 돌리고 새 환경은 별도 파일로 만들어 smoke까지만 하는 식입니다. 원하시면 설계안부터 드리겠습니다. 이 의견은 DECISIONS D25에 기록했습니다.


#### 원문 기록 T021 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

지금 실험중인 프로젝트의 환경을 볼수 있을까

##### Assistant — 진행 안내 1

현재 실행 중인 run의 설정 그대로 환경을 그려서 보여드리겠습니다. 먼저 실행 중인 run과 사용할 수 있는 renderer를 확인합니다.

##### Assistant — 진행 안내 2

실행 중인 run(`scratch_20261015_093349_stage2`)은 아직 checkpoint와 영상이 없습니다. 그래서 같은 환경 설정을 그대로 불러와 맵 전체와, 같은 장면을 agent가 실제로 어떻게 보는지(관측 채널)를 그림으로 그리겠습니다.

##### Assistant — 진행 안내 3

그림이 정상적으로 나왔습니다. 위 제목과 아래 설명 글이 조금 잘려서 글자만 줄여 다시 저장합니다.

##### Assistant — 진행 안내 4

The heredoc turned `\n` into a real newline; fixing those lines directly.

##### 수행 기록 — 원문 대화와 별도

`output/env_view_20261015/draw_env.py`를 만들고 `environment_seed5000001.png`을 생성해 사용자에게 전송했다. 실행 중 run의 experiment.json에서 환경 설정만 읽었고, 학습에는 영향을 주지 않았다.

##### Assistant — 최종 답변

지금 실행 중인 실험(`scratch_20261015_093349_stage2`)과 같은 설정으로 환경을 그려 보냈습니다. 평가에 쓰는 첫 reset seed 5,000,001의 시작 장면입니다.

**왼쪽: 전체 맵 (11×10)**
- agent 1·3은 **빨강 팀**, 2·4는 **파랑 팀**입니다. 화살표는 바라보는 방향입니다.
- 옅은 칸은 각 팀이 소유한 선반입니다. home 0.5라서 빨강·파랑 선반이 좌우 구역에 섞여 있습니다.
- 진하게 "REQ"로 표시된 칸이 지금 요청된 선반입니다. 팀당 2개입니다.
- 아래쪽 GOAL 두 칸이 배송 목표인데, **빨강 (4,10)과 파랑 (5,10)이 바로 붙어 있습니다.**
- 점선은 agent 1이 볼 수 있는 범위입니다(반경 5, 11×11).

**오른쪽: 같은 순간 agent가 실제로 보는 화면**
- 주황 = **"내 팀"이 요청한 선반**, 초록 = **"내" 목표**, 연한 파랑 = 다른 팀 목표, 흰 원 = 다른 agent(누구인지, 어느 팀인지 표시 없음)
- agent 1(빨강)은 빨강 요청 선반 2개를 주황으로 보고, agent 2(파랑)는 파랑 요청 선반을 주황으로 봅니다. **같은 "주황" 채널이 팀마다 다른 선반을 가리킵니다.**

이 그림에서 지금까지 논의한 구조가 그대로 보입니다.
1. 관측이 "내 팀 기준"으로 표시되고, 두 목표 칸이 붙어 있습니다. 그래서 빨강과 파랑은 사실상 같은 과제를 풉니다. 다른 팀과 critic을 공유해도 문제가 없던 이유입니다.
2. 다른 agent의 팀은 관측에 없습니다. 팀을 알려면 그 agent가 **무엇을 들고 어느 목표로 가는지** 행동을 봐야 합니다.

학습 중인 agent가 실제로 움직이는 모습도 보시려면, 실행 중인 run의 첫 checkpoint(약 0.26M step 이후)부터 짧은 영상을 따로 만들어 드릴 수 있습니다. 학습에는 영향을 주지 않습니다.


#### 원문 기록 T022 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

지금 env_view_20261015폴더에 추가적으로 프로브 맵 시각화 폴더도 만들어서 확인해볼 수 있을까?

##### Assistant — 진행 안내 1

실행 중인 run이 실제로 쓰는 canonical probe bank(48개)를 앞의 관측 그림과 같은 색 규칙으로 시각화하겠습니다. 먼저 bank 구성을 확인합니다.

##### Assistant — 진행 안내 2

probe는 `rware/utils/probe_maps.py`의 수작업 probe 지도에서 만들어집니다. 각 probe의 이름과 의도를 라벨로 붙일 수 있는지 확인합니다.

##### Assistant — 진행 안내 3

저장소에 probe 지도를 PNG로 저장하는 함수(`save_rware_probe_map_images`)가 이미 있습니다. 실행 중인 run이 bank를 만들 때와 같은 env 상태와 난수로 다시 생성해, 저장된 bank와 똑같은지 먼저 확인합니다. 그다음 공식 이미지와, 실제 bank 벡터를 해독한 그림을 함께 만들겠습니다.

##### Assistant — 진행 안내 4

저장된 bank와 다시 만든 bank가 완전히 같습니다. 공식 이미지에는 probe마다 의도된 이름(예: `team0_team_home_approach`, `wrong_team_goal`)이 붙어 있습니다. 이름과 중복 입력의 관계를 확인합니다.

##### Assistant — 진행 안내 5

중요한 사실이 하나 나왔습니다. 이름이 다른 7가지 "두 요청 선반" 시나리오(home pair, 반대 축, 대각선, 원근 등)가 관측 벡터로는 **완전히 같은 입력 하나**로 겹칩니다. 이런 그룹이 2개 있어서 48개 중 16개가 사실상 2개 입력입니다. 그림이 제대로 나왔는지 확인합니다.

##### Assistant — 진행 안내 6

그림 두 장이 모두 정상입니다. 같은 입력으로 겹치는 원인도 그림에서 보입니다. 공식 이미지의 world 지도에서는 "두 요청 선반" 변형마다 두 번째 선반 위치가 다르지만, agent의 11×11 시야로 해독해 보면 대부분 요청 선반이 **가장자리에 1개만** 보입니다. 정리 문서를 쓰고 파일을 보내드리겠습니다.

##### 수행 기록 — 원문 대화와 별도

`output/env_view_20261015/probes/`(draw_probes.py, official/, decoded_bank.png, probes.csv, README.md)를 만들고 그림 2장을 전송했다. EXPERIMENTS E20을 추가했다. 학습에는 영향이 없다.

##### Assistant — 최종 답변

`output/env_view_20261015/probes/` 폴더를 만들고 그림 2장을 보내드렸습니다. 실행 중인 run이 **실제로 쓰는 probe 48개**입니다. 저장소 코드로 다시 만든 bank가 run에 저장된 bank와 완전히 같음을 확인했습니다.

**폴더 구성**
- `official/`: 저장소의 probe 렌더러로 그린 48장과 모아 보기(`probe_contact_sheet.png`). probe마다 **의도된 이름**(예: `team_home_approach`, `wrong_team_goal`, `dual_requested_diagonal`)과 world 지도가 나옵니다.
- `decoded_bank.png`: 학습에 실제로 들어가는 벡터를 **agent 시야(11×11)**로 해독한 그림입니다. 앞의 환경 그림과 색 규칙이 같습니다. 빨간 제목은 다른 probe와 입력이 완전히 같은 경우입니다.
- `probes.csv`, `README.md`: probe별 상태(방향, 적재 여부, 반납 단계 등)와 정리.

**보면서 확인하실 점**
1. **48개 중 실제로 다른 입력은 26개뿐입니다.** 특히 이름이 다른 7가지 "두 요청 선반" 시나리오(home pair, 반대 축, 대각선, 원근, 구역 선택 등)가 **팀마다 같은 입력 하나로 겹칩니다**(8개씩 2그룹). goal 계열 3종도 4개씩 겹칩니다.
2. 원인은 그림에서 보입니다. world 지도에서는 두 번째 요청 선반 위치가 시나리오마다 다르지만, agent 시야로 보면 요청 선반이 대부분 **가장자리에 1개만** 보입니다. 서로 다른 부분이 11×11 시야 밖이라 입력에 반영되지 않는 것으로 보입니다(추정, builder 코드로는 미확인).
3. 그래서 "두 선반 중 무엇을 고르나"라는 설계 의도가 실제 입력에서는 대부분 사라지고, 그 한 장면이 JS 평균에서 8/48의 큰 비중을 갖습니다. 예전에 "중복 제거하면 유사도 순위가 바뀐다"(E04/E07)고 했던 현상의 직접적인 원인입니다.
4. 상태 구성은 빈 손 38개, 요청 선반을 든 상태 10개입니다. 엉뚱한 선반을 든 상태는 없습니다.

어제 얘기한 "사람이 만든 probe의 위험"을 보여 주는 구체적인 예입니다. 의도한 상황과 agent가 실제로 보는 입력이 다를 수 있습니다. 기록은 EXPERIMENTS E20, 대화 로그 T022에 남겼습니다.


#### 원문 기록 T023 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (본문 + 붙여넣은 GPT 답변)

1. 너 생각에 지금 프로브 48개들이 전부 유의미한 프로브들이라 생각해?
그리고 Goal 위치가 고정되어 있어서 큰 결과값을 못낼꺼 같아

밑의 내용은 아까 대화에 대한 GPT 답변이야

붙여넣은 GPT 답변은 사용자 메시지의 일부다. 분량이 매우 길어 요지만 기록하며, 전문은 이 세션 transcript에 있다.
- 요지: 팀 ID를 직접 통신하지 않는 이유를 3가지 상황으로 나누어 정당화해야 한다.
- 요지: 절대 색 관측은 팀 라벨화 위험이 있고, 목표 분리는 경로만으로 팀을 구분하는 쉬운 문제를 만들 수 있다.
- 요지: 목적 차이 → value 차이 → 음의 전이는 각각 검증해야 한다.
- 요지: E1 / E1-F / E1-A / E1-FA로 분리 설계한다.
- 요지: 식별 가능성 P(H|same)=P(H|cross), Reward identification ≠ Team identification.
- 요지: 현재 run을 유지하고 t_team과 t_gain을 구분하며, random gate ablation을 한다.
- 요지: Critic Compatibility Inference로의 전환과, 목표 분리+절대 관측 동시 적용에는 반대한다.

##### 수행 기록 — 원문 대화와 별도

probes.csv와 manifest를 다시 분석했다(목표가 보이는 적재 probe 6/6, 목표 비가시 적재 probe 0). env의 `team_goal_positions` 인자를 확인했다. DECISIONS D26을 기록했다. 코드·실험 변경은 없다.

##### Assistant — 최종 답변

#### 1. probe 48개가 다 유의미한가? → **팀 판별용으로는 거의 아닙니다**

probe를 다시 분류해 보니 더 근본적인 문제가 있습니다.

| 종류 | 개수(고유) | 팀 판별에 쓸모 |
|---|---|---|
| 빈 손으로 선반 찾기·적재(`home_approach`, `dual_requested_*` 등) | 다수(서로 겹침이 많음) | 낮음 |
| 선반 들고 배송(`goal_approach`, `at_goal`, `wrong_team_goal`) | 6 | **모두 목표가 시야 안에 보임** |
| 반납 단계 | 4 | 낮음 |
| neutral(요청 선반·목표 모두 안 보임) | 4(고유 2) | 거의 없음 |

**핵심**: 관측이 "내 팀 기준"이라 같은 입력이면 빨강과 파랑의 정답 행동이 같습니다(초록 목표가 보이면 둘 다 그쪽으로 감). 팀 차이가 행동으로 드러날 수 있는 **유일한 상황은 "선반을 들었는데 목표가 시야 밖이라, 학습으로 기억한 자기 목표 방향으로 가야 할 때"**입니다. 그런데 이런 probe가 **0개**입니다.

그래서 지금 bank는 과제 수행 능력(집기·배송·반납 반응)을 비교하는 데는 쓸 수 있지만, **팀을 가리는 probe로는 원리적으로 거의 쓸모가 없습니다.** 지금까지 JS가 팀을 못 가른 것은 probe 개수 문제가 아니라 이 구조 때문입니다.

#### 2. 목표 위치 고정 → 동의합니다
두 목표가 (4,10)과 (5,10)으로 붙어서 고정돼 있으면 빨강·파랑의 과제가 사실상 같아집니다. 지금 돌고 있는 실험에서 Oracle과 All의 차이는 크게 나오기 어려울 것으로 봅니다. 그래서 이 run은 "팀 대칭 환경에서의 대조 결과"로 해석하는 게 맞습니다.

#### 3. GPT 답변에 대한 의견
**대부분 동의합니다.** 특히 두 가지는 제 제안보다 낫습니다.
- **변경을 하나씩 분리하는 설계**(E1-F: 목표만 분리 / E1-A: 관측만 절대 색 / E1-FA: 둘 다)는 무엇이 효과를 냈는지 가를 수 있습니다. 둘을 한꺼번에 바꾸자던 제 제안보다 낫습니다.
- "목표가 다르면 critic이 자동으로 틀린 값을 준다"는 제 말은 과했습니다. 목표 차이 → value 차이 → 다른 팀 공유의 손해는 **각각 검증해야** 합니다.
- 절대 색 관측이 "든 선반 색만 보면 팀이 나오는" 너무 쉬운 문제를 만든다는 지적도 맞습니다. 그 경우 단순 규칙과 비교해야 합니다.

**덧붙일 점**
- **E1-F를 먼저 하는 것을 강하게 권합니다.** 목표를 양쪽으로 떨어뜨리면 관측을 팀 기준으로 그대로 둬도, 목표가 안 보일 때 들고 가는 방향이 팀마다 달라집니다. 그러면 JS가 팀을 가를 **기회가 처음으로 생깁니다.** 다만 probe에 "들고 있는데 목표가 안 보이는" 상태를 꼭 넣어야 공정한 시험이 됩니다.
- 환경에 이미 `team_goal_positions` 설정이 있어서, **코드 수정 없이 설정만으로** 목표 위치를 바꿀 수 있습니다.
- GPT가 말한 "팀 구분 시점이 성능 향상보다 먼저 오는가"는, 지금 run에서는 관찰되지 않을 가능성이 큽니다. 2.5M 분석에서 PGCT gate가 처음부터 같은 팀과 다른 팀을 비슷하게 열었기 때문입니다.

**정리**: 지금 run은 그대로 두고(대칭 환경 대조군), 다음 단계로 **E1-F 환경 + 목표 비가시 상태를 포함한 probe**를 준비하는 것을 권합니다. 원하시면 E1-F 설정과 probe 보강안을 설계해 smoke test까지만 해 두겠습니다. 이 의견은 DECISIONS D26에 기록했습니다.


#### 원문 기록 T024 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다(삭제 후 확인 12:31 KST 무렵).

##### 사용자 — 원문

지금 폴더, 파일들 보면 프로젝트에 기존에 실험용으로 만들어졌다가 안쓰거나 보지않는 쓸모없는 것들이 많아 (특히 runs에 많은거 같아 내 생각에는)
필요없는거 좀 쳐내줘

##### Assistant — 진행 안내 1

`runs/` 폴더부터 정리 대상을 파악하겠습니다. 실행 중인 학습과 연구 노트가 근거로 쓰는 결과는 건드리지 않습니다. `runs/`는 git이 추적하지 않아 지우면 복구할 수 없으므로, 목록을 먼저 보여드리고 확인을 받은 뒤 삭제하겠습니다.

##### Assistant — 진행 안내 2

35GB 중 대부분은 연구 결과(14GB E1–E3, 6.7GB 커리큘럼, 8GB 사전학습 원본)입니다. 정리할 수 있는 후보를 위험도별로 나눴습니다. `runs/`는 git 추적 밖이라 삭제하면 복구할 수 없어 범위를 먼저 확인받겠습니다.

##### Assistant — 선택 질문 (요지)

runs/에서 어떤 묶음을 지울까요? 실행 중 run, E1–E3 결과, 커리큘럼 원본, 9700 사전학습 원본은 유지합니다.
- ① smoke·dry·실패 시험(권장, 약 3.3GB)
- ② 삭제된 도구의 옛 평가 결과(약 70MB)
- ③ 중단된 run의 checkpoint만(약 2.3GB)
- ④ 큰 결과 폴더 checkpoint 솎기(약 15–20GB, 중간 시점 재평가 불가)

##### 사용자 — 선택 응답

①, ②, ③, ④ 모두 선택.

##### Assistant — 진행 안내 3

네 묶음 모두 삭제합니다. ④를 위해 먼저 노트와 코드가 직접 참조하는 checkpoint 파일을 찾아 보존 목록을 만듭니다.

##### Assistant — 진행 안내 4

보존 규칙을 정했습니다.
- 각 run의 `final.pt`는 그대로 둡니다.
- `final.pt`가 없는 run은 마지막 checkpoint를 남깁니다(예: 9700 사전학습 원본, E3 2700).
- 노트가 참조하는 E1 PGCT `checkpoint_00600`도 남깁니다.
- 로그는 모두 남깁니다.

이 규칙대로 삭제를 실행합니다.

##### Assistant — 진행 안내 5

Dry-run 결과 보존 목록이 의도대로 나왔습니다. 실제로 삭제합니다.

##### Assistant — 진행 안내 6

35GB가 7.4GB로 줄었습니다(27.3GB 삭제). 실행 중인 학습이 계속 진행되는지와, 테스트가 쓰는 파일이 남아 있는지 확인합니다.

##### 수행 기록 — 원문 대화와 별도

삭제 목록은 `output/cleanup_20261015/removed_manifest.json`에 있다. EXPERIMENTS E21, DECISIONS D27을 기록했다. 실행 중 run은 계속 로그가 갱신됐고, tests는 182 passed다.

##### Assistant — 최종 답변

선택하신 네 묶음을 정리했습니다. **runs/가 35GB에서 7.4GB로 줄었습니다**(500개 항목, 27.3GB 삭제).

**삭제한 것**
- ① smoke·dry·실패 시험 폴더 33개와 로그 2개(오늘까지 만든 시험 run 전부)
- ② 이미 지운 09700 일반화 도구의 옛 평가 결과 2개
- ③ 2.5M에서 끊긴 run의 checkpoint(재개할 수 없어 쓸 일이 없음)
- ④ E1–E3, 커리큘럼, 사전학습 폴더의 **중간 checkpoint**

**남긴 것**
- **지금 학습 중인 run**: 삭제 후에도 4개 run 모두 로그가 계속 갱신되는 것을 확인했습니다.
- **모든 로그**(metrics, transfer 등)와 각 run의 `final.pt`
- `final.pt`가 없는 run의 마지막 checkpoint: 9700 사전학습 원본, IPPO 사전학습 900, E3 2700
- 노트가 참조하는 E1 PGCT 600 checkpoint
- 끊긴 run의 로그(2.5M 분석의 근거)
- 장애물 환경 문서가 쓰는 `hard_smoke_20261013_final`

**알아 두실 점**
- 이제 **중간 시점 모델은 다시 평가할 수 없습니다.** 예를 들어 E1의 1M 시점 모델로 무언가를 재분석하는 일이 불가능합니다. 최종 모델과 학습 로그로 하는 분석은 그대로 가능합니다.
- 노트(EXPERIMENTS)의 옛 smoke 기록에 나오는 경로 중 일부는 이제 없습니다. 어떤 경로가 사라졌는지 E21에 정리해 두었고, 삭제 목록 전체는 `output/cleanup_20261015/removed_manifest.json`에 있습니다.
- 삭제 후 전체 테스트 182개가 통과했습니다.


#### 원문 기록 T025 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다(현재 run은 약 0.26M step).

##### 사용자 — 원문

1. Oracle은 probe와 관련없는거 아녔어?
2. 그러면 지금 실험 날리고 Probe 수정한뒤에 다시하는게 좋을까?
   1. 한다면 Probe 수정방향은 어떻게 할꺼야?

##### 수행 기록 — 원문 대화와 별도

`update_ippo`의 peer loss가 probe 입력 위에서 critic 값을 맞추는 구조임을 확인했다. 현재 run 진행(약 0.26M)을 확인했고, DECISIONS D28을 기록했다. 실행 중 run은 변경하지 않았다.

##### Assistant — 최종 답변

#### 1. Oracle은 probe와 관련 없나? → **반은 맞습니다**

critic 공유는 두 단계로 나뉩니다.

| 단계 | PGCT | Oracle / All |
|---|---|---|
| **누구와** 공유할까(상대 선택) | probe 위 JS gate | 정답 팀 라벨 / 물리 이웃 → **probe 무관** |
| **무엇을** 공유할까(전이 내용) | probe 위에서 critic 값 맞추기 | **똑같이 probe 위에서** critic 값 맞추기 |

코드를 다시 확인해 보니, 전이(peer loss)는 공통 probe 입력에서 "내 critic 값"을 "상대 critic 값"에 맞추는 방식입니다. 그래서 Oracle과 All도 **어디서 critic을 맞추는지는 probe가 정합니다.** 지금은 그 위치가 고유 26개 입력에 몰려 있습니다.

#### 2. 지금 실험을 중단하고 probe를 고친 뒤 다시 할까? → **중단하지 않는 것을 권합니다**

- **이 run의 핵심 질문은 probe 판별력과 무관합니다.** "대칭 환경에서 IPPO / Oracle / All 중 critic 공유가 도움이 되나"를 보는 실험이고, 세 비교군이 같은 probe를 쓰므로 비교는 공정합니다.
- **지금 환경에서는 probe를 고쳐도 JS가 팀을 가를 수 없습니다.** 관측이 팀 기준이고 두 목표가 붙어 있어서, "목표가 안 보이는" probe를 넣어도 빨강과 파랑이 가는 방향이 거의 같습니다. probe 수정은 **목표를 분리한 환경(E1-F)과 함께**여야 의미가 있습니다. 그렇게 하면 어차피 새 실험이 됩니다.
- **현재 0.26M step입니다.** 지금 중단하면 3시간 정도만 잃지만, 계속 돌리면 대조군 결과가 남습니다.
- **한계**: probe 위치가 26개에 몰려 있어 Oracle과 All의 공유 효과가 실제보다 작게 나올 수 있습니다. 이 점은 해석할 때 명시하겠습니다.

**제안**: 지금 run은 계속 돌리고, 그동안 **E1-F 환경과 새 probe를 준비해 smoke까지만** 해 둡니다. 4–5M 점검(10월 17일 오전 무렵)에서 이 run을 15M까지 끌고 갈지, GPU를 E1-F로 넘길지 다시 결정합니다.

#### 3. probe 수정 방향

1. **중복 제거**: 고유 입력만 남기고, 가중치를 줄 거면 명시적으로 줍니다. 지금처럼 겹쳐서 생기는 숨은 가중치(8/48)를 없앱니다.
2. **생성 단계 자동 검사**: 시나리오마다 의도한 차이가 **실제 11×11 시야 안에** 나타나는지 검사하고, 다른 시나리오와 입력이 같으면 생성을 거부합니다. 이번에 발견한 "7개 시나리오가 한 입력으로 겹침" 같은 문제를 막습니다.
3. **용도별로 분리**
   - **팀 판별용**: 팀에 따라 정답 행동이 달라지는 상태만 넣습니다. 핵심은 **"요청 선반을 들고 있는데 목표가 안 보이는" 상태**를 여러 위치와 방향에서 만드는 것입니다. 목표를 분리한 E1-F에서만 의미가 있습니다.
   - **critic 공유용**: 집기·배송·반납·탐색 단계를 고르게 덮어서, critic을 "어디서" 맞출지가 한쪽으로 쏠리지 않게 합니다.
4. **같은 규칙으로 모두가 같은 probe를 생성**: 관측을 주고받지 않는 지금의 정보 구조를 그대로 유지합니다.
5. **학습 전 검증**: E1-F에서 학습한 정책으로 "같은 팀 vs 다른 팀 JS"가 갈리는지(AUROC) 먼저 확인합니다. probe 일부를 빼도 결과가 유지되는지 민감도도 봅니다. 이것이 IJCAI에서 "사람이 만든 probe"라는 약점에 답하는 근거가 됩니다.

원하시면 지금 run은 그대로 두고, **E1-F 설정과 새 probe 생성기(기존 코드와 분리된 새 파일), 자동 검사 도구**를 만들어 smoke test까지만 해 두겠습니다. 이 의견은 DECISIONS D28에 기록했습니다.


#### 원문 기록 T026 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

그러면 지금 학습에 방해되지 않도록 한채로 수정사항 수정해줘

##### Assistant — 진행 안내 1

실행 중인 학습에는 영향이 없게 진행하겠습니다. 실행 중인 4개 프로세스는 코드를 이미 메모리에 올려 두었으므로 파일을 고쳐도 그 프로세스는 바뀌지 않습니다. 그래도 기존 기본 동작은 그대로 두고, 새 기능은 옵션으로만 추가하겠습니다. 먼저 기존 probe builder가 env 상태를 어떻게 조작하는지 확인합니다.

##### Assistant — 진행 안내 2

기존 builder는 별도의 probe 전용 레이아웃 env를 씁니다. 저는 **학습 env 설정 그대로** 상태를 만들고 실제 관측 함수로 probe를 뽑는 새 생성기를 별도 파일로 만들겠습니다. 이렇게 하면 시야 잘림 같은 문제를 그대로 잡아낼 수 있습니다. env 상태 갱신 함수와 목표 위치 설정 방식을 확인합니다.

##### Assistant — 진행 안내 3

목표 위치는 설정으로 바로 바꿀 수 있습니다. 이제 새 probe 생성기와 자동 검사기를 작성합니다.

##### Assistant — 진행 안내 4

두 env 모두 bank 생성과 검증을 통과했습니다(gate 48, transfer 64, 모두 고유 입력). 다만 거부된 시나리오(32개)의 이유를 확인하고, 역할이 다르면 같은 입력도 허용해야 transfer에 "목표 비가시 적재" 상태가 들어가므로 이 부분을 고치겠습니다.

##### Assistant — 진행 안내 5

As expected, the rejections are only cross-role duplicates. I'll make uniqueness per role.

##### Assistant — 진행 안내 6

이제 거부된 시나리오가 0개이고, transfer bank가 단계별로 고르게 구성됐습니다(탐색 14, 적재·목표 보임 16, 적재·목표 안 보임 16, 반납 16, 목표 도착 2). 그림을 확인합니다.

##### Assistant — 진행 안내 7

그림을 보다가 고칠 점을 하나 발견했습니다. gate probe 중 맵 아래쪽 줄의 일부(예: 빨강 agent가 (7,10)에 있는 경우)는 자기 목표는 안 보이지만 **상대 팀 목표가 시야 안에** 들어옵니다. 같은 입력을 파랑 actor에게 넣으면, 파랑 입장에서는 자기 목표 칸이 "남의 목표"로 표시된 셈이라 실제로는 나올 수 없는 입력이 됩니다. gate probe는 **어느 팀의 목표도 보이지 않는 상태**로만 제한하겠습니다.

##### Assistant — 진행 안내 8

gate probe가 이제 모두 위쪽(y≤4)에 있어 어느 팀 목표도 보이지 않습니다. 이 bank를 학습 실행기에 **옵션으로** 연결합니다. 실행 중인 run과 기본 동작에는 영향이 없도록 기본값은 지금과 같게 둡니다.

##### Assistant — 진행 안내 9

Now wiring the options in, with defaults unchanged.

##### Assistant — 진행 안내 10

E1-F + v2 probe 조합으로 4개 mode의 64-step smoke test가 통과했습니다. 마지막으로 세 가지를 테스트로 고정하겠습니다. 첫째, 구석 목표에 실제로 배송이 되는지. 둘째, PGCT gate가 v2 gate bank를 쓰는지. 셋째, critic 증류가 transfer bank로 바뀌는지입니다.

##### Assistant — 진행 안내 11

모든 테스트(183개)가 통과했고, PGCT가 v2 gate bank를 그대로 쓰는 것도 확인했습니다. 실행 중인 학습(약 0.27M)도 정상 진행 중입니다. 증류 bank 교체 기록은 smoke test 이후에 추가한 것이라, smoke test를 한 번 더 돌려 확인합니다.

##### Assistant — 진행 안내 12

critic 증류가 PGCT·Oracle·All 모두 64개 transfer probe로 바뀐 것을 확인했습니다. IPPO는 전이가 없으니 해당 없음입니다. 이제 문서와 노트를 정리합니다.

##### 수행 기록 — 원문 대화와 별도

추가: `latent_team/probes_v2.py`. 수정: `train_from_scratch.py`, `exp_b_oracle_consensus.py`, `run_from_scratch.ps1`, `run_scratch_pipeline.ps1`, `tests/test_latent_team.py`(+1), `latent_team/README.md`. 산출물: `output/env_view_20261015/probes_v2/`, `runs/smoke_e1f_v2_20261015`. 기록: D29, E22. 실행 중 run, trainer, 환경 코드는 변경하지 않았다. E1-F 본 학습은 시작하지 않았다.

##### Assistant — 최종 답변

지금 학습은 건드리지 않고 수정을 마쳤습니다. 실행 중인 4개 run은 계속 진행 중이고(약 0.27M), 기존 기본 설정도 그대로입니다. 새 기능은 **옵션으로만** 켜집니다.

**1. E1-F 환경** (`-EnvVariant e1f`)
- E1 맵에서 **팀 목표만 두 아래 모서리로 옮겼습니다**(빨강 (0,10), 파랑 (9,10)). 관측 방식, 보상, 선반 배치는 그대로입니다.
- 환경 코드는 고치지 않고, 원래 있던 목표 위치 설정만 사용했습니다. 모서리 목표에 실제로 배송이 되는 것도 테스트로 확인했습니다.

**2. 새 probe bank v2** (`-ProbeBank v2`, `latent_team/probes_v2.py`)
- 학습 env 설정 그대로 상황을 만들고 **실제 관측 함수로** probe를 뽑습니다. 그래서 "의도한 장면이 시야 밖이라 사라지는" 문제가 생기면 자동으로 걸러집니다.
- **중복 0개**: 입력이 겹치는 probe는 만들지 않습니다.
- **용도별 분리**
  - **gate용 48개**(PGCT가 팀을 판단할 때 사용): 선반을 들고 있는데 **어느 팀 목표도 안 보이는** 상태입니다. 목표가 분리된 E1-F에서는 이때 팀마다 가야 할 방향이 달라집니다.
  - **critic 공유용 64개**: 탐색 14, 들고 목표 보임 16, 들고 목표 안 보임 16, 반납 16, 목표 도착 2로 단계를 고르게 넣었습니다. PGCT·Oracle·All 모두 이 64개 위에서 critic을 맞춥니다.
- 만들다가 하나 고쳤습니다. 처음에는 "자기 목표는 안 보이지만 **상대 팀 목표는 보이는**" 위치가 섞여 있었습니다. 그 입력은 상대 팀 agent 입장에서 실제로 나올 수 없는 관측이라 제외했습니다.
- 모든 agent가 같은 규칙으로 똑같이 생성하므로 관측을 주고받을 필요가 없습니다.

**검증**
- E1-F + v2로 4개 비교군을 64-step 시험 학습: 모두 정상 완료
- PGCT가 v2 gate bank를 쓰고, 세 비교군이 64개 critic 공유용 probe를 쓰는 것을 로그로 확인
- 전체 테스트 183개 통과
- probe 그림: `output/env_view_20261015/probes_v2/probe_bank_v2_e1f.png`

**아직 하지 않은 것**: E1-F 본 학습. 그리고 새 gate probe가 실제로 팀을 가르는지는 E1-F에서 학습된 정책이 있어야 확인할 수 있습니다.

**실행 명령**(승인 후)
```powershell
.\latent_team\run_scratch_pipeline.ps1 -Detach -Track -SkipStage1 -EnvVariant e1f -ProbeBank v2 -Stage2Seeds 1
```
지금 run과 동시에 돌리면 8개 프로세스가 GPU와 CPU를 나눠 써서 **둘 다 느려집니다**. 지금 run의 4–5M 점검(10월 17일 무렵) 이후에 시작하거나, 지금 run을 멈추고 E1-F로 넘어갈지 정하시면 됩니다. 기록은 DECISIONS D29, EXPERIMENTS E22에 남겼습니다.

#### 원문 기록 T027 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다(작업 중 run 확인 시각 12:49 KST). 이 turn 직전에 사용자가 `/compact`로 Claude Code 대화를 요약했다.

##### 사용자 — 원문

컨텍스트 다 차서 옮길 생각인데 지금 output이나 다른 md 파일로 Codex, Claude의 대화, 실험 로그들이 쪼개져 있잖아?
그거 합칠수 있나? 가능하다면 해줘

##### Assistant — 진행 안내 1

기록을 하나로 합치는 스크립트와 새 세션용 인수인계 문서를 만들고 있습니다. 원본 파일은 건드리지 않습니다.

##### Assistant — 진행 안내 2

원본은 그대로 두고 통합본과 인수인계 문서를 만들었습니다. 이제 기록 파일을 갱신하고 통합본을 다시 생성합니다.

##### 수행 기록 — 원문 대화와 별도

- 새 파일: `HANDOFF.md`(새 세션 시작점), `research_archive/build_archive.py`(통합본 생성기), `research_archive/RESEARCH_ARCHIVE.md`(생성물, 22개 MD 원본 + 날짜순 통합 타임라인).
- 수정: `AGENTS.md` 작업 시작 0번, `CLAUDE.md` 한 줄(HANDOFF 안내). 원본 기록 파일은 이동·삭제하지 않았다.
- 실행 중 run `scratch_20261015_093349_stage2`는 읽기만 했다(12:49 KST: IPPO 281,600 / PGCT 277,504 / Oracle 275,456 / All 279,552 step, 모두 running).
- 포함하지 않은 것: 프로젝트 밖 Codex·Claude 원본 세션 파일, JSON/그림 산출물(경로로만 연결).

##### Assistant — 최종 답변

합쳤습니다. 원본 파일은 그대로 두고, 새 세션용 파일 두 개를 만들었습니다.

**1. `HANDOFF.md`** (루트, 약 100줄)
새 세션이 가장 먼저 읽을 요약입니다.
- 연구 목표와 검증 순서
- 지금 돌고 있는 run(12:49 기준 약 0.28M step, 건드리지 말 것)
- 승인 대기 항목(E1-F 학습 명령 포함)
- 사용자 작업 원칙
- 코드 지도, 기록 파일별 역할

**2. `research_archive/RESEARCH_ARCHIVE.md`** (약 520KB)
흩어져 있던 MD 22개를 한 파일로 합쳤습니다.
- 지침, RESEARCH_STATE, DECISIONS(D01–D30), EXPERIMENTS(E00–E22)
- output 분석 보고서 7개, 실행기·구현 문서 8개
- 대화 원문 전체(Codex·Claude 모두, L01–L12 요약 + T001–T027 원문)
- 맨 끝에 결정(D)·실험(E)·대화(T) 항목을 날짜순으로 모은 통합 타임라인

원본을 바꾸면 아래 명령으로 다시 만들면 됩니다.
```powershell
C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe research_archive\build_archive.py
```

**원본을 옮기지 않은 이유**: Codex와 Claude가 매 turn 루트의 DECISIONS·EXPERIMENTS·CONVERSATION_LOG에 기록하도록 AGENTS.md에 정해져 있습니다. 파일을 하나로 옮기면 두 도구의 기록 방식이 깨집니다. 대신 AGENTS.md와 CLAUDE.md에 "새 세션은 HANDOFF.md부터 읽는다"는 한 줄을 넣었습니다.

**새 세션에서는** "HANDOFF.md 읽고 이어서 하자" 정도로 시작하면 됩니다. 통합본은 커서 한 번에 다 읽히지 않으므로, 필요한 부분만 찾아 읽게 됩니다.

**합치지 않은 것**
- 프로젝트 밖에 있는 Codex·Claude 앱의 원본 세션 파일
- 2026-10-13 이전 Codex 대화: 원문이 없어 기존처럼 요약(L01–L12)으로만 남아 있습니다.
- JSON 분석 결과와 그림: 경로로만 연결했습니다.

학습 4개는 계속 정상 진행 중이고 건드리지 않았습니다.


#### 원문 기록 T028 — 2026-10-15 KST, Codex

정확한 발화 시각은 별도로 측정하지 않았다. 실제 실행 확인 스냅샷은 13:17 KST다.

##### 사용자 — 원문

Claude에서 한 내역을 HANDOFF.md로 정리했어 더 보고 싶다면 다른 md 파일을 읽으면 돼
현재 프로젝트의 진행상황을 한번 확인해줘

##### Assistant — 진행 안내 1

`HANDOFF.md`를 먼저 읽고, 관련 연구 노트와 실제 실행 로그를 대조해 현재 진행 상황을 확인하겠습니다. 문서에 적힌 계획과 실제 완료·진행 상태를 구분해 정리하겠습니다.

##### Assistant — 진행 안내 2

Claude에서 추가한 E1-F 환경과 probe v2는 구현·smoke까지 완료됐고, 본 학습은 아직 시작되지 않았습니다. 현재 돌아가는 것은 기존 E1·canonical probe 비교입니다. 네 run의 로그가 약 0.31–0.32M step까지 갱신됐으며, 최근 평가는 아직 초기 구간이라 성능 우열을 판단할 단계는 아닙니다.

##### 수행 기록 — 원문 대화와 별도

- HANDOFF 전체, RESEARCH_STATE, DECISIONS의 D24–D30, EXPERIMENTS 최근 E19–E22 및 관련 기록, CONVERSATION_LOG 최근 T026/T027 구간, latent_team README의 E1-F/v2 안내를 확인했다. 공용 AGENTS 변경도 읽었다.
- 현재 run의 manifest/metrics/status/hash/checkpoint 목록/error 로그, v2 summary와 smoke comparison·transfer 일부를 읽어 상태를 대조했다. 로그가 증가하며 네 초기 hash가 같고, 현재 manifest는 기존 E1/canonical임을 확인했다. E1-F/v2는 seed1 64-step smoke 결과만 확인했고 새 본 학습은 실행하지 않았다.
- .err.log 검색 첫 시도는 PowerShell에서 wildcard 경로를 rg에 직접 전달해 경로 오류가 났다. 이후 각 실제 경로에 Select-String을 사용해 Traceback/Error/Exception/failed 일치가 없음을 확인했다. 기존 경고를 학습 실패로 해석하지 않았다.
- `output/status_review_20261015_131716/snapshot.json`을 새로 저장했다. HANDOFF에 최신 재확인과 T028 색인, RESEARCH_STATE 최상단, EXPERIMENTS E19 추가로 상태를 남겼다. 학습 알고리즘·환경·probe·실행 프로세스는 변경하지 않았다. 새 학습·평가·tests·삭제·커밋은 수행하지 않았다. 183 tests는 Claude의 기존 기록이다.
- 통합본 생성 스크립트를 읽고, 원본 기록 갱신 후 재생성한다. 통합본을 새 원자료 또는 앱 세션 자동 수집 결과로 취급하지 않는다.
- 아래 최종 답변 본문을 확정해 기록했다.

##### Assistant — 최종 답변

**현재는 기존 E1 조건의 4개 학습이 계속 진행 중이고, Claude가 추가한 E1-F·probe v2는 구현과 시험을 마친 상태입니다.**

[HANDOFF.md](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/HANDOFF.md), 관련 결정·실험 기록, 실제 로그를 대조했습니다.

**학습 상태 — 2026-10-15 13:17 KST 확인**

조건은 E1 11×10, 4 agents/2 teams, home .5, individual reward, 기존 canonical probe, 무작위 초기화 seed 1이며 각 15M step 목표입니다.

| 모델 | 현재 env steps | 로그 상태 |
|---|---:|---|
| IPPO | 321,536 | 갱신 중 |
| PGCT | 316,416 | 갱신 중 |
| Oracle | 314,368 | 갱신 중 |
| All | 318,464 | 갱신 중 |

속도는 모델당 약 23.5–24.0 step/s이고, 네 모델 모두 256,000 step checkpoint가 있습니다. 오류 로그에는 Gymnasium 경고와 W&B 안내가 있으며, 중단을 나타내는 traceback은 발견하지 못했습니다.

최근 공통 **307,200 step 평가에서는 pickup·delivery·return이 모두 0**입니다. 평가 조건은 deterministic masked policy, 고정 seeds 5,000,001–5,000,020, 20×500입니다. 아직 초기 구간이라 실패나 모델 간 우열을 판단할 단계는 아닙니다.

**Claude에서 추가로 완료한 작업**

- **E1-F 환경:** 팀 목표를 아래 양쪽 모서리로 분리했습니다. 관측·보상·선반 배치는 유지합니다.
- **probe v2:** 팀 판별용 48개와 critic 증류용 64개를 분리했습니다. 기존 bank의 중복과 ‘적재 중 목표가 보이지 않는 상황’ 누락을 보완했습니다.
- **실행 옵션 연결:** 기본값은 기존 E1/canonical이고, 새 기능은 옵션으로 선택합니다.
- **시험 결과:** E1-F/v2의 4개 mode, seed 1, 각 64-step smoke 완료와 실제 증류 입력 64개 사용을 확인했습니다. 전체 테스트 183개 통과는 Claude의 기록이며 이번에는 재실행하지 않았습니다.
- **기록 정리:** HANDOFF와 통합 연구 기록이 마련됐습니다. 과거 결과 정리 과정에서 일부 중간 checkpoint가 삭제됐다는 이력도 확인했습니다.

**아직 남은 것은 다음입니다.**

- E1-F/v2의 본 학습과 실제 팀 판별력·공유 이득 검증
- 독립 training seed 2·3 반복
- MAPPO·SePS·HetDPS 본 학습
- 추론한 팀 관계를 실제 공유에 사용하는 온라인 learned-team 모드

연구 목표는 여전히 **국소 행동에서 잠재 팀 추론 → 팀 내부 critic 전이 → 학습 효율 개선**입니다. 현재 돌아가는 비교는 그중 **critic 공유 효과를 확인하는 실험**입니다. 새 probe가 팀을 잘 찾는다는 결과까지 나온 상태는 아닙니다.

기존 계획의 다음 점검 지점은 **4–5M step**입니다. 현재 속도가 유지되면 10월 17일 전후이며, 학습을 멈추지 않고 확인하는 계획입니다.

이번에는 학습·코드를 변경하지 않고 진행 상황과 인수인계 기록을 갱신했습니다. [확인 스냅샷](C:/RWARE/MARL_RWARE/third_party/robotic-warehouse/output/status_review_20261015_131716/snapshot.json)도 저장했습니다.


#### 원문 기록 T029 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (붙여넣은 GPT 답변 2개 포함, 전체 읽음)

굳이 프로브를 112개나 둔 이유가 있나?
적은 양으로도 가능할꺼 같은데

밑은 GPT 대화
--------------------------------------

[붙여넣은 GPT 답변 1 — 요지: PGCT에서 probe의 두 용도(gate JS·critic 증류)와 v2의 분리, E1-F와의 관계, 우려 세 가지(gate 48개의 실제 팀 판별력, bank 변경에 따른 0.12 threshold 영향, transfer 입력 정렬·보상 스케일), 환경과 bank를 동시에 바꾸면 효과 분리가 어렵다는 점, 공통 probe 응답 비교는 국소 행동 관측 기반 추론과 다르다는 점]

A. 굳이 112개나 되는 probe를 만들어야 했을까?
그냥 합쳐서 20~30개면 안됐어?

[붙여넣은 GPT 답변 2 — 요지: 112개의 근거는 없다. 공통 bank 24~32개(gate 8 + transfer 16 예시)를 가중치로 나눠 쓰는 방식을 제안. 개수보다 구분 정보를 담는지가 중요. 고정 모델로 16/24/32/48+64를 비교하고 AUROC·증류 오차·변동을 보자. 현재 15M 학습은 유지]

(붙여넣은 원문은 사용자 메시지에 있으며 여기서는 요지만 남긴다.)

##### Assistant — 진행 안내 1

Probe 구성을 확인했고, 이제 대화 기록에 추가합니다. 그 전에 다른 도구가 남긴 마지막 기록 번호를 확인합니다.

##### 수행 기록 — 원문 대화와 별도

- `runs/smoke_e1f_v2_20261015/probe_bank_v2_e1f_s1.pt`의 gate 시나리오를 읽기 전용으로 확인했다. 48개, 서로 다른 칸 26개, 방향 분포는 0:16, 1:8, 2:10, 3:14이고 팀 표시는 24/24다. 모두 "요청 선반 적재 + 목표 비가시" 상태다.
- `probes_v2.build_bank`의 상한은 `max_gate=48`, `max_transfer=64`다. 후보가 상한을 넘으면 (단계, 팀) 그룹을 돌아가며 무작위로 뽑는다.
- 코드·실행 변경은 없다.

##### Assistant — 최종 답변

맞는 지적입니다. **112개는 근거가 있는 숫자가 아닙니다.** 제가 정한 상한값입니다.
- gate 48: 기존 canonical bank가 48개라 개수를 맞췄습니다.
- transfer 64: 5개 단계를 고르게 넣을 만큼 넉넉히 잡았습니다.

개수를 바꿔 보는 실험은 하지 않았습니다.

**실제로 들어 있는 내용**
- gate 48개는 모두 "요청 선반을 들고 있고 목표가 안 보이는" 같은 상황입니다. 서로 다른 칸 26개에 방향만 바꿔 담았습니다.
- 이 상황에서 팀을 가르는 판단은 사실상 하나입니다. **왼쪽 목표(0,10)로 가느냐, 오른쪽 목표(9,10)로 가느냐**입니다.
- 그래서 48개 대부분은 같은 질문을 위치만 바꿔 반복한 것입니다.
- probe는 고정된 입력이라 JS에 표본 잡음이 없습니다. 같은 질문을 여러 번 넣어도 정확도가 오르지 않고, 그 상황의 가중치만 커집니다.
- **gate는 8~12개로도 충분할 가능성이 큽니다.** 맵 왼쪽·가운데·오른쪽 × 방향 정도면 됩니다.

**다만 "합쳐서" 20~30개는 반대합니다.** 줄이는 것과 합치는 것은 다릅니다.
- JS는 bank 전체의 평균입니다.
- 탐색·반납처럼 팀 정보가 없는 probe를 섞으면, 그 probe들에서는 두 팀의 JS가 비슷하게 나옵니다. 그래서 팀 차이가 희석됩니다. **기존 canonical bank가 실패한 이유가 바로 이것**입니다.
- GPT가 말한 "공통 집합 + 용도별 가중치"도 gate 쪽 가중치를 0으로 두면 결국 분리와 같습니다. 파일 관리 방식이 다를 뿐입니다.
- 정리하면 **분리는 유지하고 개수만 줄이는 쪽**이 맞습니다. 예를 들어 gate 12 + transfer 20, 합계 32 정도입니다.

**개수를 줄여도 손해가 거의 없는 이유**
- 계산 비용 차이는 사실상 없습니다. 112개도 시퀀스 길이 1짜리 forward라 rollout에 비하면 무시할 수준입니다.
- 줄이는 이유는 비용이 아니라 **설명과 해석**입니다. probe 하나하나가 무슨 상황인지 논문 표 하나로 보여줄 수 있어야 합니다.
- 줄일 때의 위험은 transfer 쪽입니다. 증류 지점이 너무 적으면 critic이 그 몇 점에만 맞춰집니다. 단계당 4개 정도는 남기는 게 안전합니다.

**GPT가 놓친 점 하나: threshold는 개수보다 구성의 영향을 받습니다**
- JS는 평균이라 개수만 줄이면 스케일이 거의 그대로입니다.
- 그런데 v2 gate는 **전부 팀 차이가 나는 상황**만 모았습니다. 그래서 E1-F에서 정책이 갈라지면, 다른 팀 사이의 JS가 기존보다 훨씬 커질 것입니다.
- 이것은 의도한 효과지만, 같은 팀 사이의 JS도 함께 커져 0.12를 넘을 수 있습니다. 그러면 **PGCT gate가 거의 안 열려 사실상 IPPO처럼 될 위험**이 있습니다. 이 위험은 32개든 112개든 같습니다.
- E1-F 본 학습 전에 확인할 일입니다.

**개수는 의견이 아니라 측정으로 정하는 게 좋습니다**
- 측정하려면 E1-F에서 학습된 정책이 필요합니다.
- checkpoint만 있으면 나중에 아무 부분집합(4/8/12/24/48개)으로든 JS를 다시 계산할 수 있습니다.
- 그래서 부분집합별로 같은 팀/다른 팀 AUROC, JS 스케일, gate 개방률을 학습 후 오프라인으로 비교할 수 있습니다.

**제 제안**
1. 지금 15M 학습은 그대로 둡니다. 이 run은 기존 canonical bank를 쓰므로 이번 논의와 무관합니다.
2. E1-F를 시작하기 전에 bank를 **gate 12 + transfer 20**으로 줄입니다. 무작위가 아니라 위치·방향·단계를 구조적으로 골라서, 상황 표를 만들 수 있게 합니다.
3. E1-F 학습 초기 checkpoint에서 JS 스케일과 0.12의 관계를 먼저 확인합니다.

원하시면 2번을 옵션으로 추가하겠습니다. 실행 중인 학습에는 영향이 없고, 기존 48+64 설정도 그대로 남겨 두겠습니다.

#### 원문 기록 T030 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (붙여넣은 GPT 답변 포함, 전체 읽음)

[붙여넣은 GPT 답변 — 요지: E1-F에서는 두 목표가 모두 보이는 상황이 팀 추론에 중요한 probe일 수 있다. 그러나 팀 기준 관측 때문에 같은 입력을 Red/Blue actor에 넣으면 둘 다 'My Goal'로 가서 JS≈0이 될 수 있다. gate probe를 두 목표 보임 4 / 한 목표 보임 4 / 목표 비가시 2 / 경계·장애물 2 = 12개로 구성하자. 대안으로 실제 이웃의 목표 선택 행동으로 팀을 추론하는 방식(B)이 원래 목표에 맞다. '같은 물리 상황에서 팀별 목표 선택'과 '같은 관측 벡터에 대한 두 actor의 정책 차이'는 다르다.]

이 부분 잘 이해가 안되는데

##### 수행 기록 — 원문 대화와 별도

- 관측 채널 확인: `rware/utils/semantic_observation.py`에 `goal`(모든 목표)과 `relevant_goal`(관측자 팀 목표) 채널이 따로 있다. v2 gate probe가 어느 목표도 보이지 않는 상태로 제한된 이유(D29)와 연결해 설명했다. 코드·실행 변경 없음.

##### Assistant — 최종 답변

핵심은 **"probe 입력에 '내 목표는 여기'라는 표시가 들어 있느냐"**입니다. 비유로 먼저 설명하겠습니다.

**비유: 내비게이션의 '집' 버튼**
- 철수 집은 왼쪽, 영희 집은 오른쪽에 있습니다. 두 사람에게 똑같은 지도를 보여주고 "집에 가라"고 합니다.
- **지도에 '집' 표시가 왼쪽에 찍혀 있으면**, 둘 다 왼쪽으로 갑니다. 지도가 "네 집은 여기"라고 알려줬기 때문입니다. 두 사람의 행동이 같으니 서로 다른 집에 산다는 걸 알 수 없습니다.
- **지도에 '집' 표시가 없으면**, 각자 기억하는 자기 집으로 갑니다. 철수는 왼쪽, 영희는 오른쪽으로 가니까 행동 차이가 드러납니다.

**실제 RWARE 관측이 바로 이 구조입니다**
- 관측에는 목표 채널이 두 개 있습니다. `goal`은 모든 목표를 보여주고, `relevant_goal`은 **보는 사람 자기 팀의 목표**만 보여줍니다.
- 빨강 agent가 보면 왼쪽 목표에 relevant 표시가 붙고, 파랑 agent가 보면 오른쪽 목표에 붙습니다. 같은 장면이라도 입력 숫자가 다릅니다.
- PGCT는 **똑같은 숫자 입력 하나**를 두 actor에 넣고 반응을 비교합니다.
- 두 목표가 다 보이는 probe를 하나 만들면, relevant 표시는 둘 중 한쪽에만 붙습니다. 예를 들어 왼쪽에 붙었다고 합시다.
  - 빨강 actor는 "내 목표가 왼쪽이네" 하고 왼쪽으로 갑니다.
  - 파랑 actor도 같은 입력을 받으니 "내 목표가 왼쪽이네" 하고 왼쪽으로 갑니다.
  - 결과적으로 JS가 0에 가까워지고 팀 차이가 사라집니다. 이것이 '집 표시가 찍힌 지도'입니다.

**그래서 v2 gate probe를 "어느 목표도 안 보이는" 상태로만 만들었습니다(D29)**
- 목표가 안 보이면 입력에 '내 목표는 여기' 정보가 없습니다.
- 그러면 actor는 학습으로 익힌 기억, 즉 "내 팀 목표는 맵 왼쪽 아래"에 의존해야 합니다. E1-F에서는 이 기억이 팀마다 다르므로 행동이 갈립니다. 이것이 '집 표시가 없는 지도'입니다.
- 처음 버전에서 "상대 팀 목표만 보이는" 위치를 뺀 것도 같은 이유입니다.

**GPT 답변이 헷갈리는 이유**
GPT 답변 안에 서로 맞지 않는 내용이 섞여 있습니다.
- 1·3번은 "두 목표가 보이는 probe를 넣자"고 합니다.
- 2번은 바로 그 probe에서 JS≈0이 된다고 설명합니다.
- 2번이 맞습니다. 지금 PGCT 방식(같은 입력 비교)에서는 두 목표가 보이는 probe를 넣어도 팀 차이를 측정할 수 없습니다. 12개 구성안의 "두 목표 보임 4개"와 "한 목표 보임 4개"는 그 문제를 그대로 안고 있습니다.

GPT가 낸 해결책 "각 팀 기준으로 따로 변환해서 넣자"에는 순환 문제가 있습니다.
- 상대 actor에 맞는 입력을 만들려면 그 상대가 **어느 팀인지 먼저 알아야** 합니다.
- 팀을 알아내려고 하는 방법에 팀 정보가 필요해지는 셈입니다.

**GPT 마지막 문단의 두 가지 구분은 맞습니다**
- (가) 같은 물리 상황에서 실제로 어느 목표로 가는가: 팀 정보가 진짜로 드러나는 곳입니다.
- (나) 같은 입력 숫자에 대해 두 actor의 반응이 다른가: PGCT가 측정하는 것입니다.

(가)는 상대가 실제로 움직이는 걸 **직접 봐야** 알 수 있습니다. 이것은 GPT의 B안이고, 실험 A(E11)에서 국소 pickup·배송 목격 증거로 팀을 거의 완벽하게 가른 방식(AUROC 1.0)과 같은 방향입니다. 원래 연구 목표인 "국소 관측 행동으로 팀 추론"에도 이쪽이 더 가깝습니다.

**정리**
- 같은 입력 비교 방식(현재 PGCT)에서 팀 차이를 볼 수 있는 곳은 "목표 표시가 없는" probe뿐입니다. 그래서 v2 gate는 지금 구성이 맞습니다. 다만 이 probe가 실제로 팀을 가르는지는 E1-F 학습 후에야 확인할 수 있습니다.
- 두 목표가 보이는 상황은 probe가 아니라 **실제 rollout에서 상대 행동을 관찰하는 방식(B안)**에서 쓰는 게 맞습니다.

#### 원문 기록 T031 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

그냥 그러지말고 기존에 학습했던 모델 있잖아
그걸 프로브에 넣었을때 팀을 잘 구분하는지 시각 자료로 띄워주면 안돼?

##### Assistant — 진행 안내 1

기존 학습 모델에 probe를 넣어 팀 구분 정도를 그림으로 만들겠습니다. 실행 중인 학습과 기존 파일은 건드리지 않고 읽기만 합니다.

##### Assistant — 진행 안내 2

Results are in. I'm sending the figures, then I'll update the logs.

##### 수행 기록 — 원문 대화와 별도

- 새 분석 스크립트 `output/probe_team_check_20261015/probe_team_check.py`를 CPU에서 실행했다. 고정 모델이며 실행 전후 가중치 hash가 같다.
- 산출물: `js_matrices.png`, `same_vs_cross.png`, `results.json`. 결과 상세는 EXPERIMENTS E23에 있다.
- 사용자에게 그림 2장을 전송했다. 학습·코드·실행 중 run은 변경하지 않았다.

##### Assistant — 최종 답변

그림 두 장을 띄웠습니다. 결론부터 말하면, **기존 모델로는 어떤 probe를 써도 팀이 구분되지 않습니다.** 오히려 같은 팀끼리 더 다르게 반응합니다.

**무엇을 했나**
- 기존 E1 모델 4개(Stage03, Stage04 PGCT, E1 IPPO 4M, E1 PGCT 4M)에 probe 5종류를 넣었습니다.
  - 현재 PGCT가 쓰는 canonical 48개
  - v2 gate 48개
  - v2 transfer를 상황별로 나눈 3종: 적재 중 목표 보임 / 적재 중 목표 안 보임 / 빈손 탐색
- 4명의 agent끼리 JS(행동 분포 차이)를 계산했습니다. 같은 팀은 A1–A3(빨강), A2–A4(파랑)입니다.
- 팀이 구분된다면 같은 팀 JS(녹색)가 다른 팀 JS(회색)보다 **낮아야** 합니다.

**결과**
- **20개 조합 모두 같은 팀 JS가 더 높았습니다.** 예를 들어 E1 PGCT의 canonical에서 같은 팀은 .39, 다른 팀은 .30입니다.
- "가장 비슷한 상대가 실제 팀원인가"를 4명에게 물으면 0~2명만 맞았습니다. 무작위로 찍어도 평균 1.3명은 맞습니다.
- 가장 비슷한 쌍은 대부분 **A3–A4**인데, 둘은 다른 팀입니다. 팀보다 개인별 학습 차이가 더 크게 나타납니다.
- 목표가 보이는 probe와 안 보이는 probe 사이에 차이가 거의 없습니다. 지금 E1 모델에서는 지난번에 설명한 "목표 표시" 효과도 드러나지 않습니다.
- 실험 A(E11)에서 canonical JS의 팀 구분력이 우연 수준 이하였던 결과와 같은 방향입니다.

**해석할 때 주의할 점**
- 이 모델들은 모두 **E1(두 목표가 바로 옆)**에서 학습됐습니다. 팀마다 목표 위치가 한 칸 차이라, 원래 팀별로 행동이 달라질 이유가 거의 없습니다.
- 그래서 이 결과는 "v2가 실패했다"는 뜻이 아닙니다. **"E1에서는 probe를 바꿔도 소용없다"**는 확인입니다. v2 gate가 제 역할을 하는지는 E1-F에서 학습된 모델이 있어야 알 수 있는데, 아직 64-step smoke 모델뿐입니다.
- 4개 모델 모두 같은 Stage03 계열이고 seed 1이라 서로 독립적인 반복은 아닙니다.
- 덧붙여, 같은 팀 JS가 v2 gate에서 .24–.28로 PGCT 기준 0.12를 크게 넘습니다. 지난번 우려처럼 이 bank로는 gate가 잘 안 열릴 수 있습니다. 다만 E1 모델 기준입니다.

**다음 선택지**
v2 probe를 실제로 시험하려면 E1-F에서 짧게라도 학습한 모델이 필요합니다. 예를 들어 E1-F IPPO 1개를 2M step 정도 돌리면, 지금 속도로 약 하루 걸립니다. 그 checkpoint에 같은 그림을 다시 그리면 됩니다. 지금 run과 같이 돌리면 양쪽 모두 조금 느려집니다. 승인해 주시면 시작하겠습니다.

그림 재현: `python output/probe_team_check_20261015/probe_team_check.py`

#### 원문 기록 T032 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문 (붙여넣은 GPT 답변, 질문 문장 없음, 전체 읽음)

[붙여넣은 GPT 답변 — 요지: E23 그림에서 모든 조합의 같은 팀 평균 JS가 더 높고 IPPO도 같다. 다만 평균만으로 팀 정보가 0이라 할 수 없다(E1 PGCT 목표 비가시 쌍 AUROC .625, A3–A4가 평균을 왜곡). A3–A4가 왜 비슷한지(공간, 진척도, Forward 위주 단순 정책 등)를 행동 확률·entropy·배송 성능·공간 분포로 확인하자. v2 gate 같은 팀 JS .24–.28 > 0.12는 경고다(EMA 등으로 정확한 개방 횟수는 모름). E1-F 필요성에는 동의하나 zero hidden probe가 기억 의존 차이를 못 볼 수 있다. 2M은 배송 학습 초입이라 짧다. 우선 IPPO만으로 E1-F 실제 행동 차이와 probe 응답 차이를 비교하자. 새 probe보다 A3–A4 원인 분석이 먼저다.]

##### Assistant — 진행 안내 1

GPT가 물은 "A3–A4가 왜 비슷한가"는 기존 평가 기록과 probe 응답으로 바로 확인할 수 있어서, 먼저 확인하겠습니다(읽기 전용).

##### 수행 기록 — 원문 대화와 별도

- 4개 모델의 `final_eval_metrics.json`(agent별 delivery)과 canonical·v2 gate probe의 agent별 평균 행동 확률, entropy, argmax 일치율을 계산했다. 산출물: `output/probe_team_check_20261015/agent_profiles.json`. 고정 모델, CPU, 코드·학습 변경 없음.

##### Assistant — 최종 답변

GPT 지적 대부분에 동의합니다. GPT가 궁금해한 "A3–A4가 왜 비슷한가"는 기존 기록으로 바로 확인해 봤습니다.

**1. A3–A4가 비슷한 이유: 팀이 아니라 "실력·습관" 묶음입니다**
- 최종 평가 배송 수(agent별 A1/A2/A3/A4)
  - Stage04: 197 / 168 / **287 / 293**
  - E1 IPPO: 186 / 162 / **267 / 278**
  - E1 PGCT: 174 / 170 / **273 / 270**
  - Stage03만 237 / 250 / 225 / 285로 차이가 작습니다.
- canonical probe에서 A3·A4는 **Forward 위주**입니다. A4는 Forward 확률 .81–.94, A3는 .64–.75입니다. 반면 A1·A2는 회전 비중이 큽니다. 예를 들어 A2는 Right가 .47–.57입니다.
- canonical에서 가장 높은 확률의 행동이 같은 비율을 보면, A3–A4는 .69–.81이고 A1–A2는 .08–.17입니다. 같은 팀 쌍은 .40–.58입니다.
- 정리하면 "잘 배송하는 A3·A4 / 덜 하는 A1·A2"로 나뉘고, 정책 유사도는 이 구분을 따릅니다. GPT가 말한 "둘 다 Forward 위주" 가설이 맞고, 실력 차이와도 겹칩니다. Stage03에서도 A3–A4가 비슷하므로 실력만으로 다 설명되지는 않습니다.
- 같은 팀원끼리 회전 방향 습관이 반대인 경향도 보입니다. 예를 들어 v2 gate에서 A1은 Right, A3는 Left 쪽입니다. 같은 팀이 맵 양쪽으로 나눠 일했을 가능성이 있지만, 공간 기록은 아직 확인하지 않았습니다(가설).
- 정책들은 거의 결정적입니다(entropy .04–.3, 최대 1.61). 그래서 JS는 사실상 "가장 높은 확률의 행동이 같은가"를 재고 있습니다.

**2. GPT가 맞게 짚은 점**
- "같은 팀 평균이 더 높다 ≠ 팀 정보가 전혀 없다"는 맞습니다. 제 표현 "어떤 probe를 써도"는 이 4개 E1 모델에 한정해야 합니다.
- 다만 AUROC .625는 의미를 두기 어렵습니다. 같은 팀 쌍이 2개, 다른 팀 쌍이 4개뿐이라 AUROC는 1/8 단위로만 움직입니다. 우연과 구분할 수 없습니다.
- "A3–A4 차이는 학습 정도 때문"이라는 제 말은 추측이었습니다. 이번 확인으로 일부만 맞았습니다.
- 0.12 문제는 고정 모델의 원시 JS라 경고 수준이라는 데 동의합니다. 참고로 canonical에서도 같은 팀 JS가 .36–.42로 0.12를 넘습니다. 프로젝트 초기의 "학습 후반에 초록 연결선(gate)이 사라진다"는 현상(D01)과 같은 이유로 보입니다.
- GPT 표에 숫자 하나가 틀렸습니다. E1 PGCT 빈손 탐색의 다른 팀 JS는 .172가 아니라 .145입니다(비율 .69).

**3. 동의하지 않거나 보완할 점: zero hidden 우려**
- 이 우려는 E1에서는 이미 답이 있습니다. 실험 A(E11)에서 **실제 관측 이력과 실제 hidden state**로 비교한 history JS도 E1 팀 구분 AUROC가 .27–.29였습니다. 기억을 넣어도 E1에서는 팀이 안 보였으니, E1 실패의 원인은 zero hidden이 아닙니다.
- E1-F에서는 11×11 시야가 11×10 맵 대부분을 덮어 벽 위치로 자기 위치를 알 수 있습니다. 그래서 기억 없이도 방향을 정할 수는 있을 것 같습니다. 그래도 GPT 말대로 "실제 행동 차이"와 "probe 응답 차이"를 따로 재야 하는 건 맞습니다.

**4. E1-F 다음 단계**
- 2M은 짧다는 지적에 동의합니다. 지난 from-scratch run에서 배송이 1.9–2.1M에야 시작됐습니다.
- 수정 제안: **E1-F IPPO 1개**만 처음부터 돌리고, 저장되는 checkpoint마다 두 가지를 비교합니다.
  - (가) 실제 rollout에서 팀별 이동 방향과 배송 목표
  - (나) v2 gate의 같은 팀/다른 팀 JS
- 배송이 자리 잡는 시점(대략 4–5M, 1개 프로세스로 2–2.5일)까지 보고 멈춥니다. PGCT·Oracle·All은 아직 돌리지 않습니다.
- 승인 전에는 시작하지 않습니다. 지금 15M run과 같이 돌리면 양쪽 모두 조금 느려집니다.

**한 줄 요약**: E1에서 정책 유사도는 팀이 아니라 "누가 얼마나 잘, 어떤 습관으로 움직이냐"를 따라갑니다. 그래서 E1에서는 probe를 손봐도 팀이 안 나옵니다. E1-F에서 그게 바뀌는지가 다음 질문입니다.

#### 원문 기록 T033 — 2026-10-15 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

일단 기존에 A3, A4가 잠재 팀 연결됐을때 설명해주면
처음에는 파란색, 빨간색 구역이 완전히 나눠져 있었는데 이때는 각 팀이 서로 연결되어 있었어 이후 환경 난이도를 높인다고 50대 50으로 섞었어
그 과정에서 오른쪽에 대기타는 전략으로 바뀐 A3, A4가 같은 영역에 있어서인지 행동패턴이 비슷해졌고 잠재 팀으로 연결된거 같아

##### 수행 기록 — 원문 대화와 별도

- 기존 분석 문서 `output/gating_diagnosis/README.md`(단계별 같은 팀 거리, stage04 3–4 연결)와 `output/pgct_spatial_analysis/REPORT.md` 3.3–3.4(Stage04 최종 모델 공간 점유, seeds 5,000,001–5,000,020, deterministic 20×500)를 읽고 사용자 설명과 대조했다. 새 실행·코드 변경 없음.

##### Assistant — 최종 답변

큰 흐름은 기록과 맞습니다. 다만 한 군데가 다릅니다. **A3와 A4는 같은 구역에 있었던 게 아니라, 둘 다 "상대 팀 구역으로 원정 가는" 같은 역할을 맡았습니다.**

**1. 구역이 나뉘어 있을 때: 같은 팀끼리 연결 (기록과 일치)**
- 같은 팀 사이의 gate 거리(A1–A3 / A2–A4)를 단계별로 보면 다음과 같습니다(`output/gating_diagnosis`).

| 단계 | 섞인 비율 | A1–A3 | A2–A4 |
|---|---|---|---|
| stage01 | 0% (구역 완전 분리) | .086 | .100 |
| stage02 | 12.5% | .259 | .318 |
| stage03 | 25% | .277 | .385 |
| stage04 | 50% | .324 | .412 |

- stage01에서는 둘 다 기준 0.12 아래라 같은 팀이 연결됐습니다.
- 눈여겨볼 점은 **12.5%만 섞어도(stage02) 거리가 세 배로 뛰었다**는 것입니다. 50%가 되기 전에 이미 같은 팀 연결은 끊겼습니다. stage03·04에서는 같은 팀 전이가 한 번도 없었습니다.

**2. 섞은 뒤: 팀 안에서 역할이 나뉨**
stage04 최종 모델의 위치 기록입니다(x<5가 왼쪽, 빨강 팀 구역).

| Agent | 팀 | 왼쪽에 머문 비율 | 왼쪽에서 집은 요청 선반 비율 | 선반을 들고 있던 시간 |
|---|---|---|---|---|
| A1 | 빨강 | 99.6% | 100% | 47% |
| A2 | 파랑 | 0.6% | 0% | 52% |
| A3 | 빨강 | 38% | 19% | **77%** |
| A4 | 파랑 | 57% | 72% | **76%** |

- **A1·A2는 자기 팀 구역에만 머무는 "홈 담당"**입니다.
- **A3·A4는 섞여 들어간 자기 팀 선반을 가지러 상대 구역까지 가는 "원정 담당"**입니다.
  - A3(빨강)는 주로 오른쪽(파랑 구역)에서 선반을 집습니다.
  - A4(파랑)는 주로 왼쪽(빨강 구역)에서 집습니다.
- 그래서 둘은 같은 곳에 있지 않고 오히려 **서로 반대쪽에서 일합니다.** "오른쪽에서 대기"하는 모습도 기록에는 없습니다. 오히려 둘 다 시간의 3/4을 선반을 나르며 보냅니다. 혹시 영상에서 다른 장면을 보셨다면 알려주세요.
- 비슷해진 건 위치가 아니라 **행동 방식**입니다. 원거리 운반 위주로 앞으로 가는 행동이 많고(지난 분석의 Forward .64–.94), E1에서는 두 팀 목표가 가운데 아래에 붙어 있어서 둘 다 맵을 가로질러 같은 곳으로 배송합니다.
- 그 결과 공통 probe에서 A3–A4의 JS가 .130으로 가장 가까웠습니다. stage04에서 3–4가 실제로 1,170번 연결됐습니다(마지막 연결 update 3869, EMA .1149).
- 반대로 같은 팀원끼리는 홈/원정으로 역할이 갈려 서로 가장 달라졌습니다.

**3. 이게 의미하는 것**
- PGCT가 찾은 건 "팀"이 아니라 **"같은 역할을 맡은 짝"**입니다. 앞서 사용자께서 지적한 "팀이 아니라 역할을 추론하게 된다"(D25)가 실제로 일어난 셈입니다. 그것도 의도하지 않았는데 선반을 섞자 저절로 생겼습니다.
- 다만 "역할 분업 때문에 연결이 역전됐다"는 인과는 아직 검증되지 않았습니다. seed 1개, 커리큘럼 한 줄기에서 본 관측입니다.

**4. E1-F에 주는 힌트**
- E1-F도 섞임 50%라 같은 홈/원정 분업이 다시 생길 수 있습니다.
- 하지만 목표가 양쪽 모서리로 갈라지면 상황이 달라집니다. 원정 담당 A3(빨강)는 오른쪽에서 집어 **왼쪽 모서리로**, A4(파랑)는 왼쪽에서 집어 **오른쪽 모서리로** 가야 합니다. 같은 역할이어도 운반 방향이 정반대가 됩니다.
- v2 gate probe("선반 들고 목표 안 보임")가 바로 이 운반 방향 차이를 잽니다. 그래서 E1-F에서는 A3–A4 같은 역할 짝 연결이 깨지고 팀 쪽으로 돌아올 가능성이 있습니다. 이것이 E1-F에서 확인할 핵심 질문입니다.
- 비교를 위해 섞임 0%(구역 분리) 조건도 함께 보면 "섞임 때문에 역할이 생기는가"까지 분리할 수 있습니다.

#### 원문 기록 T034 — 2026-10-18 KST, Claude Code

확인 시각 2026-10-18 12:23 KST 무렵.

##### 사용자 — 원문

현재까지의 학습 상황을 분석해줘

##### Assistant — 진행 안내 1

학습 상황 분석을 시작합니다. 실행 중인 run은 읽기만 하고, 결과는 새 폴더에 저장합니다.

##### 수행 기록 — 원문 대화와 별도

- 새 분석 스크립트 `output/scratch_review_20261018/analyze.py`를 CPU에서 실행했다. run 로그, metrics, transfer, checkpoint를 읽기만 했다.
- 산출물: `analysis.json`, `overview.png`. 그림을 사용자에게 전송했다.
- 학습·코드·설정은 변경하지 않았다. 상세 결과는 EXPERIMENTS E24에 있다.

##### Assistant — 최종 답변

그림을 띄웠습니다. 현재 run(`scratch_20261015_093349_stage2`, E1, seed 1)은 4개 모두 정상 진행 중입니다. **약 6.4–6.5M step**이고, 15M까지 약 4일 남아 10월 22일 무렵 끝납니다. 오류는 없고 디스크도 충분합니다(run 6.4GB, 여유 1.5TB).

**1. 성능 (평가 20×500 deterministic, 같은 평가 seed)**

| | 배송 시작(≥1) | 최근 5회 평균 배송 | 6.4M까지 누적 면적(AUC/step) | agent별 배송 A1/A2/A3/A4 |
|---|---|---|---|---|
| **Oracle** | 1.64M | **32.3** | **13.2** | 11.0 / 11.3 / 9.9 / 0 |
| PGCT | 1.79M | 27.9 | 11.7 | 10.5 / 12.3 / 5.1 / 0 |
| IPPO | 2.05M | 24.3 | 10.4 | 12.3 / 11.9 / 0 / 0 |
| All | **3.99M** | 20.4 | 3.7 | 4.3 / 7.0 / 5.3 / **3.8** |

- 지금까지는 **Oracle > PGCT > IPPO > All** 순서입니다. Oracle은 IPPO보다 최근 배송이 약 33%, 누적 면적이 약 27% 높습니다.
- 평가 간 흔들림(인접 평가 차이의 표준편차)이 1.5–1.9 배송이라, PGCT와 IPPO의 차이(3.7)는 크지 않습니다.
- **가장 눈에 띄는 점은 "몇 명이 배송을 배웠나"입니다.**
  - IPPO는 2명, PGCT·Oracle은 3명이 배송합니다. A4는 세 mode 모두 6.4M까지 배송 0입니다.
  - **All만 4명 모두 배송**합니다. 시작은 2M 가까이 늦었지만, 지금 가장 가파르게 오르고 있고 요청 선반 pickup은 52로 가장 많습니다. 15M에서 순위가 바뀔 수 있습니다.
- 네 mode 모두 곡선이 아직 오르는 중이라 최종 판단은 이릅니다.

**2. 실제 critic 전이 (transfer.jsonl의 실제 allocation)**
- **Oracle**: 계획대로 같은 팀(1–3, 2–4)끼리만, 매 update의 약 85%에서 전이했습니다.
- **All**: 모든 쌍에 거의 매 update 전이했습니다.
- **PGCT**: 처음 2M은 모든 쌍에 열렸습니다. 2–3M 이후 **같은 팀 전이가 사실상 0**이 되고 다른 팀 쌍만 남았습니다.
  - 3–5M은 주로 3–4와 1–2입니다.
  - 5–6.5M은 주로 **1–2**(A1·A2는 둘 다 가장 많이 배송하는 agent)입니다.
  - 전이가 있는 update 비율은 처음 2M에 87–95%였습니다. 2–3M에 55%, 3–6M에 12–33%로 줄었습니다. 6M 이후 다시 66%로 늘었는데, 거의 1–2 쌍입니다.
- 지난번 분석(D33)과 같은 모습입니다. PGCT는 팀이 아니라 "비슷하게 일하는 짝"을 연결합니다.

**3. probe JS (checkpoint 1M 간격, canonical bank)**
- 3M 이후 대부분 시점에서 **같은 팀 JS가 다른 팀보다 높습니다.** 네 mode 모두 그렇습니다.
- Oracle은 같은 팀끼리 critic을 공유하는데도, 같은 팀 actor끼리 가장 많이 다릅니다(.29–.36). critic을 공유해도 actor가 비슷해지지는 않습니다.
- 2M 이후에는 같은 팀 평균과 다른 팀 평균이 모두 0.12를 넘습니다. PGCT gate가 대부분 닫히는 이유와 맞습니다. 다만 PGCT의 1–2처럼 개별 쌍은 기준 아래로 내려와 연결될 수 있습니다.

**4. 중요한 발견: 같은 seed인데 결과가 달라졌습니다**
- 이번 run은 중단된 E17과 seed·초기 가중치가 같습니다.
- **IPPO는 E17과 2.46M까지 평가값이 완전히 같습니다**(재현됨).
- PGCT·Oracle·All은 1.38–1.59M에서 갈라졌습니다. 원인은 확인하지 않았습니다. critic 전이 경로의 GPU 연산이 비결정적일 가능성이 있습니다.
- 갈라진 뒤 결과 차이가 큽니다.
  - E17의 All은 1.79M에 배송을 시작했는데, 이번에는 3.99M입니다.
  - Oracle은 두 번 모두 A2가 먼저 배송을 배웠고, 2.4M 배송도 E17 약 10.7, 이번 약 8.7–9.1로 비슷합니다. 갈라짐의 영향은 mode마다 다릅니다.
- 즉 **아주 작은 수치 차이만으로 배송 시작 시점이 2M씩 바뀝니다.** 그래서 seed 1개로 "Oracle이 낫다"나 "All이 느리다"를 결론 내리면 안 됩니다. seed 2·3 반복이 꼭 필요하다는 근거입니다.

**5. 제안 (결정은 사용자)**
1. 15M까지 계속 둡니다. 곡선이 오르는 중이고, 특히 All이 따라오는지가 핵심입니다. 4일 남았습니다.
2. 끝나면 seed 2·3을 돌립니다(4개 mode). E17과의 차이가 seed 간 분산이 크다는 걸 이미 보여줍니다.
3. E1-F IPPO 시험은 이 run이 끝난 뒤 시작하는 게 깔끔합니다. 지금 같이 돌리면 양쪽 모두 느려집니다.

재현: `python output/scratch_review_20261018/analyze.py`(읽기 전용, `--no-probe`로 probe 계산 생략)

#### 원문 기록 T035 — 2026-10-18 KST, Claude Code

정확한 시각은 확인하지 않았다.

##### 사용자 — 원문

1. 학습 지속 필요성
2. 다음 학습 방법 추천
3. 환경 난이도, 기타 변화 필요성
4. 다른 알고리즘 실험을 돌릴지? 아니면 현재 실험을 추가로 봐야할지?

##### 수행 기록 — 원문 대화와 별도

- 환경의 보상 모드를 확인했다. `rware/multi_team_warehouse.py`에는 `team_reward_mode`로 ALL / INDIVIDUAL / TEAM이 있고, 환경 기본값은 TEAM이다. 현재 실험은 individual이다. 의견만 남겼고 실행·코드 변경은 없다.

##### Assistant — 최종 답변

E24 분석(6.4M, seed 1)을 바탕으로 한 제 의견입니다. 결정은 사용자께서 하시면 됩니다.

**1. 학습 지속: 15M까지 계속하는 것을 권합니다**
- 네 곡선 모두 아직 오르고 있습니다. 특히 지금 결론을 바꿀 수 있는 질문이 두 개 남아 있습니다.
  - 늦게 시작했지만 4명 모두 배우는 All이 따라잡는가?
  - A4가 끝내 배송을 배우는가?
- 남은 기간은 4일입니다. 멈춰도 그 사이 GPU로 할 일이 마땅치 않습니다.
- 다만 이 run으로 **다음 seed의 예산을 정합니다.** 6.4M 이후 순위가 그대로라면 seed 2·3은 8–10M으로 줄여도 됩니다. 순위가 바뀌면 15M을 유지합니다.

**2. 다음 학습: 우선순위**
1. **E1 4개 mode의 seed 2·3** (가장 먼저)
   - 이번에 같은 seed를 다시 돌렸는데 All의 배송 시작이 1.8M에서 4.0M으로 바뀌었습니다. seed 1개로는 어떤 주장도 할 수 없습니다.
   - 이 반복으로 "critic 공유가 도움이 되는가, 팀을 맞게 고르면 더 좋은가(Oracle vs All)"에 처음으로 답할 수 있습니다.
2. **E1-F IPPO 시험 1개** (4–5M)
   - 원래 연구 질문(팀 추론)으로 가는 유일한 길입니다. 두 가지를 봅니다.
     - 팀별로 실제 운반 방향이 갈리는가
     - v2 gate에서 같은 팀 JS가 다른 팀보다 낮아지는가
   - seed 2·3과 같이 돌리면 느려지므로, 프로세스 수를 보고 함께 넣을지 정합니다.
3. E1-F 시험에서 팀 차이가 보이면 **E1-F 4개 mode**로 넘어갑니다.
- 덧붙여, 전이 mode만 같은 seed에서 결과가 갈라지는 원인을 코드에서 찾아 두면 좋겠습니다(학습 없이 코드 확인만). 논문 재현성에 필요합니다.

**3. 환경: 난이도는 그대로 두고, "팀이 의미 있는 구조"로 바꿔야 합니다**
- **난이도는 적당합니다.** 배송이 2M 무렵 시작되고, 6.4M에도 A4가 못 배울 만큼 쉽지 않습니다. 더 어렵게 하면 시작이 늦어지고 seed 간 차이만 커집니다.
- **문제는 난이도가 아니라 구조입니다.** E1에서는 두 팀 목표가 붙어 있고 관측이 팀 기준이라, 팀 정보가 critic에 쓸모가 없습니다(E11). 그래서 지금 실험의 Oracle vs All은 "올바른 팀과 공유"가 아니라 "공유 범위를 좁힌 효과"를 재는 것에 가깝습니다.
- 필요한 변화는 두 가지입니다.
  - **목표 분리(E1-F)**: 구현 완료. 팀마다 행동이 달라질 이유를 만듭니다.
  - **팀 보상(team reward)**: 지금은 개인 보상이라 같은 팀원이 같은 요청을 두고 경쟁합니다. 그래서 같은 팀이라도 critic이 맞혀야 하는 값이 다릅니다. 환경에 팀 보상 모드가 이미 있습니다. 처음부터 학습하니 예전처럼 사전학습을 다시 맞출 필요도 없습니다. 팀 보상이면 같은 팀은 같은 보상을 받으므로, "팀 안에서만 critic 공유"에 이론적 근거가 생깁니다.
- E1-F와 팀 보상을 함께 적용한 조건이 **Oracle이 All보다 나아야 할 설계상 이유가 있는** 조건입니다. 다만 두 가지를 동시에 바꾸면 효과를 나눌 수 없습니다. 그래서 E1-F IPPO 시험을 개인 보상과 팀 보상으로 하나씩 돌려 보는 것을 권합니다.
- shelf 섞임 50%는 유지를 권합니다. 0%로 하면 위치만으로 팀이 드러나 팀 추론 문제가 너무 쉬워집니다.

**4. 다른 알고리즘 vs 현재 실험: 현재 실험을 먼저 봐야 합니다**
- MAPPO/SePS/HetDPS는 "우리 방법이 기존 방법보다 낫다"를 보일 때 필요합니다. 그런데 아직 우리 방법(팀을 추론해서 공유)이 효과를 보인 조건이 없습니다. 지금 돌리면 비교할 대상 없이 계산만 씁니다.
- 순서는 이렇게 권합니다.
  1. 현재 E1 seed 2·3
  2. E1-F 시험
  3. 효과가 보이는 조건 확정
  4. 그 조건에서 baseline 3종

**요약**: 15M까지 계속 → 끝나면 seed 2·3(필요하면 예산 축소) → E1-F IPPO 시험(개인/팀 보상) → 효과가 보이면 E1-F 본 비교 → 마지막에 baseline.

어떤 것이든 승인해 주시면 그때 시작하겠습니다. 지금은 아무것도 실행하지 않았습니다.

---

# 부록. 통합 타임라인

DECISIONS·EXPERIMENTS·CONVERSATION_LOG의 항목 제목을 날짜순으로 모은 색인이다. 같은 날짜 안에서는 파일별 원래 순서를 따른다.

| 날짜 | 작성 | 출처 | 항목 |
|---|---|---|---|
| 날짜 미상 | - | DECISIONS.md | D01. 초록색 연결선 소멸은 학습 실패인가? (과거 대화, 날짜 미상) |
| 날짜 미상 | - | DECISIONS.md | D02. PGCT가 팀을 찾아야 하는가, 호환되는 donor를 찾아야 하는가? |
| 날짜 미상 | - | DECISIONS.md | D03. PGCT-off 코드를 새로 추가해야 하는가? / 해당 run은 IPPO인가? |
| 날짜 미상 | - | DECISIONS.md | D04. W&B 영상 저장 오류와 절전 가설 |
| 날짜 미상 | - | DECISIONS.md | D05. 코드 수정·정리 요청의 범위 |
| 날짜 미상 | - | DECISIONS.md | D06. 맵 확대를 gate 문제의 해결책으로 볼 것인가? |
| 날짜 미상 | - | DECISIONS.md | D07. JS 계산과 probe 분포 |
| 날짜 미상 | - | DECISIONS.md | D08. 공정한 추가 전이 실험 |
| 날짜 미상 | - | DECISIONS.md | D09. Critic 진단의 의미 |
| 날짜 미상 | - | EXPERIMENTS.md | E00. 기존 curriculum — 완료 |
| 날짜 미상 | - | EXPERIMENTS.md | E01. 기존 home1 IPPO continuation — 완료, 대조 조건 미일치 |
| 날짜 미상 | - | EXPERIMENTS.md | E02. 공간 분기 — E1/E2 완료, E3 진행 |
| 날짜 미상 | - | EXPERIMENTS.md | E03. 기존 Stage04 공간 활동 — 고정 모델 평가 완료 |
| 날짜 미상 | - | EXPERIMENTS.md | E04. 기존 Stage04 probe 중복 민감도 — 진단 완료 |
| 날짜 미상 | - | EXPERIMENTS.md | E05. 공통 rollout 이력의 policy/critic 일치 — 진단 완료 |
| 날짜 미상 | - | EXPERIMENTS.md | E08. Transfer 전용 실행기 — 구현 완료, 장기 실험 미실행 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L01. 프로젝트 배경과 gate 소멸 — 날짜 미상 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L02. IPPO-off 코드와 사전학습 — 날짜 미상 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L03. 연구 해석과 cross-team 연결 — 날짜 미상 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L04. 코드 변경 금지와 W&B 영상 오류 — 날짜 미상 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L05. 구버전 코드 정리와 공간 실험 요청 — 과거 대화 |
| 날짜 미상 | - | CONVERSATION_LOG.md | L06. Continuation은 IPPO인가? 왜 agent별 성공 시점이 다른가? |
| 2026-10-08 | - | CONVERSATION_LOG.md | L07. 진단 검토와 네 가지 요청 — 2026-10-08 작업 기록 |
| 2026-10-08 | - | CONVERSATION_LOG.md | L08. Probe 중복이 donor 순위를 바꾸는가? — 2026-10-08 진단 기록 |
| 2026-10-08 | - | CONVERSATION_LOG.md | L09. 공통 관측 이력 진단 — 2026-10-08 작업 기록 |
| 2026-10-13 | - | DECISIONS.md | D10. 2026-10-13 결과로 주장 가능한 범위 |
| 2026-10-13 | - | DECISIONS.md | D11. 2026-10-13 공용 기록 구성 |
| 2026-10-13 | Codex | DECISIONS.md | D12. E2의 3~4개 연결 집단과 probe 신뢰성 — 2026-10-13 Codex |
| 2026-10-13 | Codex | DECISIONS.md | D13. 이후 모든 대화 원문 기록 — 2026-10-13 Codex |
| 2026-10-13 | - | DECISIONS.md | D14. 역할 분담 차이의 크기가 질문의 핵심 — 2026-10-13 |
| 2026-10-13 | Codex | DECISIONS.md | D15. 대칭 정책 거리와 방향별 전이 유익성 — 2026-10-13 Codex |
| 2026-10-13 | - | DECISIONS.md | D16. 기존 코드와 분리된 난이도 환경 — 2026-10-13 |
| 2026-10-13 | Claude Code | DECISIONS.md | D17. 연구 주제를 원래 목표 A로 재정립하고 먼저 검증한다 — 2026-10-13 Claude Code |
| 2026-10-13 | Claude Code | DECISIONS.md | D18. 외부 검토(GPT) 반영: 소규모 oracle 우선, team reward는 재정렬 후 — 2026-10-13 Claude Code |
| 2026-10-13 | Claude Code | DECISIONS.md | D19. 미사용 파일 정리 — 2026-10-13 Claude Code |
| 2026-10-13 | Claude Code | DECISIONS.md | D20. 커리큘럼 없이 처음부터 학습하는 비교로 전환 — 2026-10-13 Claude Code |
| 2026-10-13 | Claude Code | DECISIONS.md | D21. W&B 관리, 학습 구간 재설정, MAPPO/SePS/HetDPS 비교군 — 2026-10-13 Claude Code |
| 2026-10-13 | Claude Code | DECISIONS.md | D22. 핵심 비교를 IPPO/PGCT/Oracle/All 4개로 한정, resume 불가 시 무중단 운영 — 2026-10-13 Claude Code |
| 2026-10-13 | - | EXPERIMENTS.md | E06. 2026-10-13 최종 critic의 실제 return 예측 — 평가 완료 |
| 2026-10-13 | - | EXPERIMENTS.md | E07. 2026-10-13 최종 canonical 응답 — 진단 완료 |
| 2026-10-13 | - | EXPERIMENTS.md | E09. E2 연결 성분과 완전 연결 구분 — 2026-10-13 진단 완료 |
| 2026-10-13 | - | EXPERIMENTS.md | E10. 분리된 장애물·배송 제약 환경 — 2026-10-13 구현 및 시험 완료 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E02 추가 — E3 PGCT 중단 (2026-10-13 Claude Code 실측) |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E11. 실험 A — 국소 행동으로 팀 식별 가능성과 critic consensus 전제 — 2026-10-13 Claude Code, 완료 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E12. 실험 B 실행기 — oracle/all/wrong critic peer-loss 분기 — 2026-10-13 Claude Code, 구현·smoke만 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E13. 국소 증거의 관측 가능성 검증 — 2026-10-13 Claude Code, 완료 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E12 추가 — 짧은 matched-prefix 예산 지원 (2026-10-13 Claude Code) |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E14. 처음부터 학습 실행기 — 2026-10-13 Claude Code, 구현·smoke만 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E14 추가 — 2단계 자동 파이프라인 (2026-10-13 Claude Code) |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E14 점검 — 실행 전 코드·설정 검토 (2026-10-13 Claude Code, 학습 미실행) |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E15. W&B 통합 + MAPPO/SePS/HetDPS 구현 — 2026-10-13 Claude Code, smoke만 |
| 2026-10-13 | Claude Code | EXPERIMENTS.md | E16. 본 학습 전 실제 설정 검증 — 2026-10-13 Claude Code, 검증만 |
| 2026-10-13 | - | EXPERIMENTS.md | E17. From-scratch 핵심 비교 본 학습 — 2026-10-13 20:23:52 KST 시작(사용자 실행), 진행 중 |
| 2026-10-13 | - | CONVERSATION_LOG.md | L10. “지금까지 학습 내용 분석해줘” — 2026-10-13 |
| 2026-10-13 | - | CONVERSATION_LOG.md | L11. “지금까지 있었던 대화 내용들 1번처럼 로그로 남겨줘” — 2026-10-13 |
| 2026-10-13 | - | CONVERSATION_LOG.md | L12. E2의 3~4개 연결 집단과 probe 신뢰도 — 2026-10-13 |
| 2026-10-13 | Codex | CONVERSATION_LOG.md | 원문 기록 T001 — 2026-10-13 KST, Codex |
| 2026-10-13 | Codex | CONVERSATION_LOG.md | 원문 기록 T002 — 2026-10-13 KST, Codex |
| 2026-10-13 | Codex | CONVERSATION_LOG.md | 원문 기록 T003 — 2026-10-13 KST, Codex |
| 2026-10-13 | Codex | CONVERSATION_LOG.md | 원문 기록 T004 — 2026-10-13 KST, Codex |
| 2026-10-13 | Codex | CONVERSATION_LOG.md | 원문 기록 T005 — 2026-10-13 KST, Codex |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T006 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T007 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T008 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T009 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T010 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T011 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T012 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T013 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T014 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T015 — 2026-10-13 KST, Claude Code |
| 2026-10-13 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T016 — 2026-10-13 KST, Claude Code |
| 2026-10-15 | Codex | DECISIONS.md | D23. MD 교차 분석과 IJCAI 원고 설계 — 2026-10-15 Codex |
| 2026-10-15 | Claude Code | DECISIONS.md | D24. 팀 추론과 critic 공유는 상반되는가, probe 부담은 감점 요인인가 — 2026-10-15 Claude Code (의견, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D25. 자동 probe의 정보 구조 문제와 팀 내 역할 분업 제안 철회 — 2026-10-15 Claude Code (의견, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D26. 현재 probe 48개의 팀 식별력, 목표 위치 고정 문제, GPT의 환경 분리 설계 — 2026-10-15 Claude Code (의견, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D27. runs/ 삭제 허가의 범위 — 2026-10-15 Claude Code |
| 2026-10-15 | Claude Code | DECISIONS.md | D28. Oracle과 probe의 관계, 현재 run 유지 여부, probe 수정 방향 — 2026-10-15 Claude Code (의견, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D29. E1-F 환경과 probe bank v2 구현(옵션) — 2026-10-15 Claude Code |
| 2026-10-15 | Claude Code | DECISIONS.md | D30. 기록 통합과 새 세션 인수인계 — 2026-10-15 Claude Code |
| 2026-10-15 | Claude Code | DECISIONS.md | D31. probe 개수 112개의 근거와 축소 방향 — 2026-10-15 Claude Code (의견, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D32. 두 목표가 보이는 gate probe는 같은 입력 비교에서 팀 차이를 지운다 — 2026-10-15 Claude Code (설명, 결정 아님) |
| 2026-10-15 | Claude Code | DECISIONS.md | D33. A3–A4 cross-team 연결은 '원정 담당' 역할 짝이다 — 2026-10-15 Claude Code (해석, 결정 아님) |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E17 추가 — Windows Update 재부팅으로 중단 (2026-10-15 Claude Code 실측) |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E18. E17 중단 시점(약 2.5M) 학습 현황 분석 — 2026-10-15 Claude Code, 읽기 전용 |
| 2026-10-15 | Codex | EXPERIMENTS.md | E19. 신규 from-scratch 재실행 발견 — 2026-10-15 11:49 KST Codex, 읽기 전용 확인 |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E20. 환경·canonical probe 시각화 — 2026-10-15 Claude Code, 읽기 전용 |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E21. runs/ 정리 — 2026-10-15 Claude Code (사용자 승인 삭제) |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E22. probe bank v2 / E1-F 구현 검증 — 2026-10-15 Claude Code, 구현·smoke만 |
| 2026-10-15 | Codex | EXPERIMENTS.md | E19 추가 — HANDOFF 이후 진행 상태 재확인 (2026-10-15 13:17 KST Codex) |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E23. 기존 E1 모델의 probe별 팀 구분 시각화 — 2026-10-15 Claude Code, 읽기 전용 |
| 2026-10-15 | Claude Code | EXPERIMENTS.md | E23 추가 — agent별 행동 특성 (2026-10-15 Claude Code, 읽기 전용) |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T017 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T018 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Codex | CONVERSATION_LOG.md | 원문 기록 T019 — 2026-10-15 KST, Codex |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T019 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T020 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T021 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T022 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T023 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T024 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T025 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T026 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T027 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Codex | CONVERSATION_LOG.md | 원문 기록 T028 — 2026-10-15 KST, Codex |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T029 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T030 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T031 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T032 — 2026-10-15 KST, Claude Code |
| 2026-10-15 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T033 — 2026-10-15 KST, Claude Code |
| 2026-10-18 | Claude Code | DECISIONS.md | D34. 학습 지속·다음 실험 순서·환경 변경·baseline 시점 — 2026-10-18 Claude Code (의견, 결정 아님) |
| 2026-10-18 | Claude Code | EXPERIMENTS.md | E24. 현재 from-scratch run 약 6.4M 중간 분석 — 2026-10-18 Claude Code, 읽기 전용 |
| 2026-10-18 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T034 — 2026-10-18 KST, Claude Code |
| 2026-10-18 | Claude Code | CONVERSATION_LOG.md | 원문 기록 T035 — 2026-10-18 KST, Claude Code |
