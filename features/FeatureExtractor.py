import chess_app
import chess.pgn
import chess.polyglot
from Utilities import Utilities
from ScoreCalculator import ScoreCalculator

class FeatureExtractor:
    def __init__(self, game, openingLength):
        self.game = game
        self.board = game.board()
        self.openingLength = openingLength
        self.openingLengthFull = openingLength/2 # Fullmove count, not single move
        self.features = {
            # Used for Both Scores
            "whitePawnBreaks": 0,
            "blackPawnBreaks": 0,
            "whiteAttacks": 0,
            "blackAttacks": 0,

            
            # Used for Aggro Score
            "whiteInfiltrations": 0,
            "blackInfiltrations": 0,
            "whiteKingAttacks": 0,
            "blackKingAttacks": 0,
            "whiteXrayAttacks": 0,
            "blackXrayAttacks": 0,
            "whitePawnStorms": 0,
            "blackPawnStorms": 0,
            # Aggro Penalties
            "whiteRetreats": 0,
            "blackRetreats": 0,
            "whitePatientMoves": 0,
            "blackPatientMoves": 0,
            
            # Used for Activity Score
            "whitePieceMoves": 0,
            "blackPieceMoves": 0,
            "whiteActiveDefense": 0,
            "blackActiveDefense": 0,
            "whiteCentralControl": 0,
            "blackCentralControl": 0,
            "whiteSpaceAdvantage": 0,
            "blackSpaceAdvantage": 0,
            "whitePiecesAtHome": 0,
            "blackPiecesAtHome": 0,
            

            # Usefulness determines preference for early castling
            "whiteCastleTurn": 0,
            "blackCastleTurn": 0,

        }

        
    def extract_features(self):
        openingActivityScores = []
        openingAggressionScores = []
        
        midActivityScores = []
        midAggressionScores = []
        
        num = 0
        zobristHashOpening = 0
        
        for move in self.game.mainline_moves():
            if Utilities.is_endgame(self.board):
                break
            halfMoveCt = len(self.board.move_stack)
            fromSq = move.from_square
            toSq = move.to_square
            movingPiece = self.board.piece_at(fromSq)
            attackedBefore = self.board.attacks(fromSq)

            isRetreat = Utilities.is_retreating_from_attack(self.board, fromSq, toSq, movingPiece)
            isCheck = self.board.gives_check(move)
            isCastling = self.board.is_castling(move)
            isCapture = self.board.is_capture(move)
            
            # Flag for PatientMoves, if a move attacks something or actively defends something -> it isn't patient
            isActiveMove = False
            
            # Flag for Attacks, if a pawnbreak occurs -> it shouldn't be double counted as an attack
            isPawnBreak = False
            
            # Only required for methods that measure capture outcome
            targetPiece = self.board.piece_at(toSq) if isCapture else None
            defendedSq = chess_app.SquareSet(self.board.attacks(toSq)) if isCapture else None
                
            # Flag to count retreats and not double count a retreat as a patient move b/c retreats are forced
            if isRetreat:
                self._increment_feature("whiteRetreats" if movingPiece.color == chess_app.WHITE else "blackRetreats")
            
            if isCastling:
                if movingPiece.color == chess_app.WHITE:
                    self.features["whiteCastleTurn"] = self.board.fullmove_number
                else:
                    self.features["blackCastleTurn"] = self.board.fullmove_number
            
            self.board.push(move)
                        
            # Get attacked squares after the move is pushed            
            attackedSq = self.board.attacks(toSq)
            

            # Count features of the move and update flag values accordingly
            isPawnBreak = self._count_pawn_breaks(self.board, movingPiece, attackedSq, isPawnBreak)
            isActiveMove = self._count_unique_attacks(self.board, movingPiece, attackedBefore, attackedSq, isPawnBreak, isActiveMove)
            self._count_infiltrations(movingPiece, toSq, fromSq)
            self._count_king_attacks(movingPiece, isCheck, targetPiece, defendedSq, attackedSq)
            self._count_xray_attacks(self.board, toSq, movingPiece.color, movingPiece)
            self._count_piece_movement(movingPiece)
            isActiveMove = self._count_active_defends(self.board, movingPiece, attackedSq, attackedBefore, isActiveMove)
            self._count_patient_moves(isCapture, movingPiece, isActiveMove, isRetreat)
            
            # Sliding Window for central control and space advantage
            if halfMoveCt == self.openingLength:
                
                self._calculate_central_control(self.board)
                self._calculate_space_advantage(self.board)
                
                self._count_pieces_at_home(self.board)

                calc = ScoreCalculator(self.features)
                
                openingActivityScores.append(calc.activity_score())
                openingAggressionScores.append(calc.aggression_score())
                
                zobristHashOpening = chess_app.polyglot.zobrist_hash(self.board)
                print(self.board)

                self._reset_features_for_mid()
            
            elif halfMoveCt > self.openingLength:
            # Sliding window to calculate average central control every 2 full moves after opening
                if halfMoveCt % 4 == 0:
                    num+=1
                    self._calculate_central_control(self.board)
                    self._calculate_space_advantage(self.board)
            
                # Sliding window to detect pawn storms every 3 full moves
                if halfMoveCt >= self.openingLength + 6 or (6 < halfMoveCt < self.openingLength):
                    prevMoves = Utilities.get_prev_n_moves(self.board, 6)
                    if movingPiece.color == chess_app.WHITE and self._detect_pawn_storm(self.board, movingPiece.color, prevMoves):
                        self._increment_feature("whitePawnStorms")
                    elif movingPiece.color == chess_app.BLACK and self._detect_pawn_storm(self.board, movingPiece.color, prevMoves):
                        self._increment_feature("blackPawnStorms")
        
        self._avg_feature("whiteCentralControl", num)
        self._avg_feature("blackCentralControl", num)
        self._avg_feature("whiteSpaceAdvantage", num)
        self._avg_feature("blackSpaceAdvantage", num)
        
        calc = ScoreCalculator(self.features)
        midActivityScores.append(calc.activity_score())
        midAggressionScores.append(calc.aggression_score())
        
        return openingActivityScores, openingAggressionScores, midActivityScores, midAggressionScores, zobristHashOpening
    
    
    def _increment_feature(self, featureName, amount=1):
        self.features[featureName] += amount
    
    def _avg_feature(self, featureName, amount):
        self.features[featureName] /= amount
        
    def _count_pawn_breaks(self, board, movingPiece, attackedSq, isPawnBreak):

        # Only include pawn moves
        if movingPiece and movingPiece.piece_type == chess_app.PAWN:
                    
            # Check if the pawn is now attacking an opponent's pawn
            for square in attackedSq:
                targetPiece = board.piece_at(square)

                if targetPiece and targetPiece.piece_type == chess_app.PAWN and targetPiece.color != movingPiece.color:
                    self._increment_feature("whitePawnBreaks" if movingPiece.color == chess_app.WHITE else "blackPawnBreaks")
                    isPawnBreak = True
        
        return isPawnBreak
                    
                        
    # Counter for moves that attack a piece or pawn                    
    def _count_unique_attacks(self, board, movingPiece, attackedBefore, attackedSq, isPawnBreak, isActiveMove):
        
        # Dont count pawn break as an attack
        if isPawnBreak:
            # Flag for determining patient moves
            isActiveMove = True
            return isActiveMove
            
        # Check if any of the attacked squares contain an opponent's piece
        for square in attackedSq:
            if board.piece_at(square) and board.color_at(square) != movingPiece.color:
                    #check if piece was not already attacked before move
                    if not (attackedBefore & chess_app.BB_SQUARES[square]): 
                        self._increment_feature("whiteAttacks" if movingPiece.color == chess_app.WHITE else "blackAttacks")
                        isActiveMove = True
                        return isActiveMove
    
        
    
    # Count number of times a piece or pawn is pushed to the opp side of the board
    def _count_infiltrations(self, movingPiece, toSq, fromSq):
        if movingPiece.color == chess_app.WHITE and toSq > 31 and fromSq < 32:
            self._increment_feature("whiteInfiltrations")
        elif movingPiece.color == chess_app.BLACK and toSq < 32 and fromSq > 31:
            self._increment_feature("blackInfiltrations")
            
            
    # Count king attacks, 
    #   including targeting sq around king, 
    #   checks, 
    #   and removing pieces that defend sq around king
    def _count_king_attacks(self, movingPiece, isCheck, targetPiece, defendedSq, attackedSq):
        
        whiteKingSq = self.board.king(chess_app.WHITE)
        blackKingSq = self.board.king(chess_app.BLACK)
        # List of squares around each king
        
        whiteKingAdjSq = chess_app.SquareSet(chess_app.BB_KING_ATTACKS[whiteKingSq])
        blackKingAdjSq = chess_app.SquareSet(chess_app.BB_KING_ATTACKS[blackKingSq])
                
        # Determine if the king is an attacked sq, or if king adj sq is an attacked sq
        if movingPiece.color == chess_app.WHITE:
            if blackKingSq in attackedSq or not blackKingAdjSq.isdisjoint(attackedSq):
                self._increment_feature("whiteKingAttacks", 2 if isCheck else 1)
                # Award bonus point if defending piece was taken
                if targetPiece and targetPiece.color == chess_app.BLACK and not blackKingAdjSq.isdisjoint(defendedSq):
                    self._increment_feature("whiteKingAttacks", 2)
        elif movingPiece.color == chess_app.BLACK:
            if whiteKingSq in attackedSq or not whiteKingAdjSq.isdisjoint(attackedSq):
                self._increment_feature("blackKingAttacks", 2 if isCheck else 1)
                if targetPiece and targetPiece.color == chess_app.BLACK and not whiteKingAdjSq.isdisjoint(defendedSq):
                    self._increment_feature("blackKingAttacks", 3)


    def _count_xray_attacks(self, board, toSq, color, movingPiece):

        # Moving piece must be rook, queen or bishop
        if movingPiece and movingPiece.color == color and movingPiece.piece_type in {chess_app.ROOK, chess_app.BISHOP, chess_app.QUEEN}:
            occupied = board.occupied
            
            if movingPiece.piece_type == chess_app.ROOK:
                rank_pieces = chess_app.BB_RANK_MASKS[toSq] & occupied
                file_pieces = chess_app.BB_FILE_MASKS[toSq] & occupied

                # Find the closest piece in each direction that may block attacks
                blockers = chess_app.BB_RANK_ATTACKS[toSq][rank_pieces] | chess_app.BB_FILE_ATTACKS[toSq][file_pieces]

                # Only consider blocking pieces of the opponent
                blockers &= board.occupied_co[not color]

                # Ignore those blocking pieces to calculate the X-ray
                occupied ^= blockers

                # Identify rook attacks from the toSq, IGNORE PAWNS
                xray_attacked_squares = chess_app.SquareSet(
                    board.occupied_co[not color] & ~board.pawns & (
                        chess_app.BB_RANK_ATTACKS[toSq][rank_pieces] |
                        chess_app.BB_FILE_ATTACKS[toSq][file_pieces])
                )

            elif movingPiece.piece_type == chess_app.BISHOP:
                diag_pieces = chess_app.BB_DIAG_MASKS[toSq] & occupied

                # Find the closest piece in each diagonal direction that may block attacks
                blockers = chess_app.BB_DIAG_ATTACKS[toSq][diag_pieces]

                # Only consider blocking pieces of the opponent
                blockers &= board.occupied_co[not color]

                # Ignore those blocking pieces to calculate the X-ray
                occupied ^= blockers

                # Identify bishop attacks from the toSq, IGNORE PAWNS
                xray_attacked_squares = chess_app.SquareSet(
                    board.occupied_co[not color] & ~board.pawns & chess_app.BB_DIAG_ATTACKS[toSq][diag_pieces]
                )

            elif movingPiece.piece_type == chess_app.QUEEN:
                rank_pieces = chess_app.BB_RANK_MASKS[toSq] & occupied
                file_pieces = chess_app.BB_FILE_MASKS[toSq] & occupied
                diag_pieces = chess_app.BB_DIAG_MASKS[toSq] & occupied

                # Find the closest piece in each direction that may block attacks
                blockers = (
                    chess_app.BB_RANK_ATTACKS[toSq][rank_pieces] |
                    chess_app.BB_FILE_ATTACKS[toSq][file_pieces] |
                    chess_app.BB_DIAG_ATTACKS[toSq][diag_pieces]
                )

                # Only consider blocking pieces of the opponent
                blockers &= board.occupied_co[not color]

                # Ignore those blocking pieces to calculate the X-ray
                occupied ^= blockers

                # Compute queen attacks from the toSq, IGNORE PAWNS
                xray_attacked_squares = chess_app.SquareSet(
                    board.occupied_co[not color] & ~board.pawns & (
                        chess_app.BB_RANK_ATTACKS[toSq][rank_pieces] |
                        chess_app.BB_FILE_ATTACKS[toSq][file_pieces] |
                        chess_app.BB_DIAG_ATTACKS[toSq][diag_pieces])
                )

            if len(xray_attacked_squares) > 0:
                self._increment_feature("whiteXrayAttacks" if movingPiece.color == chess_app.WHITE else "blackXrayAttacks", 1)


    # Counter for moves that are not active, not captures, and not retreats                   
    def _count_patient_moves(self, isCapture, movingPiece, isActiveMove, isRetreat):
        if not isActiveMove and not isCapture and not isRetreat:
            self._increment_feature("whitePatientMoves" if movingPiece.color == chess_app.WHITE else "blackPatientMoves")


    # If a piece is moved, increment    
    def _count_piece_movement(self, movingPiece):
        if movingPiece.piece_type not in [chess_app.PAWN, chess_app.KING]:
            self._increment_feature("whitePieceMoves" if movingPiece.color == chess_app.WHITE else "blackPieceMoves")
    
    
    # Increment if pieces are defended by a move
    def _count_active_defends(self, board, movingPiece, attackedSq, attackedBefore, isActiveMove):
        
        for square in attackedSq:
            defendedPiece = board.piece_at(square)
            
            # Exclude Kings, ensure that piece is same color
            if defendedPiece and defendedPiece.piece_type != chess_app.KING and board.color_at(square) == movingPiece.color:
                # Check if piece was not already attacked and check that piece is currently being attacked
                if not (attackedBefore & chess_app.BB_SQUARES[square]) and board.is_attacked_by(not movingPiece.color, square):
                    self._increment_feature("whiteActiveDefense" if movingPiece.color == chess_app.WHITE else "blackActiveDefense")
                    # Flag for determining patient moves
                    isActiveMove = True
    
        return isActiveMove

    def _count_pieces_at_home(self, board):

        # Define home squares for each piece type
        whiteHomeSq = {chess_app.A1: chess_app.ROOK,
                       chess_app.B1: chess_app.KNIGHT,
                       chess_app.C1: chess_app.BISHOP,
                       chess_app.D1: chess_app.QUEEN,
                       chess_app.E1: chess_app.KING,
                       chess_app.F1: chess_app.BISHOP,
                       chess_app.G1: chess_app.KNIGHT,
                       chess_app.H1: chess_app.ROOK}

        blackHomeSq = {chess_app.A8: chess_app.ROOK,
                       chess_app.B8: chess_app.KNIGHT,
                       chess_app.C8: chess_app.BISHOP,
                       chess_app.D8: chess_app.QUEEN,
                       chess_app.E8: chess_app.KING,
                       chess_app.F8: chess_app.BISHOP,
                       chess_app.G8: chess_app.KNIGHT,
                       chess_app.H8: chess_app.ROOK}

        # Iterate through the board and check if pieces are on their exact home squares
        for square, piece in board.piece_map().items():
            if piece.color == chess_app.WHITE:
                if square in whiteHomeSq and piece.piece_type == whiteHomeSq[square]:
                    self._increment_feature("whitePiecesAtHome")
            elif piece.color == chess_app.BLACK:
                if square in blackHomeSq and piece.piece_type == blackHomeSq[square]:
                    self._increment_feature("blackPiecesAtHome")


    def _calculate_central_control(self, board):
        central_squares = [chess_app.D4, chess_app.E4, chess_app.D5, chess_app.E5]
        supporting_squares = [chess_app.C3, chess_app.C4, chess_app.C5, chess_app.C6, 
                              chess_app.F3, chess_app.F4, chess_app.F5, chess_app.F6]
 
        for square in central_squares:
            attackers_white = board.attackers(chess_app.WHITE, square)
            attackers_black = board.attackers(chess_app.BLACK, square)

            # Value for central squares is greater than supporting squares
            if attackers_white:
                self._increment_feature("whiteCentralControl", 2)
            if attackers_black:
                self._increment_feature("blackCentralControl", 2)

        for square in supporting_squares:
            attackers_white = board.attackers(chess_app.WHITE, square)
            attackers_black = board.attackers(chess_app.BLACK, square)

            if attackers_white:
                self._increment_feature("whiteCentralControl", 1)
            if attackers_black:
                self._increment_feature("blackCentralControl", 1)



    def _calculate_space_advantage(self, board):
        for square in chess_app.SQUARES:
            rank = chess_app.square_rank(square)
            attackers_white = board.attackers(chess_app.WHITE, square)
            attackers_black = board.attackers(chess_app.BLACK, square)

            if attackers_white and rank >= 4:  # White controls squares in opponent's territory
                self._increment_feature("whiteSpaceAdvantage", (rank - 3))

            if attackers_black and rank <= 3:  # Black controls squares in opponent's territory
                self._increment_feature("blackSpaceAdvantage", (4 - rank))



    # Iterate through previous moves to check if multiple pawns have been pushed toward opp king
    def _detect_pawn_storm(self, board, color, prevMoves) -> bool:

        kingside_files = [5, 6, 7]
        queenside_files = [0, 1, 2]

        # Count advances, pawn storm requires atleast 2
        kingside_advances = 0
        queenside_advances = 0
        
        for move in prevMoves:
            movingPiece = board.piece_at(move.from_square)
            
            if movingPiece and movingPiece.piece_type == chess_app.PAWN and movingPiece.color == color:
                
                from_file = chess_app.square_file(move.from_square)
                to_file = chess_app.square_file(move.to_square)
                
                # Check for kingside pawn storm
                if from_file in kingside_files and to_file in kingside_files:
                    if chess_app.square_rank(move.to_square) > chess_app.square_rank(move.from_square):  # Pawn advanced
                        kingside_advances += 1
                
                # Check for queenside pawn storm
                elif from_file in queenside_files and to_file in queenside_files:
                    if chess_app.square_rank(move.to_square) > chess_app.square_rank(move.from_square):  # Pawn advanced
                        queenside_advances += 1
                
        if kingside_advances >= 2 or queenside_advances >= 2:
            return True

        return False
    
    # After the opening, values are reset to zero for the mid game values
    def _reset_features_for_mid(self):
        reset_keys = ["whitePawnBreaks", "blackPawnBreaks",
                      "whitePieceMoves", "blackPieceMoves",
                      "whiteAttacks", "blackAttacks",
                      "whiteInfiltrations", "blackInfiltrations",
                      "whiteKingAttacks", "blackKingAttacks",
                      "whiteActiveDefense", "blackActiveDefense",
                      "whiteXrayAttacks", "blackXrayAttacks",
                      "whiteRetreats", "blackRetreats",
                      "whitePatientMoves", "blackPatientMoves",
                      "whitePiecesAtHome", "blackPiecesAtHome",
                      "whiteCentralControl", "blackCentralControl",
                      "whiteSpaceAdvantage", "blackSpaceAdvantage",
                      "whitePawnStorms", "blackPawnStorms"]
        
        for key in reset_keys:
            self.features[key] = 0
