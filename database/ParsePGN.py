import pandas as pd
from collections import defaultdict


def count_games(pgn_file_path):
    # Initialize dictionaries to count games played by each player as White and Black
    white_games = defaultdict(int)
    black_games = defaultdict(int)
    
    with open(pgn_file_path, 'r') as pgnFile:
        for line in pgnFile:
            line = line.strip()
            
            if line.startswith("[White "):
                white_player = line.split('"')[1]
            elif line.startswith("[Black "):
                black_player = line.split('"')[1]
            elif line == "":  # End of a game
                white_games[white_player] += 1
                black_games[black_player] += 1
    
    return white_games, black_games

def filter_players(white_games, black_games, min_white_games, min_black_games):
    qualifying_players = set()
    for player in white_games:
        if white_games[player] >= min_white_games and black_games.get(player, 0) >= min_black_games:
            qualifying_players.add(player)
    return qualifying_players


def extract_game_data(pgn_file_path, qualifying_players):
    # Initialize dictionaries to count games played by each player as White and Black
    data = []
    


    # Second pass: extract data only for eligible players
    with open(pgn_file_path, 'r') as pgnFile:
        for line in pgnFile:
            line = line.strip()
            
            if line.startswith("[Event "):
                # When a new game starts, reset the variables
                eco_code = ""
                opening_name = ""
                white_player = ""
                black_player = ""
                game_date = ""
            elif line.startswith("[Date "):
                game_date = line.split('"')[1]
            elif line.startswith("[White "):
                white_player = line.split('"')[1]
            elif line.startswith("[Black "):
                black_player = line.split('"')[1]
            elif line.startswith("[ECO "):
                eco_code = line.split('"')[1]
            elif line.startswith("[Opening "):
                opening_name = line.split('"')[1]


                
                # Only add data for eligible players
                if white_player in qualifying_players and black_player in qualifying_players:
                    data.append({
                        "Player": white_player,
                        "Color": "White",
                        "ECO Code": eco_code,
                        "Opening ": opening_name,
                        "Date": game_date
                    })
                    data.append({
                        "Player": black_player,
                        "Color": "Black",
                        "ECO Code": eco_code,
                        "Opening ": opening_name,
                        "Date": game_date
                    })
                    
                elif black_player in qualifying_players and white_player not in qualifying_players:
                    data.append({
                        "Player": black_player,
                        "Color": "Black",
                        "ECO Code": eco_code,
                        "Opening ": opening_name,
                        "Date": game_date
                    })
                elif white_player in qualifying_players and black_player not in qualifying_players:
                    data.append({
                        "Player": white_player,
                        "Color": "White",
                        "ECO Code": eco_code,
                        "Opening ": opening_name,
                        "Date": game_date
                    })
                    
    
    return data

def create_csv(pgn_file_path, output_csv, qualifying_players):
    game_data = extract_game_data(pgn_file_path, qualifying_players)
    df = pd.DataFrame(game_data)
    df.to_csv(output_csv, index=False)

#Process testDb
testDB_white_games, testDB_black_games = count_games(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\testdb.pgn')
testDB_players = filter_players(testDB_white_games, testDB_black_games, 25, 25)
print(len(testDB_players))
# # Process the Jan-Sept_Lumbra PGN file
# jan_sept_white_games, jan_sept_black_games = count_games(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\Jan-Sept_Lumbra.pgn')
# jan_sept_players = filter_players(jan_sept_white_games, jan_sept_black_games, 100, 100)
# print(len(jan_sept_players))
# # Process the July-Sept_Lumbra PGN file for players who already qualify in Jan-Sept_Lumbra
# july_sept_white_games, july_sept_black_games = count_games(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\July-Sept_Lumbra.pgn')
# july_sept_players = filter_players(july_sept_white_games, july_sept_black_games, 50, 50)
# print(len(july_sept_players))
# # Process the Oct-Dec_Lumbra PGN file for players who already qualify in Jan-Sept_Lumbra
# oct_dec_white_games, oct_dec_black_games = count_games(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\Oct-Dec_Lumbra.pgn')
# oct_dec_players = filter_players(oct_dec_white_games, oct_dec_black_games, 50, 50)
# oct_dec_players = oct_dec_players.intersection(july_sept_players)  # Ensure players were also in Jan-Sept
# print(len(oct_dec_players))
# Create CSV files for each period
create_csv(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\testdb.pgn', 'testDB_filtered.csv', testDB_players)

# create_csv(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\Jan-Sept_Lumbra.pgn', 'Jan-Sept_Lumbra_filtered.csv', jan_sept_players)
# create_csv(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\July-Sept_Lumbra.pgn', 'July-Sept_Lumbra_filtered.csv', oct_dec_players)
# create_csv(r'C:\Users\DELL\Downloads\chess_pgns\pgn_sorted\Oct-Dec_Lumbra.pgn', 'Oct-Dec_Lumbra_filtered.csv', oct_dec_players)

