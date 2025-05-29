import chromadb
import os

# ChromaDB 경로 설정
PERSIST_DIR = "./data/vector_store_pymupdf_text-embedding-ada-002_chroma"


def inspect_chroma():
    # ChromaDB 클라이언트 생성
    client = chromadb.PersistentClient(path=PERSIST_DIR)

    # 모든 컬렉션 리스트 확인
    collections = client.list_collections()
    print("\n=== Collections ===")
    for collection in collections:
        print(f"Collection name: {collection.name}")
        print(f"Collection count: {collection.count()}")

        # 컬렉션의 첫 번째 문서 몇 개 확인
        result = collection.peek()
        print("\n=== Sample Documents ===")
        if result["ids"]:
            print(f"Sample IDs: {result['ids']}")
        if result["metadatas"]:
            print(f"Sample Metadatas: {result['metadatas']}")
        if result["documents"]:
            print("\nSample Documents content:")
            for doc in result["documents"]:
                print(f"\n---Document---\n{doc[:200]}...")  # 처음 200자만 출력

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    inspect_chroma()
