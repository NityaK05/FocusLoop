# gaze_ws_server.py
import asyncio
import json
import zmq
import zmq.asyncio
from websockets import serve

ctx = zmq.asyncio.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")  # raw gaze → ZMQ on 5556

async def handler(ws):
    async for raw in ws:
        data = json.loads(raw)
        await pub.send_json(data)

async def main():
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
