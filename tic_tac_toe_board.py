from dataclasses import dataclass, field
import redis #redis is a library that allows us to connect to a Redis database
from redis.commands.json.path import Path #redis commands are used to interact with the Redis database
import os #os is a library that allows us to access environment variables

r = redis.Redis( #redis connection
    host='ai.thewcl.com', #host
    port=6379, #port
    password=os.getenv("PASSWORD"), #password
    decode_responses=True #decode_responses=True means that the data will be decoded from bytes to strings
)

REDIS_KEY_TEMPLATE = "tic_tac_toe:game_state:{team_number}" #this is the template for my Redis keys and team_number can be replaced with any number

@dataclass
class TicTacToeBoard: 
    state: str = "is_playing" 
    player_turn: str = "x" 
    positions: list = field(default_factory=lambda: ["", "", "", "", "", "", "", "", ""])
  
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
    
    def serialize(self): #serialize turns the object into a JSON string
        return {
            "state": self.state, #game state key
            "player_turn": self.player_turn, #player turn key
            "positions": self.positions #positions key
        }
    
    def save_to_redis(self, team_number: int):
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number) #creates a new variable called redis key with the template
        board_data = self.serialize() #uses the serialize function to turn the object into a JSON string and store into board_data
        r.json().set(redis_key, Path("$"), board_data) #saves the board data to redis

    @classmethod #this is a class method, not an instance method
    def load_from_redis(cls, team_number: int): #we load the object from redis and since it is a class, instead of self, we use cls
        redis_key = REDIS_KEY_TEMPLATE.format(team_number=team_number) #creates a new variable called redis key with the template
        data = r.json().get(redis_key) #gets the data from the variable redis_key
        if data:
            return cls(**data) #returns the object if the data is not empty
        else:
            return None #returns None if the data is empty

    def reset(self, team_number: int): #resets the board
        self.state = "is_playing" #changes the state to is_playing again
        self.player_turn = "x" #changes the player turn to x again
        self.positions = ["", "", "", "", "", "", "", "", ""] #resets the positions again
        self.save_to_redis(team_number=team_number) #saves the board to redis

