import asyncio
from random import randint
import typing
import json
import aiohttp

K = typing.TypeVar("K")


class GPT:
    def __init__(self, api_key: str, system_prompt: str):
        self.api_key = api_key
        self.system = system_prompt
        self.headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }

    # async def complete(self, message: str, key: K = None, temperature: float = 1) -> tuple[str, K] | None:
    async def complete(self, message: str, temperature: float = 1) -> str | None:
        await asyncio.sleep(randint(0, 4000) / 1000)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            data = {
                    "model": "gpt-3.5-turbo",
                    "temperature": temperature,
                    "messages": [
                            {"role": "system", "content": self.system},
                            {"role": "user", "content": message}
                        ],
                }
            # print(json.dumps(data))
            response = await session.post("https://api.openai.com/v1/chat/completions", data=json.dumps(data))
            if response.status != 200: return
            response = await response.json()

        answer: str = response["choices"][0]["message"]["content"]

        return answer
