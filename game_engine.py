import argparse
import asyncio
import os
import httpx  #used to send HTTP requests
import redis.asyncio as aioredis  #used for Pub/Sub

CHANNEL_NAME = "tictactoe_game_state_changed"

#now uses HTTP to get and submit board state instead of calling board methods
async def handle_board_state(i_am_playing: str, redis_client):
    async with httpx.AsyncClient() as client: #uses HTTP to get and submit board state instead of calling board methods
        response = await client.get("http://localhost:8000/state") #gets board via HTTP
        board_data = response.json()

        if "error" in board_data:
            print("No saved board found. Did you forget to --reset?")
            return

        if board_data["state"] == "winner_decided":
            print("Game Over, winner is", board_data["winner"])
            return
        elif board_data["state"] == "draw":
            print("Game Over, it is a draw")
            return

        if board_data["player_turn"] == i_am_playing:
            print(f"It's your turn! Here's the board:")
            import json
            print(json.dumps(board_data, indent=2))

            try:
                index = int(input(f"{i_am_playing}'s move (0–8): "))
                #send move via HTTP POST
                response = await client.post("http://localhost:8000/move", json={ #sends POST to /move
                    "player": i_am_playing,
                    "index": index
                })
                result = response.json()
                print(result.get("message") or result.get("error"))

                if result.get("success"): #if move was successful
                    response = await client.get("http://localhost:8000/state")  # refresh state after move
                    board_data = response.json() #get updated board state

                    if board_data["state"] == "winner_decided":
                        print(f"Game Over, winner is {board_data['winner']}")
                    elif board_data["state"] == "draw":
                        print("Game Over, it is a draw")
                    else:
                        print(json.dumps(board_data, indent=2))

            except ValueError:
                print("Invalid input. Please enter a number from 0 to 8.")
        else:
            print(f"Waiting for {board_data['player_turn']} to move...")

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
    async with httpx.AsyncClient() as client: #uses HTTP to get and submit board state instead of calling board methods
        if args.reset: #if reset flag is set
            #sends POST to /reset instead of calling board directly
            response = await client.post("http://localhost:8000/reset") #sends POST to /reset
            print(response.json()["message"]) #prints message from response
            return

    print("Time to play Tic Tac Toe!")
    await listen_for_updates(args.player)

parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI")
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True)
parser.add_argument("--reset", action="store_true", help="Reset the game board")
args = parser.parse_args()

if __name__ == "__main__":
    asyncio.run(main())
    