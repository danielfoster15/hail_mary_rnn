from database import *
from models import *
import numpy as np
from sklearn.preprocessing import normalize


def retrieve_players(session):
    players = session.query(Player).all()
    players = [player.id for player in players]

    return players


def get_career_stat_vectors(model_list, players):
    vectors = []
    for player in players:
        vector = []
        for Model, features in model_list:
            all_stats = session.query(Model).filter_by(player_id=player).all()
            if(len(all_stats)) == 0:
                for i in range(0,features):
                    vector.append(0)
            else:
                total_stats_dict = all_stats[0].get_stats()
                for stat in all_stats:
                    for key, value in stat.get_stats().items():
                        total_stats_dict[key] += value
                for key, value in total_stats_dict.items():
                    vector.append(value)
        vector = np.array(vector)
        vectors.append(vector)
    full_vector = np.stack(vectors)
    vectors = normalize(full_vector)
    return vectors


def print_team(Team):
    team_players = session.query(Player).filter_by(team_id=Team).all()
    return team_players


if __name__ == '__main__':

    players = retrieve_players(session)
    model_list = [(Passing, 8), (Receiving, 4), (Rushing, 3), (Secondary, 4),
                  (Tackles, 6), (Fumbles, 4), (KickReturns, 3), (PuntReturns, 3), (Kicks, 4), (Punts, 2)]
    print(get_career_stat_vectors(model_list,  players))
    # print(session.query(Player).filter_by(last_name="Newton").first().first_name)
