from __future__ import annotations

import random
from typing import Dict, Any, List
import logging
import time
import json
import ast
import re

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.services.tools import job_posting_tool, course_search_tool
from src.config.config import settings
from src.services.ingestion_client import IngestionClient

logger = logging.getLogger(__name__)

class GTAgent:
    """LangChain 기반 GT 생성 에이전트"""

    def __init__(self):
        self.ingest_client = IngestionClient()

        llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)
        tools = [job_posting_tool, course_search_tool]
        system_prompt = (
            "당신은 채용공고를 분석해 해당 공고들에 꼭 맞는 3-4학년 학생 프로필을 작성하는 전문가입니다.\n"
            "profile 필드는 JSON 형태이어야 하며 major, catalogs, interest_job, certification 키를 포함해야 합니다.\n"
            "catalogs 필드는 백엔드 search_course_catalog 응답 객체(id, course_name, course_code, credit_units, instructor, total_credits 등)를 그대로 원소로 갖는 리스트여야 합니다. 예: [{{\"id\": 2746, \"course_name\": \"AI+X:딥러닝\", \"course_code\": \"AIX0003\", \"credit_units\": \"100단위\", \"instructor\": \"원영준\", \"total_credits\": \"3.0\"}}].\n"
            "catalogs를 채우기 위해서는 search_course_catalog 툴을 활용하세요. 키워드는 관련 과목명(예: '딥러닝', '컴퓨터비전') 또는 개설학과명(예: '컴퓨터소프트웨어학부')을 사용하여 검색할 수 있습니다.\n"
            "catalogs를 채우기 위해 여러번 search_course_catalog 툴을 호출해야 할 수 있습니다. 여러 번 사용하는 동안 키워드를 다양하게 변경하여 검색하세요.(해당 프로필과 적절한 키워드로 검색하는 것이 중요합니다.)\n"
            "search_course_catalog 툴 사용시 특정 키워드에 대해 빈 값이 반환되면 적절한 다른 키워드를 사용하여 검색하세요.\n"
            "catalogs의 개수는 반드시 15~20개 사이로 채워야 합니다.\n"
            "catalogs의 course_name이 중복되지 않도록 채워야 합니다.\n"
            "채용공고의 본문 내용을 참고해야겠다 생각이 들면 get_job_posting 툴을 활용하세요.\n"
            "query 필드는 학생이 챗봇에게 물어볼 하나의 질문 문장입니다.\n"
            "학생은 챗봇에게 주로 본인 상황에 맞는 채용공고를 추천해 줄 것을 질문합니다. (예: '나는 java로 프로젝트를 몇 번 해봤고 서버 개발자가 되고 싶어. 나에게 맞는 채용 공고를 추천해줄래?', '나는 인사관리 하는 것에 관심이 있어. 나에게 맞는 채용 공고를 추천해줄래?')\n"
            "반드시 JSON 스키마 {{profile, query, relevant_ids}} 로만 응답하세요."
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=100)

    # -------------------- 유사 문서 검색 --------------------
    async def _all_ids(self) -> List[str]:
        return await self.ingest_client.get_all_ids()

    async def _random_seed(self) -> str:
        ids = await self._all_ids()
        if not ids:
            raise RuntimeError("collection empty")
        return random.choice(ids)

    async def _similar(self, seed: str, top_n=10, pick_k=4) -> List[Dict[str, Any]]:
        candidates = await self.ingest_client.get_similar_docs(seed, top_n=top_n, pick_k=pick_k)
        return [{"rec_idx": seed, "distance": 0.0}] + candidates

    # -------------------- 공개 API --------------------
    async def create_sample(self, seed_rec_idx: str | None, num_similar: int) -> Dict[str, Any]:
        start_ts = time.perf_counter()
        logger.info("🚩 [GTAgent] create_sample 시작 | seed_rec_idx=%s | num_similar=%s", seed_rec_idx, num_similar)

        seed = seed_rec_idx or await self._random_seed()
        logger.info("🔑 선택된 시드 id=%s", seed)

        relevant_ids = await self._similar(seed, pick_k=num_similar)
        logger.info("📄 관련 공고 %d개 선택: %s", len(relevant_ids), [obj["rec_idx"] for obj in relevant_ids])

        # 중복 rec_idx 제거 (시드가 두 번 들어오는 문제 방지)
        _uniq = {}
        for item in relevant_ids:
            _uniq[item["rec_idx"]] = item
        relevant_ids = list(_uniq.values())
        logger.info("📄 중복 제거 후 관련 공고 %d개", len(relevant_ids))

        # Agent에게 컨텍스트 메시지 전달 (seed와 주요 후보 제목)
        context_msgs = []
        for obj in relevant_ids:
            rec_idx = obj["rec_idx"]
            posting = await self.ingest_client.get_posting(rec_idx)
            logger.debug("🔍 채용공고 %s 메타데이터 로드 완료", rec_idx)
            meta = posting.get("metadata", {})
            title = meta.get("post_title", meta.get("title", "제목 없음"))
            context_msgs.append(f"- {title} (id: {rec_idx})")
        context_str = "\n".join(context_msgs)

        user_message = (
            f"다음 채용공고들을 분석하고 공통 요구에 맞는 학생 프로필을 작성하세요.\n{context_str}"
        )

        logger.info("🤖 LLM 에이전트 호출 시작")
        
        result = await self.executor.ainvoke({"input": user_message})

        logger.info("✅ LLM 에이전트 응답 수신 (경과 %.2f초)", time.perf_counter() - start_ts)

        for attempt in range(3):
            # ---------------- 결과 파싱 ----------------
            if isinstance(result, dict) and "output" in result:
                raw = result["output"]
            else:
                raw = result

            data = None
            if isinstance(raw, str):
                try:
                    cleaned = re.sub(r"```.*?\n|```", "", raw, flags=re.S)
                    m = re.search(r"\{.*\}", cleaned, flags=re.S)
                    if m:
                        cleaned = m.group(0)
                    cleaned2 = cleaned.replace("'", '"')
                    data = json.loads(cleaned2)
                except Exception:
                    try:
                        data = ast.literal_eval(cleaned)
                    except Exception:
                        data = None
            elif isinstance(raw, dict):
                data = raw

            # ---------- 유효성 검사 ----------
            valid = False
            reason = ""
            if data and isinstance(data, dict) and "profile" in data:
                catalogs = data["profile"].get("catalogs", [])
                # 중복 제거 후 개수 확인
                seen = set()
                dup = False
                for c in catalogs:
                    key = (c.get("course_code") or c.get("course_name"))
                    if key in seen:
                        dup = True
                        break
                    seen.add(key)
                if dup:
                    reason = "중복 과목 존재"
                elif len(catalogs) < 15:
                    reason = f"과목 수 부족({len(catalogs)})"
                else:
                    valid = True

            if valid:
                break  # validation passed

            # ---------------- 피드백 메시지로 재시도 ----------------
            feedback_msg = (
                f"이전 출력의 문제가 있습니다: {reason}. \n"
                "catalogs 필드는 반드시 중복 없이 15~20개 과목을 포함해야 합니다. \n"
                "중복을 제거하고 부족하면 search_course_catalog를 추가 호출하여 채워주세요. \n"
                "JSON 스키마 {profile, query, relevant_ids} 로만 응답하세요."
            )
            logger.info("🔄 재시도 %d - 이유: %s", attempt + 1, reason)
            result = await self.executor.ainvoke({"input": feedback_msg})

        if not data:
            raise RuntimeError("GTAgent failed to produce valid JSON after retries")

        data["seed_rec_idx"] = seed
        data["relevant_ids"] = relevant_ids

        logger.info("🎉 create_sample 완료 (총 %.2f초)", time.perf_counter() - start_ts)
        return data 