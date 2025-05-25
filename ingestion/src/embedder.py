# 임베딩 생성

# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings


import os
from openai import OpenAI
from typing import List


class OpenAITextEmbedder:
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model_name

    def embed(self, texts: List[str], batch_size: int = 5) -> List[List[float]]:
        """
        텍스트 리스트를 OpenAI 임베딩 벡터로 변환합니다. (배치 단위)

        Args:
            texts (List[str]): 텍스트 리스트
            batch_size (int): 한 번에 요청할 문서 수

        Returns:
            List[List[float]]: 임베딩 벡터 리스트
        """
        texts = [t for t in texts if isinstance(t, str) and len(t.strip()) > 0]
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(input=batch, model=self.model)
            embeddings = [d.embedding for d in response.data]
            all_embeddings.extend(embeddings)

        return all_embeddings
