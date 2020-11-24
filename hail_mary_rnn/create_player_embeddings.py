from database import *
from models import *


def retrieve_players(session):
    players = session.query(Player).all()
    players = [player.id for player in players]

    return players


def get_career_stat_vector(Model, players):
    for player in players[:5]:
        print(player)
        all_stats = session.query(Model).filter_by(player_id=player).all()
        total_stats_dict = all_stats[0].get_stats()
        avg_stats_dict = {}
        counter = 0
        for stat in all_stats:
            for key, value in stat.get_stats().items():
                total_stats_dict[key] += value
            counter+=1
        print("counter: ",counter)
        print(total_stats_dict, avg_stats_dict)    

def print_team(Team):
    team_players = session.query(Player).filter_by(team_id=Team).all()
    return team_players
if __name__ == '__main__':

    #players = retrieve_players(session)
    #get_career_stat_vector(Passing, players)
    print(session.query(Player).filter_by(last_name="Newton").first().first_name)