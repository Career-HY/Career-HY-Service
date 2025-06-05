import httpx
import asyncio
from typing import Dict, List
import json
import os
from datetime import datetime

# API 설정
API_URL = "http://localhost:5003"  # Docker 컨테이너의 API 주소
TIMEOUT = 30.0  # 요청 타임아웃 (초)

# 테스트용 샘플 데이터
test_request = {
    "query": "백엔드 개발자로 취업하고 싶은데 어떤 회사가 좋을까요?",
    "profile": {
        "major": "컴퓨터공학",
        "catalogs": [
            {
                "course_name": "자료구조",
                "core_competency": "알고리즘 및 데이터 구조",
                "course_overview": "기본적인 자료구조의 이해와 구현",
                "course_objectives": "자료구조의 기본 개념 습득",
                "week1_plan": "배열과 리스트",
                "week2_plan": "스택과 큐",
                "week3_plan": "트리",
                "week4_plan": "그래프",
                "week5_plan": "해시",
                "week6_plan": "정렬",
                "week7_plan": "탐색",
                "week8_plan": "중간고사",
                "week9_plan": "고급 트리",
                "week10_plan": "고급 그래프",
                "week11_plan": "동적 프로그래밍",
                "week12_plan": "그리디 알고리즘",
                "week13_plan": "문자열 알고리즘",
                "week14_plan": "프로젝트",
                "week15_plan": "프로젝트 발표",
                "week16_plan": "기말고사",
            }
        ],
        "interest_job": ["백엔드 개발", "데브옵스"],
        "certification": ["정보처리기사"],
    },
}


async def test_llm_api():
    """LLM API 테스트"""
    async with httpx.AsyncClient() as client:
        try:
            # 1. 헬스체크
            print("\n1. Testing health check endpoint...")
            response = await client.get(f"{API_URL}/")  # health 대신 루트 경로 사용
            print(f"Health check response: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200

            # 2. LLM 응답 생성 테스트
            print("\n2. Testing LLM response generation...")
            print(f"Request: {json.dumps(test_request, indent=2, ensure_ascii=False)}")

            start_time = datetime.now()
            response = await client.post(
                f"{API_URL}/api/v1/generatellm", json=test_request, timeout=TIMEOUT
            )
            end_time = datetime.now()

            print(f"\nStatus code: {response.status_code}")
            print(
                f"Response time: {(end_time - start_time).total_seconds():.2f} seconds"
            )

            if response.status_code == 200:
                result = response.json()

                # 응답 구조 검증
                assert "content" in result
                assert "recommended_jobs" in result
                assert "metadata" in result
                assert "relevant_documents" in result

                # 메타데이터 출력
                print("\nMetadata:")
                print(json.dumps(result["metadata"], indent=2, ensure_ascii=False))

                # 추천 채용공고 출력
                print("\nRecommended Jobs:")
                for idx, job in enumerate(result["recommended_jobs"], 1):
                    print(f"\n{idx}. {job['title']} - {job['company']}")
                    print(f"URL: {job['url']}")
                    print(f"추천 이유: {job['recommendation_reason']}")

                # 토큰 사용량 확인
                tokens = result["metadata"]["tokens"]
                print(f"\nToken Usage:")
                print(f"- Prompt tokens: {tokens['prompt_tokens']}")
                print(f"- Completion tokens: {tokens['completion_tokens']}")
                print(f"- Total tokens: {tokens['total_tokens']}")
                print(f"- Estimated cost: ${result['metadata']['total_cost']:.4f}")

            else:
                print(f"Error response: {response.text}")

        except httpx.TimeoutException:
            print("Request timed out!")
        except Exception as e:
            print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    print("Starting LLM API test...")
    asyncio.run(test_llm_api())
