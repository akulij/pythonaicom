import asyncio
import json

from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.types import Message, Channel, User
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest

from async_gpt import GPT




async def get_admin_user(client: TelegramClient) -> User:
    return await client.get_entity(ADMIN_USER)

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

async def main():
    admin = await get_admin_user(client)
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
            await client.send_message(admin, f"Unable to generate comment to post {post_link} cause:\n{e}")
            return
        try:
            await client.send_message(event.chat, comment_text, comment_to=event.message)
        except Exception as e:
            await client.send_message(admin, f"Unable to LEAVE comment to post {post_link} cause:\n{e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
