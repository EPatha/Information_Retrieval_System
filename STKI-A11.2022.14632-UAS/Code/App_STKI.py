import streamlit as st
import chess.pgn
import pandas as pd
import os
import io
import nltk
from nltk.tokenize import word_tokenize
from docx import Document
from PyPDF2 import PdfFileReader
import requests
from bs4 import BeautifulSoup

# Function to download NLTK data
def download_nltk_data():
    with st.spinner('Downloading NLTK data...'):
        nltk.download('punkt')
    st.success('NLTK data downloaded!')

# Function to preprocess text
def preprocess_text(file_content, file_type):
    text = ""
    if file_type == "application/pdf":
        reader = PdfFileReader(file_content)
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file_content)
        for para in doc.paragraphs:
            text += para.text
    tokens = word_tokenize(text.lower())
    return tokens

# Function to search in e-books
def search_engine(query):
    matched_files = []
    dataset_url = "https://github.com/EPatha/Information_Retrieval_System/tree/main/STKI-A11.2022.14632-UAS/Dataset/"
    response = requests.get(dataset_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf') or a['href'].endswith('.docx')]
        for file in files:
            file_url = "https://raw.githubusercontent.com" + file.replace('/blob/', '/')
            response = requests.get(file_url)
            if response.status_code == 200:
                file_type = response.headers['Content-Type']
                with io.BytesIO(response.content) as file_content:
                    tokens = preprocess_text(file_content, file_type)
                    if query in " ".join(tokens):
                        matched_files.append((file_url, file))
    return matched_files

# Function to load PGN files
def load_pgn(uploaded_file):
    games = []
    pgn_content = uploaded_file.read().decode("utf-8")
    pgn_file = io.StringIO(pgn_content)
    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        moves = [move.uci() for move in game.mainline_moves()]
        result = game.headers["Result"]
        games.append({"Moves": moves, "Result": result})
    return games

# Function to compute win rates
def compute_win_rates(data, color):
    openings = {}
    for game in data:
        if len(game["Moves"]) < 2:
            continue
        opening = " ".join([game["Moves"][0][2:], game["Moves"][1][2:]])
        if opening not in openings:
            openings[opening] = {"games": 0, "wins": 0}
        openings[opening]["games"] += 1
        if (color == "white" and game["Result"] == "1-0") or (color == "black" and game["Result"] == "0-1"):
            openings[opening]["wins"] += 1

    analysis = []
    for opening, stats in openings.items():
        if stats["games"] >= 30:  # Filter to include only openings with 30 or more games
            win_rate = (stats["wins"] / stats["games"]) * 100
            analysis.append({"Opening": opening, "Games": stats["games"], "Win Rate (%)": win_rate})

    return pd.DataFrame(analysis)

def main():
    st.title("Recomendation E-Book Recommendation System Based on Opening Chess Weakness Analysis")

    st.markdown(
        """
        Dataset berada di link ini, download dulu di link Google Drive tersebut:
        [Google Drive Dataset](https://drive.google.com/drive/folders/1_FWcpYO7noxe5gpb_DLPTKnc2PVimuzu?usp=sharing)
        """
        """
        Search E-book muncul saat sudah mendapat hasil winrate terendah dari permainan catur yang telah diupload.
        """
    )

    # Download NLTK data
    if 'nltk_data_downloaded' not in st.session_state:
        download_nltk_data()
        st.session_state['nltk_data_downloaded'] = True

    st.sidebar.title("Options")
    tutorial_button = st.sidebar.button("Tutorial")
    if tutorial_button:
        tutorial_text = (
            "Cara Menggunakan Recomendation E-Book Recommendation System Based on Opening Chess Weakness Analysis:\n"
            "1. Dapatkan file PGN dari permainan catur. \n"
            "   (Klik tombol 'Dataset' untuk membuka link Google Drive yang berisi dataset PGN yang tersedia untuk diunduh.)\n"
            "   Atau\n"
            "   (Anda bisa mendapatkan file PGN pribadi atau orang lain dari situs seperti lichess.com atau chess.com.\n"
            "   Pergi ke situs openingtree.com dan masukkan nickname Anda untuk menganalisis permainan Anda.\n"
            "   Setelah analisis selesai, unduh file PGN dari situs tersebut).\n"
            "2. Klik 'Select White PGN' untuk memilih file PGN permainan Anda sebagai putih.\n"
            "3. Klik 'Select Black PGN' untuk memilih file PGN permainan Anda sebagai hitam.\n"
            "4. Setelah kedua file PGN dipilih, klik tombol 'Analyze'.\n"
            "5. Aplikasi akan menganalisis permainan Anda dan menampilkan hasilnya di tabel.\n"
            "6. Hasil evaluasi akan menunjukkan pembukaan yang perlu Anda pelajari lebih lanjut berdasarkan win rate.\n"
            "7. Klik tombol 'Search Moves in E-books' untuk mencari rekomendasi e-book berdasarkan pembukaan yang perlu dipelajari.\n"
            "8. Aplikasi akan menampilkan daftar e-book yang sesuai dengan pembukaan yang perlu dipelajari.\n"
            "9. Klik link e-book untuk membuka e-book tersebut.\n"
            "10. Selamat membaca!"
        )
        st.info(tutorial_text)

    if 'nltk_data_downloaded' in st.session_state and st.session_state['nltk_data_downloaded']:
        white_pgn_file = st.sidebar.file_uploader("Select White PGN file", type=["pgn"])
        black_pgn_file = st.sidebar.file_uploader("Select Black PGN file", type=["pgn"])

        if st.sidebar.button("Analyze"):
            if white_pgn_file is None or black_pgn_file is None:
                st.error("Please select both White and Black PGN files.")
                return

            white_games = load_pgn(white_pgn_file)
            black_games = load_pgn(black_pgn_file)

            white_analysis = compute_win_rates(white_games, "white")
            black_analysis = compute_win_rates(black_games, "black")

            st.subheader("White Analysis")
            st.dataframe(white_analysis)

            st.subheader("Black Analysis")
            st.dataframe(black_analysis)

            white_least_winrate = white_analysis.loc[white_analysis["Win Rate (%)"].idxmin()]
            black_least_winrate = black_analysis.loc[black_analysis["Win Rate (%)"].idxmin()]

            st.subheader("Hasil Evaluasi")
            st.write(f"Pembukaan Putih yang perlu dipelajari = {white_least_winrate['Opening']} (Win Rate: {white_least_winrate['Win Rate (%)']:.2f}%)")
            st.write(f"Pembukaan Hitam yang perlu dipelajari = {black_least_winrate['Opening']} (Win Rate: {black_least_winrate['Win Rate (%)']:.2f}%)")

            search_query = white_least_winrate['Opening'] if white_least_winrate['Win Rate (%)'] < black_least_winrate['Win Rate (%)'] else black_least_winrate['Opening']
            if st.button("Search Moves in E-books"):
                matched_files = search_engine(search_query)
                if matched_files:
                    st.write("Search Results for Query: '{}':".format(search_query))
                    for file_url, file_name in matched_files:
                        st.write(f"- [{file_name}]({file_url})")
                else:
                    st.write("No matching files found.")
    else:
        st.warning("NLTK data is being downloaded. Please wait...")

if __name__ == "__main__":
    main()