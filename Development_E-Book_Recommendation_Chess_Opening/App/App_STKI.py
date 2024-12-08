import os
import re
import pandas as pd
import chess.pgn
from nltk.corpus import stopwords
import nltk
import docx
from PyPDF2 import PdfReader
from tkinter import Tk, Label, Button, filedialog, ttk, Text

nltk.download('punkt')
nltk.download('stopwords')

# Fungsi tambahan
def simple_tokenizer(text):
    stop_words = set(stopwords.words('english'))
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [word for word in tokens if word not in stop_words]

def preprocess_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = " ".join([page.extract_text() for page in reader.pages])
    elif file_path.endswith(".doc") or file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    return simple_tokenizer(text)

def process_pgn_file(file_path, color):
    games_data = []
    with open(file_path, 'r') as pgn_file:
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

def analyze_win_rate(df):
    if 'Moves' not in df.columns:
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
    return pd.merge(white_win_rate, black_win_rate, left_index=True, right_index=True, how='outer')

# GUI Utama
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PGN Files", "*.pgn")])
    if file_path:
        process_file(file_path)

def process_file(file_path):
    color = color_input.get()
    if color not in ["White", "Black"]:
        result_label.config(text="Error: Please enter 'White' or 'Black'")
        return
    try:
        pgn_df = process_pgn_file(file_path, color)
        if pgn_df.empty:
            result_label.config(text="No data found in PGN file.")
            return
        win_rate_df = analyze_win_rate(pgn_df)
        if win_rate_df.empty:
            result_label.config(text="No valid win rate data.")
            return
        display_results(win_rate_df)
    except Exception as e:
        result_label.config(text=f"Error: {e}")

def display_results(df):
    for widget in result_frame.winfo_children():
        widget.destroy()
    tree = ttk.Treeview(result_frame, columns=list(df.columns), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))
    tree.pack(fill="both", expand=True)

# Main GUI Setup
root = Tk()
root.title("Chess Analysis Tool")
root.geometry("800x600")

Label(root, text="PGN Chess Analyzer", font=("Arial", 16)).pack(pady=10)
Button(root, text="Select PGN File", command=select_file).pack(pady=5)

Label(root, text="Enter Color (White or Black):").pack()
color_input = Text(root, height=1, width=20)
color_input.pack()

result_label = Label(root, text="", fg="red")
result_label.pack(pady=5)

result_frame = ttk.Frame(root)
result_frame.pack(fill="both", expand=True, pady=10)

root.mainloop()