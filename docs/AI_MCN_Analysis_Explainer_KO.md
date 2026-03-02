# AI-MCN 전체 분석 설명서 (한국어)

이 문서는 이 프로젝트를 처음 보는 팀원도 이해할 수 있도록,
데이터 준비부터 클리닝, 분석, 추천 생성, 대시보드 해석까지 전체 과정을 자세히 설명합니다.

대상:
- 코드에 익숙하지 않은 팀원
- 발표/Q&A 준비 중인 팀원
- 추천 결과가 어떻게 나왔는지 검증하려는 팀원

범위:
- 현재 코드(`app.py`, `src/*`)에 실제 구현된 동작 기준
- "앞으로 하고 싶은 것"이 아니라 "지금 실제로 하는 것" 설명

---

## 0) 1분 요약

시스템은 캠페인 브리프를 입력받아, 보유한 CSV 데이터 안에서 인플루언서 채널을 점수화하고 순위를 매깁니다.

핵심 결합 신호:
- 네트워크 구조 영향력
- 캠페인 텍스트 적합도
- 의미/톤 정합성
- 관측된 참여 성과
- 옵션 ML 잠재력
- 신뢰도 페널티 + 다양성 가드레일

결과는 단순 Top-N이 아니라:
- 왜 추천됐는지
- 리스크가 무엇인지
- 벤치마크 대비 어떤지
- ROI 시나리오가 어떤지
까지 같이 제공합니다.

중요:
- 입력 텍스트가 실시간 웹 리서치를 수행하지는 않습니다.
- 입력값은 기존 CSV에 대한 필터/점수 기준으로 작동합니다.

---

## 1) 코드 구조 (어디에 무엇이 있는지)

앱 UI:
- `app.py`: Streamlit 화면, 컨트롤, 탭, 인터랙션 차트

파이프라인 총괄:
- `src/orchestrator.py`: 전체 실행 순서

데이터 준비:
- `src/data_prep.py`: 정제, 필터, 피처 생성, 채널 집계

네트워크 분석:
- `src/network_scoring.py`: 그래프 생성, 중심성, 커뮤니티

텍스트 분석:
- `src/text_scoring.py`: TF-IDF + 키워드 가중/감점
- `src/semantic_enrichment.py`: 상위 후보 semantic/tone 정밀 분석

ML 분석:
- `src/ml_modeling.py`: 모델 학습, GroupKFold, baseline 비교, SHAP

최종 랭킹:
- `src/ranking.py`: 최종 점수식, 신뢰도 배수, 다양성 선택

ROI:
- `src/roi_simulation.py`

전략/메모:
- `src/content_generation.py`

상세 정보 보강:
- `src/channel_details.py`
- `src/channel_media.py`

데이터 경로/다운로드:
- `src/config.py`: combined 우선, demo fallback
- `src/data_bootstrap.py`: GDrive 자동 다운로드

---

## 2) 데이터 로딩 로직 (full/demo/GDrive)

### 2.1 파일 선택 우선순위

런타임에서 아래 순서로 파일을 찾습니다.

1. `data/videos_text_ready_combined.csv` 없으면 `data/videos_text_ready_demo.csv`
2. `data/comments_raw_combined.csv` 없으면 `data/comments_raw_demo.csv`
3. `data/master_prd_slim_combined.csv` 없으면 `data/master_prd_slim_demo.csv`

즉, combined 파일이 있으면 full 데이터 분석입니다.

### 2.2 Cloud에서 full 데이터 자동 다운로드

파이프라인 시작 전에 GDrive 다운로드를 먼저 시도합니다.

지원 키:
- 폴더 단위:
  - `GDRIVE_FOLDER_URL` 또는 `GDRIVE_FOLDER_ID`
- 파일 단위:
  - `GDRIVE_VIDEOS_FILE_ID` / `GDRIVE_VIDEOS_URL`
  - `GDRIVE_COMMENTS_FILE_ID` / `GDRIVE_COMMENTS_URL`
  - `GDRIVE_MASTER_FILE_ID` / `GDRIVE_MASTER_URL`

현재 레포 기본값:
- `GDRIVE_*`가 전혀 없으면 코드에 내장된 기본 폴더 URL을 사용합니다.

### 2.3 폴더 내 파일명 조건

폴더에 아래 이름이 정확히 있어야 자동 인식됩니다.
- `videos_text_ready_combined.csv`
- `comments_raw_combined.csv`
- `master_prd_slim_combined.csv`

---

## 3) 캠페인 입력값 영향도

입력 항목:
- Brand Name
- Product Name
- Category
- Target Audience
- Campaign Goal
- USP
- Budget
- Market
- Must keywords
- Exclude keywords
- Top-N
- 네트워크 고급 설정
- ML on/off 및 모델 선택
- 벤치마크 on/off

영향이 큰 항목:
- must/exclude keywords
- campaign goal
- 네트워크 설정값(엣지 강도/태그 비율/커뮤니티 최소 크기)

중간 영향:
- audience 텍스트
- USP 텍스트

낮은 영향(현재 구현):
- brand name만 변경
- product name만 변경
- market 텍스트만 변경

Budget 영향:
- ROI 탭 수치에 강하게 영향
- 핵심 랭킹 점수식에는 직접 반영되지 않음

---

## 4) 전체 파이프라인 실행 순서

1. 입력값으로 `BrandBrief` 생성
2. 영상/댓글 데이터 전처리
3. 공유 태그 기반 그래프 생성
4. 네트워크 점수 + 커뮤니티 계산
5. (옵션) ML 학습 후 채널별 ML 잠재력 점수 생성
6. TF-IDF 텍스트 점수 계산
7. 사전 랭킹으로 상위 후보 추출
8. 상위 후보에 semantic/tone 정밀 분석
9. semantic 결과 병합
10. 최종 점수 계산 + 신뢰도 페널티 + 다양성 적용
11. 채널 상세정보/미디어 정보 병합
12. (옵션) CeraVe 벤치마크 수행
13. ROI 시뮬레이션
14. 전략 텍스트/메모 생성
15. CSV/메모/ML 산출물 저장
16. 대시보드 탭 렌더링

---

## 5) 데이터 준비/클리닝 상세

### 5.1 영상 데이터 정제

`prepare_videos`에서 수행:

- `_video_id` 중복 제거
- 조회수/좋아요/댓글수 숫자형 변환
- 게시일 파싱
- 텍스트 필드 구성:
  - `video_title`, `video_description`, `tags_list`, `tags_text`, `full_text`

### 5.2 포함/제외 필터

포함 키워드:
- 뷰티 기본 키워드 + 사용자가 입력한 must 키워드

제외 키워드:
- 노이즈 기본 키워드 + 사용자가 입력한 exclude 키워드

필터 결과:
- include hit true
- exclude hit false
인 행만 남김

### 5.3 하드 품질 조건

아래 조건을 만족하는 영상만 유지:
- `viewCount > 0`
- likes/comments 음수 아님

### 5.4 ML 타깃 생성

수식:
- `engagement_rate = (likes + comments + 1) / (views + 100)`
- `engagement_target = log1p(engagement_rate)`

### 5.5 보조 피처 생성

- `days_since_publish`
- `title_len`, `desc_len`
- `hashtag_count`, `tag_count`
- `log_views`, `log_likes`, `log_comments`

### 5.6 댓글 데이터 정제

`prepare_comments`:
- `_comment_id` 중복 제거
- like count 정규화
- 날짜 파싱
- `comment_len` 생성

### 5.7 채널 단위 집계

채널별로:
- `n_videos`
- `median_views`, `median_likes`, `median_comments`
- `mean_engagement`
- `latest_publish`

추가 필드:
- 대표 영상 id(조회수 최대)
- 태그 집계
- `channel_text` (텍스트 분석 입력)
- 댓글 통계 병합

---

## 6) 네트워크 분석 상세

### 6.1 그래프 생성

노드:
- 채널 1개당 노드 1개

엣지:
- 공통 태그가 있는 채널끼리 연결
- 엣지 가중치 = 공통 태그 수

노이즈 제어:
- 너무 흔한 태그는 제거
- `weight >= min_shared_tags`만 엣지 유지

### 6.2 중심성 피처

- `degree_centrality`
- `betweenness_centrality` (proxy)
- `eigenvector_centrality` proxy

결합 점수:
- `sna_score_raw = 0.33*degree + 0.34*betweenness + 0.33*eigenvector`
- `sna_score = min-max(sna_score_raw)`

### 6.3 커뮤니티

- label propagation 방식
- `min_community_size`보다 작은 군집은 `community_id = -1`

---

## 7) 텍스트 분석 상세

### 7.1 TF-IDF 유사도

- Corpus: 채널별 `channel_text`
- Query: 브랜드 브리프 전체 + must keywords
- 코사인 유사도 계산

### 7.2 키워드 가중/감점

채널별:
- `must_hit` 개수
- `exclude_hit` 개수
- `keyword_boost = 0.08*must_hit - 0.12*exclude_hit`

최종:
- `tfidf_similarity = min-max(raw_similarity + keyword_boost)`

---

## 8) Semantic/Tone 정밀 분석

전체 채널이 아니라 상위 후보에만 적용합니다.

### 8.1 semantic 점수

기본 유사도에:
- `+0.04 * must_hit`
- `-0.08 * exclude_hit`

적용 후 `[0,1]`로 제한

### 8.2 tone 점수

목표(goal)에 따라 톤 사전을 바꿔 매칭:
- conversion 성격: review/demo/results 등
- awareness 성격: story/tips/guide 등

### 8.3 red flag

아래 경우 경고 생성:
- 제외 키워드 신호 포함
- semantic < 0.20
- `n_videos < 5`

---

## 9) ML 분석 상세

### 9.1 목적

- 단순 baseline보다 예측력이 의미 있게 좋아지는지 검증
- 좋아질 때만 최종 랭킹에 ML 신호 반영

### 9.2 입력과 타깃

타깃:
- `engagement_target`

피처(숫자 8개):
- `log_views`, `log_likes`, `log_comments`
- `days_since_publish`
- `title_len`, `desc_len`
- `hashtag_count`, `tag_count`

정규화:
- `StandardScaler`

### 9.3 검증

- `GroupKFold(n_splits=5)`
- 그룹 단위 = channel id

### 9.4 모델

- LinearRegression
- LASSO
- Ridge
- CART
- RandomForest
- LightGBM(설치 시)

기준선:
- BaselineMedian

### 9.5 지표

- RMSE
- MAE
- R2

최고 모델 선택:
- CV RMSE 최저

### 9.6 ML 반영 게이트

최종 점수에 ML 반영 조건:
- best model이 baseline 대비 RMSE 2% 이상 개선

### 9.7 SHAP

트리 모델 + SHAP 패키지 있을 때:
- SHAP summary
- SHAP dependence

---

## 10) 최종 랭킹 엔진 (가장 중요)

### 10.1 참여 점수

- `engagement_score = min-max(mean_engagement)`

### 10.2 증거 점수(evidence)

구성:
- `scale_score = min-max(log1p(median_views))`
- `activity_score = min-max(log1p(n_videos))`
- `interaction_score = min-max(log1p(median_likes + median_comments))`

수식:
- `evidence_score = 0.55*scale + 0.30*activity + 0.15*interaction`

### 10.3 신뢰도 배수(credibility multiplier)

기본:
- `credibility_multiplier = clip(0.35 + 0.65*evidence_score, 0.20, 1.00)`

초저신호 추가 페널티:
- `median_views < 100` and `median_likes <= 1` and `median_comments <= 1`
- 위 조건이면 배수에 `*0.30`

최종 clip:
- `[0.08, 1.00]`

### 10.4 추천 가능 조건

아래 중 하나 만족하면 추천 풀 유지:
- `evidence_score >= 0.20`
- `median_views >= 500`
- `n_videos >= 12`

### 10.5 가중합 점수식

ML 활성 시:
- `0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`

ML 비활성 시:
- `0.34*SNA + 0.24*TFIDF + 0.18*Semantic + 0.10*Tone + 0.14*Engagement`

그 다음:
- `final_score_base = weighted_sum`
- `final_score = final_score_base * credibility_multiplier`

### 10.6 다양성 가드레일

정렬 후 Top-N 구성 시,
커뮤니티 다양성을 만족하도록 재선정 시도합니다.

---

## 11) 벤치마크 분석 (Anchor vs CeraVe)

옵션 ON이면:
- CeraVe 고정 브리프로 동일 랭킹을 1회 더 수행

비교값:
- anchor Top-N 평균 점수
- benchmark Top-N 평균 점수
- gap (anchor - benchmark)

목적:
- "우리 shortlist가 상대적으로 강한가"를 컨텍스트로 보여줌

---

## 12) 채널 상세정보 보강

`channel_details.py`에서 제공:
- 채널 스냅샷
- 키워드 요약
- 최근 영상
- 최고 조회 영상
- 최근 댓글
- 최다 좋아요 댓글
- 구독자/영상수 추정치(master 기반)

`channel_media.py`에서 제공:
- 채널 이미지(가능 시 API)
- fallback 썸네일
- 채널/영상 링크

---

## 13) ROI 시뮬레이터

입력:
- Budget, CPM, CTR, CVR, AOV

수식:
- `impressions = (budget / cpm) * 1000`
- `clicks = impressions * ctr`
- `conversions = clicks * cvr`
- `revenue = conversions * aov`
- `roas = revenue / budget`

불확실성 밴드:
- `roas_low = roas * 0.7`
- `roas_high = roas * 1.3`

해석:
- 인과추론 결과가 아니라 시나리오 계산

---

## 14) 전략 생성 / 메모 생성

전략 생성:
- `OPENAI_API_KEY`가 있으면 채널별 문안 생성
- 없으면 템플릿 fallback

메모 생성:
- Top 채널 + ROI + 리스크를 묶어 markdown/text로 내보냄

---

## 15) 탭별 해석 가이드

## 15.1 Overview

- 데이터 규모, 모델 요약
- 캠페인 입력 스냅샷
- 평균 evidence 기반 신뢰도 배너
- 벤치마크 패널

## 15.2 Top Matches

이 탭은 전략 프리셋으로 재랭킹할 수 있습니다.

흐름:
1. 전략 선택
2. `display_score` 계산
3. Min Match / Min Evidence 필터
4. 다양성 미리보기 적용
5. 카드 + 상세 테이블 출력

프리셋 가중치:
- Network-first: SNA 0.46, TF-IDF 0.16, Semantic 0.14, Tone 0.08, Eng 0.14, ML 0.02
- Keyword-first: SNA 0.20, TF-IDF 0.42, Semantic 0.18, Tone 0.08, Eng 0.10, ML 0.02
- Performance-first: SNA 0.20, TF-IDF 0.12, Semantic 0.16, Tone 0.08, Eng 0.38, ML 0.06

ML 비활성 런은 ML 가중치 0 처리 후 정규화합니다.

## 15.3 Network Studio

- 인터랙티브 네트워크 그래프
- 커뮤니티 분포
- 그래프 메타
- bias report(centrality-only 대비 hybrid 중복)

## 15.4 Text Intelligence

- TF-IDF vs semantic 산점도
- 상위 빈출어
- 키워드 커버리지 매트릭스
- 텍스트 리더보드

## 15.5 ML Studio

- 모델 CV 비교
- 예측 vs 실제
- SHAP 해석
- 모델 선택 재실행

## 15.6 ROI Lab

- 시나리오 튜닝
- ROI 퍼널
- 예산 민감도

## 15.7 Content Strategy

- 채널별 전략 카드
- 훅 카드

## 15.8 Executive Memo

- 섹션형 메모 뷰
- 다운로드

## 15.9 Glossary

- 고객 설명용 용어 정리

---

## 16) 왜 결과가 바뀌거나 안 바뀌는가

브랜드명/제품명만 바꾸고 결과가 비슷할 수 있는 이유:
- 이름 자체보다 키워드/목표/텍스트 문맥이 더 큰 영향을 주기 때문

결과를 크게 바꾸는 레버:
- must/exclude keywords
- campaign goal
- Top Matches 전략/필터
- graph controls

---

## 17) 자주 헷갈리는 포인트

"입력을 바꾸면 항상 결과가 완전히 달라져야 하나?"
- 아님. 핵심 신호가 비슷하면 상위 겹침이 높을 수 있음

"조회수 낮은 채널이 왜 보이나?"
- 텍스트/네트워크 적합도가 높으면 후보가 될 수 있음
- 최종 의사결정 시 `evidence_score`와 `credibility_multiplier`를 같이 봐야 함

"ROI가 실제 성과를 보장하나?"
- 아님. 가정 기반 시나리오 결과

"ML은 항상 최종 점수에 들어가나?"
- 아님. baseline 대비 개선 게이트를 통과할 때만 반영

---

## 18) 산출물 저장 위치

주요 산출물:
- Top-N CSV: `artifacts/reports/top{N}_{brand}.csv`
- 전체 채널 점수 CSV: `artifacts/reports/scored_channels_{brand}.csv`
- 메모: `artifacts/reports/memo_{brand}.md`
- ML 결과: `artifacts/reports/ml_cv_results.csv`

보조 산출물:
- 캐시/플롯: `artifacts/cache/`, `artifacts/plots/`

---

## 19) 수업 기반 분석 vs 프로젝트 확장

수업 기반(강의 주제와 직접 연결):
- Social Network Analysis (그래프, 중심성, 커뮤니티)
- Text Analysis (TF-IDF 기반 유사도)
- ML 모델 평가 개념(CV, baseline 비교)

프로젝트 확장:
- 신뢰도 배수와 eligible 조건
- 다양성 가드레일 Top-N 선택
- ML 반영 게이트
- 벤치마크 모드, ROI 시뮬레이터
- 전략/메모 자동화

---

## 20) 팀원 재현 방법

로컬 실행:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

빠른 파이프라인 실행:

```bash
python3 run_pipeline.py --no-benchmark
```

GDrive 다운로드 확인:

```bash
python3 scripts/bootstrap_full_data_from_gdrive.py
```

---

## 21) 비전공 팀원에게 설명할 때 추천 순서

1. 캠페인 조건을 입력한다.
2. 네트워크/텍스트/성과/ML 신호를 결합해 점수를 만든다.
3. 근거가 약한 채널은 자동 감점한다.
4. 커뮤니티 다양성을 반영해 Top-N을 조정한다.
5. 결과 카드에서 이유/리스크를 함께 본다.
6. 벤치마크/ROI로 실행 계획을 세운다.

---

## 22) 최종 정리

이 시스템은 "팔로워 수 큰 순 추천" 도구가 아니라,
브랜드 의사결정을 위한 투명한 분석 워크플로우입니다.

핵심 가치:
- 더 빠른 shortlist
- 더 설명 가능한 추천
- 더 낮은 매칭 실패 리스크
- 더 명확한 가정 기반 계획

