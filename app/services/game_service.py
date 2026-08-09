from typing import Dict, Optional, Tuple
from enum import Enum
import uuid

class Status(Enum):
    ACTIVE = 1
    CHECKMATE = 2
    STALEMATE = 3
    DRAW = 4
    RESIGNED = 5
    INSUFFICIENT_MATERIAL = 6

class GameSession:
    """Represents a single active chess match stored in RAM."""
    def __init__(self, game_id: str, white_player_id: str, black_player_id: str):
        self.game_id = game_id
        self.white_player_id = white_player_id
        self.black_player_id = black_player_id
        self.status = Status.ACTIVE
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0"  # Placeholder for the FEN string representing the board state

    def update_state(self, new_fen: str):
        self.fen = new_fen
        self.update_status()

    def get_state(self) -> dict:
        """Returns the current state to send to the frontend."""
        return {
            "game_id": self.game_id,
            "fen": self.fen,
            "status": self.status.value
        }

    def update_status(self):
        return Status.ACTIVE  # Placeholder for actual game status update logic


class GameService:
    def __init__(self):
        self._active_games: Dict[str, GameSession] = {}

    def create_game(self, white_player_id: str, black_player_id: str) -> GameSession:
        game_uuid = uuid.uuid4()
        game_id = str(game_uuid)
        game_session = GameSession(game_id, white_player_id, black_player_id)
        self._active_games[game_id] = game_session
        return game_session

    def get_game(self, game_id: str) -> Optional[GameSession]:
        game = self._active_games.get(game_id)
        if game:
            return game
        
        raise ValueError(f"Game with ID {game_id} not found.")

    