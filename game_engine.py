import argparse
import asyncio
import os
import httpx 
import redis.asyncio as aioredis 
from websockets.legacy.server import serve #used for WebSocket connection
import websockets #used for WebSocket connection
import json #used for JSON parsing

websocket_ready = asyncio.Event()
websocket_server = None 
connected_clients = set()
CHANNEL_NAME = "tictactoe_game_state_changed"

parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI")
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True)
parser.add_argument("--reset", action="store_true", help="Reset the game board")
parser.add_argument("--no-websocket", action="store_true", help="Do not start WebSocket server") #do not start WebSocket server
args = parser.parse_args()

async def handle_board_state(i_am_playing: str, redis_client):
    async with httpx.AsyncClient() as client:  # creates a new HTTP client
        response = await client.get("http://localhost:8000/state")  # sends GET request to fetch the current board state
        board_data = response.json()  # parses the response into a Python dictionary

        if "error" in board_data:  # checks if the board is missing
            print("No saved board found. Did you forget to --reset?")
            return

        if board_data["state"] == "winner_decided":  # handles win condition
            print("Game Over, winner is", board_data["winner"])
            return
        elif board_data["state"] == "draw":  # handles draw condition
            print("Game Over, it is a draw")
            return

        if board_data["player_turn"] == i_am_playing:  # checks if it's this player's turn
            print(f"It's your turn! Here's the board:")
            print(json.dumps(board_data, indent=2))  # prints the board neatly

            try:
                index = int(input(f"{i_am_playing}'s move (0–8): "))  # prompts user for move
                response = await client.post("http://localhost:8000/move", json={  # sends POST to /move
                    "player": i_am_playing,
                    "index": index
                })
                result = response.json()  # parses the server's response
                print(result.get("message") or result.get("error"))  # prints move result

                if result.get("success"):  # only continue if move was valid
                    await asyncio.sleep(0.2)  # small delay to let backend persist updated board

                    response = await client.get("http://localhost:8000/state")  # refreshes board state
                    board_data = response.json()  # gets latest board data

                    if board_data["state"] == "winner_decided":  # handles win after move
                        print(f"Game Over, winner is {board_data['winner']}")
                    elif board_data["state"] == "draw":  # handles draw after move
                        print("Game Over, it is a draw")
                    else:
                        print(json.dumps(board_data, indent=2))  # prints updated board

                    # --- WebSocket broadcast logic ---
                    message = json.dumps({"positions": board_data.get("positions", [""] * 9)})  # prepares board data for broadcast
                    print("[Broadcasting to WebSocket clients]:", message)  # logs what’s being sent

                    disconnected = set()  # keeps track of any clients that have disconnected
                    for client_ws in connected_clients:  # loops through connected WebSocket clients
                        try:
                            await client_ws.send(message)  # sends board update
                        except websockets.exceptions.ConnectionClosed:  # catches dead connections
                            disconnected.add(client_ws)  # marks disconnected client

                    connected_clients.difference_update(disconnected)  # removes disconnected clients from the set
                    # --- End WebSocket broadcast ---

            except ValueError:  # handles invalid input
                print("Invalid input. Please enter a number from 0 to 8.")
        else:
            print(f"Waiting for {board_data['player_turn']} to move...")  # shows whose turn it is

async def listen_for_updates(i_am_playing: str):
    redis_client = aioredis.Redis(
        host='ai.thewcl.com',
        port=6379,
        password=os.getenv("PASSWORD"),
        decode_responses=True
    )
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)
    await handle_board_state(i_am_playing, redis_client)
    async for message in pubsub.listen():
        if message["type"] == "message":
            await handle_board_state(i_am_playing, redis_client)

async def main():
    async with httpx.AsyncClient() as client:
        if args.reset:
            response = await client.post("http://localhost:8000/reset")
            print(response.json()["message"])
            return

    print("Time to play Tic Tac Toe!")
    tasks = []

    if not args.no_websocket:
        websocket_task = await start_websocket_server()
        tasks.append(websocket_task)
        await websocket_ready.wait()  # Wait here until server is ready

    tasks.append(listen_for_updates(args.player))
    await asyncio.gather(*tasks)

# ✨ Use an Event to signal readiness

async def websocket_handler(websocket):
    print("[websocket_handler] Running!")
    connected_clients.add(websocket)  # adds client to the set
    print("[Server] New client connected via WebSocket")

    try:
        async with httpx.AsyncClient() as client:
            # --- Get the current board state on client connect ---
            response = await client.get("http://localhost:8000/state")  # fetch latest board
            board_data = response.json()  # parse response
            initial_board_msg = json.dumps({"positions": board_data.get("positions", [""] * 9)})  # prepare message

            await asyncio.sleep(0.1)  # small delay to prevent race condition
            await websocket.send(initial_board_msg)  # sends current state to new client
            print("[Sent initial board to client]")
            # --- End initial board send ---

        await websocket.wait_closed()  # waits until client disconnects
    except Exception as e:
        print(f"[WebSocket] Error with client: {e}")  # log error
    finally:
        connected_clients.discard(websocket)  # removes client when done


async def start_websocket_server():
    port = 8701
    print(f"Starting WebSocket server on ws://127.0.0.1:{port}")

    async def run_server():
        print("run_server() has started")
        async with serve(websocket_handler, "127.0.0.1", port):
            await asyncio.sleep(0.1)  # tiny delay to ensure socket is ready
            print("[WebSocket] Server is ready and accepting connections")
            websocket_ready.set()  # Signal readiness
            await asyncio.Future()

    return asyncio.create_task(run_server())

if __name__ == "__main__":
    asyncio.run(main())
