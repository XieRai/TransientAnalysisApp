"""In-memory sample history and WebSocket client manager."""
from collections import deque

from fastapi import WebSocket

from app.schemas.sample import Sample


class SampleStore:
    def __init__(self, capacity: int = 600) -> None:
        self._samples: deque[Sample] = deque(maxlen=capacity)
        self._clients: set[WebSocket] = set()

    @property
    def count(self) -> int:
        return len(self._samples)

    def recent(self, limit: int = 300) -> list[Sample]:
        return list(self._samples)[-max(1, min(limit, 600)):]

    def add(self, sample: Sample) -> Sample:
        self._samples.append(sample)
        return sample

    async def connect(self, client: WebSocket) -> None:
        await client.accept()
        self._clients.add(client)

    def disconnect(self, client: WebSocket) -> None:
        self._clients.discard(client)

    async def broadcast(self, message: dict) -> None:
        stale: list[WebSocket] = []
        for client in self._clients:
            try:
                await client.send_json(message)
            except Exception:
                stale.append(client)
        for client in stale:
            self.disconnect(client)


sample_store = SampleStore()
