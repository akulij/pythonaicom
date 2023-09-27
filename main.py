import asyncio
import json

import redis
from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.types import Message, Channel
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest

from async_gpt import GPT


API_ID = 14858129
API_HASH = "27145bedb4839158ea59498642c2b904"

API_KEY = "sk-PROXYMODE"
API_ENDPOINT = "http://51.222.31.16:3000/v1"

client = TelegramClient("echo", API_ID, API_HASH)
r = redis.Redis(host='localhost', port=6379, db=0)
gpt = GPT(API_KEY, api_endpoint=API_ENDPOINT, system_prompt="""Тебе дается текст поста в Telegram. Твоя задача придумать к нему комментарий в шуточной форме. Ты мужского рода иу тебя есть блог.
Примеры комментариев:
Почему-то вспомнился детский стишок про мишку и «все равно его не брошу, потому что он хороший»))
Сложно только первые 3 месяца😂, потом привычка
Только при регулярном ведении канала будет результат 🔥 но и посты должны быть интересны""")
short = GPT(API_KEY, api_endpoint=API_ENDPOINT, system_prompt="Сделай короткую выжимку из текста")


async def get_channels(client: TelegramClient) -> list[Channel]:
    ch_links: list[str] = []
    with open("channels.txt") as f:
        ch_links = f.read().split("\n")

    ch_entities = [await client.get_entity(link) for link in ch_links]

    return ch_entities

async def joined(c: Channel) -> bool:
    channel = await client(GetFullChannelRequest(c))
    print(channel)
    if channel: return True
    return False

async def main():
    print(await joined(tab))
    if not await joined(tab):
        await client(JoinChannelRequest(tab))
    @client.on(events.NewMessage(chats=[entity, tab]))
    async def test(event):
        print(event)

    await client.run_until_disconnected()

# if __name__ == "__main__":
#     asyncio.run(main())

with client:
    client.loop.run_until_complete(main())
