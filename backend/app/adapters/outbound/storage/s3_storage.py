import json

from app.infrastructure.aws import client_kwargs, get_session
from app.infrastructure.config import settings

PRESIGNED_URL_EXPIRY = 604800  # 7 days


class S3FileStorage:
    async def upload_report(self, job_id: str, data: dict) -> str:
        key = f"reports/{job_id}.json"
        kwargs = client_kwargs()

        async with get_session().client("s3", **kwargs) as s3:
            await s3.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json",
            )

            # LocalStack: return direct URL (presigned not needed locally)
            if settings.AWS_ENDPOINT_URL:
                return f"{settings.AWS_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"

            # Production: generate presigned URL (valid 7 days)
            url: str = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
                ExpiresIn=PRESIGNED_URL_EXPIRY,
            )
            return url
