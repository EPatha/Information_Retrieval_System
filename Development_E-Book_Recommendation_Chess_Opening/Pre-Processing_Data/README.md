**PGN Data Preprocessing**:
   - The collected **PGN data** from Chess.com will be preprocessed to convert it into a more analyzable format.
   - The **preprocessing** steps include:
     - **Opening Name Extraction**: Identify the names of the chess openings used in the games from the PGN data.
     - **Opening Accuracy Calculation**: For each opening used, calculate the success rate based on the game results (e.g., win percentage for a particular opening).
     - **Weak Opening Identification**: Openings with the **lowest accuracy**, whether played by **White or Black**, will be considered as weak openings that need improvement.
