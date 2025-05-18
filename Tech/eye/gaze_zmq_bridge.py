#!/usr/bin/env python3
import asyncio
import json

import zmq
import zmq.asyncio
import websockets

ZMQ_ADDR = "tcp://127.0.0.1:5557"  # where your client (Unity/Go/etc) will SUB
WS_PORT  = 8081                   # where your HTML will WS→bridge

async def handler(ws):
    print("WS client connected")
    try:
        async for msg in ws:
            data = json.loads(msg)
            # re-publish via the already-bound PUB socket
            await pub.send_json(data)
    except websockets.ConnectionClosed:
        pass
    print("WS client disconnected")

async def main():
    global pub
    # 1) create & bind PUB only once
    ctx = zmq.asyncio.Context()
    pub = ctx.socket(zmq.PUB)
    pub.bind(ZMQ_ADDR)
    print(f"ØMQ PUB bound to {ZMQ_ADDR}")

    # 2) start the WebSocket server
    async with websockets.serve(handler, "localhost", WS_PORT):
        print(f"WS→ØMQ bridge listening on ws://localhost:{WS_PORT} → {ZMQ_ADDR}")
        await asyncio.Future()   # run until cancelled

    # 3) cleanup (never reached unless you exit)
    pub.close()
    ctx.term()

if __name__ == "__main__":
    asyncio.run(main())
