from fastapi import FastAPI, Request, Body  
from tic_tac_toe_board import TicTacToeBoard  
import os
import redis.asyncio as aioredis  

app = FastAPI()  

@app.get("/state")  
async def get_state():
    board = await TicTacToeBoard.load_from_redis(team_number=1) 
    if board is None:
        return { "error": "No board found. Please reset first." }
    return board.to_dict()

@app.post("/move") 
async def make_move(player: str = Body(...), index: int = Body(...)):
    board = await TicTacToeBoard.load_from_redis(team_number=1) 
    if board is None:
        return { "error": "No board found. Please reset first." }
    if not board.is_my_turn(player): 
        return { "error": "It is not your turn." }

    result = board.make_move(index) 
    if result["success"]:
        await board.save_to_redis(team_number=1)

        redis = aioredis.Redis(
            host='ai.thewcl.com',
            port=6379,
            password=os.getenv("PASSWORD"),
            decode_responses=True
        )
        await redis.publish("tictactoe_game_state_changed", "board_updated")

    return result

@app.post("/reset") 
async def reset_board():
    new_board = TicTacToeBoard()
    await new_board.save_to_redis(team_number=1)
    return { "message": "Game reset." }