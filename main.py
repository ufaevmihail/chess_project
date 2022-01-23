# This is a sample Python script.
import websockets
import asyncio
import json
import os
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



  # Press Ctrl+F8 to toggle the breakpoint.
class Game:
    is_started=False
    player1 = None
    player2 = None
    viewers =[]
    count = 0
    web_sockets={}
    on_connection=[]
    on_move=[]

    def __init__(self):
        self.events = [("connection",self.on_connection),("move",self.on_move)]
        self.on_connection.append(self.start_game)
        self.on_connection.append(self.on_new_game)
        self.on_move.append(self.move_done)

    async def new_game(self):
        self.count=0
        for ws in self.web_sockets.values():
            await ws.wait_closed()
        self.web_sockets={}

    async def listen(self,websocket):
        while websocket.open:
            try:
                msge = await websocket.recv()
            except websockets.exceptions.ConnectionClosedOK:
                self.count -= 1
                if self.count == 0:
                   await self.new_game()
                break
            message = json.loads(msge)
            for etype,list_handlers in self.events:
                if message["type"] == etype:
                    for handler in list_handlers:
                        await handler(websocket,message)

    async def start_game(self,websocket,message):
        if message['content']=="startgame":
            if self.count < 2:
                await websocket.send(json.dumps({"type":"startgame","content":"ok","user_id":self.count}))
            else:
                await websocket.send(json.dumps({"type":"startgame","content":"viewer","user_id":self.count}))
            self.web_sockets.update({self.count: websocket})
            self.count += 1

    async def on_new_game(self,websocket,message):
        if message["content"]=="newgame":
            self.new_game()

    async def move_done(self,websocket,message):
        id = message["user_id"]
        websocket = self.web_sockets[id]
        for identifier,ws in self.web_sockets.items():
            if identifier != id:
                await ws.send(json.dumps({"type":"move_done","content":"","startfield":message['startfield'],
                                    'endfield':message['endfield'],'user_id':id,"swt":message["swt"]}))


async def main():
    async with websockets.serve(game.listen, "localhost", port) as server:
        await asyncio.Future()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8001"))
    game = Game()
    asyncio.run(main())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
