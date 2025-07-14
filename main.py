from fastapi import FastAPI, Request, Body
from tic_tac_toe_board import TicTacToeBoard
import os
import redis.asyncio as aioredis
import json
import asyncio
import websockets
from typing import Set



app = FastAPI()  # create FastAPI app
connected_clients: Set[websockets.WebSocketServerProtocol] = set()  #tracks all UI clients

# Broadcast current board to all connected UI clients
async def broadcast_game_state():
    board = await TicTacToeBoard.load_from_redis(team_number=1)  # load current board
    if board:
        message = json.dumps({"positions": board.positions})  # prepare broadcast
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send(message)  # send board update
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)  # track closed clients
        connected_clients.difference_update(disconnected)  # remove dead clients

# Send current board to a new client who just connected
async def send_initial_board(client_ws):
    board = await TicTacToeBoard.load_from_redis(team_number=1)
    if board:
        message = json.dumps({"positions": board.positions})  # prepare welcome message
        await client_ws.send(message)  # send current state

# Start WebSocket server and handle new connections
async def websocket_handler(websocket):
    print("[WebSocket] New client connected")
    connected_clients.add(websocket)  # track client
    try:
        await send_initial_board(websocket)  # send current board right away
        await websocket.wait_closed()  # stay open until they disconnect
    finally:
        connected_clients.discard(websocket)  # remove client when they leave
        print("[WebSocket] Client disconnected")

# Run WebSocket server on a background task
async def start_websocket_server():
    port = 8701
    print(f"Starting WebSocket server on ws://127.0.0.1:{port}")
    async with websockets.serve(websocket_handler, "127.0.0.1", port):
        await asyncio.Future()  # keep server running forever

# Start both FastAPI and WebSocket server
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_websocket_server())  # run WS server alongside FastAPI

# FastAPI endpoints
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
        await broadcast_game_state()  # broadcast after move
    return result

@app.post("/reset")
async def reset_board():
    new_board = TicTacToeBoard()
    await new_board.save_to_redis(team_number=1)
    await broadcast_game_state()  # broadcast after reset
    return { "message": "Game reset." }
