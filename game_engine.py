from tic_tac_toe_board import TicTacToeBoard #imports the class
import argparse #argparse is a library that allows us to parse command line arguments
import time

#helper function to make sure input is valid
def get_valid_move(player_symbol): #player_symbol is x or o
    while True:
        move_input = input(f"{player_symbol}'s move: Enter a position (0–8): ") #asks for input
        if move_input.isdigit(): #checks if the input is a digit
            index = int(move_input)
            if 0 <= index <= 8: #checks if the input is between 0 and 8
                return index
        print("Invalid input. Please enter a number from 0 to 8.")

parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI") #parser is an object that will parse the command line arguments
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True) #player can be x or o
parser.add_argument("--reset", action="store_true", help="Reset the game board") #reset the game board if the flag is there
args = parser.parse_args() #args is an object that will store the command line arguments

if args.reset: #if the reset flag is there
    board = TicTacToeBoard() #new object
    board.reset(team_number=1) #resets the board
    print("Board reset.")
    exit()

board = TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
if board is None: #if the board is not found
    print("No saved board found. Did you forget to --reset?") #tells the user to reset the board
    exit()

print("Time to play Tic-Tac-Toe!")
player_symbol = args.player #player decides whether they are x or o
if player_symbol == "x":
    opponent_symbol = "o"
else:
    player_symbol = "o"
    opponent_symbol = "x"

while board.state == "is_playing": #repeats until game is over
    board = TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
    if player_symbol == board.player_turn: #if it is the player's turn player can make a move
        index = get_valid_move(player_symbol) #asks for input
        board.make_move(index) #makes the move
        board.save_to_redis(team_number=1) #saves the board to redis
    else:
        print(f"Waiting... it's {board.player_turn}'s turn.") #instead of crashing, it just informs and waits
        time.sleep(3)
    
    if board.state == "winner_decided": #if there is a winner
        print("Game Over, winner is", board.check_winner())
        break
    elif board.state == "draw": #if there is a draw
        print("Game Over, it is a draw")
        break