import os
import asyncio
import nats
from dotenv import load_dotenv


def get_url():
    load_dotenv()

    host = os.getenv('NATS_HOST')
    port = os.getenv('NATS_PORT')
    return f"nats://{host}:{port}"


async def send_json_message(subject, json_obj):
    json_obj_serialized = json_obj.json(ensure_ascii=False)
    nc = await asyncio.wait_for(nats.connect(get_url()), timeout=2)
    await nc.publish(subject, bytes(json_obj_serialized, encoding='utf-8'))
    await nc.drain()

