from fastapi import APIRouter, HTTPException
import logging
from fastapi import Body

from src.api.models_gt import (
    GTGenerateRequest,
    GTBatchGenerateRequest,
    GTBatchGenerateResponse,
)
from src.services.gt_agent import GTAgent
from src.services.backend_client import BackendClient
from src.services.gt_batch_generator import GTBatchGenerator

router = APIRouter()

# 로거 설정
logger = logging.getLogger(__name__)


@router.post("/gt/generate")
async def generate_gt(request: GTGenerateRequest):
    try:
        agent = GTAgent()
        gt_data = await agent.create_sample(request.seed_rec_idx, request.num_similar)

        async with BackendClient() as backend:
            new_id = await backend.create_gt_sample(gt_data)

        return {**gt_data, "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post(
    "/gt/generate-batch",
    response_model=GTBatchGenerateResponse,
    summary="여러 개의 Ground Truth 샘플을 한 번에 생성",
    description="count 개수만큼 GT 샘플을 생성하여 백엔드에 저장합니다.",
)
async def generate_gt_batch(request: GTBatchGenerateRequest):

    logger.info(
        "[generate_gt_batch] 요청 수신 | count=%s | num_similar=%s",
        request.count,
        request.num_similar,
    )

    generator = GTBatchGenerator()
    ids, errors = await generator.generate(request.count, request.num_similar)

    return GTBatchGenerateResponse(
        generated=len(ids),
        failed=len(errors),
        ids=ids,
        errors=errors,
    ) 