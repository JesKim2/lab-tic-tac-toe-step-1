from dataclasses import dataclass, field
import redis.asyncio as aioredis #imported redis.asyncio to have async work
from redis.commands.json.path import Path 
import os 

r = aioredis.Redis( #have aioredis.Redis now instead of the regular redis from before
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
    winner: str = ""  # <-- NEW LINE
  
    def is_my_turn(self, i_am: str) -> bool:
        if i_am == self.player_turn and self.state == "is_playing": 
            return True
        else:
            return False
        
    def make_move(self, index: int): 
        if self.state != "is_playing":
            print("Game is not playing")
            return
        if index < 0 or index > 8: 
            print("Invalid index")
            return
        if self.positions[index] != "": 
            print("Position already taken")
            return
        print("Player", self.player_turn, "is making a move") 
        self.positions[index] = self.player_turn
        print(self.positions)
        self.check_winner() 
        self.check_draw() 
        if self.state == "is_playing":
            self.switch_turn() 
            
    def check_winner(self):
        winning_lines = [ 
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ]
        for line in winning_lines:
            a, b, c = line    
            if self.positions[a] != "" and self.positions[a] == self.positions[b] == self.positions[c]: 
                self.state = "winner_decided"
                self.winner = self.positions[a] #sets the winner
                return self.positions[a]
        return None           
    
    def check_draw(self): 
        if "" not in self.positions and self.check_winner() is None: 
            self.state = "draw"
            print("It is a draw")
            return True
        return False 
    
    def switch_turn(self):
        if self.player_turn == "x":
            self.player_turn = "o"
        else:
            self.player_turn = "x"
    
    def serialize(self): 
        return {
            "state": self.state, 
            "player_turn": self.player_turn, 
            "positions": self.positions,
            "winner": self.winner
        } 
    
    async def save_to_redis(self, team_number: int): 
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number) #created a redis key
        board_data = self.serialize() #serialized the board data
        await r.json().set(redis_key, Path("$"), board_data) 

    @classmethod 
    async def load_from_redis(cls, team_number: int): 
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number) 
        data = await r.json().get(redis_key)

        if data and isinstance(data, dict):  # now checking for a dictionary
            return cls(**data)
        else:
            return None

    async def reset(self, team_number: int): 
        self.state = "is_playing" 
        self.player_turn = "x" 
        self.positions = ["", "", "", "", "", "", "", "", ""] 
        await self.save_to_redis(team_number=team_number)
