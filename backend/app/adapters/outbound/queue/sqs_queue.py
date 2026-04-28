import json

from app.infrastructure.aws import client_kwargs, get_session
from app.infrastructure.config import settings


class SqsMessageQueue:
    async def publish(self, job_id: str) -> None:
        async with get_session().client("sqs", **client_kwargs()) as sqs:
            await sqs.send_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MessageBody=json.dumps({"job_id": job_id}),
            )

    async def receive(self, max_messages: int = 10) -> list[dict]:
        async with get_session().client("sqs", **client_kwargs()) as sqs:
            response = await sqs.receive_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=settings.SQS_WAIT_SECONDS,
                VisibilityTimeout=settings.SQS_VISIBILITY_TIMEOUT,
            )
            return response.get("Messages", [])

    async def delete(self, receipt_handle: str) -> None:
        async with get_session().client("sqs", **client_kwargs()) as sqs:
            await sqs.delete_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                ReceiptHandle=receipt_handle,
            )
