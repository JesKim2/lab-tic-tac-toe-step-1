# echo_server.py
import asyncio
from websockets.legacy.server import serve

async def echo(websocket):
    print("[echo_server] Client connected")
    try:
        async for message in websocket:
            print("[echo_server] Received:", message)
            await websocket.send(f"Echo: {message}")
    except Exception as e:
        print(f"[echo_server] Error: {type(e).__name__}: {e}")

async def main():
    print("[echo_server] Starting on ws://127.0.0.1:8703")
    async with serve(echo, "127.0.0.1", 8703):
        await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
