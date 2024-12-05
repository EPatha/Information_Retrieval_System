import chess.pgn
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Step 1: Process PGN file and convert to DataFrame
def process_pgn_file(pgn_file_path, color):
    """Process PGN file and return a DataFrame with color information."""
    games_data = []
    with open(pgn_file_path) as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_info = game.headers
            game_moves = []
            board = game.board()
            for move in game.mainline_moves():
                game_moves.append(board.san(move))
                board.push(move)
            games_data.append({
                "White": game_info["White"],
                "Black": game_info["Black"],
                "Date": game_info["Date"],
                "Result": game_info["Result"],
                "Moves": " ".join(game_moves),
                "Color": color  # Add a 'Color' column to distinguish between White and Black PGN
            })
    return pd.DataFrame(games_data)

# Step 2: Process and encode result and moves
def process_and_encode_data(df):
    """Convert 'Result' and 'Moves' columns to one-hot encoding."""
    # Convert result to one-hot encoding
    result_one_hot = pd.get_dummies(df['Result'], prefix='Result')

    # Extract first two moves
    df['First_Two_Moves'] = df['Moves'].apply(lambda x: ' '.join(x.split()[:2]))

    # Create one-hot encoding for first two moves
    moves_one_hot = pd.get_dummies(df['First_Two_Moves'], prefix='Move')

    # Concatenate the results into a final DataFrame
    final_data = pd.concat([result_one_hot, moves_one_hot, df['Color']], axis=1)
    return final_data

def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves, separately for White and Black."""
    # Reset index to avoid duplicate index issues
    if df.index.duplicated().any():
        df = df.reset_index(drop=True)

    # Ensure Moves column is a string
    df['Moves'] = df['Moves'].astype(str)

    # Add a column for the first two moves
    df['First_Two_Moves'] = df['Moves'].str[:2]

    # Map results to numerical values for White and Black
    df['White_Result'] = df['Result'].map({'1-0': 1, '0-1': 0, '1/2-1/2': 0.5})
    df['Black_Result'] = df['Result'].map({'1-0': 0, '0-1': 1, '1/2-1/2': 0.5})

    # Group by the first two moves for White
    white_win_rate = df[df['Color'] == 'White'].groupby('First_Two_Moves', as_index=False).agg(
        total_games_white=('White_Result', 'count'),
        white_win_rate=('White_Result', 'mean')
    )

    # Group by the first two moves for Black
    black_win_rate = df[df['Color'] == 'Black'].groupby('First_Two_Moves', as_index=False).agg(
        total_games_black=('Black_Result', 'count'),
        black_win_rate=('Black_Result', 'mean')
    )

    # Merge both dataframes on 'First_Two_Moves'
    win_rate = pd.merge(white_win_rate, black_win_rate, on='First_Two_Moves', how='outer')

    # Rename columns for clarity
    win_rate.columns = ['Opening Move', 'Total Games White', 'Win Rate White', 'Total Games Black', 'Win Rate Black']
    
    return win_rate



# Main execution
if __name__ == "__main__":
    # Set up Tkinter for file dialog (replace with askopenfilename for local)
    Tk().withdraw()  # Prevent root window from showing
    print("Select PGN file for White player.")
    
    # Ask for PGN file for White player and process it
    white_pgn_file_path = askopenfilename(filetypes=[("PGN files", "*.pgn")], title="Select PGN file for White player")
    
    if white_pgn_file_path:
        # Process the PGN file for White player
        df_white = process_pgn_file(white_pgn_file_path, 'White')
        print(f"Processed White PGN file: {white_pgn_file_path}")

        # Ask for PGN file for Black player
        print("Now, select PGN file for Black player.")
        black_pgn_file_path = askopenfilename(filetypes=[("PGN files", "*.pgn")], title="Select PGN file for Black player")
        
        if black_pgn_file_path:
            # Process the PGN file for Black player
            df_black = process_pgn_file(black_pgn_file_path, 'Black')
            print(f"Processed Black PGN file: {black_pgn_file_path}")

            # Combine the data from both files into one DataFrame
            df_combined = pd.concat([df_white, df_black])

            # Process and encode data
            final_data = process_and_encode_data(df_combined)

            # Analyze win rate for the first moves
            win_rate_df = analyze_win_rate(df_combined)

            # Output the win rate analysis
            print("\nWin rate analysis:")
            print(win_rate_df)

            # Optionally, save the final data to Excel
            output_file = 'preprocessed_output.xlsx'
            final_data.to_excel(output_file, index=False)
            print(f"Data successfully saved to {output_file}")
        
        else:
            print("No Black PGN file selected. Exiting.")
    else:
        print("No White PGN file selected. Exiting.")
