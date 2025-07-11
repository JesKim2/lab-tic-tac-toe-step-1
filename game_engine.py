from tic_tac_toe_board import TicTacToeBoard 
import argparse 
import redis.asyncio as aioredis
import asyncio
import os

CHANNEL_NAME = "tictactoe_game_state_changed" #we created a channel name for pub/sub

async def handle_board_state(i_am_playing: str, redis_client): 
    board = await TicTacToeBoard.load_from_redis(team_number=1) #loads the board from redis
    if board is None: #checks if the board did not load, and reminds the user to use reset
        print("No saved board found. Did you forget to --reset?") 
        return
    if board.state == "winner_decided": # always check for winner after loading
        print("Game Over, winner is", board.winner)
        return
    elif board.state == "draw":
        print("Game Over, it is a draw")
        return
    if board.is_my_turn(i_am_playing): #checks if it is my turn
        try:
            index = int(input(f"{i_am_playing}'s move (0–8): ")) #asks for a move and turns the number into an integer
            board.make_move(index) #inputs the integer above into make_move
            if board.state == "winner_decided": #moved the winner check here
                await board.save_to_redis(team_number=1)  # SAVE
                await redis_client.publish(CHANNEL_NAME, "board_updated")
                print("Game Over, winner is", board.winner)
                return
            elif board.state == "draw": #moved the draw check here
                await board.save_to_redis(team_number=1)  # SAVE
                await redis_client.publish(CHANNEL_NAME, "board_updated")
                print("Game Over, it is a draw") 
                return 
            await board.save_to_redis(team_number=1)  # saves board to redis
            await redis_client.publish(CHANNEL_NAME, "board_updated") #publishes the board to redis
        except ValueError:
            print("Invalid input. Please enter a number from 0 to 8.") #when the number is invalid, it will print this

async def listen_for_updates(i_am_playing: str): #Connects to Redis, subscribes to channel, calls handle_board_state 
    redis_client = aioredis.Redis( #Connects to Redis
        host='ai.thewcl.com', 
        port=6379,
        password=os.getenv("PASSWORD"), 
        decode_responses=True 
    )
    pubsub = redis_client.pubsub() #creates an object to handle Pub/Sub
    await pubsub.subscribe(CHANNEL_NAME) #subscribes to the channel to listen for messages (await pauses until subscription is complete)
    await handle_board_state(i_am_playing, redis_client) #calls handle_board_state
    async for message in pubsub.listen(): #waits for messages
        if message["type"] == "message": #checks if the message is a message
            await handle_board_state(i_am_playing, redis_client) #calls handle_board_state again

async def main(): 
    if args.reset: #reset is handled here, also talked about in last video
        board = TicTacToeBoard() 
        await board.reset(team_number=1)  # await added for reset
        print("Board reset.")
        return
    print("Time to play Tic Tac Toe!") 
    await listen_for_updates(args.player) #calls listen_for_updates

#below is the argparse code for player and reset, but we've already covered this last video
parser = argparse.ArgumentParser(description="Tic Tac Toe Game CLI")
parser.add_argument("--player", choices=["x", "o"], help="Which player you are", required=True) #we have player required to be true here
parser.add_argument("--reset", action="store_true", help="Reset the game board")
args = parser.parse_args() 

if __name__ == "__main__": 
    asyncio.run(main())