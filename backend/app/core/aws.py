import aioboto3

from app.core.config import settings

_session = aioboto3.Session()


def client_kwargs() -> dict:
    kwargs = {
        "region_name": settings.AWS_DEFAULT_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    if settings.AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.AWS_ENDPOINT_URL
    return kwargs


def get_session() -> aioboto3.Session:
    return _session
