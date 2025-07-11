import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from httpx import AsyncClient
from main import app
from tic_tac_toe_board import TicTacToeBoard

import redis  # use sync Redis for tests
r = redis.Redis(
    host="ai.thewcl.com",
    port=6379,
    password=os.getenv("PASSWORD"),
    decode_responses=True
)

@pytest.mark.asyncio
async def test_state_no_board():
    # Reset the board to simulate missing board
    r.delete("tic_tac_toe:game_state:1")

    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        response = await client.get("/state")

    assert response.status_code == 200
    assert "error" in response.json()

    
@pytest.mark.asyncio
async def test_valid_move():
    empty_board = TicTacToeBoard()
    await empty_board.save_to_redis(team_number=1)

    async with AsyncClient(app=app, base_url="http://test") as client:
        move = {"player": "x", "index": 0}
        response = await client.post("/move", json=move)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Move accepted."
    assert data["board"][0] == "x"

    
