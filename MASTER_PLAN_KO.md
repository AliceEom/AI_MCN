# AI-MCN 실행 플랜 (한국어)

## 1) 목표
뷰티 브랜드용 인플루언서 매칭 프로토타입을 영어 데모 기준으로 완성한다.
- 메인 케이스: Beauty of Joseon
- 비교 벤치마크: CeraVe
- 데이터 기반 매칭 + ML 비교 + 설명가능성 포함

## 2) 범위 고정
- 제품 범위: 뷰티 인플루언서 추천 도구.
- 데모 범위: BOJ 1개 케이스를 중심으로 CeraVe 비교 제공.
- 산출물: Streamlit 앱, 모델 성능 결과, 시각화, executive memo.

## 3) 입력 데이터
- `data/videos_text_ready_combined.csv`
- `data/comments_raw_combined.csv`
- `data/master_prd_slim_combined.csv`

## 4) 핵심 파이프라인
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

## 5) 최종 점수식
`final_score = 0.30*SNA + 0.20*TFIDF + 0.15*Semantic + 0.10*Tone + 0.15*ObservedEngagement + 0.10*MLPotential`

보조 규칙:
- ML이 baseline 대비 유의미한 개선이 없으면 ML 가중치를 0으로 처리.

## 6) ML 설계
- 타깃: 비디오 단위 `log1p((likes + comments + 1)/(views + 100))`
- 검증: 채널 기준 `GroupKFold(5)`
- 지표: MAE, RMSE, R2
- 베이스라인: 중앙값 예측
- 결과물: 모델 비교표, best 모델, 예측-실측 플롯, SHAP 플롯

## 7) 데모 UI(전부 영어)
입력:
- 브랜드명, 상품명, 카테고리, 타깃, 캠페인 목표, 예산, USP,
  필수 키워드, 제외 키워드, 시장

출력:
- Overview, Top Recommendations, Network/Diversity,
  ML Benchmark, ROI, Content Strategy, Executive Memo

## 8) 채널 카드 정보
- 채널 이미지
- 채널명
- 채널 링크
- 점수 분해
- 추천 근거/리스크 플래그

이미지 규칙:
- 1순위: YouTube 채널 썸네일 API
- 2순위: 대표 비디오 썸네일 fallback

## 9) 아티팩트 저장
- `artifacts/reports/top5_<brand>.csv`
- `artifacts/reports/scored_channels_<brand>.csv`
- `artifacts/reports/memo_<brand>.md`
- `artifacts/reports/ml_cv_results.csv`
- `artifacts/plots/*` (CV/예측/SHAP)

## 10) 완료 기준
- 전체 파이프라인 오류 없이 실행.
- 주요 데모 섹션 영어 표시 완료.
- 사용 가능한 모델 기준 5-fold CV 결과 생성.
- SHAP 가능한 경우 결과 생성.
- Top-5 다양성 규칙 반영.
- BOJ/CeraVe 결과 모두 확인 가능.

## 11) 리스크 대응
- API 불안정: 캐시 우선 + fallback 템플릿.
- 데이터 잡음: 필터링 근거 명시.
- 과장 위험: ROI는 시뮬레이션으로 표기.
- 모델 불안정: baseline 비교 + 가중치 fallback.

