# univariate lstm example
from webscraper import get_all_game_urls, get_game_page, get_row_value_where, read_table
from prepare_team_vectors import *
from bs4 import BeautifulSoup, Comment
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from database import session, Base, engine
from sqlalchemy import or_
from keras.models import load_model
HEADERS = {
    'user-agent': 'Daniel Foster/daniel.a.foster@gmail.com/Doing a home project'}

model = load_model('/home/daniel/git/hail_mary_rnn/model-files/best_modelv3.h5', compile=True)


def scrape_game_preview(url, last_week, year,  vector_dict):
    parsed_html = get_game_page(url)
    team_ranks = read_table(parsed_html, "div_teams_ranks", table_in_comment=True,
                            comment_out_of_div=True, clean_column_names=False)
    away_team_abbrev, home_team_abbrev = team_ranks.columns[1], team_ranks.columns[2]
    injury_divs_re = re.compile(r'div_\w+_current_injuries')
    comments = parsed_html.find_all(
        text=lambda text: isinstance(text, Comment))
    count = 0
    for comment in comments:
        table = BeautifulSoup(comment, "html.parser")
        div = table.find_all(id=injury_divs_re)
        if len(div) > 0:
            if count == 0:
                table = div[0].find('table')
                home_injuries = pd.read_html(
                    table.prettify(), header=0, flavor='bs4')[0]
                count += 1
            else:
                table = div[0].find('table')
                away_injuries = pd.read_html(
                    table.prettify(), header=0, flavor='bs4')[0]

    teams = session.query(Team).all()
    games = session.query(Game).filter_by(
        week=last_week).filter(Game.date > year).all()
    for team in teams:
        if team.abbrev.lower() == home_team_abbrev:
            prediction_team = team
            team_injuries = home_injuries
        elif team.abbrev.lower() == away_team_abbrev:
            prediction_opponent = team
            opponent_injuries = away_injuries
    prediction_team_vector, prediction_opponent_vector = None, None
    for game in games:
        ids = game.home_id, game.away_id
        if prediction_team.id in ids:
            if prediction_team.id == game.home_id:
                prediction_team_vector = get_team_vectors(
                    game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_team.id)[0]
            elif prediction_team.id == game.away_id:
                prediction_team_vector = get_team_vectors(
                    game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_team.id)[1]
        elif prediction_opponent.id in ids:
            if prediction_opponent.id == game.home_id:
                prediction_opponent_vector = get_team_vectors(
                    game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_opponent.id)[0]
            elif prediction_opponent.id == game.away_id:
                prediction_opponent_vector = get_team_vectors(
                    game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_opponent.id)[1]
    
    if prediction_team_vector is None:
        games = session.query(Game).filter_by(
        week=last_week-1).filter(Game.date > year).all()
        for game in games:
            ids = game.home_id, game.away_id
            if prediction_team.id in ids:
                if prediction_team.id == game.home_id:
                    prediction_team_vector = get_team_vectors(
                        game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_team.id)[0]
                elif prediction_team.id == game.away_id:
                    prediction_team_vector = get_team_vectors(
                        game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_team.id)[1]
    if prediction_opponent_vector is None:
        print('giants')
        games = session.query(Game).filter_by(
        week=last_week-1).filter(Game.date > year).all()
        for game in games:
            ids = game.home_id, game.away_id
            if prediction_opponent.id in ids:
                    if prediction_opponent.id == game.home_id:
                        prediction_opponent_vector = get_team_vectors(
                            game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_opponent.id)[0]
                    elif prediction_opponent.id == game.away_id:
                        prediction_opponent_vector = get_team_vectors(
                            game, vector_dict, injuries=team_injuries, prediction_team_id=prediction_opponent.id)[1]
            
    return prediction_team_vector, prediction_opponent_vector


if __name__ == '__main__':
    urls = get_all_game_urls(2020, 12, "Preview")
    vector_dict = load_vectors_to_dict('resources/player_vectors.txt')
    for url, week in urls:
        print(url)
        prediction_team_vector, prediction_opponent_vector = scrape_game_preview(
            url, 11, datetime(2020, 1, 1), vector_dict)

        prediction_vector = np.sum(prediction_team_vector, axis=0) - np.sum(prediction_opponent_vector, axis=0)
        prediction_vector = prediction_vector.reshape(1,41)
        prediction = model.predict(prediction_vector)
        max_index_row = np.argmax(prediction, axis=1)[0]
        if max_index_row == 0:
            print('home team wins')
        elif max_index_row == 2:
            print('away team wins')
        elif max_index_row == 1:
            print('tie')