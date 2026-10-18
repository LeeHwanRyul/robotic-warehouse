# IJCAI 방법 논문 초안 v0.3 (Overleaf 프로젝트)

2026-10-18 Claude Code. 경과는 다음과 같다.
- 사용자 요청: 새 알고리즘(PGCT)의 성능을 보이는 논문 초판을 지금까지의 데이터로 작성한다.
- 원래 기획에 맞게 수정했다(v0.2, D41).
- 외부 검토와 이론 보강안(D43)을 반영해 다시 썼다(v0.3, D44).

## v0.3에서 바뀐 것

- **이름 통일**: Probe-Gated Critic Transfer(PGCT).
- **표현**: "팀 발견"을 "국소 팀원 추론(local teammate inference)"으로 바꿨다. 질문은 Q1(누가 팀원인가), Q2(누구의 critic이 돕는가), Q3(Q1이 언제 Q2의 좋은 답인가)로 나눴다.
- **이론 절 신설(Section 6, 증명은 부록 A)**
  - 명제 1: probe divergence의 성질(유계, 대칭, 결합 볼록, √D pseudometric). 교수님의 JS convexity 질문에 답한다(JS는 최적화 대상이 아니다).
  - 가정 1(probe 비교 가능성), 가정 2(분리 마진).
  - 명제 2: 2ε<Δ이면 국소 팀 관계를 정확히 복원한다.
  - 보조정리 1·명제 3: 정책 변화(KL) → divergence 변화 → EMA 추적 오차 ≤ (1−β)/β·ρ.
  - 명제 4: distillation은 출력 공간에서 강볼록이고, 잘못된 donor 편향 ≤ λ/(c+λ)·[(1−a_w)η + a_w Γ](≈0.02배)다.
  - 명제 5: 정책 유사 ≠ 가치 유사(반례).
  - 명제 6: 팀이 유도하는 결정 문제가 일치하면 식별할 수 없다(E1 설명). 절대 위치 관측과 목표 분리가 있으면 적용되지 않는다(E1-F).
- **실험 설계**: 식별 가능성 × 호환성 2×2 표. Random-gated(전이량 통제)와 budget-matched Oracle을 추가했다(TBD). 지표에 정밀도·재현율·F1, 실측 Δ·ρ를 넣었다.
- **결과 해석**: E1의 성능 향상은 H1(팀원 전이)로 설명할 수 없다(4M 이후 전이의 95%가 팀 간). H2(선택적 전이)와 H3(전이량 감소)는 random gate로 가른다.
- **알고리즘 세부**(코드로 확인): EMA는 첫 측정값으로 초기화하고 이웃일 때만 갱신한다. 범위를 벗어나면 값을 유지하되 전이하지 않는다. n_min=8, 빈 donor 집합이면 peer 항 0, 양방향 동시 전이, 자연로그(τ=0.12 nats), 통신량을 명시했다.
- **참고문헌**: MADPS(AAMAS 2024), HetDPS(AAMAS 2026, 검토 제공 서지 — 확인 필요), Ng & Russell 2000, Endres & Schindelin 2003을 추가했다.

## 파일

| 파일 | 내용 |
|---|---|
| `main.tex` | **v0.3 영어 원고(제출용)**. IJCAI 형식, 익명 |
| `main_ko.tex` | **v0.3 한국어 번역본** |
| `main_v0.2.tex`, `main_ko_v0.2.tex` | v0.2 보존본 |
| `main_v0.1.tex`, `main_ko_v0.1.tex` | v0.1 보존본("호환되는 상대 선택" 서사, 원래 기획에서 벗어남) |
| `references.bib` | 참고문헌(v0.3은 14개 인용) |
| `figures/`, `tables/` | 그림·표(`output/paper_e1_20261018/make_paper_materials.py`로 생성) |
| `ijcai_method_paper_20261018_overleaf.zip` | 위 전부. Overleaf에 그대로 업로드 |

## v0.2 서사

- **제목**: *Finding Your Team Without Labels: Policy-Probe Discovery of Latent Teammates for Critic Sharing in Multi-Agent Reinforcement Learning*
- **방법**: PGCT는 공유 probe에 대한 정책 응답(JS 거리, EMA)으로 **잠재 팀원을 추정**하고, 추정한 팀 안에서 critic을 distillation한다. 변형 PGCT-v2는 팀을 가르는 발견용 probe 48개와 distillation용 probe 64개를 분리한다.
- **실험 두 조건**
  - **E1 = 팀 대칭 대조 조건**: 팀이 라벨로만 달라 행동으로 구분할 수 없다. 이 조건에서도 PGCT는 IPPO와 All-peer를 앞섰고(seed 1), 팀 대신 같은 역할의 agent를 연결했다. 그래도 해가 없다는 결과로 쓴다.
  - **E1-F = 주 실험**(TBD): 팀 목표가 갈라진다. 네 고리를 차례로 평가한다. ① Oracle > All인가 ② 팀원의 critic이 더 호환되는가 ③ PGCT가 팀을 찾는가(같은 팀 전이 비율, probe AUROC, 행동 분화) ④ 학습이 개선되는가.

## 현재 수치 (E1, seed 1, 공통 구간 6.4M)

| | 시작 | 평균 | 최종 | 학습 agent |
|---|---|---|---|---|
| IPPO | 2.05M | 10.4 | 23.2 | 2/4 |
| All-peer | 3.99M | 3.7 | 19.4 | 4/4 |
| **PGCT** | **1.79M** | **11.7** | **27.3** | 3/4 |
| Oracle-team | 1.64M | 13.2 | 32.2 | 3/4 |

## 위험 요소

1. PGCT와 IPPO의 차이가 작고 seed 1개다. 같은 seed를 다시 돌린 E17에서는 2.4M 무렵 순위가 반대였다.
2. 원래 기획의 성패는 E1-F에 달려 있다. 분기는 D41에 있다(Oracle>All + 같은 팀 선택 → 기획대로; 같은 팀을 못 고름 → v2 비교; Oracle≈All → 조건 추가나 방향 재논의).
3. "뒤처진 agent 구제" 메커니즘은 관찰이며, 개입 실험이 필요하다.

## Overleaf

1. New Project → Upload Project → zip.
2. IJCAI Author Kit의 `ijcai27.sty`(또는 `ijcai26.sty`)와 `named.bst`를 추가한다. 없으면 비슷한 2단 형식으로 컴파일된다.
3. 영어 `main.tex`는 pdfLaTeX, 한국어 `main_ko.tex`는 pdfLaTeX(글꼴 오류 시 XeLaTeX)로 컴파일한다.

로컬에 LaTeX가 없어 컴파일하지 않았다. 구조 검사(환경, 중괄호, `$`, 인용, 참조)만 통과했다.

## 실험이 끝나면 채울 곳

| 결과 | 위치 |
|---|---|
| E1 seed 2–3 | Table 1 마지막 열, Fig. 1, 본문 %, 초록 |
| E1-F 5개 run | Section 7(E1-F), Table 2, 초록 마지막 문장, 결론 |
| E1-F 팀 분화·probe AUROC | `python latent_team/e1f_team_divergence.py --run runs/e1f_20261018_124343_main_canonical`(main_v2도) |
| E1-F 가치 호환성 | E11 방식(`latent_team/exp_a_team_identifiability.py`)을 E1-F checkpoint에 적용(스크립트 확장 필요) |
| 개입 실험, baseline 3종 | 해당 TODO |
