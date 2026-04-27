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


async def publish_job(job_id: str) -> None:
    async with _session.client("sqs", **_client_kwargs()) as sqs:
        await sqs.send_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MessageBody=json.dumps({"job_id": job_id}),
        )


async def receive_messages(max_messages: int = 10) -> list[dict]:
    async with _session.client("sqs", **_client_kwargs()) as sqs:
        response = await sqs.receive_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=settings.SQS_WAIT_SECONDS,
            VisibilityTimeout=settings.SQS_VISIBILITY_TIMEOUT,
        )
        return response.get("Messages", [])


async def delete_message(receipt_handle: str) -> None:
    async with _session.client("sqs", **_client_kwargs()) as sqs:
        await sqs.delete_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle,
        )
