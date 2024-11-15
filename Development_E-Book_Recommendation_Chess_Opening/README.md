# Development of an E-Book Recommendation System Based on Opening Chess Weakness Analysis

## Project Description

This project aims to develop an **e-book recommendation system** that suggests books based on the analysis of weaknesses in chess openings. The system utilizes **data retrieval techniques** to find relevant e-books and provide recommendations that can help chess players improve their understanding of and strategies for opening play.

The project uses **personal PGN data** obtained from chess games on Chess.com, which is then analyzed using **data mining techniques**. The results of this analysis are used to recommend e-books focused on improving players' performance in chess openings that are identified as weak.

## Key Features
- **Chess Opening Weakness Analysis**: Identifies ineffective or suboptimal openings based on personal PGN game data.
- **E-Book Recommendations**: Suggests relevant e-books in PDF and DOCX formats to help improve understanding of effective chess openings.
- **Data Retrieval**: Retrieves and recommends e-books based on the identified weaknesses in a player's chess openings.

## Datasets

### 1. **Data Retrieval Dataset**  
This dataset consists of **8 e-books** in **PDF and DOCX** formats, covering various topics related to chess strategy, particularly opening theory. These e-books are used to recommend books based on the analysis of weaknesses in chess openings.

### 2. **Opening Weakness Analysis Dataset**  
The dataset for analyzing opening weaknesses consists of **personal PGN game data** obtained from **Chess.com** via **OpeningTree.com**. This data is converted into personal **PGN files** and used to analyze the effectiveness of different chess openings in personal games.

## Workflow

1. **Data Collection**: Collect chess game data (PGN files) and e-books.
2. **Data Preprocessing**: Clean the PGN data and e-book text (lowercasing, stemming, stopword removal).
3. **Feature Extraction**: Use techniques like **TF-IDF** and **word embeddings** to extract relevant features from game data and e-books.
4. **Model Training**: Train a machine learning model, such as **Support Vector Machine (SVM)**, to classify chess openings as optimal or suboptimal.
5. **Recommendation Generation**: Based on the analysis of opening weaknesses, the system generates recommendations for relevant e-books.
