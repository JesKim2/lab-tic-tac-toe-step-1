from fastapi import FastAPI, Request, Body #imports FastAPI, Request, and Body
from tic_tac_toe_board import TicTacToeBoard #imports TicTacToeBoard
import os #imports os

app = FastAPI() #creates the app

@app.get("/state")
async def get_state():
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
    if board is None: #checks if the board did not load, and reminds the user to use reset
        return { "error": "No board found. Please reset first." }
    return board.to_dict() #returns the board as a dictionary

@app.post("/move") #accepts a player and an index
async def make_move(player: str = Body(...), index: int = Body(...)): #accepts a player and an index
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
    if board is None: #checks if the board did not load, and reminds the user to use reset
        return { "error": "No board found. Please reset first." }
    if not board.is_my_turn(player): #checks if it is my turn
        return { "error": "It is not your turn." }
    result = board.make_move(index) #get the result dict
    if result["success"]: #if the move was successful
        await board.save_to_redis(team_number=1) #save the board
    return result #returns the result dict

@app.post("/reset") #resets the board
async def reset_board():
    new_board = TicTacToeBoard()  # empty board is created
    await new_board.save_to_redis(team_number=1)  # overwrite any existing board
    return { 
        "message": "Game reset.",
        "board": new_board.to_dict()
    }

#FastAPI delegates logic by accepting the HTTP requests and calls the methods with the data from the request
#FastAPI itself does not know the game rules, it just calls the methods

#This design allows any frontend to now be used since the game is exposed as an HTTP API. 
#As long as the frontend calls the same endpoints with the same data, it will work.
