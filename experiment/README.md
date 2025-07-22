# 🧪 Experiment Directory

이 디렉토리는 RAG 파이프라인의 다양한 구성 요소(임베딩 모델, 벡터 DB, 청킹 전략 등)에 따른 성능 실험을 수행하기 위해 구성되었습니다.  
실험 파라미터는 `configs/`에서 관리하며, 실험 결과는 LangSmith 및 `results/` 폴더를 통해 분석합니다.

## 파일 구조

```
experiments/
├── configs/                                    # 실험 파라미터 파일들
│   ├── exp_01_openai_chroma_chunk-doc.yml
│   ├── exp_02_openai_chroma_chunk-1000.yml
│   └── exp_03_openai_faiss_chunk-1000.yml
│
├── data/                                       # Ground Truth 데이터 저장 폴더
│   └── gt_profiles.csv
│
├── notebooks/                                  # 실험 결과 분석용 Jupyter 노트북
│   └── 1_visualize_results.ipynb
│
├── results/                                    # 실험 결과 저장 폴더
│   ├── exp_01_openai_chroma_chunk-doc/
│   │   └── metrics.json
│   └── exp_02_openai_chroma_chunk-1000/
│       └── metrics.json
│
├── src/                                        # 평가 및 유틸리티 코드
│   ├── evaluation.py
│   └── utils.py
│
├── scripts/                                    # 실행용 스크립트
│   ├── run_ingestion.py                        # 실험용 벡터DB 생성
│   └── run_evaluation.py                       # LLM 응답 평가 및 LangSmith 연동
│
└── README.md                                   # (현재 문서)
```

## 실험 실행 방법

### 1. 실험 파라미터 설정

`configs/` 폴더에 `.yml` 형식의 실험 설정 파일을 추가합니다.

```yaml
# 예시: exp_01_openai_chroma_chunk-doc.yml
embedding_model: "text-embedding-ada-002"
vector_db: "chroma"
chunking_strategy: "by_document"
retriever_top_k: 5
```

### 2. 데이터 준비

Ground Truth 데이터는 `data/` 폴더에 위치합니다.

### 3. 실험 실행

1. **임베딩 및 벡터 DB 구축**
   ```bash
   python scripts/run_ingestion.py --config configs/exp_01_openai_chroma_chunk-doc.yml
   ```

2. **평가 로그 저장**
   ```bash
   python scripts/run_evaluation.py --config configs/exp_01_openai_chroma_chunk-doc.yml
   ```

3. **결과 확인**
   - 실행 결과는 `results/exp.../metrics.json`으로 저장
   - 동시에 LangSmith 대시보드에 trace 및 평가가 기록됩니다

## 결과 분석 방법

`results/` 디렉토리에 저장된 파일의 지표를 분석합니다:
- `recall@k`
- `similarity_score`
- `token_usage`
- `latency` 등

## 향후 실험 방향

- **다양한 임베딩 모델 실험**
  - `text-embedding-ada-002`

- **벡터 DB 교체 실험**
  - Chroma, FAISS

- **청킹 전략 개선**
  - 문서 전체
  - 슬라이딩 윈도우
  - 섹션 기반

- **포스터형 데이터 로더 개선**

- **LLM 평가 지표 개선**
