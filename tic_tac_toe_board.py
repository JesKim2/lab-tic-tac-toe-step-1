from dataclasses import dataclass, field

@dataclass
class TicTacToeBoard: #the blueprint (class)
    state: str = "is_playing" # game is still on-going
    player_turn: str = "x" 
    positions: list = field(default_factory=lambda: ["", "", "", "", "", "", "", "", ""]) # 3 x 3 grid
  
    def is_my_turn(self, i_am: str) -> bool:
        if i_am == self.player_turn: 
            return True
        else:
            return False
        
    def make_move(self, index: int): #Player makes a move
        if self.state != "is_playing":
            print("Game is not playing")
            return
        if index < 0 or index > 8: #Invalid index
            print("Invalid index")
            return
        if self.positions[index] != "": #Position already taken
            print("Position already taken")
            return
        print("Player", self.player_turn, "is making a move") #This will run only if it clears everything else above
        self.positions[index] = self.player_turn
        print(self.positions)
        self.check_winner() #Check if there is a winner
        self.check_draw() #Check if there is a draw
        if self.state == "is_playing":
            self.switch_turn() #Switch player turn after move is made  
            
    def check_winner(self):
        winning_lines = [ #All the possible winning lines 
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
            a, b, c = line    # each letter is an index placeholder
            if self.positions[a] != "" and self.positions[a] == self.positions[b] == self.positions[c]: # replace each letter with a winning line number
                self.state = "winner_decided"
                return self.positions[a]
        return None            #If the above if statement did not happen, then report None
    
    def check_draw(self): #If there are no spaces and there is no winner
        if "" not in self.positions and self.check_winner() is None: 
            self.state = "draw"
            print("It is a draw")
            return True
        return False       #If the above if statement did not happen, then report false
    
    def switch_turn(self):
        if self.player_turn == "x":
            self.player_turn = "o"
        else:
            self.player_turn = "x"
    
board = TicTacToeBoard() #This is an instance of the class where board is an object

    

    
    
   