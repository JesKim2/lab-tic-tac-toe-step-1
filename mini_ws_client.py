import asyncio
from websockets.legacy.client import connect

async def test_ws():
    WEBSOCKET_URL = "ws://localhost:8703"
    print("[mini_ws_client] Trying to connect...")
    try:
        async with connect(WEBSOCKET_URL) as websocket:
            print("[mini_ws_client] Connected!")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"[mini_ws_client] Connection failed: {type(e).__name__}: {e}")

asyncio.run(test_ws())
