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
from langsmith import traceable

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
            "profile 필드는 JSON 형태이어야 하며 major, catalogs, interest_job, certification, club_activities 키를 포함해야 합니다.\n"
            "catalogs 필드는 백엔드 search_course_catalog 응답 객체(id, course_name, course_code, credit_units, instructor, total_credits 등)를 그대로 원소로 갖는 리스트여야 합니다. 예: [{{\"id\": 2746, \"course_name\": \"AI+X:딥러닝\", \"course_code\": \"AIX0003\", \"credit_units\": \"100단위\", \"instructor\": \"원영준\", \"total_credits\": \"3.0\"}}].\n"
            "catalogs를 채우기 위해서는 search_course_catalog 툴을 활용하세요. 키워드는 관련 과목명(예: '딥러닝', '컴퓨터비전') 또는 개설학과명(예: '컴퓨터소프트웨어학부')을 사용하여 검색할 수 있습니다.\n"
            "catalogs를 채우기 위해 여러번 search_course_catalog 툴을 호출해야 할 수 있습니다. 여러 번 사용하는 동안 키워드를 다양하게 변경하여 검색하세요.(해당 프로필과 적절한 키워드로 검색하는 것이 중요합니다.)\n"
            "search_course_catalog 툴 사용시 특정 키워드에 대해 빈 값이 반환되면 적절한 다른 키워드를 사용하여 검색하세요.\n"
            "catalogs의 개수는 반드시 15~20개 사이로 채워야 합니다.\n"
            "catalogs의 course_code 및 course_name이 중복되지 않도록 채워야 합니다. 동일한 course_code 및 course_name을 가진 과목은 절대 포함하지 마세요.\n"
            "채용공고의 본문 내용을 참고해야겠다 생각이 들면 get_job_posting 툴을 활용하세요.\n"
            "query 필드는 학생이 챗봇에게 물어볼 하나의 질문 문장입니다.\n"
            "club_activities 필드는 학생의 동아리 활동, 대외활동, 프로젝트 경험 등을 포함하는 문자열입니다. 해당 채용공고와 관련된 실제적이고 구체적인 활동들을 작성하세요. (예: '프로그래밍 동아리 활동, 알고리즘 스터디 운영', '마케팅 동아리, 창업 경진대회 참가')\n"
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

    # -------------------- 유틸리티 메서드 --------------------
    def _deduplicate_catalogs(self, catalogs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """course_code와 course_name 기준으로 중복 제거"""
        seen_codes = set()
        seen_names = set()
        unique_catalogs = []
        
        for catalog in catalogs:
            course_code = catalog.get("course_code")
            course_name = catalog.get("course_name")
            
            # course_code나 course_name 중 하나라도 중복이면 제외
            if course_code in seen_codes or course_name in seen_names:
                continue
                
            if course_code:
                seen_codes.add(course_code)
            if course_name:
                seen_names.add(course_name)
            unique_catalogs.append(catalog)
            
        return unique_catalogs



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
    @traceable(name="gt_sample_creation")
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
        posting_titles = []
        for obj in relevant_ids:
            rec_idx = obj["rec_idx"]
            posting = await self.ingest_client.get_posting(rec_idx)
            logger.debug("🔍 채용공고 %s 메타데이터 로드 완료", rec_idx)
            meta = posting.get("metadata", {})
            title = meta.get("post_title", meta.get("title", "제목 없음"))
            posting_titles.append(title)
            context_msgs.append(f"- {title} (id: {rec_idx})")
        context_str = "\n".join(context_msgs)

        user_message = (
            f"다음 채용공고들을 분석하고 공통 요구에 맞는 학생 프로필을 작성하세요.\n{context_str}"
        )

        logger.info("🤖 LLM 에이전트 호출 시작")
        
        result = await self.executor.ainvoke({"input": user_message})

        logger.info("✅ LLM 에이전트 응답 수신 (경과 %.2f초)", time.perf_counter() - start_ts)

        # 최대 5회 재시도
        for attempt in range(5):
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

            # ---------- 유효성 검사 및 개선된 처리 ----------
            if data and isinstance(data, dict) and "profile" in data:
                catalogs = data["profile"].get("catalogs", [])
                
                # 1. 중복 제거를 먼저 수행
                original_count = len(catalogs)
                catalogs = self._deduplicate_catalogs(catalogs)
                dedup_count = len(catalogs)
                
                if original_count > dedup_count:
                    logger.info("🔧 중복 과목 %d개 자동 제거 (%d → %d)", 
                              original_count - dedup_count, original_count, dedup_count)
                    data["profile"]["catalogs"] = catalogs

                # 2. 개수 확인 및 부족분 처리
                if dedup_count >= 15:
                    logger.info("✅ 과목 개수 충족 (%d개)", dedup_count)
                    break  # 성공
                else:
                    needed = 15 - dedup_count
                    logger.info("📝 과목 %d개 부족 → %d개 추가 요청", dedup_count, needed)
                    
                    # 이미 선택된 course_code와 course_name 목록
                    existing_codes = [c.get("course_code") for c in catalogs if c.get("course_code")]
                    existing_names = [c.get("course_name") for c in catalogs if c.get("course_name")]
                    
                    feedback_msg = (
                        f"아래 {dedup_count}개 과목은 이미 확정되었습니다:\n"
                        f"{json.dumps(catalogs, ensure_ascii=False, indent=2)}\n\n"
                        f"이 과목들과 course_code 또는 course_name이 중복되지 않도록 {needed}개 과목을 추가로 검색하여 채워주세요.\n"
                        f"이미 사용된 course_code: {existing_codes}\n"
                        f"이미 사용된 course_name: {existing_names}\n\n"
                        f"기존 과목들과 중복되지 않도록 키워드 선정을 잘 해주세요.\n"
                        f"추가 과목만 JSON 형태로 반환하세요: {{\"additional_catalogs\": [...]}}"
                    )
                    logger.info("🔄 부족분 추가 요청 (시도 %d)", attempt + 1)
                    additional_result = await self.executor.ainvoke({"input": feedback_msg})
                    
                    # 추가 과목 파싱 및 병합
                    additional_data = None
                    if isinstance(additional_result, dict) and "output" in additional_result:
                        additional_raw = additional_result["output"]
                    else:
                        additional_raw = additional_result
                        
                    if isinstance(additional_raw, str):
                        try:
                            cleaned = re.sub(r"```.*?\n|```", "", additional_raw, flags=re.S)
                            m = re.search(r"\{.*\}", cleaned, flags=re.S)
                            if m:
                                cleaned = m.group(0)
                            cleaned2 = cleaned.replace("'", '"')
                            additional_data = json.loads(cleaned2)
                        except Exception:
                            try:
                                additional_data = ast.literal_eval(cleaned)
                            except Exception:
                                logger.warning("⚠️ 추가 과목 파싱 실패")
                                continue
                    elif isinstance(additional_raw, dict):
                        additional_data = additional_raw
                    
                    # 추가 과목을 기존 catalogs에 병합
                    if additional_data and "additional_catalogs" in additional_data:
                        additional_catalogs = additional_data["additional_catalogs"]
                        logger.info("📚 추가 과목 %d개 수신", len(additional_catalogs))
                        
                        # 중복 제거하면서 병합
                        all_catalogs = catalogs + additional_catalogs
                        merged_catalogs = self._deduplicate_catalogs(all_catalogs)
                        data["profile"]["catalogs"] = merged_catalogs
                        
                        logger.info("🔄 병합 완료: %d + %d → %d개 (중복 제거 후)", 
                                  len(catalogs), len(additional_catalogs), len(merged_catalogs))
                        
                        # 병합 후 재검증
                        if len(merged_catalogs) >= 15:
                            break
            else:
                logger.warning("⚠️ 파싱 실패 또는 잘못된 구조")
                feedback_msg = (
                    "이전 출력이 올바른 JSON 형태가 아닙니다. "
                    "반드시 JSON 스키마 {profile, query, relevant_ids} 로만 응답하세요."
                )
                logger.info("🔄 재시도 %d - JSON 형태 오류", attempt + 1)
                result = await self.executor.ainvoke({"input": feedback_msg})
                continue

        # 최종 검증
        if not data or not isinstance(data, dict) or "profile" not in data:
            raise RuntimeError(f"GTAgent failed to produce valid JSON after {3} retries")
        
        final_catalogs = data["profile"].get("catalogs", [])
        final_count = len(self._deduplicate_catalogs(final_catalogs))
        
        if final_count < 15:
            raise RuntimeError(
                f"GTAgent failed to generate sufficient catalogs: {final_count}/15. "
                f"This seed ({seed}) may not have enough relevant course data."
            )

        # 최종 중복 제거 적용
        data["profile"]["catalogs"] = self._deduplicate_catalogs(final_catalogs)
        data["seed_rec_idx"] = seed
        data["relevant_ids"] = relevant_ids

        logger.info("🎉 create_sample 완료 (총 %.2f초) | 최종 과목 수: %d개", 
                   time.perf_counter() - start_ts, len(data["profile"]["catalogs"]))
        return data 