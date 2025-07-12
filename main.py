from fastapi import FastAPI, Request, Body  # imports FastAPI tools
from tic_tac_toe_board import TicTacToeBoard  # imports game logic
import os
import redis.asyncio as aioredis  # used for publishing updates

app = FastAPI()  # creates the FastAPI app

@app.get("/state")  # handles GET requests for current board state
async def get_state(): #returns current board state
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads board from Redis
    if board is None:
        return { "error": "No board found. Please reset first." }
    return board.to_dict()

@app.post("/move")  # handles POST requests to make a move
async def make_move(player: str = Body(...), index: int = Body(...)): #handles POST requests to make a move
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads board from Redis
    if board is None:
        return { "error": "No board found. Please reset first." }
    if not board.is_my_turn(player):  # HTTP version of turn-checking
        return { "error": "It is not your turn." }

    result = board.make_move(index)  # HTTP version of making a move
    if result["success"]:
        await board.save_to_redis(team_number=1)

        #publish update so CLI sees the change via Redis
        redis = aioredis.Redis(
            host='ai.thewcl.com',
            port=6379,
            password=os.getenv("PASSWORD"),
            decode_responses=True
        )
        await redis.publish("tictactoe_game_state_changed", "board_updated")

    return result

@app.post("/reset")  # handles POST requests to reset the game board
async def reset_board():
    new_board = TicTacToeBoard()
    await new_board.save_to_redis(team_number=1)
    return { "message": "Game reset." }

#game_engine.py does not use the TicTacToeBoard class anymore. 
#It doesn't know how the game works, it just sends requests to the server at localhost:8000. 
#The server handles all the game logic, not the CLI.