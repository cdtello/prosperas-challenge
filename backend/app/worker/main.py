import asyncio
import logging

from app.worker.consumer import poll_and_process

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


if __name__ == "__main__":
    asyncio.run(poll_and_process())
