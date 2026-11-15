"""Versioned API endpoints for sensor samples and live streaming."""
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.sample import Sample, SampleAccepted
from app.services.sample_store import sample_store

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "transient-analyzer"}


@router.get("/samples", response_model=list[Sample])
async def get_samples(limit: int = 300) -> list[Sample]:
    return sample_store.recent(limit)


@router.post("/samples", response_model=SampleAccepted, status_code=202)
async def ingest_sample(sample: Sample) -> SampleAccepted:
    point = sample_store.add(sample)
    await sample_store.broadcast({"type": "sample", "data": point.model_dump(mode="json")})
    return SampleAccepted(accepted=True, count=sample_store.count)


@router.websocket("/ws")
async def sample_stream(websocket: WebSocket) -> None:
    await sample_store.connect(websocket)
    try:
        await websocket.send_json({
            "type": "history",
            "data": [point.model_dump(mode="json") for point in sample_store.recent(600)],
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        sample_store.disconnect(websocket)
