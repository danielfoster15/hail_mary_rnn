from database import *
from models import *
from sqlalchemy import and_
import numpy as np
import time
from sklearn import preprocessing
from collections import OrderedDict, defaultdict

MODEL_LIST = [
    (Passing, 8),
    (Receiving, 4),
    (Rushing, 3),
    (Secondary, 4),
    (Tackles, 6),
    (Fumbles, 4),
    (KickReturns, 3),
    (PuntReturns, 3),
    (Kicks, 4),
    (Punts, 2),
]


def load_vectors_to_dict(file):
    vector_dict = {}
    with open(file, "r") as f:
        for line in f:
            player_id, vector = line.strip().split(" ")[0], line.strip().split(" ")[1:]
            vector_dict[player_id] = np.array(vector, dtype=np.float32)
    return vector_dict


def normalize_vector(career_stats):
    vector = np.array(list(career_stats.values()))
    avg_vector = [
        abs(i) / career_stats["game_count"] if career_stats["game_count"] > 0 else 0
        for i in career_stats.values()
    ]
    if career_stats["game_count"] > 36:
        factor = 3
        avg_vector = np.power(avg_vector, factor)
    else:
        factor = 1 + 2 * (career_stats["game_count"] / 36)
        avg_vector = np.power(avg_vector, factor)
    vector = vector * avg_vector

    vector = np.array(vector)

    return vector


def get_career_stats_up_to_date(player, game_instance, model_list=MODEL_LIST):
    career_stats = OrderedDict()
    game_ids = set()
    filtered_games = [
        game.id
        for game in session.query(Game).filter(Game.date < game_instance.date).all()
    ]
    for model_instance, features in model_list:
        model_keys = [
            model_instance.__tablename__ + "_" + k
            for k in list(model_instance.get_stats(model_instance).keys())
        ]
        total_stats_dict = {k: 0 for k in model_keys}
        # total number of unique game_ids where this player_id appears
        # Get stats filtered by date
        all_stats = (
            session.query(model_instance)
            .filter(model_instance.game_id.in_(filtered_games))
            .filter(model_instance.player_id == player)
            .all()
        )

        if (len(all_stats)) == 0:
            for i in range(0, features):
                career_stats[model_keys[i]] = 0
        else:
            # building the career stats dictionary
            for stat in all_stats:
                game_ids.add(stat.game_id)
                stats = stat.get_stats()
                for key, value in stats.items():
                    total_stats_dict[f"{model_instance.__tablename__}_{key}"] += value

            # normalizing some values in the career stats dictionary and adding to career_stats
            for key, value in total_stats_dict.items():
                if "yards" in key:
                    value /= 100
                elif "qb_rating" in key:
                    value /= 158.3
                career_stats[key] = value
    career_stats["game_count"] = len(game_ids)

    return career_stats


def get_team_vectors(team, game_instance):
    stat_models = [
        Passing,
        Rushing,
        Receiving,
        Secondary,
        Tackles,
        Fumbles,
        KickReturns,
        PuntReturns,
        Punts,
        Kicks,
    ]
    players = {}
    player_vectors = []
    for stat_instance in stat_models:
        stats = (
            session.query(stat_instance)
            .filter_by(game_id=game_instance.id, team_id=team)
            .all()
        )
        for stat_model in stats:
            players[stat_model.player_id] = []
    for player in players:
        player_vectors.append(
            normalize_vector(get_career_stats_up_to_date(str(player), game_instance))
        )
    while len(player_vectors) < 48:
        player_vectors.append(np.zeros(42))
    team_vector = preprocessing.scale(np.stack(player_vectors))

    return team_vector


def get_home_away_vector(game_instance):
    home_id = game_instance.home_id
    away_id = game_instance.away_id

    away_team_vector = get_team_vectors(away_id, game_instance)
    home_team_vector = get_team_vectors(home_id, game_instance)

    return np.sum(away_team_vector, axis=0), np.sum(home_team_vector, axis=0)


def get_game_vectors(games):
    game_vectors = {}
    for game in games:
        print(game.game)
        start = time.time()
        away_team_vector, home_team_vector = get_home_away_vector(game)
        end = time.time()
        print(f"getvectors execution time: {end - start} seconds")

        game_vectors[game.game] = (
            away_team_vector.tolist(),
            home_team_vector.tolist(),
            game.away_final,
            game.home_final,
        )
    return game_vectors
