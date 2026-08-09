from enum import StrEnum

import socketio
import uvicorn
from app.services.matchmaker import Matchmaker
from app.services.game_service import GameService
from app.services.move_service import MoveService


sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

class EventArguments(StrEnum):
    MOVE = 'move'
    GAME_ID = 'game_id'


app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"🟢 Client connected: {sid}")
    await matchmaker.add_player(sid)

@sio.event
async def move(sid, data):
    game_id = data.get(EventArguments.GAME_ID)
    move = data.get(EventArguments.MOVE)
    game_session = game_service.get_game(game_id)
    fen = game_session.fen
    new_fen = MoveService.get_updated_fen(move, fen) 
    game_session.update_state(new_fen)
    sio.emit('game_state_update', game_session.get_state(), room=game_id)
    
@sio.event
async def disconnect(sid):
    print(f"🔴 Client disconnected: {sid}")

async def on_match_found(white_player_id, black_player_id):
    game_session = game_service.create_game(white_player_id, black_player_id)
    new_game_id = game_session.game_id
    await sio.enter_room(white_player_id, new_game_id)
    await sio.enter_room(black_player_id, new_game_id)
    await sio.emit('match_found', game_session.get_state(), room = new_game_id)
    print(f"Match found: {white_player_id} vs {black_player_id} in game {new_game_id}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

matchmaker = Matchmaker(on_match_found)
game_service = GameService()




