import os
import json
import pandas as pd

def combine_json_to_csv(players_dir: str, output_csv: str) -> None:
    """
    Combines multiple JSON files from the players directory into a single CSV file.

    Parameters:
        players_dir (str): Path to the directory containing player JSON files.
        output_csv (str): Path to the output CSV file.
    
    Returns:
        None
    
    Outputs:
        tt_games.csv in root folder
    """
    # List to hold all game records
    all_games = []

    # Iterate over all files in the players directory
    for filename in os.listdir(players_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(players_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    # Extract username
                    username = data.get('username', 'unknown').lower()
                    
                    # Extract games
                    games = data.get('games', [])
                    if not games:
                        print(f"No games found for player: {username} in file: {filename}")
                        continue

                    for game in games:
                        # Extract the required fields
                        game_record = {
                            "username": username,  # Include username
                            "white": game.get("white", None),
                            "score": game.get("score", None),
                            "accuracy": game.get("accuracy", None),
                            "rating": game.get("rating", None),
                            "tournament": game.get("tournament", None),
                            "round": game.get("round", None),
                            "points": game.get("points", None),
                            "rank": game.get("rank", None),
                            "possible_rank": game.get("possible_rank", None)
                        }
                        all_games.append(game_record)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {filename}. Skipping.")
            except Exception as e:
                print(f"An error occurred while processing file: {filename}. Error: {e}")

    # Create DataFrame
    df = pd.DataFrame(all_games)

    # Optional: Handle missing values or data types here
    # For example, you might want to fill missing accuracies with 0 or drop such rows

    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"Successfully saved {len(df)} records to {output_csv}")

if __name__ == "__main__":
    # Define the path to the players directory and output CSV
    players_directory = "players"  # Update this path if necessary
    output_csv_file = "tt_games.csv"

    combine_json_to_csv(players_directory, output_csv_file)
