from database import *
from models import *
import numpy as np
import re
from sklearn import preprocessing

def load_vectors_to_dict(file):
    vector_dict = {}
    with open(file, 'r') as f:
        for line in f:
            player_id, vector = line.strip().split(' ')[0], line.strip().split(' ')[1:]
            vector_dict[player_id] = np.array(vector, dtype=np.float)
    return vector_dict

def get_team_vectors(Game, vector_dict):
    stat_models = [Passing, Rushing, Receiving, Secondary,
                   Tackles, Fumbles, KickReturns, PuntReturns, Punts, Kicks]
    home_players = []
    away_players = []

    away_player_vectors = []
    home_player_vectors = []
    
    for Stat in stat_models:
        for stat_model in session.query(Stat).filter_by(game_id=Game.id, team_id=Game.home_id).all():
            if stat_model.player_id not in home_players:
                home_players.append(stat_model.player_id)
        for stat_model in session.query(Stat).filter_by(game_id=Game.id, team_id=Game.away_id).all():
            if stat_model.player_id not in away_players:
                away_players.append(stat_model.player_id)

    for player in away_players:
        away_player_vectors.append(vector_dict[str(player)])

    for player in home_players:
        home_player_vectors.append(vector_dict[str(player)])

    if len(away_player_vectors) < 48:
        for i in range(len(away_player_vectors), 48):
            away_player_vectors.append(np.zeros(41))
    
    if len(home_player_vectors) < 48:
        for i in range(len(home_player_vectors), 48):
            home_player_vectors.append(np.zeros(41))

    away_team_vector = np.stack(away_player_vectors)
    home_team_vector = np.stack(home_player_vectors)
    
    return home_team_vector, away_team_vector

def get_game_vectors_and_scores(games, vector_dict):
    vectors_by_game = []
    for game in games:
        away_team_vector, home_team_vector = get_team_vectors(game, vector_dict)
        vectors_by_game.append((away_team_vector, home_team_vector, game))
    return vectors_by_game


def get_vector_by_team_and_game(games, Team, vector_dict):
    vectors_and_scores_by_game_and_team = []
    for game in games:
        ids = game.home_id, game.away_id
        if Team.id in ids:
            home_team_vector, away_team_vector = get_team_vectors(game, vector_dict)
            if Team.id == game.home_id:
                team_vector, opponent_vector = home_team_vector, away_team_vector
                team_score = game.home_final
                opponent_score = game.away_final

            elif Team.id == game.away_id:
                opponent_vector, team_vector = home_team_vector, away_team_vector
                team_score = game.away_final
                opponent_score = game.home_final

            vectors_and_scores_by_game_and_team.append((team_vector, opponent_vector, team_score, opponent_score, game.date))
    return vectors_and_scores_by_game_and_team