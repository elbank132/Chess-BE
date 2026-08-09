class MoveService:

    @staticmethod
    def get_updated_fen(move: str, fen: str) -> str:
        # Placeholder for actual move validation logic
        if not MoveService.is_valid_move(move, fen):
            raise ValueError("Invalid move")
        return fen  # Placeholder for actual updated FEN

    @staticmethod
    def is_valid_move(move: str , fen: str) -> bool:
        return True  # Placeholder for actual move validation logic