from typing import Protocol


class IFileStorage(Protocol):
    async def upload_report(self, job_id: str, data: dict) -> str: ...
