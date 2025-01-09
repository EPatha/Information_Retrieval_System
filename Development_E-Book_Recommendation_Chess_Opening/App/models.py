import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import chess.pgn
import pandas as pd
from tkinter import font
import os

class ChessAnalysisModel:
    def __init__(self):
        self.white_pgn_path = None
        self.black_pgn_path = None
        self.white_analysis = None
        self.black_analysis = None

    def process_pgn(self, pgn_path):
        data = []
        try:
            with open(pgn_path, "r") as file:
                while True:
                    game = chess.pgn.read_game(file)
                    if game is None:
                        break
                    moves = list(game.mainline_moves())
                    result = game.headers.get("Result", "*")
                    data.append((moves, result))
        except Exception as e:
            print(f"Error processing PGN file: {e}")
            return None
        return data

    def compute_win_rates(self, data, color):
        openings = {}

        for moves, result in data:
            if len(moves) < 2:
                continue
            opening = " ".join([str(moves[0]), str(moves[1])])
            if opening not in openings:
                openings[opening] = {"games": 0, "wins": 0}

            openings[opening]["games"] += 1
            if (result == "1-0" and color == "white") or (result == "0-1" and color == "black"):
                openings[opening]["wins"] += 1

        result_list = []
        for opening, stats in openings.items():
            games = stats["games"]
            win_rate = (stats["wins"] / games * 100) if games > 0 else 0
            result_list.append((opening, games, round(win_rate, 2)))

        return result_list

class ChessAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Opening Analyzer")
        self.root.geometry("800x600")
        self.model = ChessAnalysisModel()

        # Font settings
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        section_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Section for White PGN
        self.white_frame = ttk.LabelFrame(root, text="White PGN", padding=10)
        self.white_frame.pack(fill=tk.X, padx=10, pady=5)

        self.white_pgn_label = tk.Label(self.white_frame, text="File: None", font=section_font)
        self.white_pgn_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.white_pgn_button = tk.Button(self.white_frame, text="Select PGN", command=self.select_white_pgn)
        self.white_pgn_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Section for Black PGN
        self.black_frame = ttk.LabelFrame(root, text="Black PGN", padding=10)
        self.black_frame.pack(fill=tk.X, padx=10, pady=5)

        self.black_pgn_label = tk.Label(self.black_frame, text="File: None", font=section_font)
        self.black_pgn_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.black_pgn_button = tk.Button(self.black_frame, text="Select PGN", command=self.select_black_pgn)
        self.black_pgn_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Section for File Conversion
        self.convert_frame = ttk.LabelFrame(root, text="File Conversion", padding=10)
        self.convert_frame.pack(fill=tk.X, padx=10, pady=5)

        self.convert_button = tk.Button(self.convert_frame, text="Convert File to TXT", command=self.convert_file_to_txt)
        self.convert_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Action buttons
        self.action_frame = ttk.Frame(root, padding=10)
        self.action_frame.pack(fill=tk.X, padx=10, pady=5)

        self.analyze_button = tk.Button(self.action_frame, text="Analyze", command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.filter_button = tk.Button(self.action_frame, text="Most Used Opening", command=self.filter_most_used_openings)
        self.filter_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.action_frame, text="Save to Excel", command=self.save_to_excel, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Results TreeView
        self.result_frame = ttk.LabelFrame(root, text="Results", padding=10)
        self.result_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        self.tree = ttk.Treeview(self.result_frame, columns=("Opening", "Games", "Win Rate (%)"), show='headings', height=15)
        self.tree.heading("Opening", text="Opening")
        self.tree.heading("Games", text="Games")
        self.tree.heading("Win Rate (%)", text="Win Rate (%)")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def select_white_pgn(self):
        self.model.white_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.model.white_pgn_path:
            self.white_pgn_label.config(text=f"File: {self.model.white_pgn_path}")

    def select_black_pgn(self):
        self.model.black_pgn_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if self.model.black_pgn_path:
            self.black_pgn_label.config(text=f"File: {self.model.black_pgn_path}")

    def convert_file_to_txt(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if not file_path:
            return

        file_extension = os.path.splitext(file_path)[-1].lower()
        if file_extension not in [".pdf", ".torrent", ".docx", ".pgn"]:
            messagebox.showerror("Error", "Unsupported file type.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not output_path:
            return

        try:
            with open(file_path, "r") as infile, open(output_path, "w") as outfile:
                content = infile.read()
                outfile.write(content)

            messagebox.showinfo("Success", f"File converted to {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file: {e}")

    def analyze(self):
        if not self.model.white_pgn_path or not self.model.black_pgn_path:
            messagebox.showerror("Error", "Please select both White and Black PGN files.")
            return

        white_data = self.model.process_pgn(self.model.white_pgn_path)
        black_data = self.model.process_pgn(self.model.black_pgn_path)

        if not white_data or not black_data:
            messagebox.showerror("Error", "Unable to process one or both PGN files.")
            return

        self.model.white_analysis = self.model.compute_win_rates(white_data, "white")
        self.model.black_analysis = self.model.compute_win_rates(black_data, "black")
        self.display_results()
        self.save_button.config(state=tk.NORMAL)

    def display_results(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add header for White results
        self.tree.insert("", tk.END, values=("White:", "", ""), tags=("header",))
        for entry in self.model.white_analysis:
            self.tree.insert("", tk.END, values=entry, tags=("white",))

        # Add a separator row
        self.tree.insert("", tk.END, values=("", "", ""), tags=("separator",))

        # Add header for Black results
        self.tree.insert("", tk.END, values=("Black:", "", ""), tags=("header",))
        for entry in self.model.black_analysis:
            self.tree.insert("", tk.END, values=entry, tags=("black",))

        # Apply styles
        self.tree.tag_configure("header", font=("Helvetica", 12, "bold"), background="#f0f0f0")
        self.tree.tag_configure("white", background="#e6f7ff")
        self.tree.tag_configure("black", background="#fff3e6")
        self.tree.tag_configure("separator", background="#ffffff")

    def filter_most_used_openings(self):
        if not self.model.white_analysis or not self.model.black_analysis:
            messagebox.showerror("Error", "No data to filter. Please analyze first.")
            return

        self.model.white_analysis = [entry for entry in self.model.white_analysis if entry[1] >= 30]
        self.model.black_analysis = [entry for entry in self.model.black_analysis if entry[1] >= 30]

        self.display_results()

    def save_to_excel(self):
        if not self.model.white_analysis or not self.model.black_analysis:
            messagebox.showerror("Error", "No data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        white_df = pd.DataFrame(self.model.white_analysis, columns=["Opening", "Games", "Win Rate (%)"])
        black_df = pd.DataFrame(self.model.black_analysis, columns=["Opening", "Games", "Win Rate (%)"])

        with pd.ExcelWriter(file_path) as writer:
            white_df.to_excel(writer, sheet_name="White", index=False)
            black_df.to_excel(writer, sheet_name="Black", index=False)

        messagebox.showinfo("Success", f"Results saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessAnalysisApp(root)
    root.mainloop()