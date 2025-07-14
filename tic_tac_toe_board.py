from dataclasses import dataclass, field, asdict
import redis.asyncio as aioredis
from redis.commands.json.path import Path
import os

r = aioredis.Redis(
    host='ai.thewcl.com',
    port=6379,
    password=os.getenv("PASSWORD"),
    decode_responses=True
)

REDIS_KEY_TEMPLATE = "tic_tac_toe:game_state:{team_number}"

@dataclass
class TicTacToeBoard:
    state: str = "is_playing"
    player_turn: str = "x"
    positions: list = field(default_factory=lambda: ["", "", "", "", "", "", "", "", ""])
    winner: str = ""

    def is_my_turn(self, i_am: str) -> bool:
        return i_am == self.player_turn and self.state == "is_playing"

    def make_move(self, index: int):
        if self.state != "is_playing":
            return {"success": False, "message": "Game is not currently active."}
        if index < 0 or index > 8:
            return {"success": False, "message": "Invalid index. Please enter a number between 0 and 8."}
        if self.positions[index] != "":
            return {"success": False, "message": "That position is already taken."}

        self.positions[index] = self.player_turn
        self.check_winner()
        self.check_draw()
        if self.state == "is_playing":
            self.switch_turn()
        return {"success": True, "message": "Move accepted.", "board": self.positions}

    def check_winner(self):
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for line in winning_lines:
            a, b, c = line
            if self.positions[a] != "" and self.positions[a] == self.positions[b] == self.positions[c]:
                self.state = "winner_decided"
                self.winner = self.positions[a]
                return self.positions[a]
        return None

    def check_draw(self):
        if "" not in self.positions and self.state != "winner_decided":
            self.state = "draw"
            print("It is a draw")
            return True
        return False

    def switch_turn(self):
        self.player_turn = "o" if self.player_turn == "x" else "x"

    def to_dict(self):
        return asdict(self)

    async def save_to_redis(self, team_number: int):
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number)
        board_data = self.to_dict()
        await r.json().set(redis_key, Path("$"), board_data)

    @classmethod
    async def load_from_redis(cls, team_number: int):
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number)
        data = await r.json().get(redis_key)
        if data and isinstance(data, dict):
            return cls(**data)
        return None

    async def reset(self, team_number: int):
        self.state = "is_playing"
        self.player_turn = "x"
        self.positions = ["", "", "", "", "", "", "", "", ""]
        await self.save_to_redis(team_number=team_number)