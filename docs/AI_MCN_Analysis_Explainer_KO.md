# AI-MCN 분석 동작 설명서 (한국어)

이 문서는 현재 코드(`app.py`, `src/*`) 기준으로,  
캠페인 입력이 어떤 과정을 거쳐 최종 추천으로 나오는지 처음부터 끝까지 쉽게 설명합니다.

## 1) 핵심 한 줄 요약

현재 시스템은 **캠페인 입력을 넣는다고 실시간 웹 리서치를 하지는 않습니다.**  
입력값은 이미 CSV에 있는 채널/영상 데이터에 대해 필터링, 점수화, 재정렬하는 기준으로 사용됩니다.

## 2) 전체 파이프라인 (입력 -> 결과)

```text
Campaign Input Form
  -> BrandBrief + 실행 설정 생성
  -> CSV 로드 (full 파일 우선, 없으면 demo 파일)
  -> 영상 정제/필터링 + 채널 집계
  -> 태그 기반 채널 그래프 생성
  -> 네트워크 점수(SNA) + 커뮤니티 계산
  -> (옵션) ML 벤치마크 + ML 잠재력 점수 생성
  -> 텍스트(TF-IDF) 적합도 계산
  -> 상위 후보에 semantic/tone 정밀 분석
  -> 최종 점수 계산 + 신뢰도 페널티 + 다양성 가드레일
  -> Top-N 추천 + 벤치마크 + ROI + 전략 + 메모 생성
  -> Streamlit 탭에 시각화/리포팅
```

## 3) 어떤 데이터가 실제로 쓰이는가 (full vs demo)

코드는 아래 순서로 파일을 자동 선택합니다.

- 영상: `data/videos_text_ready_combined.csv` -> 없으면 `data/videos_text_ready_demo.csv`
- 댓글: `data/comments_raw_combined.csv` -> 없으면 `data/comments_raw_demo.csv`
- 마스터 채널: `data/master_prd_slim_combined.csv` -> 없으면 `data/master_prd_slim_demo.csv`

즉 로컬에 `*_combined.csv`가 있으면 full 데이터가 사용됩니다.

## 4) 캠페인 입력값이 어디에 반영되는지

| 입력 항목 | 반영 위치 | 실제 영향 |
|---|---|---|
| Brand/Product/Category/Audience/Goal/USP/Market | `BrandBrief` (텍스트/시맨틱 쿼리) | 어떤 채널을 “적합”으로 볼지 기준이 바뀜 |
| Budget | ROI 탭 + 벤치마크 예산 | ROAS 시뮬레이션 숫자가 바뀜 |
| Must-Have Keywords | 데이터 전처리 + 텍스트 점수 + 시맨틱 점수 + 키워드 매트릭스 | 포함 필터 강화, 키워드 히트 채널 가점 |
| Excluded Keywords | 데이터 전처리 + 텍스트 점수 + 시맨틱 점수 | 노이즈 영상 제거 + 제외 키워드 포함 채널 감점 |
| Top-N Default | 랭킹 설정 | 추천 개수, semantic 정밀분석 후보 수에 영향 |
| Min Shared Tags per Edge | 네트워크 그래프 | 높일수록 엣지 기준이 엄격해짐 |
| Max Tag Coverage Ratio | 네트워크 그래프 | 너무 흔한 태그 제거 강도 조절 |
| Min Community Size | 커뮤니티 후처리 | 작은 커뮤니티를 `-1`(micro/other)로 보냄 |
| Enable ML Benchmark Block | 파이프라인 | ML 학습 블록 실행 여부 |
| ML Models | ML Studio 재실행 / 파이프라인 | 5-fold CV에 포함할 모델 선택 |
| Run CeraVe Benchmark | 파이프라인 | CeraVe 고정 시나리오와 점수 비교 |

## 5) 내부 분석 로직 상세

## 5.1 데이터 전처리 (`src/data_prep.py`)

영상 단위 처리:

1. `_video_id` 기준 중복 제거
2. 조회/좋아요/댓글 수 숫자형 변환
3. `full_text = title + description + tags` 생성
4. 포함 필터: 뷰티 기본 키워드 + 사용자 must 키워드
5. 제외 필터: 노이즈 키워드 + 사용자 exclude 키워드
6. 기본 품질 조건: `views > 0`, likes/comments 비음수
7. ML 타깃 생성:
   - `engagement_rate = (likes + comments + 1) / (views + 100)`
   - `engagement_target = log1p(engagement_rate)`
8. ML 보조 피처 생성:
   - 게시 후 경과일, 제목 길이, 설명 길이, 해시태그 수, 태그 수, 로그 변환 조회/좋아요/댓글

댓글 단위 처리:

- `_comment_id` 중복 제거, 좋아요 수/텍스트 길이/날짜 정규화

채널 단위 집계:

- `n_videos`, `median_views`, `median_likes`, `median_comments`, `mean_engagement`, `latest_publish`
- 대표 영상 id
- 태그 목록 집계
- `channel_text` 생성(텍스트/시맨틱 점수 입력)
- 댓글 집계 통계

## 5.2 네트워크 그래프 생성 (`src/network_scoring.py`)

노드:

- 채널 ID 하나당 노드 1개

엣지:

- 공통 태그가 많은 채널끼리 연결
- 엣지 가중치 = 공통 태그 수
- `weight >= min_shared_tags`인 경우만 유지
- 너무 흔한 태그는 제거:
  - 절대 상한: `max_channels_per_tag` (기본 150)
  - 비율 상한: `max_tag_channel_ratio * 전체 채널 수`
  - 실제 상한 = 두 값 중 더 작은 값

## 5.3 네트워크 점수

채널별 계산:

- `degree_centrality`
- `betweenness_centrality` (근사 proxy)
- `eigenvector_centrality` (현재 구현은 정규화된 strength proxy)
- 결합:
  - `sna_score_raw = 0.33*degree + 0.34*betweenness_proxy + 0.33*eigenvector_proxy`
  - `sna_score = min-max 정규화`

커뮤니티:

- label propagation 방식
- `min_community_size`보다 작은 커뮤니티는 `community_id = -1`

## 5.4 ML 벤치마크 (`src/ml_modeling.py`)

옵션에서 켰을 때만 실행됩니다.

타깃:

- 영상 단위 `engagement_target = log1p(engagement_rate)`

입력 피처(숫자형 8개):

- `log_views, log_likes, log_comments, days_since_publish, title_len, desc_len, hashtag_count, tag_count`
- `StandardScaler` 적용

검증 방식:

- `GroupKFold(n_splits=5)` + 그룹=`_channel_id`
- 같은 채널 영상이 train/test에 섞이지 않게 하여 leakage 완화

모델:

- LinearRegression, LASSO, Ridge, CART, RandomForest, LightGBM(설치 시)

출력:

- CV 지표 (`RMSE`, `MAE`, `R2`)
- 최적 모델(최저 RMSE)
- 채널별 `ml_pred_engagement` 중앙값
- `ml_potential_score = min-max(ml_pred_engagement)`
- SHAP summary/dependence (트리 모델 + shap 설치 시)

중요 게이트:

- BaselineMedian 대비 RMSE 개선율이 2% 이상일 때만 최종 점수에 ML 가중치가 반영됩니다.

## 5.5 텍스트 적합도 (`src/text_scoring.py`)

TF-IDF:

- Corpus: 채널별 `channel_text`
- Query: 브랜드 브리프 전체 텍스트 + must keywords
- 코사인 유사도 계산

키워드 보정:

- `keyword_boost = 0.08*(must_hit 수) - 0.12*(exclude_hit 수)`
- `tfidf_similarity = min-max(raw_similarity + keyword_boost)`

## 5.6 Semantic/Tone 정밀 분석 (`src/semantic_enrichment.py`)

전체 채널이 아니라 상위 사전 후보에만 적용됩니다.  
(기본: top 30 또는 `3 * top_n` 중 큰 값)

채널별 계산:

- semantic 기본값(유사도)에
  - `+0.04 * must_hit`
  - `-0.08 * exclude_hit`
- [0,1] 범위로 클램프 -> `semantic_score`

Tone 매칭:

- Goal에 conversion이 들어가면: `review, demo, before after, results, routine`
- 아니면: `story, favorites, tips, routine, guide`
- 톤 키워드 히트 비율로 `tone_match_score` 계산

Red flag:

- 제외 키워드 신호 존재
- semantic < 0.20
- `n_videos < 5`

## 5.7 최종 점수/신뢰도/다양성 (`src/ranking.py`)

기본 신호:

- `engagement_score = min-max(mean_engagement)`

증거(신뢰도) 점수:

- `scale_score = min-max(log1p(median_views))`
- `activity_score = min-max(log1p(n_videos))`
- `interaction_score = min-max(log1p(median_likes + median_comments))`
- `evidence_score = 0.55*scale + 0.30*activity + 0.15*interaction`

신뢰도 배수:

- `credibility_multiplier = clip(0.35 + 0.65*evidence_score, 0.20, 1.00)`
- 초저신호 채널 추가 페널티:
  - `median_views < 100` AND `median_likes <= 1` AND `median_comments <= 1`
  - 배수를 다시 `* 0.30`
- 최종 clip 범위: `[0.08, 1.00]`

추천 가능 조건(eligible):

- 아래 중 하나 충족 시 추천 풀 유지
  - `evidence_score >= 0.20`
  - `median_views >= 500`
  - `n_videos >= 12`

가중 합 점수:

- ML 활성 시:
  - `0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*Engagement + 0.10*ML`
- ML 비활성 시:
  - `0.34*SNA + 0.24*TFIDF + 0.18*Semantic + 0.10*Tone + 0.14*Engagement + 0.00*ML`

최종:

- `final_score_base = 가중합`
- `final_score = final_score_base * credibility_multiplier`

다양성 가드레일:

- Top-N 구성 시 커뮤니티 다양성(기본 최소 3개)을 만족하도록 재선정 시도

## 5.8 채널 상세정보 보강

`src/channel_details.py`:

- 채널 스냅샷(설명 텍스트)
- 키워드 요약
- 최근 영상 제목 목록
- 최고 조회 영상 제목/조회수/URL
- 최근 댓글, 최다 좋아요 댓글
- master CSV 기반 구독자/영상수 추정치

`src/channel_media.py`:

- `YOUTUBE_API_KEY`가 있으면 채널 썸네일 API 호출
- 없으면 대표 영상 썸네일 fallback
- 채널/대표영상 URL 생성

## 5.9 벤치마크 블록

옵션이 켜져 있으면 CeraVe 고정 브리프로 한 번 더 동일 랭킹을 수행합니다.

대시보드 비교값:

- 현재 브랜드 Top-N 평균 `final_score`
- CeraVe Top-N 평균 `final_score`
- 차이(Anchor - Benchmark)

## 5.10 ROI / Content Strategy / Executive Memo

ROI (`src/roi_simulation.py`):

- `impressions = (budget / cpm) * 1000`
- `clicks = impressions * ctr`
- `conversions = clicks * cvr`
- `revenue = conversions * aov`
- `roas = revenue / budget`
- 범위: base ROAS의 0.7x ~ 1.3x

Content Strategy (`src/content_generation.py`):

- `OPENAI_API_KEY` 있으면 채널별 전략 문안 생성
- 키가 없으면 템플릿 fallback
- 앱에서 채널별 썸네일 훅 3개도 자동 생성

Executive Memo:

- Top 채널 + ROI + 리스크 플래그 + 다음 액션 기반 마크다운 메모 생성

## 6) 탭별로 화면에서 실제로 하는 일

## Overview

- 캠페인 입력 요약
- 상단 KPI
- 신뢰도 배너(Top 추천의 평균 evidence)
- 벤치마크 패널(옵션)

## Top Matches

- 최소 점수/최소 evidence 필터
- 랭킹 전략 프리셋 선택
- Display Top-N 조절
- 다양성 가드레일 미리보기/적용
- 채널 카드별 상세 시그널과 근거 표시

이 탭의 전략 프리셋:

- Model Default: 파이프라인의 `final_score` 그대로
- Network-first / Keyword-first / Performance-first:
  - 프리셋 가중치로 `display_score` 재계산
  - 신뢰도 배수(`credibility_multiplier`)는 계속 적용

## Network Studio

- 인터랙티브 네트워크 그래프 (zoom/pan/hover)
- 커뮤니티 분포
- 그래프 메타 정보
- Bias report:
  - degree-only 상위와 hybrid 최종 상위의 겹침 정도

## Text Intelligence

- TF-IDF vs Semantic 산점도 (색=evidence)
- 상위 채널 텍스트 빈출어
- 키워드 커버리지 매트릭스/차트
- TF-IDF/semantic 리더보드

## ML Studio

- 5-fold CV 모델 비교
- 모델 선택 재실행
- Predicted vs Actual 산점도
- SHAP 중요도/의존도

## ROI Lab

- 예산/CPM/CTR/CVR/AOV 조절형 시뮬레이터
- 퍼널/예산 민감도 인터랙티브 그래프

## Content Strategy

- 채널별 전략 카드
- 전략 문서를 탭 구조로 분해 표시
- 크리에이티브 훅 카드

## Executive Memo

- 섹션별 메모 뷰
- markdown/txt 다운로드

## Glossary

- 고객 설명용 핵심 용어 사전

## 6.1 Top Matches에서 실제 추천이 만들어지는 순서

Top Matches 탭에서 앱은 아래 순서로 동작합니다.

1. `result["scored_df"]`를 불러옴 (파이프라인 점수 완료된 테이블).
2. `display_score` 생성:
   - `Model Default` -> `display_score = final_score`
   - 나머지 전략 -> 컴포넌트 가중합을 다시 계산하고 `credibility_multiplier`를 곱함
3. 사용자 필터 적용:
   - `display_score >= Min Match Score`
   - `evidence_score >= Min Evidence`
4. `display_score` 내림차순 정렬
5. Diversity preview 적용 시:
   - 임시로 `final_score = display_score`로 바꿔서 다양성 선택기 실행
6. `Display Top-N`만큼 자름
7. 카드/차트/상세 테이블 렌더링

중요 포인트:

- Top Matches 실제 순위는 `display_score` 기준입니다.
- 파이프라인 기본 점수는 `final_score`입니다.
- 전략 프리셋을 바꾸면 둘이 달라질 수 있습니다.

## 6.2 Top Matches 전략별 가중치 (실제 코드값)

`Model Default`가 아니면 아래 가중치를 사용합니다.

| 전략 | SNA | TF-IDF | Semantic | Tone | Engagement | ML |
|---|---:|---:|---:|---:|---:|---:|
| Network-first | 0.46 | 0.16 | 0.14 | 0.08 | 0.14 | 0.02 |
| Keyword-first | 0.20 | 0.42 | 0.18 | 0.08 | 0.10 | 0.02 |
| Performance-first | 0.20 | 0.12 | 0.16 | 0.08 | 0.38 | 0.06 |

그 다음:

- ML 비활성 런이면 ML 가중치를 0으로 만들고 전체를 재정규화합니다.
- 탭 점수는:
  - `display_score = 가중합 * credibility_multiplier`

## 6.3 카드 배지 기준 (Match / Evidence)

적합도 배지(`display_score` 기준):

- `>= 0.65`: Very Strong Match
- `>= 0.45`: Strong Match
- `>= 0.30`: Moderate Match
- `< 0.30`: Exploratory

증거 배지(`evidence_score` 기준):

- `>= 0.60`: High Evidence
- `>= 0.35`: Medium Evidence
- `< 0.35`: Low Evidence

이 값들은 모델 학습 라벨이 아니라, UI 해석용 버킷입니다.

## 6.4 “Why this creator” 문장이 만들어지는 기준

아래 임계값을 넘으면 설명 문장에 이유가 추가됩니다.

- TF-IDF >= 0.55 -> 키워드/언어 적합
- SNA >= 0.55 -> 네트워크 중심성 강함
- Engagement >= 0.45 -> 반응 품질 양호
- Semantic >= 0.45 -> 의미/톤 정합성 양호

아무것도 기준을 못 넘으면 탐색 후보(caution) 문구가 나옵니다.

## 6.5 Top Matches 카드 항목별 의미

점수/제어:

- `Final Match Score`: 현재 탭에서 실제 순위에 쓰는 점수(`display_score`)
- `Signal Breakdown`: 가중합에 들어가는 세부 시그널 값
- `Score Controls`:
  - `Base` = 감점 전 점수(`final_score_base`)
  - `Reliability x...` = 신뢰도 배수(`credibility_multiplier`)
  - `Community` = 다양성 제어용 커뮤니티 번호

관측 증거:

- `Videos Used`: 해당 채널에서 분석에 실제 사용된 영상 수
- `Median Views/Likes`: 평균보다 이상치 영향이 적은 중앙값
- `Comments Collected`: 연결된 댓글 샘플 수

신선도:

- `Latest publish`, `Days since latest`: 최근 활동성 참고 지표

콘텐츠 맥락:

- `Channel Snapshot`: 채널 설명 텍스트 요약
- `Channel Keywords`: 태그 기반 키워드 요약
- `Best Video in Dataset`: 현재 데이터셋 내 최고 조회 영상
- `Recent Video Titles`, `Recent Audience Comments`, `Top Liked Audience Comment`: 정성 검토 보조

리스크/근거:

- `Model Rationale`: semantic/tone 계산 결과 설명
- `red_flags`: 제외 키워드 포함, 낮은 semantic, 낮은 활동성 등 경고

## 6.6 그래프 해석 가이드 (핵심 차트 전부)

### A) Top Influencer Score Breakdown (Top Matches)

- X축: 채널
- Y축: 각 컴포넌트 점수(0~1)
- 색상: 시그널 종류(SNA/TF-IDF/Semantic/Tone/Engagement/ML)

해석 팁:

- SNA만 높고 TF-IDF가 낮으면: 영향력은 높은데 캠페인 문구 적합성은 약할 수 있음
- TF-IDF 높고 evidence 낮으면: 키워드는 맞지만 실제 성과 근거가 약할 수 있음

### B) Influencer Network 그래프 (Network Studio)

노드:

- 노드 1개 = 채널 1개
- 색상 = `community_id`
- 크기 = `8 + 28 * max(final_score, 0)` (코드 기준)

엣지:

- 채널 간 공통 태그 연결
- `Min Edge Strength`를 올리면 약한 연결 제거

표시 로직:

- 우선 상위 점수 노드 중심으로 그림
- 너무 희소하면 fallback으로 더 넓은 엣지 샘플을 보여줌

읽는 법:

- 큰 노드가 밀집 중심에 있으면 구조적으로 강한 후보
- 고립 노드는 니치 카테고리이거나 태그 겹침이 약한 채널

### C) Community Distribution (Network Studio)

- X축: community id
- Y축: 해당 커뮤니티 채널 수
- `Include micro/isolated` 끄면 `-1` 군집 제외

용도:

- 추천이 특정 커뮤니티에 과도하게 몰리는지 확인

### D) Text Match Map (Text Intelligence)

- X축: TF-IDF(어휘/키워드 적합)
- Y축: Semantic(의미 적합)
- 색상: evidence 점수
- 버블 크기: 변환된 median views

사분면 해석:

- 우상단: 키워드+의미 둘 다 잘 맞음
- 좌상단: 의미는 맞는데 직접 키워드 겹침은 약함
- 우하단: 키워드 맞지만 의미 정합은 약함
- 좌하단: 전반적 텍스트 적합 약함

### E) Top Terms / Keyword Coverage (Text Intelligence)

Top Terms:

- 상위 후보 텍스트에서 자주 나오는 단어 빈도
- 후보군 언어가 캠페인 문맥과 맞는지 확인

Keyword Coverage:

- 각 키워드를 포함한 채널 비율
- must 키워드 커버리지가 낮으면 쿼리/데이터 범위 조정 필요

### F) ML Studio 그래프

CV RMSE 바 차트:

- RMSE가 낮을수록 좋음
- `BaselineMedian` 대비 개선 여부를 먼저 봐야 함

Predicted vs Actual:

- 45도 점선이 이상적 예측선
- 점이 선에서 멀수록 오차가 큼

SHAP Summary:

- Mean |SHAP|가 클수록 해당 피처 영향력 큼

SHAP Dependence:

- X=피처 값, Y=해당 피처의 예측 기여도
- 값이 커질수록 예측을 올리는지/내리는지 방향성 파악 가능

### G) ROI Lab 그래프

ROI Funnel:

- 노출 -> 클릭 -> 전환 -> 매출 단계별 시뮬레이션
- 인과추론이 아니라 가정값 기반 시나리오

Budget Sensitivity:

- X축 예산, 좌측 Y ROAS, 우측 Y 전환수
- 효율(ROAS)과 규모(전환수) 트레이드오프를 계획할 때 사용

## 6.7 그래프 인상과 최종순위가 다른 이유

차트상 좋아 보이는데 순위가 낮을 때 대표 원인:

1. `credibility_multiplier` 감점이 크게 들어감
2. 다양성 가드레일 때문에 같은 커뮤니티 후보가 대체됨
3. 현재 탭 전략이 `Model Default`가 아님 (`display_score` 재계산)
4. `Min Evidence` 필터에 걸렸음

디버깅 순서 권장:

1. 전략 프리셋 + `display_score` 확인
2. `evidence_score`, `credibility_multiplier` 확인
3. `community_id` + 다양성 설정 확인
4. `red_flags` + `Model Rationale` 확인

## 7) 왜 조회수 낮은 채널이 보일 수 있나

텍스트/네트워크 적합도가 매우 높으면 후보로 들어올 수 있습니다.  
다만 시스템은 이미 `credibility_multiplier`와 `eligible_recommendation`으로 약한 증거 채널을 감점/제한합니다.

데모에서 더 보수적으로 보이게 하려면:

1. Top Matches의 `Min Evidence`를 올리기
2. `Min Match Score`를 올리기
3. `Performance-first` 전략 사용
4. 다양성 가드레일은 유지하되, 데이터가 희소할 때 저증거 채널을 끌어오는지 점검

## 8) 자주 오해하는 포인트

- "브랜드명을 입력하면 외부 리서치를 자동으로 가져오나?"  
  - 아니요. 현재는 CSV 내부 데이터 기반 분석입니다.

- "Brand Name만 바꿔도 점수가 크게 바뀌나?"  
  - 일부 반영되지만, 영향력이 큰 것은 must/exclude keywords, audience, goal 텍스트입니다.

- "ROI는 실제 성과를 보장하나?"  
  - 아니요. 가정값 기반 시나리오 계산입니다.

- "ML을 켜면 항상 최종 점수에 ML이 반영되나?"  
  - 아니요. baseline 대비 성능 개선이 충분할 때만 반영됩니다.

## 9) 핵심 점수 용어 정리

| 필드명 | 의미 |
|---|---|
| `sna_score` | 네트워크 구조상 영향력 점수 |
| `tfidf_similarity` | 캠페인 텍스트와의 어휘적 유사도 |
| `semantic_score` | 의미 수준 적합도 |
| `tone_match_score` | 톤/목표 스타일 적합도 |
| `engagement_score` | 관측 참여 품질 점수 |
| `ml_potential_score` | ML 예측 기반 잠재력 점수 |
| `evidence_score` | 데이터 증거 강도(신뢰도) |
| `credibility_multiplier` | 증거 약한 채널 감점 배수 |
| `final_score_base` | 감점 전 가중합 점수 |
| `final_score` | 감점 반영 후 최종 추천 점수 |

## 10) 산출물 저장 위치

- Top-N CSV: `artifacts/reports/top{N}_{brand}.csv`
- 전체 채널 점수 CSV: `artifacts/reports/scored_channels_{brand}.csv`
- 메모: `artifacts/reports/memo_{brand}.md`
- ML 결과: `artifacts/reports/ml_cv_results.csv`
- 전략/미디어 캐시: `artifacts/cache/`
