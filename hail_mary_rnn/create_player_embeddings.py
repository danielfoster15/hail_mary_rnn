from database import *
from models import *
import numpy as np
import re
from sklearn import preprocessing


def retrieve_players(session):
    players = session.query(Player).all()
    players = [player.id for player in players]

    return players


def get_career_stat_vectors(model_list, players):
    vectors = []
    for player in players:
        avg_stats = []
        vector = []
        game_ids = []
        for Model, features in model_list:
            #total number of unique game_ids where this player_id appears
            all_stats = session.query(Model).filter_by(player_id=player).all()
            if(len(all_stats)) == 0:
                for i in range(0,features):
                    vector.append(0)
            else:
                total_stats_dict = all_stats[0].get_stats()
                for stat in all_stats:
                    game_id = stat.game_id
                    if game_id not in game_ids:
                        game_ids.append(game_id)
                    for key, value in stat.get_stats().items():
                        total_stats_dict[key] += value
                for key, value in total_stats_dict.items():
                    if key == 'yards':
                        value = value/100
                    if key == 'qb_rating':
                        value = value/158.3
                    vector.append(value)
        game_count = len(game_ids)
        avg_vector = [abs(i)/game_count for i in vector]
        vector = np.array(vector)
        
        if game_count > 36:
            factor = 3
            avg_vector = np.power(avg_vector, factor)
        else:
            factor = 1 + 2*(game_count/36)
            avg_vector = np.power(avg_vector, factor)
        vector = vector * avg_vector
        
        vectors.append(vector)


    full_vector = np.stack(vectors)
    vectors = preprocessing.scale(full_vector)
    return vectors



def print_team(Team):
    team_players = session.query(Player).filter_by(team_id=Team).all()
    return team_players


if __name__ == '__main__':

    players = retrieve_players(session)
    model_list = [(Passing, 8), (Receiving, 4), (Rushing, 3), (Secondary, 4),
                  (Tackles, 6), (Fumbles, 4), (KickReturns, 3), (PuntReturns, 3), (Kicks, 4), (Punts, 2)]
    vectors = get_career_stat_vectors(model_list,  players)
    pid = 1
    with open('resources/player_vectors.txt', 'w') as f:
        for vector in vectors:
            player = session.query(Player).filter_by(id=pid).first()
            player_name = player.first_name+' '+player.last_name
            player_name = re.sub(' ', '_', player_name)
            f.write(str(pid)+' ')
            pid += 1
            
            for number in vector:
                f.write(str(number)+' ')
            f.write('\n')
    # print(session.query(Player).filter_by(last_name="Newton").first().first_name)
