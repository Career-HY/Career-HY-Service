# Carrer-Hi-RAG
현재까지 구현한 파이프라인 요약 
1. pdf 로딩 및 텍스트 추출 (loader.py)
   - pymupdf 사용
2. 텍스트 전처리 (cleaner.py)
   - 공백, 특수문자등 제거
3. 임베딩 (embedder.py)
   - open ai: text-embedding-ada-002
   - 토큰 수가 많아 API 제한을 초과하지 않도록 평균 토큰 수를 계산하여 적절한 배치 크기(예: 5)를 설정합니다.
4. 벡터 저장 및 검색 (vector.py)
   - chroma 벡터 데이터베이스를 사용해 임베딩한 벡터 저장
   - store_to_chroma 함수로 벡터, 메타데이터 저장, query_chroma함수로 유사한 문서 검색
5. 실험 스크립트 (test_experiment.py)
   - 전체 파이프라인 실행해 pdf 로딩 ~ 벡터 저장까지 수행
   - 예시 쿼리 통해 유사한 채용공고까지 출력함.
   - 추후 다양한 laoder, embedding 조합해 성능 비교 가능. 
