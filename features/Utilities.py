


import chess_app
import chess.pgn
import math
import psycopg2

# Utility functions
class Utilities:
    @staticmethod
    def is_endgame(board):
        white_pieces = sum(1 for piece in board.piece_map().values() if piece.color == chess_app.WHITE and piece.piece_type not in [chess_app.PAWN, chess_app.KING])
        black_pieces = sum(1 for piece in board.piece_map().values() if piece.color == chess_app.BLACK and piece.piece_type not in [chess_app.PAWN, chess_app.KING])

        return white_pieces + black_pieces <= 6
    
    @staticmethod
    def is_retreating_from_attack(board, fromSq, toSq, movingPiece):
        if movingPiece.piece_type in [chess_app.PAWN, chess_app.KING]:
            return False
        
        attackers = board.attackers(not movingPiece.color, fromSq)
        if not attackers:
            return False

        def square_distance(sq1, sq2):
            file_distance = abs(chess_app.square_file(sq1) - chess_app.square_file(sq2))
            rank_distance = abs(chess_app.square_rank(sq1) - chess_app.square_rank(sq2))
            return math.sqrt(file_distance**2 + rank_distance**2)
        
        current_distances = [square_distance(fromSq, attacker) for attacker in attackers]
        new_distances = [square_distance(toSq, attacker) for attacker in attackers]
        
        return current_distances < new_distances

    @staticmethod
    def get_prev_n_moves(board, n):
        prevMoves = []
        if n > len(board.move_stack):
            return prevMoves 
        
        for _ in range(min(n, len(board.move_stack))):
            move = board.pop()
            prevMoves.append(move)

        prevMoves.reverse()
        for move in prevMoves:
            board.push(move)

        return prevMoves