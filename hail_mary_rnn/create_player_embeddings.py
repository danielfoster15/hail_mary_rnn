from database import *
from models import *
import numpy as np
import re
from sklearn import preprocessing
from collections import OrderedDict


def retrieve_players(session):
    players = session.query(Player).all()
    players = [player.id for player in players]

    return players


def get_career_stats(model_list, players):
    career_stats_per_player = []
    for player in players:
        avg_stats = []
        career_stats = OrderedDict()
        game_ids = []
        for model_instance, features in model_list:
            model_keys = list(model_instance.get_stats(model_instance).keys())
            # total number of unique game_ids where this player_id appears
            all_stats = session.query(model_instance).filter_by(player_id=player).all()
            if (len(all_stats)) == 0:
                for i in range(0, features):
                    career_stats[model_keys[i]] = 0
            else:
                total_stats_dict = all_stats[0].get_stats()
                for stat in all_stats:
                    game_id = stat.game_id
                    if game_id not in game_ids:
                        game_ids.append(game_id)
                    for key, value in stat.get_stats().items():
                        total_stats_dict[key] += value
                for key, value in total_stats_dict.items():
                    if key == "yards":
                        value = value / 100
                    if key == "qb_rating":
                        value = value / 158.3
                    career_stats[key] = value
        career_stats["game_count"] = len(game_ids)
        career_stats_per_player.append(career_stats)

    return career_stats_per_player


def normalize_vector(career_stats_per_player):
    vectors = []
    for career_stats in career_stats_per_player:
        avg_vector = [
            abs(i) / career_stats["game_count"] for i in career_stats.values()
        ]
        if career_stats["game_count"] > 36:
            factor = 3
            avg_vector = np.power(avg_vector, factor)
        else:
            factor = 1 + 2 * (game_count / 36)
            avg_vector = np.power(avg_vector, factor)
        vector = vector * avg_vector

        vector = np.array(vector)
        vectors.append(vector)
    full_vector = np.stack(vectors)
    vectors = preprocessing.scale(full_vector)

    return vectors


def print_team(Team):
    team_players = session.query(Player).filter_by(team_id=Team).all()
    return team_players


if __name__ == "__main__":
    players = retrieve_players(session)
    model_list = [
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
    vectors = get_career_stats(model_list, players)
    pid = 1
    with open("resources/player_vectors23_labels.txt", "w") as f:
        for vector in vectors:
            player = session.query(Player).filter_by(id=pid).first()
            player_name = player.first_name + " " + player.last_name
            player_name = re.sub(" ", "_", player_name)
            # f.write(str(pid)+' ')
            f.write(player_name + " ")
            pid += 1

            for number in vector:
                f.write(str(number) + " ")
            f.write("\n")
    # print(session.query(Player).filter_by(last_name="Newton").first().first_name)
