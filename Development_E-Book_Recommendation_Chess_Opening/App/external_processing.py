import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import docx
from PyPDF2 import PdfReader

nltk.download('punkt')
nltk.download('stopwords')

# Text Preprocessing Functions
def simple_tokenizer(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalnum() and word not in stop_words]

def preprocess_text(file_path):
    """
    Preprocess the text of a given file (PDF or DOCX).
    :param file_path: Path to the file.
    :return: List of tokens.
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    return simple_tokenizer(text)
