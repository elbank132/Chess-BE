class MoveService:

    @staticmethod
    def get_updated_fen(move: str, fen: str) -> str:
        if not MoveService.is_valid_move(move, fen):
            raise ValueError("Invalid move")
            
        board = MoveService.turn_fen_to_board(fen)
        move_start, move_end = MoveService.parse_move(move)
        piece = board[move_start[0]][move_start[1]]
        
        fen_parts = fen.split(' ')
        turn = fen_parts[1]
        castling = fen_parts[2] if len(fen_parts) > 2 else "-"
        halfmove = int(fen_parts[4]) if len(fen_parts) > 4 else 0
        fullmove = int(fen_parts[5]) if len(fen_parts) > 5 else 1
        
        is_capture = MoveService.execute_move_on_board(board, move, move_start, move_end, turn)
        is_pawn_move = piece.lower() == 'p'
        
        new_board_fen = MoveService.turn_board_to_fen(board)
        new_castling = MoveService.update_castling_rights(castling, piece, move_start, move_end)
        new_ep_target = MoveService.get_new_en_passant_target(piece, move_start, move_end)
        new_turn, new_halfmove, new_fullmove = MoveService.update_clocks(turn, halfmove, fullmove, is_pawn_move, is_capture)
        
        return f"{new_board_fen} {new_turn} {new_castling} {new_ep_target} {new_halfmove} {new_fullmove}"

    

    @staticmethod
    def execute_move_on_board(board: list[list[str]], move: str, move_start: tuple[int, int], move_end: tuple[int, int], turn: str) -> bool:
        start_row, start_col = move_start
        end_row, end_col = move_end
        piece = board[start_row][start_col]
        target_piece = board[end_row][end_col]
        is_capture = target_piece != '.'
        is_pawn_move = piece.lower() == 'p'
        
        if is_pawn_move and target_piece == '.' and start_col != end_col:
            board[start_row][end_col] = '.' 
            is_capture = True
        elif piece.lower() == 'k' and abs(start_col - end_col) == 2:
            if end_col == 6:  
                board[end_row][5] = board[end_row][7]
                board[end_row][7] = '.'
            elif end_col == 2: 
                board[end_row][3] = board[end_row][0]
                board[end_row][0] = '.'
        elif is_pawn_move and len(move) == 5:
            promo_char = move[4]
            piece = promo_char.upper() if turn == 'w' else promo_char.lower()
            
        board[end_row][end_col] = piece
        board[start_row][start_col] = '.'
        
        return is_capture


    @staticmethod
    def turn_board_to_fen(board: list[list[str]]) -> str:
        fen_rows = []
        for row in board:
            empty_count = 0
            fen_row = ""
            for char in row:
                if char == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += char
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        return "/".join(fen_rows)


    @staticmethod
    def update_castling_rights(current_castling: str, piece: str, move_start: tuple[int, int], move_end: tuple[int, int]) -> str:
        if current_castling == '-':
            return '-'
            
        new_castling = current_castling
        
        if piece == 'K': new_castling = new_castling.replace('K', '').replace('Q', '')
        elif piece == 'k': new_castling = new_castling.replace('k', '').replace('q', '')
        
        rook_starts = {(7, 7): 'K', (7, 0): 'Q', (0, 7): 'k', (0, 0): 'q'}
        if move_start in rook_starts:
            new_castling = new_castling.replace(rook_starts[move_start], '')
        if move_end in rook_starts:
            new_castling = new_castling.replace(rook_starts[move_end], '')
            
        return new_castling if new_castling else '-'


    @staticmethod
    def get_new_en_passant_target(piece: str, move_start: tuple[int, int], move_end: tuple[int, int]) -> str:
        if piece.lower() == 'p' and abs(move_start[0] - move_end[0]) == 2:
            target_row = (move_start[0] + move_end[0]) // 2
            target_col_char = chr(move_start[1] + ord('a'))
            target_row_char = str(8 - target_row)
            return f"{target_col_char}{target_row_char}"
        return '-'


    @staticmethod
    def update_clocks(turn: str, halfmove: int, fullmove: int, is_pawn_move: bool, is_capture: bool) -> tuple[str, int, int]:
        new_halfmove = 0 if is_pawn_move or is_capture else halfmove + 1
        new_fullmove = fullmove + 1 if turn == 'b' else fullmove
        new_turn = 'b' if turn == 'w' else 'w'
        return new_turn, new_halfmove, new_fullmove

    @staticmethod
    def is_valid_move(move: str, fen: str) -> bool:
        board = MoveService.turn_fen_to_board(fen)
        move_start, move_end = MoveService.parse_move(move)
        
        fen_parts = fen.split(' ')
        turn = fen_parts[1]
        castling_rights = fen_parts[2] if len(fen_parts) > 2 else "-"
        en_passant_target = fen_parts[3] if len(fen_parts) > 3 else "-"

        if not MoveService.check_starting_square(board, move_start, turn):
            return False
        if not MoveService.check_target_square(board, move_end, turn):
            return False

        piece_char = board[move_start[0]][move_start[1]]

        if not MoveService.is_piece_move_valid(piece_char, move_start, move_end, board, en_passant_target, castling_rights):
            return False

        if not MoveService.is_promotion_valid(move, piece_char, move_end):
            return False
            
        if not MoveService.is_king_safe_after_move(board, move_start, move_end, piece_char, turn):
            return False
        
        return True
    
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
    def is_piece_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]], en_passant_fen: str = "-", castling_fen: str = "-") -> bool:
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
            return MoveService.is_king_move_valid(piece, start, end, board, castling_fen)
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
    def is_king_move_valid(piece: str, start: tuple[int, int], end: tuple[int, int], board: list[list[str]], castling_fen: str) -> bool:
        row_diff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])
        
        if row_diff <= 1 and col_diff <= 1:
            return True
            
        if row_diff == 0 and col_diff == 2:
            

            if piece == 'K' and start == (7, 4):
                if end[1] == 6 and 'K' in castling_fen: 
                    return board[7][5] == '.' and board[7][6] == '.'
                if end[1] == 2 and 'Q' in castling_fen: 
                    return board[7][1] == '.' and board[7][2] == '.' and board[7][3] == '.'
                    

            elif piece == 'k' and start == (0, 4):
                if end[1] == 6 and 'k' in castling_fen: 
                    return board[0][5] == '.' and board[0][6] == '.'
                if end[1] == 2 and 'q' in castling_fen: 
                    return board[0][1] == '.' and board[0][2] == '.' and board[0][3] == '.'
                    
        return False


    @staticmethod
    def is_promotion_valid(move: str, piece_char: str, move_end: tuple[int, int]) -> bool:
        if piece_char.lower() == 'p':
            is_promotion_rank = (move_end[0] == 0) or (move_end[0] == 7)
            has_promotion_char = len(move) == 5
            
            if is_promotion_rank and not has_promotion_char:
                return False  
            if not is_promotion_rank and has_promotion_char:
                return False 
                
        elif len(move) == 5:
            return False  
            
        return True


    @staticmethod
    def is_square_attacked(board: list[list[str]], target_square: tuple[int, int], attacker_turn: str) -> bool:
        target_row, target_col = target_square

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == '.':
                    continue
                
                is_white_piece = piece.isupper()
                if (attacker_turn == 'w' and not is_white_piece) or (attacker_turn == 'b' and is_white_piece):
                    continue
                
                piece_type = piece.lower()
                start = (row, col)
                
                if piece_type == 'p':
                    if attacker_turn == 'w':
                        direction = -1
                    else:
                        direction = 1
                    if target_row == row + direction and abs(target_col - col) == 1:
                        return True
                        
                elif piece_type == 'n':
                    if MoveService.is_knight_move_valid(piece, start, target_square, board):
                        return True
                        
                elif piece_type == 'r':
                    if MoveService.is_rook_move_valid(piece, start, target_square, board):
                        return True
                        
                elif piece_type == 'b':
                    if MoveService.is_bishop_move_valid(piece, start, target_square, board):
                        return True
                        
                elif piece_type == 'q':
                    if MoveService.is_queen_move_valid(piece, start, target_square, board):
                        return True
                        
                elif piece_type == 'k':
                    if abs(row - target_row) <= 1 and abs(col - target_col) <= 1:
                        return True
                        
        return False
    

    @staticmethod
    def is_king_safe_after_move(board: list[list[str]], move_start: tuple[int, int], move_end: tuple[int, int], piece_char: str, turn: str) -> bool:
        enemy_turn = 'b' if turn == 'w' else 'w'

        if piece_char.lower() == 'k' and abs(move_start[1] - move_end[1]) == 2:
            if MoveService.is_square_attacked(board, move_start, enemy_turn):
                return False 
            
            pass_col = (move_start[1] + move_end[1]) // 2
            if MoveService.is_square_attacked(board, (move_start[0], pass_col), enemy_turn):
                return False 

        temp_board = [row[:] for row in board] 
        temp_board[move_end[0]][move_end[1]] = piece_char
        temp_board[move_start[0]][move_start[1]] = '.'
        
        king_char = 'K' if turn == 'w' else 'k'
        king_pos = None
        for r in range(8):
            for c in range(8):
                if temp_board[r][c] == king_char:
                    king_pos = (r, c)
                    break
            if king_pos: 
                break
                
        if king_pos and MoveService.is_square_attacked(temp_board, king_pos, enemy_turn):
            return False

        return True