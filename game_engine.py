from tic_tac_toe_board import TicTacToeBoard 
import argparse 
import redis.asyncio as aioredis
import asyncio
import os
import httpx  # imports httpx


CHANNEL_NAME = "tictactoe_game_state_changed" 

async def handle_board_state(i_am_playing: str, redis_client):  # calls the FastAPI endpoint to get the board state
    async with httpx.AsyncClient() as client:  # uses httpx to make HTTP requests
        response = await client.get("http://localhost:8000/state")  # GETs the board state from FastAPI
        board_data = response.json()  # returns the board as a dictionary

        if "error" in board_data:  # checks if the board did not load, and reminds the user to use reset
            print("No saved board found. Did you forget to --reset?")
            return

        if board_data["state"] == "winner_decided":  # checks if the game is over
            print("Game Over, winner is", board_data["winner"]) #uses board_data to print the winner
            return
        elif board_data["state"] == "draw":  # checks if the game is a draw
            print("Game Over, it is a draw") #uses board_data to print the result
            return

        if board_data["player_turn"] == i_am_playing:  # checks if it is my turn
            print(f"It's your turn! Here's the board:")
            import json
            print(json.dumps(board_data, indent=2))  # pretty-prints the board

            try:
                index = int(input(f"{i_am_playing}'s move (0–8): "))  # asks the player for their move
                # sends the move to FastAPI using POST /move
                response = await client.post("http://localhost:8000/move", json={
                    "player": i_am_playing,
                    "index": index
                })
                result = response.json()  # gets back the result dictionary
                print(result.get("message") or result.get("error"))  # prints success or error message

                if result.get("success"):  # if the move was accepted
                    # fetches the updated board state
                    response = await client.get("http://localhost:8000/state")
                    board_data = response.json()

                    if board_data["state"] == "winner_decided":  # if the game is now over
                        print(f"Game Over, winner is {board_data['winner']}")
                    elif board_data["state"] == "draw":  # if the game is now a draw
                        print("Game Over, it is a draw")
                    else:
                        print(json.dumps(board_data, indent=2))  # show updated board

            except ValueError:
                print("Invalid input. Please enter a number from 0 to 8.")  # handles non-number input
        else:
            print(f"Waiting for {board_data['player_turn']} to move...")  # tells you to wait if it’s not your turn

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
    if args.reset: 
        board = TicTacToeBoard() 
        await board.reset(team_number=1)  
        print("Board reset.")
        return
    print("Time to play Tic Tac Toe!") 
    await listen_for_updates(args.player) 

parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI")
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True) 
parser.add_argument("--reset", action="store_true", help="Reset the game board")
args = parser.parse_args() 

if __name__ == "__main__": 
    asyncio.run(main())
