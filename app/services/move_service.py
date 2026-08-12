class MoveService:

    @staticmethod
    def get_updated_fen(move: str, fen: str) -> str:
        # Placeholder for actual move validation logic
        if not MoveService.is_valid_move(move, fen):
            raise ValueError("Invalid move")
        return fen  # Placeholder for actual updated FEN

    @staticmethod
    def is_valid_move(move: str , fen: str) -> bool:
        board = MoveService.turn_fen_to_board(fen)
        move_start, move_end = MoveService.parse_move(move)
        turn = fen.split(' ')[1]  
        if not MoveService.check_starting_square(board, move_start, turn):
            return False
        
        return True  # Placeholder for actual move validation logic
    
    @staticmethod
    def turn_fen_to_board(fen: str) -> list[list[str]]: #maybe board should be a class instead of static method
        rows = fen.split(' ')[0].split('/')
        board = []
        for row in rows:
            board_row = []
            for char in row:
                if char.isdigit():
                    board_row.extend(['.'] * int(char)) 
                else:
                    board_row.append(char)
            board.append(board_row)
        return board

    @staticmethod
    def parse_move(move: str) -> tuple[tuple[int, int], tuple[int, int]]:
        if len(move) != 4:
            raise ValueError("Invalid move format")
        start_col = ord(move[0]) - ord('a')
        start_row = 8 - int(move[1])
        end_col = ord(move[2]) - ord('a')
        end_row = 8 - int(move[3])
        return (start_row, start_col), (end_row, end_col)

    @staticmethod
    def check_starting_square(board: list[list[str]], start: tuple[int, int], turn: str) -> bool:
        piece = board[start[0]][start[1]]
        if turn == 'w' and piece.isupper():
            return True
        elif turn == 'b' and piece.islower():
            return True
        return False