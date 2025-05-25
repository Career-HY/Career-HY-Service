# vector DB 관련 기능 (저장/ 검색 등)
import chromadb
from typing import List
from chromadb.utils import embedding_functions

from langchain_teddynote import logging

logging.langsmith("chroma_store")

from langchain_community.document_loaders import TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain_chroma import Chroma


# ✅ 문서 저장 함수
def store_to_chroma(
    texts: List[str], embeddings: List[List[float]], ids: List[str], persist_dir: str
):
    """
    텍스트와 임베딩을 Chroma DB에 저장 (PersistentClient 기반)

    Args:
        texts (List[str]): 문서 텍스트 리스트
        embeddings (List[List[float]]): 임베딩 벡터 리스트
        ids (List[str]): 문서 ID 리스트 (예: 파일명)
        persist_dir (str): Chroma 저장 경로
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    for text, emb, doc_id in zip(texts, embeddings, ids):
        collection.add(
            documents=[text],
            embeddings=[emb],
            ids=[doc_id],
            metadatas=[{"source": doc_id}],
        )

    print(f"✅ 저장 완료: {len(texts)}개의 문서를 Chroma DB에 저장했습니다.")


# ✅ 문서 검색 함수
def query_chroma(query: str, embedder, persist_dir: str, top_k: int = 3):
    """
    쿼리 임베딩 후 Chroma에서 Top-K 문서 검색

    Args:
        query (str): 사용자 쿼리
        embedder: 임베딩 생성기 (embed(text: List[str]) 지원)
        persist_dir (str): Chroma 저장 경로
        top_k (int): 검색할 문서 수

    Returns:
        dict: {'documents': ..., 'ids': ..., 'distances': ...}
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    # 쿼리를 임베딩
    query_embedding = embedder.embed([query])[0]

    # 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    return results
