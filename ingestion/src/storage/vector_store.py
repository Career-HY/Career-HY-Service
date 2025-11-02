# vector DB 관련 기능 (저장/ 검색 등)
import os
import sys

# ChromaDB telemetry 완전 비활성화 (import 전에 설정 필수)
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_IMPL"] = "chromadb.telemetry.product.posthog.Posthog"


import chromadb
from typing import List, Dict, Any
from chromadb.utils import embedding_functions

# ChromaDB 텔레메트리 강제 비활성화
try:
    chromadb.telemetry.product.posthog.Posthog.capture = lambda *args, **kwargs: None
except:
    pass

# from langchain_teddynote import logging
# logging.langsmith("chroma_store")  # 주석처리: langchain-teddynote 의존성 제거

from langchain_community.document_loaders import TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain_chroma import Chroma

import random


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


# ✅ 문서 upsert 함수 (중복 체크 + 추가/업데이트)
def upsert_to_chroma(
    texts: List[str],
    embeddings: List[List[float]],
    ids: List[str],
    metadatas: List[Dict[str, Any]],
    persist_dir: str,
    force_update: bool = False
) -> Dict[str, int]:
    """
    텍스트와 임베딩을 Chroma DB에 upsert (중복 시 업데이트 또는 스킵)

    Args:
        texts (List[str]): 문서 텍스트 리스트
        embeddings (List[List[float]]): 임베딩 벡터 리스트
        ids (List[str]): 문서 ID 리스트 (rec_idx)
        metadatas (List[Dict[str, Any]]): 문서 메타데이터 리스트
        persist_dir (str): Chroma 저장 경로
        force_update (bool): True면 중복 시 덮어쓰기, False면 스킵

    Returns:
        Dict[str, int]: {
            "added": 신규 추가 개수,
            "updated": 업데이트 개수,
            "skipped": 스킵 개수
        }
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    added_count = 0
    updated_count = 0
    skipped_count = 0

    # 기존에 저장된 모든 ID 조회
    existing_ids = set(get_all_rec_ids(persist_dir))

    for text, emb, doc_id, metadata in zip(texts, embeddings, ids, metadatas):
        doc_metadata = metadata.copy()

        if "source" not in doc_metadata:
            doc_metadata["source"] = doc_id

        if doc_id in existing_ids:
            if force_update:
                # 업데이트: 기존 문서 삭제 후 재추가
                try:
                    collection.delete(ids=[doc_id])
                    collection.add(
                        documents=[text],
                        embeddings=[emb],
                        ids=[doc_id],
                        metadatas=[doc_metadata]
                    )
                    updated_count += 1
                    print(f"🔄 업데이트: {doc_id}")
                except Exception as e:
                    print(f"⚠️  업데이트 실패 ({doc_id}): {e}")
            else:
                # 스킵
                skipped_count += 1
                print(f"⏭️  스킵 (이미 존재): {doc_id}")
        else:
            # 신규 추가
            try:
                collection.add(
                    documents=[text],
                    embeddings=[emb],
                    ids=[doc_id],
                    metadatas=[doc_metadata]
                )
                added_count += 1
                print(f"✅ 신규 추가: {doc_id}")
            except Exception as e:
                print(f"⚠️  추가 실패 ({doc_id}): {e}")

    result = {
        "added": added_count,
        "updated": updated_count,
        "skipped": skipped_count
    }

    print(f"\n📊 Upsert 결과:")
    print(f"   - 신규 추가: {added_count}개")
    print(f"   - 업데이트: {updated_count}개")
    print(f"   - 스킵: {skipped_count}개")
    print(f"   - 총 처리: {added_count + updated_count + skipped_count}개\n")

    return result


# ✅ 문서 검색 함수
def query_chroma(
    query: str, embedder, persist_dir: str, top_k: int = 10, filter_expired: bool = True
) -> Dict[str, Any]:
    """
    쿼리 임베딩 후 Chroma에서 Top-K 문서 검색 (마감일 필터링 지원)

    Args:
        query (str): 사용자 쿼리
        embedder: 임베딩 생성기 (embed(text: List[str]) 지원)
        persist_dir (str): Chroma 저장 경로
        top_k (int): 검색할 문서 수 (기본값: 10)
        filter_expired (bool): True면 마감 지난 공고 제외, False면 모두 검색 (기본값: True)

    Returns:
        dict: {
            'documents': List[List[str]],  # 검색된 문서 텍스트
            'metadatas': List[List[Dict]],  # 문서 메타데이터 (제목, 마감일 등)
            'distances': List[List[float]]  # 유사도 점수 (낮을수록 유사)
        }
    """
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    # 쿼리를 임베딩
    query_embedding = embedder.embed([query])[0]

    # 🆕 마감일 필터 생성 (임시 비활성화 - ChromaDB $gte 연산자 이슈)
    where_filter = None
    if filter_expired:
        today = datetime.now().strftime('%Y-%m-%d')
        # ChromaDB는 $gte 같은 비교 연산자를 지원하지 않을 수 있음
        # 필터링은 검색 후 Python에서 처리하는 방식으로 변경 필요
        logger.info(f"⚠️ 마감일 필터링 임시 비활성화 (전체 검색 후 필터링 예정)")
        where_filter = None

    # 검색 (메타데이터와 거리 점수 포함, where 필터 적용)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,  # 🆕 필터 추가
        include=["documents", "metadatas", "distances"],
    )

    return results


# -------------------------------
# 🔎 Helper: 전체 rec_idx 목록 로드
# -------------------------------

def get_all_rec_ids(persist_dir: str) -> List[str]:
    """Chroma 컬렉션에 저장된 모든 rec_idx(id) 리스트를 반환합니다.

    Args:
        persist_dir (str): Chroma Persist 디렉터리 경로

    Returns:
        List[str]: id 문자열 리스트 (중복 없음)
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    data = collection.get(limit=None)
    return data.get("ids", [])


def choose_random_seed_id(persist_dir: str) -> str:
    """저장소에서 무작위 rec_idx 하나를 선택합니다."""
    ids = get_all_rec_ids(persist_dir)
    if not ids:
        raise ValueError("Collection is empty – cannot choose random seed id.")
    return random.choice(ids)

# -----------------------------------------
# 🔎 Helper: 기준 공고로부터 유사 공고 k개 추출
# -----------------------------------------

def get_similar_postings(
    seed_id: str,
    persist_dir: str,
    top_n: int = 10,   # 후보로 가져올 문서 수 (seed 제외)
    pick_k: int = 4,   # 최종 선택할 문서 수
) -> List[dict]:
    """seed_id 기준으로 비슷한 문서 후보 top_n개를 가져온 뒤 무작위로 pick_k개 선택합니다.

    Args:
        seed_id (str): 기준 채용공고 rec_idx
        persist_dir (str): Chroma Persist 경로
        top_n (int): 후보 개수(top-N). 기본 10개
        pick_k (int): 최종 선택할 문서 수. 기본 4개

    Returns:
        List[dict]: [{rec_idx, distance}, ...] (seed 포함)
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="job-postings")

    # 1) 기준 문서 임베딩 로드
    seed_data = collection.get(ids=[seed_id], include=["embeddings"])
    if len(seed_data.get("embeddings", [])) == 0:
        raise ValueError(f"Seed ID {seed_id} not found in collection")
    seed_embedding = seed_data["embeddings"][0]

    # 2) Top-(top_n+1) 검색 (seed 포함으로 +1)
    res = collection.query(
        query_embeddings=[seed_embedding],
        n_results=top_n + 1,
        include=["distances"],
    )

    ids = res["ids"][0]
    dists = res["distances"][0]

    # 3) seed 제외 후 후보 (dict) 확보
    candidates = [
        {"rec_idx": rid, "distance": dist}
        for rid, dist in zip(ids, dists)
        if rid != seed_id
    ][:top_n]

    # 4) 후보 중 무작위 pick_k 선택
    if len(candidates) > pick_k:
        candidates = random.sample(candidates, pick_k)

    # 5) seed 엔트리(distance=0) 맨 앞에 추가
    return [{"rec_idx": seed_id, "distance": 0.0}] + candidates
