from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import (
        SQLModel,
        Field,
        )

from modules.config import Settings


class ClientConfig(SQLModel, table=True):
    client_id: Optional[int] = Field(default=None, primary_key=True)
    api_id: int
    api_hash: str
    openai_key: str
    openai_endpoint: str
    admin_user: str | None
    session_file: str
    channels_file: str
    gpt_prompt: str


class DB:
    def __init__(self, config: Settings):
        self.engine = create_async_engine(config.database_uri)

    async def get_client_config(self, id: int) -> ClientConfig | None:
        async with AsyncSession(self.engine) as session:
            config = await session.get(ClientConfig, id)

        return config
