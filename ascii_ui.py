import asyncio
from websockets.legacy.client import connect

async def test_connection():
    url = "ws://127.0.0.1:8703"
    print("[ascii_ui] Trying to connect to:", url)
    try:
        async with connect(url) as websocket:
            print("[ascii_ui] Connected!")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"[ascii_ui] Connection failed: {type(e).__name__}: {e}")

asyncio.run(test_connection())