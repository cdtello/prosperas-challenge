import json

from app.infrastructure.aws import client_kwargs, get_session
from app.infrastructure.config import settings

PRESIGNED_URL_EXPIRY = 604800  # 7 days


class S3FileStorage:
    async def upload_report(self, job_id: str, data: dict) -> str:
        key = f"reports/{job_id}.json"

        async with get_session().client("s3", **client_kwargs()) as s3:
            await s3.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json",
            )

            if settings.AWS_ENDPOINT_URL:
                return f"{settings.AWS_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"

            url: str = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
                ExpiresIn=PRESIGNED_URL_EXPIRY,
            )
            return url
