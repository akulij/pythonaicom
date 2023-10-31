import asyncio
from sys import argv

from telethon import TelegramClient
from telethon.tl.types import Channel, User
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from pydantic import BaseModel

from async_gpt import GPT
from modules.db import DB
from modules.config import config


class Config(BaseModel):
    api_id: int
    api_hash: str
    openai_key: str
    openai_endpoint: str
    admin_user: str | None
    session_file: str
    channels_file: str
    gpt_prompt: str


async def get_admin_user(client: TelegramClient, admin: str | None) -> User | None:
    if not admin: return None
    return await client.get_entity(admin)

async def get_channels(client: TelegramClient) -> list[Channel]:
    ch_links: list[str] = []
    with open("channels.txt") as f:
        ch_links = f.read().strip().split("\n")

    async def entwrap(link: str):
        print(link)
        return await client.get_entity(link)
    ch_entities = [await entwrap(link) for link in ch_links]

    return ch_entities

async def joined(c: Channel) -> bool:
    channel = await client(GetFullChannelRequest(c))
    if channel: return True
    return False

async def main(client: TelegramClient, config: Config):
    gpt = GPT(config.openai_key, api_endpoint=config.openai_endpoint, system_prompt=config.gpt_prompt)
    admin = await get_admin_user(client, config.admin_user)
    channels = await get_channels(client)
    for channel in channels:
        print(f"checking channel {channel}")
        if not await joined(channel):
            await client(JoinChannelRequest(channel))
            print(f"joined channel {channel}")
            await asyncio.sleep(2)
    print("joined all")
    @client.on(events.NewMessage(chats=channels))
    async def comment_post(event: events.NewMessage):
        post_text = event.message.raw_text # post text without formating. To get markdown-formated text use event.message.text
        post_link = "" # will be created later
        try:
            comment_text = await gpt.complete(post_text)
        except Exception as e:
            if admin:
                await client.send_message(admin, f"Unable to generate comment to post {post_link} cause:\n{e}")
            return
        try:
            await client.send_message(event.chat, comment_text, comment_to=event.message)
        except Exception as e:
            if admin:
                await client.send_message(admin, f"Unable to LEAVE comment to post {post_link} cause:\n{e}")

    runner = client.run_until_disconnected()
    if runner:
        await runner

async def initalize(client_id: int) -> Config:
    db = DB(config)
    cc = await db.get_client_config(client_id)
    if not cc:
        raise Exception(f"Not found ClientConfig for {client_id=}")
    c = Config(
            api_id=cc.api_id,
            api_hash=cc.api_hash,
            openai_key=cc.openai_key,
            openai_endpoint=cc.openai_endpoint,
            admin_user=cc.admin_user,
            session_file=cc.session_file,
            channels_file=cc.channels_file,
            gpt_prompt=cc.gpt_prompt
            )

    return c

def get_client_id() -> int:
    try:
        return int(argv[1])
    except:
        print(f"Usage: {argv[0]} (int_client_id)")
        exit(-1)

if __name__ == "__main__":
    client_id = get_client_id()
    config = asyncio.run(initalize(client_id))
    client = TelegramClient(config.session_file, config.api_id, config.api_hash)
    with client:
        client.loop.run_until_complete(main(client, config))
