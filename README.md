
**NFL Player Embeddings and Prediction Model**

This repository contains two main components:

1. **Web Scraper**: A Python script `webscraper.py` that scrapes NFL player statistics from 
[pro football reference](https://www.pro-football-reference.com/)
3. **Embedding Generator**: A Python script that takes the scraped 
historical stats and creates embeddings for each player and team.
4. **Prediction Model**: A Python script that trains a prediction model to 
forecast future player performance based on their embeddings versus 
another set of player embeddings up to a certain game.

**Scripts**

* `scrape_nfl_stats.py`: Web scraper script that fetches NFL player stats 
from [pro football reference](https://www.pro-football-reference.com/)
* `create_player_embeddings.py`: Script that takes scraped historical 
stats and generates embeddings for each player.
* `prepare_team_vectors.py` creates a vector for a team based on player vectors of stats up to the date of that game
* `model.py` trains a model using keras with the input vectors and game scores
* `predict.py`: Script that predicts a game with input vectors

**Setup and Usage**

1. Clone this repository to your local machine.
2. Install the required libraries using pip: `pip install -r 
requirements.txt`.
3. Run the web scraper script
4. Run the embedding generator scripts
5. Run the prediction model training script: `python model.py` 
(specify input files, model parameters, etc.)

**Future Work**

* Experiment with different embedding methods and architectures.
* Improve prediction accuracy
* Increase dataset size by incorporating additional sources of data (e.g. 
weather, home and away, coaches, formation styles).
