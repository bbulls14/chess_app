
class ScoreCalculator:
    def __init__(self, features):
        self.features = features

    def activity_score(self):
        # Weight assignments for the activity score
        pawn_break_weight = 1.5
        attacks_weight = 1.5
        piece_moves_weight = 1.5
        active_defense_weight = 1.0  
        central_control_weight = 1.5
        space_advantage_weight = 1.5
        piece_at_home_penalty = -0.5

        # Calculate activity scores for white
        white_activity = (pawn_break_weight * self.features["whitePawnBreaks"] +
                          attacks_weight * self.features["whiteAttacks"] + 
                          piece_moves_weight * self.features["whitePieceMoves"] + 
                          active_defense_weight * self.features["whiteActiveDefense"] +
                          central_control_weight * self.features["whiteCentralControl"] +
                          space_advantage_weight * self.features["whiteSpaceAdvantage"] +
                          piece_at_home_penalty * self.features["whitePiecesAtHome"])

        # Calculate activity scores for black
        black_activity = (pawn_break_weight * self.features["blackPawnBreaks"] +
                          attacks_weight * self.features["blackAttacks"] + 
                          piece_moves_weight * self.features["blackPieceMoves"] + 
                          active_defense_weight * self.features["blackActiveDefense"] +
                          central_control_weight * self.features["blackCentralControl"] +
                          space_advantage_weight * self.features["blackSpaceAdvantage"] +
                          piece_at_home_penalty * self.features["blackPiecesAtHome"])

        return white_activity, black_activity

    def aggression_score(self):
        # Weight assignments for the aggression score
        pawn_breaks_weight = 1.5
        attacks_weight = 1.5  

        infiltration_weight = 2.5  
        king_attack_weight = 4.5  
        xray_attacks_weight = 3.0  
        pawn_storm_weight = 4.0  
        retreat_penalty = -2.0 
        patient_move_penalty = -1.0 

        # Calculate aggression scores for white
        white_aggressiveness = (pawn_breaks_weight * self.features["whitePawnBreaks"] +
                                attacks_weight * self.features["whiteAttacks"] + 
                                infiltration_weight * self.features["whiteInfiltrations"] +
                                king_attack_weight * self.features["whiteKingAttacks"] +
                                xray_attacks_weight * self.features["whiteXrayAttacks"] +
                                pawn_storm_weight * self.features["whitePawnStorms"] +
                                retreat_penalty * self.features["whiteRetreats"] + 
                                patient_move_penalty * self.features["whitePatientMoves"])

        # Calculate aggression scores for black
        black_aggressiveness = (pawn_breaks_weight * self.features["blackPawnBreaks"] +
                                attacks_weight * self.features["blackAttacks"] + 
                                infiltration_weight * self.features["blackInfiltrations"] +
                                king_attack_weight * self.features["blackKingAttacks"] +
                                xray_attacks_weight * self.features["blackXrayAttacks"] +
                                pawn_storm_weight * self.features["blackPawnStorms"] +
                                retreat_penalty * self.features["blackRetreats"] + 
                                patient_move_penalty * self.features["blackPatientMoves"])

        return white_aggressiveness, black_aggressiveness

    def calculate_all_scores(self):
        # Calculate and return all scores at once
        white_activity, black_activity = self.activity_score()
        white_aggressiveness, black_aggressiveness = self.aggression_score()

        return {
            "white_activity": white_activity,
            "black_activity": black_activity,
            "white_aggressiveness": white_aggressiveness,
            "black_aggressiveness": black_aggressiveness
        }