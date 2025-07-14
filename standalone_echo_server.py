import asyncio
from websockets.legacy.server import serve

async def echo(websocket):
    print("[echo_server] Got a connection")
    await websocket.send("Hello from standalone echo server")
    await websocket.wait_closed()

async def main():
    print("[echo_server] Starting on ws://127.0.0.1:8703")
    async with serve(echo, "127.0.0.1", 8703):
        await asyncio.Future()  # run forever

asyncio.run(main())
