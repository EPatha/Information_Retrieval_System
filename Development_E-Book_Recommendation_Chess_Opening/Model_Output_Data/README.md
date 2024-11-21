# Accuracy Winrate Model for Chess Opening Analysis

## Project Overview
This project aims to analyze personal chess gameplay data by focusing on the effectiveness of various opening strategies. By using a Accuracy model, we can evaluate opening moves, identify strengths and weaknesses, and provide insights on optimal strategies based on past game outcomes.

## Model Output: Accuracy Winrate
The model outputs a Accuracy Winrate that categorizes different chess openings and their likely results (Win, Lose, Draw) based on historical gameplay data. Each branch of the tree represents Accuracy points influenced by factors such as:

- **Win Rate**: The success rate of each opening for the player.
- **Moves**: Evaluates the precision of moves played within a given opening.

## How the Model Works
1. **Data Collection**: The raw dataset (in PGN format) from Chess.com is processed and converted to Excel for structured analysis.
2. **Feature Selection**: Relevant features are extracted, including results, moves, opening type, and accuracy.
3. **Training the Decision Tree**: The model uses game data to train the decision tree, focusing on the variables that impact game outcomes.
4. **Model Evaluation**: The decision tree is evaluated to measure accuracy, helping to ensure reliable recommendations for opening strategies.
