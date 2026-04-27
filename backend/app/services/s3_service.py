import json

import aioboto3

from app.core.config import settings

_session = aioboto3.Session()


def _client_kwargs() -> dict:
    kwargs = {
        "region_name": settings.AWS_DEFAULT_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    if settings.AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.AWS_ENDPOINT_URL
    return kwargs


async def upload_report(job_id: str, data: dict) -> str:
    key = f"reports/{job_id}.json"
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json",
        )
    if settings.AWS_ENDPOINT_URL:
        return f"{settings.AWS_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"
    return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{key}"
