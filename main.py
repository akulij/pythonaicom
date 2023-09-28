import asyncio
import json

import redis
from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.types import Message, Channel, User
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest

from async_gpt import GPT


API_ID = 14858129
API_HASH = "27145bedb4839158ea59498642c2b904"

API_KEY = "sk-PROXYMODE"
API_ENDPOINT = "http://51.222.31.16:3000/v1"

ADMIN_USER = "akulij"

client = TelegramClient("echo", API_ID, API_HASH)
r = redis.Redis(host='localhost', port=6379, db=0)
gpt = GPT(API_KEY, api_endpoint=API_ENDPOINT, system_prompt="""Тебе дается текст поста в Telegram. Твоя задача придумать к нему комментарий в шуточной форме. Ты мужского рода иу тебя есть блог.
Примеры комментариев:
Почему-то вспомнился детский стишок про мишку и «все равно его не брошу, потому что он хороший»))
Сложно только первые 3 месяца😂, потом привычка
Только при регулярном ведении канала будет результат 🔥 но и посты должны быть интересны""")
short = GPT(API_KEY, api_endpoint=API_ENDPOINT, system_prompt="Сделай короткую выжимку из текста")


async def get_admin_user(client: TelegramClient) -> User:
    return await client.get_entity(ADMIN_USER)

async def get_channels(client: TelegramClient) -> list[Channel]:
    ch_links: list[str] = []
    with open("channels.txt") as f:
        ch_links = f.read().strip().split("\n")

    ch_entities = [await client.get_entity(link) for link in ch_links]

    return ch_entities

async def joined(c: Channel) -> bool:
    channel = await client(GetFullChannelRequest(c))
    if channel: return True
    return False

async def main():
    admin = await get_admin_user(client)
    channels = await get_channels(client)
    for channel in channels:
        if not await joined(channel):
            await client(JoinChannelRequest(channel))
    @client.on(events.NewMessage(chats=channels))
    async def comment_post(event: events.NewMessage):
        post_text = event.message.raw_text # post text without formating. To get markdown-formated text use event.message.text
        post_link = ""
        try:
            comment_text = await gpt.complete(post_text)
        except Exception as e:
            await client.send_message(admin, f"Unable to generate comment to post {post_link} cause:\n{e}")
        try:
            await client.send_message(event.chat, comment_text, comment_to=event.message)
        except Exception as e:
            await client.send_message(admin, f"Unable to LEAVE comment to post {post_link} cause:\n{e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
