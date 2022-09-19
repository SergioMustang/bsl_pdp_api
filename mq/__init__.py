import os
import asyncio
import nats
from dotenv import load_dotenv


def get_url():
    load_dotenv()

    host = os.getenv('NATS_HOST')
    port = os.getenv('NATS_PORT')
    return f"nats://{host}:{port}"


class NatsQuery:

    async def __aenter__(self):
        self.nc = await asyncio.wait_for(nats.connect(get_url()), timeout=2)
        return self

    async def __aexit__(self, *args):
        self.nc.drain()

    async def send_json_message(self, subject, json_obj):
        json_obj_serialized = json_obj.json(ensure_ascii=False)
        await self.nc.publish(subject, bytes(json_obj_serialized, encoding='utf-8'))




