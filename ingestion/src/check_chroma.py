import chromadb
from pprint import pprint

# ChromaDB 저장 경로
PERSIST_DIR = "./data/vector_store_pymupdf_text-embedding-ada-002_chroma"


def check_collection():
    """ChromaDB 컬렉션의 내용을 확인합니다."""
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(name="job-postings")

    # 전체 문서 수 확인
    print(f"\n총 문서 수: {collection.count()}")

    # 샘플 문서 확인
    results = collection.peek(limit=5)
    print("\n샘플 문서 메타데이터:")
    pprint(results["metadatas"])


if __name__ == "__main__":
    check_collection()
