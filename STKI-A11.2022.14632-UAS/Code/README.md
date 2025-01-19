### Penjelasan Kode

1. **Import Libraries**:
   Mengimpor pustaka yang diperlukan seperti `streamlit`, `chess.pgn`, `pandas`, `os`, `io`, `nltk`, `docx`, `PyPDF2`, `requests`, dan `BeautifulSoup`.

2. **Download NLTK Data**:
   Fungsi `download_nltk_data` digunakan untuk mengunduh data NLTK dan menampilkan indikator pemuatan.

3. **Preprocess Text**:
   Fungsi `preprocess_text` digunakan untuk membaca dan memproses teks dari file PDF dan DOCX. Teks yang diekstrak kemudian di-tokenisasi menggunakan NLTK.

4. **Search Engine**:
   Fungsi `search_engine` digunakan untuk mencari e-book dari URL GitHub berdasarkan nama file. Fungsi ini mengunduh file e-book, memproses teksnya, dan mencari query yang diberikan.

5. **Load PGN Files**:
   Fungsi `load_pgn` digunakan untuk memuat file PGN dan mengurai permainan catur. Setiap permainan diurai menjadi daftar gerakan dan hasil.

6. **Compute Win Rates**:
   Fungsi `compute_win_rates` digunakan untuk menghitung win rate untuk setiap pembukaan berdasarkan warna. Hanya pembukaan dengan 30 atau lebih permainan yang disertakan dalam analisis.

7. **Main Function**:
   Fungsi `main` digunakan untuk membuat antarmuka pengguna menggunakan Streamlit. Ini termasuk judul, teks informasi tentang link dataset, tombol, pemuat file PGN, dan fitur pencarian. Tombol lain dinonaktifkan selama proses pemuatan data NLTK.

8. **Run Application**:
   Memanggil fungsi `main` untuk menjalankan aplikasi Streamlit.

### Fitur NLTK dan Pencarian E-Book

#### NLTK (Natural Language Toolkit)
NLTK adalah pustaka Python yang menyediakan alat untuk bekerja dengan teks, termasuk tokenisasi, stemming, dan analisis teks lainnya. Dalam proyek ini, NLTK digunakan untuk:
- **Tokenisasi**: Memecah teks menjadi kata-kata atau token individu untuk analisis lebih lanjut.

#### Pencarian E-Book
Fitur pencarian e-book memungkinkan pengguna untuk mencari e-book yang relevan berdasarkan analisis kelemahan pembukaan catur. Prosesnya meliputi:
- **Mengunduh dan Memproses E-Book**: E-book dalam format PDF dan DOCX diunduh dari URL GitHub dan diproses untuk mengekstrak teks.
- **Mencocokkan Query**: Teks yang diekstrak dibandingkan dengan query yang diberikan untuk menemukan e-book yang relevan.
- **Menampilkan Hasil**: Hasil pencarian ditampilkan dalam bentuk daftar link e-book yang cocok dengan query.

### Menjalankan Aplikasi Streamlit

Untuk menjalankan aplikasi Streamlit, gunakan perintah berikut di terminal:

```sh
streamlit run /home/ep/Documents/Github/Information_Retrieval_System/STKI-A11.2022.14632-UAS/Code/App_STKI.py
```

Ini akan membuka aplikasi Streamlit di peramban web Anda, dan Anda dapat menggunakan antarmuka web untuk memuat file PGN, menganalisis permainan catur, melihat hasil evaluasi, dan mencari gerakan dalam e-book berdasarkan hasil evaluasi win rate terendah.
```
