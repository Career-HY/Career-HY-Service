from fastapi import APIRouter, HTTPException

from src.api.models_gt import GTGenerateRequest
from src.services.gt_agent import GTAgent
from src.services.backend_client import BackendClient

router = APIRouter()


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