import tic_tac_toe_board #imports the class

board = tic_tac_toe_board.TicTacToeBoard() #new object

print("Time to play Tic-Tac-Toe!")
player_symbol = input("Who are you (x or o)?") #player decides whether they are x or o
if player_symbol == "x":
    opponent_symbol = "o"
else:
    opponent_symbol = "x"

while board.state == "is_playing": #repeats until game is over
    if player_symbol == board.player_turn: #if it is the player's turn player can make a move
        index =int(input("Enter board position: "))
        board.make_move(index)    
    else:
        index = int(input(f"{opponent_symbol}'s move: Enter a position (0–8): ")) #if it is not the player's turn, they cannot make a move
        board.make_move(index)
    
    if board.state == "winner_decided": #if there is a winner
        print("Game Over, winner is", board.check_winner())
        break
    elif board.state == "draw": #if there is a draw
        print("Game Over, it is a draw")
        break