# AI-MCN 실행 플랜 (한국어)

## 1) 목표
뷰티 브랜드용 인플루언서 매칭 프로토타입을 영어 데모 기준으로 완성한다.
- 메인 케이스: Beauty of Joseon
- 비교 벤치마크: CeraVe
- 데이터 기반 매칭 + ML 비교 + 설명가능성 포함

## 2) 브랜드 선택 근거 및 브랜드 리서치
왜 **Beauty of Joseon(BOJ)** 인가:
- 과제 목적 적합성: 포지셔닝/메시지가 명확해서 설명가능한 인플루언서 매칭 데모에 적합.
- 캠페인 명확성: BOJ의 SPF + 경량 스킨케어 메시지가 키워드/시맨틱 매칭에 잘 맞음.
- 비교 가능성: BOJ와 CeraVe는 포지셔닝이 달라(트렌드 K-뷰티 vs 피부과 신뢰 중심) 벤치마크 스토리가 좋음.

브랜드 리서치 요약(프로젝트 관점):
- 브랜드 포지셔닝: 헤리티지 스토리와 성분 중심 커뮤니케이션을 결합한 K-뷰티 스킨케어.
- 핵심 타깃 가설: 경량 데일리 스킨케어/SPF, 민감성·여드름 고민 사용자 중심의 Gen Z/밀레니얼.
- 캠페인 과제: 팔로워 규모 중심이 아니라 맥락 적합성과 성과 근거를 동시에 만족하는 채널 선별.

케이스 타당성 데이터 근거(`videos_text_ready_combined`, n=67,283):
- `sunscreen`: 3,981개 영상 / 340개 채널
- `spf`: 3,850개 영상 / 344개 채널
- `k-beauty`: 636개 영상 / 76개 채널
- `beauty of joseon`: 286개 영상 / 69개 채널
- `cerave`: 747개 영상 / 118개 채널

## 3) 범위 고정
- 제품 범위: 뷰티 인플루언서 추천 도구.
- 데모 범위: BOJ 1개 케이스를 중심으로 CeraVe 비교 제공.
- 산출물: Streamlit 앱, 모델 성능 결과, 시각화, executive memo.

## 4) 입력 데이터
- `data/videos_text_ready_combined.csv`
- `data/comments_raw_combined.csv`
- `data/master_prd_slim_combined.csv`

## 5) 핵심 파이프라인
1. 데이터 정제 + 뷰티 필터링.
2. 채널 단위 집계.
3. SNA 그래프/중심성/커뮤니티 점수.
4. TF-IDF 텍스트 적합도.
5. 관측 engagement 점수.
6. ML 블록(Linear/LASSO/Ridge/CART/RF/LightGBM) + 5-fold GroupCV.
7. SHAP 설명가능성(트리 계열 best 모델 기준).
8. Top-20 semantic 보정.
9. 최종 점수 계산 및 Top-5 다양성 규칙 적용.
10. ROI 시나리오 시뮬레이션.
11. 콘텐츠 전략 + executive memo 생성.
12. BOJ vs CeraVe 비교.

## 6) 최종 점수식
`final_score = 0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*ObservedEngagement + 0.10*MLPotential`

보조 규칙:
- ML이 baseline 대비 유의미한 개선이 없으면 ML 가중치를 0으로 처리.

## 7) ML 설계
- 타깃: 비디오 단위 `log1p((likes + comments + 1)/(views + 100))`
- 검증: 채널 기준 `GroupKFold(5)`
- 지표: MAE, RMSE, R2
- 베이스라인: 중앙값 예측
- 결과물: 모델 비교표, best 모델, 예측-실측 플롯, SHAP 플롯

## 8) 데모 UI(전부 영어)
입력:
- 브랜드명, 상품명, 카테고리, 타깃, 캠페인 목표, 예산, USP,
  필수 키워드, 제외 키워드, 시장

출력:
- Overview, Top Recommendations, Network/Diversity,
  ML Benchmark, ROI, Content Strategy, Executive Memo

## 9) 채널 카드 정보
- 채널 이미지
- 채널명
- 채널 링크
- 점수 분해
- 추천 근거/리스크 플래그

이미지 규칙:
- 1순위: YouTube 채널 썸네일 API
- 2순위: 대표 비디오 썸네일 fallback

## 10) 아티팩트 저장
- `artifacts/reports/top5_<brand>.csv`
- `artifacts/reports/scored_channels_<brand>.csv`
- `artifacts/reports/memo_<brand>.md`
- `artifacts/reports/ml_cv_results.csv`
- `artifacts/plots/*` (CV/예측/SHAP)

## 11) 완료 기준
- 전체 파이프라인 오류 없이 실행.
- 주요 데모 섹션 영어 표시 완료.
- 사용 가능한 모델 기준 5-fold CV 결과 생성.
- SHAP 가능한 경우 결과 생성.
- Top-5 다양성 규칙 반영.
- BOJ/CeraVe 결과 모두 확인 가능.

## 12) 리스크 대응
- API 불안정: 캐시 우선 + fallback 템플릿.
- 데이터 잡음: 필터링 근거 명시.
- 과장 위험: ROI는 시뮬레이션으로 표기.
- 모델 불안정: baseline 비교 + 가중치 fallback.
