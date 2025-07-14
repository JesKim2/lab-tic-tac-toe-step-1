import asyncio
import websockets

async def main():
    uri = "ws://127.0.0.1:8703"
    print("[client] Trying to connect to", uri)
    async with websockets.connect(uri) as websocket:
        print("[client] Connected!")
        await websocket.send("Hello from client!")
        response = await websocket.recv()
        print("[client] Got back:", response)

asyncio.run(main())
