import os
import re
import pandas as pd
import chess.pgn
import nltk
import docx
from PyPDF2 import PdfReader
from tkinter import Tk, filedialog, Label, Button, Entry, Text, Scrollbar, messagebox
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

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
        messagebox.showerror("Error", f"Error processing file {file_path}: {e}")
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
        messagebox.showerror("Error", f"Error processing PGN file: {e}")

    return pd.DataFrame(games_data)

# Analisis Win Rate
def analyze_win_rate(df):
    """Calculate win rates for openings based on the first two moves."""
    if 'Moves' not in df.columns:
        messagebox.showwarning("Warning", "Column 'Moves' not found in DataFrame.")
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
        messagebox.showwarning("Warning", "Win rate DataFrame is empty!")
        return None

    try:
        return win_rate_df.sort_values(by=['win_rate_white', 'win_rate_black'], ascending=True).index[0]
    except Exception as e:
        messagebox.showerror("Error", f"Error finding minimum accuracy move: {e}")
        return None

# Proses otomatis semua file PDF dan DOCX
def process_all_files(directory):
    """Process all PDF and DOCX files in the directory."""
    tokens = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".docx"):
                file_path = os.path.join(root, file)
                tokens.extend(preprocess_text(file_path))
    return tokens

# Fungsi utama GUI
def main():
    def select_pgn_file():
        file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if file_path:
            entry_pgn_file.delete(0, "end")
            entry_pgn_file.insert(0, file_path)

    def analyze_file():
        pgn_file_path = entry_pgn_file.get()
        color = entry_color.get()

        if not os.path.exists(pgn_file_path):
            messagebox.showerror("Error", "PGN file not found!")
            return

        if color.lower() not in ['white', 'black']:
            messagebox.showerror("Error", "Invalid color! Please enter 'White' or 'Black'.")
            return

        with open(pgn_file_path, 'r') as pgn_file:
            pgn_df = process_pgn_file(pgn_file, color.capitalize())

        win_rate_df = analyze_win_rate(pgn_df)
        if not win_rate_df.empty:
            min_accuracy_move = find_min_accuracy_move(win_rate_df)
            result_text.delete(1.0, "end")
            result_text.insert("end", f"Lowest accuracy move: {min_accuracy_move}\n")
            result_text.insert("end", win_rate_df.to_string())

    def search_engine():
        search_query = " ".join(global_tokens[:2]) if global_tokens else ""
        result_text.delete(1.0, "end")
        result_text.insert("end", f"Search Query: {search_query}\n")

    # GUI
    root = Tk()
    root.title("Chess Analysis Tool")

    Label(root, text="PGN File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_pgn_file = Entry(root, width=50)
    entry_pgn_file.grid(row=0, column=1, padx=10, pady=5)
    Button(root, text="Browse", command=select_pgn_file).grid(row=0, column=2, padx=10, pady=5)

    Label(root, text="Color (White/Black):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_color = Entry(root, width=50)
    entry_color.grid(row=1, column=1, padx=10, pady=5)

    Button(root, text="Analyze", command=analyze_file).grid(row=2, column=1, pady=10)
    Button(root, text="Search Engine", command=search_engine).grid(row=3, column=1, pady=10)

    result_text = Text(root, wrap="word", height=25, width=100)
    result_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    scrollbar = Scrollbar(root, command=result_text.yview)
    result_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=4, column=3, sticky="ns")

    # Proses otomatis semua file di direktori
    global_tokens = process_all_files("/home/ep/Documents/Github/Information_Retrieval_System/Analyze_E-book/Dataset/")

    root.mainloop()

if __name__ == "__main__":
    main()
