from tic_tac_toe_board import TicTacToeBoard 
import argparse 
import redis.asyncio as aioredis
import asyncio
import os

CHANNEL_NAME = "tictactoe_game_state_changed" 

async def handle_board_state(i_am_playing: str, redis_client): 
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
    if board is None: #checks if the board did not load, and reminds the user to use reset
        print("No saved board found. Did you forget to --reset?") 
        return
    if board.state == "winner_decided": #always check for winner after loading
        print("Game Over, winner is", board.winner)
        return
    elif board.state == "draw":
        print("Game Over, it is a draw")
        return
    if board.is_my_turn(i_am_playing): #checks if it is my turn
        try:
            index = int(input(f"{i_am_playing}'s move (0–8): ")) #asks for a move and turns the number into an integer
            result = board.make_move(index) #get the result dict
            print(result["message"]) #prints the message from the result dict
            
            if result["success"]: #if the move was successful
                if board.state == "winner_decided": #if the game is over
                    await board.save_to_redis(team_number=1) #save the board
                    await redis_client.publish(CHANNEL_NAME, "board_updated") #publish the board
                    print(f"Game Over, winner is {board.winner}") #show the winner
                    return
                elif board.state == "draw": #if the game is a draw
                    await board.save_to_redis(team_number=1) #save the board
                    await redis_client.publish(CHANNEL_NAME, "board_updated") #publish the board
                    print("Game Over, it is a draw") #show the draw message
                    return
                await board.save_to_redis(team_number=1) #save the board
                await redis_client.publish(CHANNEL_NAME, "board_updated") #publish the board
                #show updated board after successful move
                import json
                print(json.dumps(board.to_dict(), indent=2)) #show the updated board

        except ValueError:
            print("Invalid input. Please enter a number from 0 to 8.") #when the number is invalid, it will print this
    else:
        print(f"Waiting for {board.player_turn} to move...") #wait for the other player to move


async def listen_for_updates(i_am_playing: str): 
    redis_client = aioredis.Redis( 
        host='ai.thewcl.com', 
        port=6379,
        password=os.getenv("PASSWORD"), 
        decode_responses=True 
    )
    pubsub = redis_client.pubsub() 
    await pubsub.subscribe(CHANNEL_NAME) 
    await handle_board_state(i_am_playing, redis_client) 
    async for message in pubsub.listen(): 
        if message["type"] == "message": 
            await handle_board_state(i_am_playing, redis_client) 

async def main(): 
    if args.reset: 
        board = TicTacToeBoard() 
        await board.reset(team_number=1)  
        print("Board reset.")
        return
    print("Time to play Tic Tac Toe!") 
    await listen_for_updates(args.player) 

parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI")
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True) 
parser.add_argument("--reset", action="store_true", help="Reset the game board")
args = parser.parse_args() 

if __name__ == "__main__": 
    asyncio.run(main())