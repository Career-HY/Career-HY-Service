#현재는 문서 단위 처리로 사용 x 


# #텍스트 분할 
# #1. 고정된 chunk단위로 분할 
# import re
# from typing import List, Tuple

# def chunk_by_fixed_size(text: str, size: int = 400, overlap: int = 100) -> List[str]:
#     """
#     고정 길이 단위로 텍스트를 나눕니다.

#     Args:
#         text (str): 전체 텍스트
#         size (int): 하나의 청크 길이
#         overlap (int): 이전 청크와 겹치는 길이

#     Returns:
#         List[str]: 텍스트 청크 리스트
#     """
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = min(start + size, len(text))
#         chunk = text[start:end]
#         chunks.append(chunk)
#         start += size - overlap  # 겹치는 부분을 고려하여 시작 위치 조정
#     return chunks


# #2. 키워드 단위로 분할 
# def chunk_by_keywords(text: str) -> List[Tuple[str, str]]:
#     """
#     주요 키워드(지원자격, 담당업무 등)를 기준으로 텍스트를 분리합니다.

#     Args:
#         text (str): 전체 텍스트

#     Returns:
#         List[Tuple[str, str]]: (섹션명, 내용) 형태의 튜플 리스트
#     """
#     keywords = [
#         "자격요건", "지원자격", "담당업무", "우대사항", "근무조건", "복리후생",
#         "전형절차", "제출서류", "기업정보", "모집부문", "공통 자격요건", "필수사항"
#     ]

#     # 키워드를 기준으로 분리
#     pattern = "(" + "|".join(re.escape(k) for k in keywords) + ")"
#     parts = re.split(pattern, text)

#     chunks = []
#     for i in range(1, len(parts) - 1, 2):  # (섹션명, 내용) 쌍
#         section = parts[i].strip()
#         content = parts[i + 1].strip()
#         if content:
#             chunks.append((section, content))
#     return chunks