from FeatureExtractor import FeatureExtractor
from ScoreCalculator import ScoreCalculator
import psycopg2
import chess_app.database.ParsePGN as ParsePGN

connection = psycopg2.connect('')
cursor = connection.cursor()

pgn = r"C:\Users\DELL\IdeaProjects\django\out.pgn"

ParsePGN.parse_pgn_update_db(pgn, cursor)

        


cursor.execute("""
    SELECT opening_move_length 
    FROM opening_book
    WHERE eco_code = %s AND opening_name = %s AND variation_name = %s
    """, (eco_code, opening_name, variation_name))

# openingLength = cursor.fetchone() 




# cursor.close()
# connection.close()

# features = FeatureExtractor(game, openingLength[0])

# opAct, opAggro, midAct, midAggro, zobristHashOpening = features.extract_features()

# print(opAct, opAggro)

# print(midAct, midAggro)

# print(zobristHashOpening)
