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
        fen_parts = fen.split(' ')
        turn = fen_parts[1]
        en_passant_target = fen_parts[3] if len(fen_parts) > 3 else "-"

        if not MoveService.check_starting_square(board, move_start, turn):
            return False
        if not MoveService.check_target_square(board, move_end, turn):
            return False

        
        

        piece_char = board[move_start[0]][move_start[1]]
        if not MoveService.is_piece_move_valid(piece_char, move_start, move_end, board, en_passant_target):
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
        if len(move) not in [4, 5]:
            raise ValueError("Invalid move format.")

        start_file, start_rank, end_file, end_rank = move[0], move[1], move[2], move[3]
        
        if start_file < 'a' or start_file > 'h' or end_file < 'a' or end_file > 'h':
            raise ValueError("Move file must be between a and h")
        if start_rank < '1' or start_rank > '8' or end_rank < '1' or end_rank > '8':
            raise ValueError("Move rank must be between 1 and 8")
            
        if len(move) == 5 and move[4].lower() not in ['q', 'r', 'b', 'n']:
            raise ValueError("Invalid promotion piece.")

        start_col = ord(start_file) - ord('a')
        start_row = 8 - int(start_rank)
        end_col = ord(end_file) - ord('a')
        end_row = 8 - int(end_rank)
        
        return (start_row, start_col), (end_row, end_col)

    @staticmethod
    def check_starting_square(board: list[list[str]], start: tuple[int, int], turn: str) -> bool:
        piece = board[start[0]][start[1]]
        if turn == 'w' and piece.isupper():
            return True
        elif turn == 'b' and piece.islower():
            return True
        return False

    @staticmethod
    def check_target_square(board: list[list[str]], end: tuple[int, int], turn: str) -> bool:
        piece = board[end[0]][end[1]]
        if piece == '.':
            return True
        if turn == 'w' and piece.islower():
            return True
        elif turn == 'b' and piece.isupper():
            return True
        return False


    @staticmethod
    def is_piece_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]], en_passant_fen: str = "-") -> bool:
        if piece.lower() == 'p':
            return MoveService.is_pawn_move_valid(piece, start, end, board, en_passant_fen)
        if piece.lower() == 'r':
            return MoveService.is_rook_move_valid(piece, start, end, board)
        if piece.lower() == 'n':
            return MoveService.is_knight_move_valid(piece, start, end, board)
        if piece.lower() == 'b':
            return MoveService.is_bishop_move_valid(piece, start, end, board)
        if piece.lower() == 'q':
            return MoveService.is_queen_move_valid(piece, start, end, board)
        if piece.lower() == 'k':
            return MoveService.is_king_move_valid(piece, start, end, board)
        raise ValueError("Unknown piece type")
    
    @staticmethod
    def is_pawn_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]], en_passant_fen: str = "-") -> bool:
        if start == end:
            return False
            
        direction = 1 if piece.islower() else -1  
        start_row, start_col = start
        end_row, end_col = end
        
        if start_col == end_col:  
            if end_row == start_row + direction and board[end_row][end_col] == '.':
                return True
            if (start_row == 1 and piece.islower()) or (start_row == 6 and piece.isupper()): 
                if end_row == start_row + 2 * direction and board[start_row + direction][start_col] == '.' and board[end_row][end_col] == '.':
                    return True
                    
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:
            target_piece = board[end_row][end_col]
            if target_piece != '.':
                return True
                
            if en_passant_fen != '-':
                en_col = ord(en_passant_fen[0]) - ord('a')
                en_row = 8 - int(en_passant_fen[1])
                
                if end_row == en_row and end_col == en_col:
                    return True

        return False

    @staticmethod
    def is_rook_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]]) -> bool:
        if start == end:
            return False
        if start[0] != end[0] and start[1] != end[1]:  # straight line check
            return False 
        # Check if path is clear
        if start[0] == end[0]:  # Horizontal move
            step = 1 if end[1] > start[1] else -1
            for col in range(start[1] + step, end[1], step):
                if board[start[0]][col] != '.':
                    return False
        else:  # Vertical move
            step = 1 if end[0] > start[0] else -1
            for row in range(start[0] + step, end[0], step):
                if board[row][start[1]] != '.':
                    return False
        return True

    @staticmethod
    def is_knight_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]]) -> bool:
        row_diff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])
        if row_diff == 2 and col_diff == 1:
            return True
        if row_diff == 1 and col_diff == 2:
            return True
        return False
    
    @staticmethod
    def is_bishop_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]]) -> bool:
        if start == end:
            return False
        if abs(start[0] - end[0]) != abs(start[1] - end[1]):  # Diagonal move check
            return False
        row_step = 1 if end[0] > start[0] else -1
        col_step = 1 if end[1] > start[1] else -1
        row, col = start[0] + row_step, start[1] + col_step
        while (row, col) != end:
            if board[row][col] != '.':
                return False
            row += row_step
            col += col_step
        return True
        

    @staticmethod
    def is_queen_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]]) -> bool:
        return (
            MoveService.is_rook_move_valid(piece, start, end, board)
            or MoveService.is_bishop_move_valid(piece, start, end, board)
        )

    @staticmethod
    def is_king_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]]) -> bool:
        return True  # Placeholder for actual king move validation logic 