import asyncio

from app.db.session import Base, engine
from app.models import models  # noqa: F401 — registers models on Base.metadata


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
