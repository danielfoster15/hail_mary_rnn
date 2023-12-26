from database import *
from models import *
import numpy as np
import re
from sklearn import preprocessing
from collections import OrderedDict

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
    game_ids = []
    for model_instance, features in model_list:
        model_keys = [
            model_instance.__tablename__ + "_" + k
            for k in list(model_instance.get_stats(model_instance).keys())
        ]
        # total number of unique game_ids where this player_id appears
        # Get stats filtered by date
        all_stats = (
            session.query(model_instance)
            .filter_by(player_id=player)
            .filter(Game.date < game_instance.date)  # Apply the date filter
            .all()
        )

        if (len(all_stats)) == 0:
            for i in range(0, features):
                career_stats[model_keys[i]] = 0
        else:
            total_stats_dict = all_stats[0].get_stats()
            # building the career stats dictionary
            for stat in all_stats:
                game_id = stat.game_id
                if game_id not in game_ids:
                    game_ids.append(game_id)
                for key, value in stat.get_stats().items():
                    total_stats_dict[key] += value
            # normalizing some values in the career stats dictionary and adding to career_stats
            for key, value in total_stats_dict.items():
                if key == "yards":
                    value = value / 100
                if key == "qb_rating":
                    value = value / 158.3
                career_stats[model_instance.__tablename__ + "_" + key] = value
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
    players = []
    player_vectors = []

    for stat_instance in stat_models:
        for stat_model in (
            session.query(stat_instance)
            .filter_by(game_id=game_instance.id, team_id=team)
            .all()
        ):
            if stat_model.player_id not in players:
                players.append(stat_model.player_id)

        for player in players:
            # call function here
            player_vectors.append(
                normalize_vector(
                    get_career_stats_up_to_date(str(player), game_instance)
                )
            )

        if len(player_vectors) < 48:
            for i in range(len(player_vectors), 48):
                player_vectors.append(np.zeros(42))
    team_vector = preprocessing.scale(np.stack(player_vectors))

    return team_vector


def get_home_away_vector(game_instance):
    home_id = game_instance.home_id
    away_id = game_instance.away_id

    away_team_vector = get_team_vectors(away_id, game_instance)
    home_team_vector = get_team_vectors(home_id, game_instance)

    return away_team_vector, home_team_vector


def get_game_vectors_and_scores(games):
    vectors_by_game = []
    for game in games:
        away_team_vector, home_team_vector = get_home_away_vector(game)
        vectors_by_game.append((away_team_vector, home_team_vector, game))
    return vectors_by_game


def get_vector_by_team_and_game(games, team_instance):
    vectors_and_scores_by_game_and_team = []
    for game in games:
        ids = game.home_id, game.away_id
        if team_instance.id in ids:
            away_team_vector, home_team_vector = get_home_away_vector(game)
            if team_instance.id == game.home_id:
                team_vector, opponent_vector = home_team_vector, away_team_vector
                team_score = game.home_final
                opponent_score = game.away_final

            elif team_instance.id == game.away_id:
                opponent_vector, team_vector = home_team_vector, away_team_vector
                team_score = game.away_final
                opponent_score = game.home_final

            vectors_and_scores_by_game_and_team.append(
                (team_vector, opponent_vector, team_score, opponent_score, game.date)
            )
    return vectors_and_scores_by_game_and_team
