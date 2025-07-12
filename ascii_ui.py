import asyncio
import os
import json
import sys
import websockets # used for WebSocket connection

WEBSOCKET_URL = "ws://ai.thewcl.com:8703"  #My WebSocket URL

async def listen_for_updates(): #listens for updates from the WebSocket server
    async with websockets.connect(WEBSOCKET_URL) as websocket: #connects to the WebSocket server
        print(f"Connected to {WEBSOCKET_URL}")
        async for message in websocket: #listens for updates from the WebSocket server
            try:
                data = json.loads(message) #parses the JSON string into a Python dictionary
                positions = data.get("positions") #tries to get the positions from the dictionary
                if positions and isinstance(positions, list) and len(positions) == 9: #checks if the positions are valid (if all three equals nine)
                    os.system('cls' if os.name == 'nt' else 'clear') #clears the screen 
                    draw_board(positions) #draws the board
                else: #if the positions are not valid
                    print("Invalid 'positions' data:", data) #prints the validation fails
            except json.JSONDecodeError: #catches any JSON parsing errors
                print("Received malformed JSON:", message) #shows the data received

def draw_board(positions): #draws the board to look like a Tic Tac Toe board
    def format_cell(pos, i): #formats the board
        return pos.upper() if pos.strip() else str(i) #returns the position if it is not empty, otherwise returns the index
    cells = [format_cell(pos, i) for i, pos in enumerate(positions)] #creates a list of cells for the number of positions
    print("\n")
    print(f" {cells[0]} | {cells[1]} | {cells[2]} ") #prints the first line of the board
    print("---+---+---")
    print(f" {cells[3]} | {cells[4]} | {cells[5]} ") #prints the second line of the board
    print("---+---+---")
    print(f" {cells[6]} | {cells[7]} | {cells[8]} ") #prints the third line of the board
    print("\n")

def test_draw_board(): 
    test_positions = ["x", "", "o", "", "x", "", "o", "", ""]
    os.system('cls' if os.name == 'nt' else 'clear')
    draw_board(test_positions)

if __name__ == "__main__": 
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_draw_board()
    else:
        asyncio.run(listen_for_updates())

#This architecture lets the UI stay simple. 
#The UI and backend are not tightly connected
#This is a decoupled system where the UI just displays whatever the backend sends
#This means that the UI could work with any backend with the same format