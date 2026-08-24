import os
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
    GAME_ID = 'gameId'


app = socketio.ASGIApp(sio)

async def on_match_found(white_player_id, black_player_id):
    game_session = game_service.create_game(white_player_id, black_player_id)
    new_game_id = str(game_session.game_id)
    
    await sio.enter_room(white_player_id, new_game_id)
    await sio.enter_room(black_player_id, new_game_id)
    await sio.emit('match_found', game_session.get_match_found_message(), room = new_game_id)
    print(f"Match found: {white_player_id} vs {black_player_id} in game {new_game_id}")


matchmaker = Matchmaker(on_match_found)
game_service = GameService()

@sio.event
async def connect(sid, environ):
    print(f"🟢 Client connected: {sid}")
    await matchmaker.add_player(sid)

@sio.event
async def move(sid, data):
    game_id = str(data.get(EventArguments.GAME_ID))
    move_str = data.get(EventArguments.MOVE)
    
    game_session = game_service.get_game(game_id)
    
    if not game_session:
        return
        
    fen = game_session.fen
    
    try:
        new_fen = MoveService.get_updated_fen(move_str, fen) 
        game_session.update_state(new_fen)
        await sio.emit('game_state_update', game_session.get_state(), room=game_id)
        
    except ValueError as e:
        await sio.emit('invalid_move', {'message': str(e)}, to=sid)
    
@sio.event
async def disconnect(sid):
    print(f"🔴 Client disconnected: {sid}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)