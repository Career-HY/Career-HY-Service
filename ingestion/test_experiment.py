
from pathlib import Path
from src.loader import extract_text_PyMuPDF
from src.cleaner import clean_text
from src.embedder import OpenAITextEmbedder
from src.vector import store_to_chroma, query_chroma
from src.tokencounter import count_tokens

import os 

# ✅ 실험 설정
loader_name = "pymupdf"
embedder_provider = "openai"       # "openai" or "local"
embedder_name = "text-embedding-ada-002"
vector_name = "chroma"
vector_store_path = f"./ingestion/data/vector_store_{loader_name}_{embedder_name.replace('/', '-')}_{vector_name}/"

# ✅ Step 1: PDF 로드 
pdf_dir = "./ingestion/data/vector_store/pdf"
pdf_paths = list(Path(pdf_dir).glob("*.pdf"))
all_texts = []
ids = []


# ✅ Step 2: 텍스트 전처리 & 청킹
for pdf in pdf_paths:
    print(f"📄 {pdf.name} 처리 중...")
    raw_text = extract_text_PyMuPDF(pdf)
    cleaned_text = clean_text(raw_text)
    all_texts.append(cleaned_text)
    ids.append(pdf.stem)

# ✅ Step 3: 임베딩
embedder = OpenAITextEmbedder()
embeddings = embedder.embed(all_texts, batch_size=5)

# ✅ Step 4: chroma db 저장
#persist_dir = "./ingestion/data/vector_store" # 다시 바꿔야 함 
persist_dir = vector_store_path

store_to_chroma(all_texts, embeddings, ids, persist_dir)

#쿼리 예시 
query = '회계 직무를 희망하며 SAP 사용 경험이 있는 기업'
results = query_chroma(query, embedder, persist_dir, top_k=3)

# 결과 출력
for doc, score in zip(results['documents'][0], results['distances'][0]):
    print(f"\n📌 유사도: {score:.4f}")
    print(f"문서 내용: {doc[:500]}...")
