import os
import re
import pandas as pd
import chess.pgn
import nltk
import docx
from PyPDF2 import PdfReader
from tkinter import Tk
from tkinter.filedialog import askopenfilename

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

# Tokenizer sederhana
def simple_tokenizer(text):
    """Tokenizer sederhana yang menghapus stopword."""
    stop_words = set(stopwords.words('english'))
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [word for word in tokens if word not in stop_words]

# Preprocessing e-book
def preprocess_text(file_path):
    """Preprocess text from a PDF or DOCX file."""
    try:
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = " ".join([page.extract_text() for page in reader.pages])
        elif file_path.endswith(".doc") or file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = " ".join([p.text for p in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")

        return simple_tokenizer(text)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

# Analisis PGN
def process_pgn_file(pgn_file, color):
    """Process PGN file and return a DataFrame with color information."""
    games_data = []
    try:
        game = chess.pgn.read_game(pgn_file)

        while game:
            game_info = game.headers
            game_moves = []
            board = game.board()
            for move in game.mainline_moves():
                game_moves.append(board.san(move))
                board.push(move)
            games_data.append({
                "White": game_info.get("White", "Unknown"),
                "Black": game_info.get("Black", "Unknown"),
                "Date": game_info.get("Date", "Unknown"),
                "Result": game_info.get("Result", "*"),
                "Moves": " ".join(game_moves),
                "Color": color
            })
            game = chess.pgn.read_game(pgn_file)
    except Exception as e:
        print(f"Error processing PGN file: {e}")

    return pd.DataFrame(games_data)

# Analisis Win Rate
def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves."""
    if 'Moves' not in df.columns:
        print("Column 'Moves' not found in DataFrame.")
        return pd.DataFrame()

    df['First_Two_Moves'] = df['Moves'].apply(lambda x: ' '.join(x.split()[:2]))
    df['White_Result'] = df['Result'].map({'1-0': 1, '0-1': 0, '1/2-1/2': 0.5})
    df['Black_Result'] = df['Result'].map({'1-0': 0, '0-1': 1, '1/2-1/2': 0.5})

    white_win_rate = df[df['Color'] == 'White'].groupby('First_Two_Moves').agg(
        total_games_white=('White_Result', 'count'),
        win_rate_white=('White_Result', 'mean')
    )

    black_win_rate = df[df['Color'] == 'Black'].groupby('First_Two_Moves').agg(
        total_games_black=('Black_Result', 'count'),
        win_rate_black=('Black_Result', 'mean')
    )

    win_rate = pd.merge(white_win_rate, black_win_rate, left_index=True, right_index=True, how='outer').fillna(0)
    win_rate = win_rate[(win_rate['total_games_white'] > 20) | (win_rate['total_games_black'] > 20)]

    return win_rate

# Temukan langkah dengan akurasi terendah
def find_min_accuracy_move(win_rate_df):
    """Find the move with the lowest accuracy."""
    if win_rate_df.empty:
        print("Win rate DataFrame is empty!")
        return None

    try:
        return win_rate_df.sort_values(by=['win_rate_white', 'win_rate_black'], ascending=True).index[0]
    except Exception as e:
        print(f"Error finding minimum accuracy move: {e}")
        return None

# Pencarian teks pada e-books
def search_text_in_ebooks(folder_path, query):
    """Search for specific moves in e-books."""
    results = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".pdf", ".docx")):
                file_path = os.path.join(root, file)
                try:
                    tokens = preprocess_text(file_path)
                    if query in tokens:
                        results[file] = file_path
                except Exception as e:
                    print(f"Error processing {file}: {e}")
    return results

# Main Execution
if __name__ == "__main__":
    dataset_folder = "/home/ep/Documents/Github/Information_Retrieval_System/Analyze_E-book/Dataset"

    print("Preprocessing e-books...")
    e_books = [f for f in os.listdir(dataset_folder) if f.endswith(('.pdf', '.docx'))]
    processed_books = {}
    for book in e_books:
        book_path = os.path.join(dataset_folder, book)
        processed_books[book] = preprocess_text(book_path)

    Tk().withdraw()
    pgn_file_path = askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])

    if not pgn_file_path:
        print("No file selected!")
    else:
        color = input("Enter the color (White or Black): ")

        with open(pgn_file_path, 'r') as pgn_file:
            pgn_df = process_pgn_file(pgn_file, color)

        win_rate_df = analyze_win_rate(pgn_df)
        if not win_rate_df.empty:
            min_accuracy_move = find_min_accuracy_move(win_rate_df)
            print(f"Lowest accuracy move: {min_accuracy_move}")

            search_results = search_text_in_ebooks(dataset_folder, min_accuracy_move)
            print("Search Results:")
            for file, path in search_results.items():
                print(f"{file}: {path}")
