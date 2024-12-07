import os
import re
import pandas as pd
import chess.pgn
from nltk.corpus import stopwords
import nltk
import docx
from PyPDF2 import PdfReader
from tkinter import Tk
from tkinter.filedialog import askopenfilename

nltk.download('punkt')
nltk.download('stopwords')

# Tokenizer sederhana
def simple_tokenizer(text):
    """Tokenizer sederhana yang menghapus stopword."""
    stop_words = set(stopwords.words('english'))
    tokens = re.findall(r'\b\w+\b', text.lower())  # Memisahkan kata-kata berdasarkan karakter alfanumerik
    return [word for word in tokens if word not in stop_words]

# Preprocessing e-book
def preprocess_text(file_path):
    """Preprocess text from a PDF or DOCX file."""
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = " ".join([page.extract_text() for page in reader.pages])
    elif file_path.endswith(".doc") or file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")

    # Tokenization with simple_tokenizer
    tokens = simple_tokenizer(text)
    return tokens

# Analisis PGN
def process_pgn_file(pgn_file, color):
    """Process PGN file and return a DataFrame with color information."""
    games_data = []
    game = chess.pgn.read_game(pgn_file)
    
    while game:
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
            "Color": color
        })
        game = chess.pgn.read_game(pgn_file)
    return pd.DataFrame(games_data)

# Analisis Win Rate dengan Filter Frekuensi
def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves, separately for White and Black."""
    # Pastikan kolom 'Moves' ada dan diolah dengan benar
    if 'Moves' not in df.columns:
        print("Kolom 'Moves' tidak ditemukan dalam DataFrame.")
        return pd.DataFrame()

    df['First_Two_Moves'] = df['Moves'].apply(lambda x: ' '.join(x.split()[:2]))
    
    # Cek apakah kolom First_Two_Moves terbentuk
    print("Kolom 'First_Two_Moves' setelah penambahan:")
    print(df[['Moves', 'First_Two_Moves']].head())

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

    win_rate = pd.merge(white_win_rate, black_win_rate, left_index=True, right_index=True, how='outer')

    # Filter only rows with total games > 20
    win_rate = win_rate[
        (win_rate['total_games_white'] > 20) | (win_rate['total_games_black'] > 20)
    ]

    # Cek hasil win_rate DataFrame
    print("DataFrame 'win_rate' setelah analisis:")
    print(win_rate.head())

    return win_rate

# Fungsi utama
if __name__ == "__main__":
    dataset_folder = "/home/ep/Documents/Github/Information_Retrieval_System/UTS_STKI/Dataset/"

    # Step 1: Preprocess PDF and DOCX
    print("Preprocessing e-books...")
    e_books = [f for f in os.listdir(dataset_folder) if f.endswith(('.pdf', '.docx'))]
    processed_books = {}
    for book in e_books:
        book_path = os.path.join(dataset_folder, book)
        processed_books[book] = preprocess_text(book_path)

    # Step 2: Upload PGN file via file dialog
    Tk().withdraw()  # Hide the root Tk window
    pgn_file_path = askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])

    if not pgn_file_path:
        print("No file selected!")
    else:
        color = input("Enter the color (White or Black): ")
        
        with open(pgn_file_path, 'r') as pgn_file:
            pgn_df = process_pgn_file(pgn_file, color)
        
        # Menambahkan verifikasi data
        if pgn_df.empty:
            print("Data PGN kosong!")
        else:
            win_rate_df = analyze_win_rate(pgn_df)

            if not win_rate_df.empty:
                # Find lowest accuracy move
                min_accuracy_move = win_rate_df.sort_values(
                    by=['win_rate_white', 'win_rate_black'], ascending=True
                ).iloc[0]['First_Two_Moves']

                # Step 3: Search based on lowest accuracy move
                print(f"Searching e-books for move: {min_accuracy_move}")
                search_results = search_text_in_ebooks(dataset_folder, min_accuracy_move)

                print("Search Results:")
                for file, path in search_results.items():
                    print(f"{file}: {path}")
            else:
                print("Tidak ada data win rate yang valid.")

# Fungsi pencarian teks berdasarkan query
def search_text_in_ebooks(folder_path, query):
    """Search for specific moves in e-books."""
    results = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".pdf", ".docx")):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file}")
                try:
                    tokens = preprocess_text(file_path)
                    text = " ".join(tokens)
                    if re.search(r'\b' + re.escape(query) + r'\b', text):
                        results[file] = file_path
                except Exception as e:
                    print(f"Error processing {file}: {e}")
    return results

# Main Execution
if __name__ == "__main__":
    dataset_folder = "/home/ep/Documents/Github/Information_Retrieval_System/UTS_STKI/Dataset/"

    # Step 1: Preprocess PDF and DOCX
    print("Preprocessing e-books...")
    e_books = [f for f in os.listdir(dataset_folder) if f.endswith(('.pdf', '.docx'))]
    processed_books = {}
    for book in e_books:
        book_path = os.path.join(dataset_folder, book)
        processed_books[book] = preprocess_text(book_path)

    # Step 2: Upload PGN file via file dialog
    Tk().withdraw()  # Hide the root Tk window
    pgn_file_path = askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])

    if not pgn_file_path:
        print("No file selected!")
    else:
        color = input("Enter the color (White or Black): ")
        
        with open(pgn_file_path, 'r') as pgn_file:
            pgn_df = process_pgn_file(pgn_file, color)
        
        win_rate_df = analyze_win_rate(pgn_df)

        # Find lowest accuracy move
        min_accuracy_move = win_rate_df.sort_values(
            by=['win_rate_white', 'win_rate_black'], ascending=True
        ).iloc[0]['First_Two_Moves']

        # Step 3: Search based on lowest accuracy move
        print(f"Searching e-books for move: {min_accuracy_move}")
        search_results = search_text_in_ebooks(dataset_folder, min_accuracy_move)

        print("Search Results:")
        for file, path in search_results.items():
            print(f"{file}: {path}")
