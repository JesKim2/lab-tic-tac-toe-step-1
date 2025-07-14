import asyncio
import websockets

async def echo(websocket):
    print("[server] Client connected")
    async for message in websocket:
        print(f"[server] Received: {message}")
        await websocket.send(f"Echo: {message}")

async def main():
    async with websockets.serve(echo, "0.0.0.0", 8703):
        print("[server] Mini server running on ws://127.0.0.1:8703")
        await asyncio.Future()

asyncio.run(main())
