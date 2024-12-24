import os
from tkinter import Tk, Label, Button, ttk
from external_processing import preprocess_text  # Import dari external_processing.py
import nltk

# Menambahkan path untuk nltk_data
nltk.data.path.append('/home/ep/nltk_data')

# Folder berisi file lokal (PDF dan DOCX)
LOCAL_FILES_DIR = "/home/ep/Documents/Github/Information_Retrieval_System/Analyze_E-book/Dataset"

# Debugging: Pastikan resource 'punkt' tersedia
try:
    nltk.download('punkt')
except Exception as e:
    print(f"Error downloading NLTK punkt resource: {e}")

def process_local_files():
    """
    Process all PDF and DOCX files in the local directory.
    :return: List of dictionaries containing file names and tokens.
    """
    local_data = []
    if not os.path.exists(LOCAL_FILES_DIR):
        print(f"Directory {LOCAL_FILES_DIR} tidak ditemukan.")
        return local_data

    for file_name in os.listdir(LOCAL_FILES_DIR):
        file_path = os.path.join(LOCAL_FILES_DIR, file_name)
        if file_path.endswith((".pdf", ".docx")):
            try:
                tokens = preprocess_text(file_path)
                local_data.append({
                    "file": file_name,
                    "tokens": tokens,
                    "token_count": len(tokens)
                })
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
    return local_data

def display_results(local_files_data):
    """
    Display the results of processed local files in the GUI.
    :param local_files_data: List of tokenized data from local files.
    """
    for widget in result_frame.winfo_children():
        widget.destroy()

    if not local_files_data:
        Label(result_frame, text="No files processed.", font=("Arial", 12, "bold"), fg="red").pack()
        return

    Label(result_frame, text="Local Files Preprocessing Results", font=("Arial", 12, "bold")).pack()
    for file_data in local_files_data:
        Label(result_frame, text=f"File: {file_data['file']}").pack()
        Label(result_frame, text=f"Token Count: {file_data['token_count']}").pack()
        Label(result_frame, text="Tokens: " + ", ".join(file_data['tokens'][:20]) + "...").pack(pady=5)

def process_and_display_local_files():
    """
    Process local files and update the GUI with results.
    """
    try:
        local_files_data = process_local_files()
        display_results(local_files_data)
    except Exception as e:
        result_label.config(text=f"Error: {e}")

# Main GUI Setup
root = Tk()
root.title("Local File Preprocessing Tool")
root.geometry("800x600")

Label(root, text="Preprocess Local PDF and DOCX Files", font=("Arial", 16)).pack(pady=10)
Button(root, text="Process Local Files", command=process_and_display_local_files).pack(pady=5)

result_label = Label(root, text="", fg="red")
result_label.pack(pady=5)

result_frame = ttk.Frame(root)
result_frame.pack(fill="both", expand=True, pady=10)

root.mainloop()
