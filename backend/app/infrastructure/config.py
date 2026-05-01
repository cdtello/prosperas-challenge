from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str | None = None

    SQS_QUEUE_URL: str
    SQS_DLQ_URL: str

    S3_BUCKET_NAME: str

    WORKER_CONCURRENCY: int = 4
    SQS_VISIBILITY_TIMEOUT: int = 120
    SQS_MAX_MESSAGES: int = 10
    SQS_WAIT_SECONDS: int = 20


settings = Settings()
