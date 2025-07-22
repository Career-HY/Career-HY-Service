RAG 파이프라인(임베딩 모델, 벡터DB, 청킹 전략 등) 실험을 위한 디렉토리입니다.
이곳에서는 다양한 실험 파라미터를 체계적으로 관리하고, LangSmith를 통한 성능 트레이싱 및 결과 분석을 수행합니다.
#파일 구조 
experiments/
├── configs/
│   ├── exp_01_openai_chroma_chunk-doc.yml
│       exp_02_openai_chroma_chunk-1000.yml
    └── exp_03_openai_faiss_chunk-1000.yml
│
├── data/
│   └── # Ground Truth 데이터
│   
│
├── notebooks/
│   └── 1_ 결과 시각화 
│ 
│
├── results/
│   ├── eexp_01_openai_chroma_chunk-doc/
│   │   └── metrics.json
│   └── exp_02_openai_chroma_chunk-1000/
│       └── metrics.json
│
├── src/
│   ├── evaluation.py     # 평가지표 계산 로직
│   └── utils.py          # 실험용 유틸리티 함수
│
├── scripts/
│   ├── run_ingestion.py  # 데이터 수집 및 벡터 DB 저장 스크립트 -> 기존 모듈 이용 
│   └── run_evaluation.py # GT 기반 성능 평가 및 LangSmith 로깅 스크립트
│
└── README.md             # 실험 환경 설정, 실행 방법, 결과 분석 가이드


#실험 실행 방법 
#실험 파리미터 설정 
 1. configs/ 파일에 실험 파라미터 파일을 정의합니다. 
 2. 데이터: GT는 data/ 폴더에 위치합니다. 
 
#실험 추가 
1. configs/ 에 새로운 실험 파라미터 파일을 추가합니다. 
2. 위 실행 방법을 반복합니다. 
3. 결과를 result/ 또는 Langsmith 에서 비교 / 분석 합니다. 
-> 실험별 세부 trace, 응답 품질, 속도, 토큰 사용량을 대시보드에서 확인 