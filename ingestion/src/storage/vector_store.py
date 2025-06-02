# vector DB 관련 기능 (저장/ 검색 등)
import chromadb
from typing import List, Dict, Any
from chromadb.utils import embedding_functions

from langchain_teddynote import logging

logging.langsmith("chroma_store")

from langchain_community.document_loaders import TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain_chroma import Chroma


# ✅ 문서 저장 함수
def store_to_chroma(
    texts: List[str],
    embeddings: List[List[float]],
    ids: List[str],
    metadatas: List[Dict[str, Any]],
    persist_dir: str,
):
    """
    텍스트와 임베딩을 Chroma DB에 저장 (PersistentClient 기반)

    Args:
        texts (List[str]): 문서 텍스트 리스트
        embeddings (List[List[float]]): 임베딩 벡터 리스트
        ids (List[str]): 문서 ID 리스트 (예: 파일명)
        metadatas (List[Dict[str, Any]]): 문서 메타데이터 리스트 (제목, URL, 마감일 등)
        persist_dir (str): Chroma 저장 경로
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    # 각 문서마다 메타데이터 추가
    for text, emb, doc_id, metadata in zip(texts, embeddings, ids, metadatas):
        # 원본 메타데이터를 그대로 보존
        doc_metadata = metadata.copy()  # 원본 메타데이터 복사
        
        # 필수 필드가 없는 경우에만 기본값 설정
        if "source" not in doc_metadata:
            doc_metadata["source"] = doc_id

        collection.add(
            documents=[text], embeddings=[emb], ids=[doc_id], metadatas=[doc_metadata]
        )

    print(f"✅ 저장 완료: {len(texts)}개의 문서를 Chroma DB에 저장했습니다.")


# ✅ 문서 검색 함수
def query_chroma(
    query: str, embedder, persist_dir: str, top_k: int = 10
) -> Dict[str, Any]:
    """
    쿼리 임베딩 후 Chroma에서 Top-K 문서 검색

    Args:
        query (str): 사용자 쿼리
        embedder: 임베딩 생성기 (embed(text: List[str]) 지원)
        persist_dir (str): Chroma 저장 경로
        top_k (int): 검색할 문서 수 (기본값: 10)

    Returns:
        dict: {
            'documents': List[List[str]],  # 검색된 문서 텍스트
            'metadatas': List[List[Dict]],  # 문서 메타데이터 (제목, 마감일 등)
            'distances': List[List[float]]  # 유사도 점수 (낮을수록 유사)
        }
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    # 쿼리를 임베딩
    query_embedding = embedder.embed([query])[0]

    # 검색 (메타데이터와 거리 점수 포함)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    return results
