import asyncio
import os
import json
import sys
from websockets.client import connect

WEBSOCKET_URL = "ws://127.0.0.1:8701"

def draw_board(positions):
    def format_cell(pos, i):
        return pos.upper() if pos.strip() else str(i)
    cells = [format_cell(pos, i) for i, pos in enumerate(positions)]

    print("\n")
    print(f" {cells[0]} | {cells[1]} | {cells[2]} ")
    print("---+---+---")
    print(f" {cells[3]} | {cells[4]} | {cells[5]} ")
    print("---+---+---")
    print(f" {cells[6]} | {cells[7]} | {cells[8]} ")
    print("\n")

async def listen_for_updates():
    print("[ascii_ui] Trying to connect to:", WEBSOCKET_URL)

    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            async with connect(WEBSOCKET_URL, open_timeout=3) as websocket:
                print(f"[ascii_ui] Connected to {WEBSOCKET_URL}")
                async for message in websocket:
                    print("[ascii_ui] Received message:", message)

                    try:
                        data = json.loads(message)
                        print("[ascii_ui] Parsed JSON:", data)
                        positions = data.get("positions")

                        if positions and isinstance(positions, list) and len(positions) == 9:
                            os.system('cls' if os.name == 'nt' else 'clear')
                            draw_board(positions)
                        else:
                            print("Invalid 'positions' data:", data)
                    except json.JSONDecodeError:
                        print("Received malformed JSON:", message)
                return
        except Exception as e:
            print(f"[ascii_ui] Connection attempt {attempt} failed: {type(e).__name__}: {e}")
            await asyncio.sleep(1)

    print("[ascii_ui] Could not connect after several attempts.")

if __name__ == "__main__":
    asyncio.run(listen_for_updates())
