from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, Date, String, Interval
from sqlalchemy.orm import relationship
from .database import Base


from datetime import datetime


class NFLGame(Base):
    __tablename__ = "games"

    # main columns
    id = Column('id', Integer, primary_key=True)
    game = Column('game', String, unique=True)
    home_team = Column('home_team', String, unique=True)
    away_team = Column('away_team', String, unique=True)
    date = Column('date', Date)

    #relationships
    passing = relationship('Passing', backref='game')
    rushing = relationship('Rushing', backref='game')
    receiving = relationship('Receiving', backref='game')
    secondary = relationship('Secondary', backref='game')
    tackles = relationship('Tackles', backref='game')
    fumbles = relationship('Fumbles', backref='game')
    punt_returns = relationship('PuntReturns', backref='game')
    kick_returns = relationship('KickReturns', backref='game')
    punts = relationship('Punts', backref='game')
    kicks = relationship('Kicks', backref='game')

    # scoring
    home_final = Column('home_final', Integer)
    home_first = Column('home_first', Integer)
    home_second = Column('home_second', Integer)
    home_third = Column('home_third', Integer)
    home_fourth = Column('home_fourth', Integer)
    home_ot = Column('home_ot', Integer)
    home_ot2 = Column('home_ot2', Integer)

    away_final = Column('away_final', Integer)
    away_first = Column('away_first', Integer)
    away_second = Column('away_second', Integer)
    away_third = Column('away_third', Integer)
    away_fourth = Column('away_fourth', Integer)
    away_ot = Column('away_ot', Integer)
    away_ot2 = Column('away_ot2', Integer)

    # game_info
    won_toss = Column('won_toss', String)
    roof = Column('roof', String)
    surface = Column('surface', String)
    duration = Column('duration', Interval)
    #weather = Column('weather', String)
    temp = Column('temp', Integer)
    humidity = Column('humidity', Integer)
    wind = Column('wind', Integer)
    wind_chill = Column('wind_chill', Integer)
    vegas_line = Column('vegas_line', String)
    vegas_line_num = Column('vegas_line_num', Float)
    over_under = Column('over_under', String)
    over_under_num = Column('over_under_num', Float)
    week = Column('week', Integer)

    def __init__(self, home_team, away_team, date, scores, game_info):
        self.home_team = home_team
        self.away_team = away_team
        self.date = date

        self.home_final = scores['home_scoring']['home_score']['final']
        self.home_first = scores['home_scoring']['home_score']['1']
        self.home_second = scores['home_scoring']['home_score']['2']
        self.home_third = scores['home_scoring']['home_score']['3']
        self.home_fourth = scores['home_scoring']['home_score']['4']
        if game_info['ot']:
            self.home_ot = scores['home_scoring']['home_score']['ot']
        if game_info['ot2']:
            self.home_ot2 = scores['home_scoring']['home_score']['ot2']

        self.away_final = scores['away_scoring']['away_score']['final']
        self.away_first = scores['away_scoring']['away_score']['1']
        self.away_second = scores['away_scoring']['away_score']['2']
        self.away_third = scores['away_scoring']['away_score']['3']
        self.away_fourth = scores['away_scoring']['away_score']['4']
        if game_info['ot']:
            self.away_ot = scores['away_scoring']['away_score']['ot']
        if game_info['ot2']:
            self.away_ot = scores['away_scoring']['away_score']['ot2']

        self.won_toss = game_info['won_toss']
        self.roof = game_info['roof']
        self.surface = game_info['surface']
        self.duration = game_info['duration']
        self.vegas_line = game_info['vegas_line']
        self.vegas_line_num = game_info['vegas_line_num']
        self.over_under = game_info['over_under']
        self.over_under_num = game_info['over_under_num']
        self.week = game_info['week']
        self.game = self.home_team+"_vs_"+self.away_team+"_week_" + \
            str(self.game_info['week'])+"_"+self.date.strftime("%m%d%Y")

    def to_string(self):
        return self.home_team+"_vs_"+self.away_team+"_week_"+str(self.game_info['week'])+"_"+self.date.strftime("%m%d%Y")


class Player(Base):
    # main columns
    id = Column('id', Integer, primary_key=True)
    first_name = Column('game', String)
    last_name = Column('home_team', String, unique=True)
    full_name = Column('away_team', String, unique=True)
    
    passing = relationship('Passing', backref='player')
    rushing = relationship('Rushing', backref='player')
    receiving = relationship('Receiving', backref='player')
    secondary = relationship('Secondary', backref='player')
    tackles = relationship('Tackles', backref='player')
    fumbles = relationship('Fumbles', backref='player')
    punt_returns = relationship('PuntReturns', backref='player')
    kick_returns = relationship('KickReturns', backref='player')
    punts = relationship('Punts', backref='player')
    kicks = relationship('Kicks', backref='player')

    def __init__(self, first_name, last_name, id):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = first_name+' '+last_name
        self.nfldb_id = id
        self.position = []
        self.teams_by_year = {}
        self.stats_by_game = {}

    # def add_team_for_year(self, team, year):
    #     if year in self.teams_by_year.keys():
    #         if team not in self.teams_by_year[year]:
    #             self.teams_by_year[year].append(team)
    #     else:
    #         self.teams_by_year[year] = team

    # def add_stats_from_game(self, NFLGame, PlayerStats):
    #     if PlayerStats.first_name+" "+PlayerStats.last_name == self.first_name+" "+self.last_name:
    #         if NFLGame.to_string() not in self.stats_by_game:
    #             self.stats_by_game[NFLGame.to_string()] = PlayerStats
    #         else:
    #             print("this game already has stats")
    #     else:
    #         print("this is the wrong player!")

    # def overwrite_stats_from_game(self, NFLGame, PlayerStats):
    #     if PlayerStats.first_name+" "+PlayerStats.last_name == self.first_name+" "+self.last_name:
    #         if NFLGame.to_string() in self.stats_by_game.keys():
    #             self.stats_by_game[NFLGame.to_string()] = PlayerStats
    #         else:
    #             print("game not found")
    #     else:
    #         print("this is the wrong player!")

    # def add_position(self, positions_df):
    #     for index, row in positions_df.iterrows():
    #         if (row['player'].lower() == self.full_name) & (row['id'] == self.id):
    #             if row['pos'] not in self.position:
    #                 self.position.append(row['pos'])


class Passing(Base):
    __tablename__ = "passing"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    completions = Column('completions', Integer)
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    interceptions = Column('interceptions', Integer)
    sacked = Column('sacked', Integer)
    sacked_yds = Column('sacked_yds', Integer)
    longest = Column('longest', Integer)
    qb_rating = Column('qb_rating', Float)

    def __init__(self, first_name, last_name, id, passing, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.completions = passing['completions']
        self.attempts = passing['attempts']
        self.yards = passing['yards']
        self.touchdowns = passing['touchdowns']
        self.interceptions = passing['interceptions']
        self.sacked = passing['sacked']
        self.sack_yards = passing['sack_yards']
        self.longest = passing['longest']
        self.qb_rating = passing['qb_rating']


class Rushing(Base):
    __tablename__ = "rushing"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, rushing, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.attempts = rushing['attempts']
        self.yards = rushing['yards']
        self.touchdowns = rushing['touchdowns']
        self.longest = rushing['longest']


class Receiving(Base):

    __tablename__ = "receiving"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    receptions = Column('receptions', Integer)
    targeted = Column('targeted', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, receiving, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.receptions = receiving['receptions']
        self.targeted = ['targeted']
        self.yards = ['yards']
        self.touchdowns = ['touchdowns']
        self.longest = ['longest']


class Secondary(Base):

    __tablename__ = "secondary"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    interceptions = Column('interceptions', Integer)
    passes_defended = Column('passes_defended', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, secondary, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.interceptions = secondary['interceptions']
        self.passes_defended = secondary['passes_defended']
        self.yards = secondary['yards']
        self.touchdowns = secondary['touchdowns']
        self.longest = secondary['longest']


class Tackles(Base):

    __tablename__ = "tackles"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    sacks = Column('sacks', Integer)
    combined = Column('combined', Integer)
    solo = Column('solo', Integer)
    assists = Column('assists', Integer)
    tackles_for_loss = Column('tackles_for_loss', Integer)
    qb_hits = Column('qb_hits', Integer)

    def __init__(self, first_name, last_name, id, tackles, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.sacks = tackles['sacks']
        self.combined = tackles['combined']
        self.solo = tackles['solo']
        self.assists = tackles['assists']
        self.tackles_for_loss = tackles['tackles_for_loss']
        self.qb_hits = tackles['qb_hits']


class Fumbles(Base):

    __tablename__ = "fumbles"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    forced = Column('forced', Integer)
    recovered = Column('recovered', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)

    def __init__(self, first_name, last_name, id, fumbles, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.forced = fumbles['forced']
        self.recovered = fumbles['recovered']
        self.yards = fumbles['yards']
        self.touchdowns = fumbles['touchdowns']


class PuntReturns(Base):

    __tablename__ = "punt_returns"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, punt_returns, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.returns = punt_returns['returns']
        self.yards = punt_returns['yards']
        self.touchdowns = punt_returns['touchdowns']
        self.longest = punt_returns['longest']


class KickReturns(Base):

    __tablename__ = "kick_returns"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, kick_returns, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.returns = kick_returns['returns']
        self.yards = kick_returns['yards']
        self.touchdowns = kick_returns['touchdowns']
        self.longest = kick_returns['longest']


class Kicks(Base):

    __tablename__ = "punt_returns"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    extra_point_attempt = Column('extra_point_attempt', Integer)
    extra_point_made = Column('extra_point_made', Integer)
    field_goal_attempt = Column('field_goal_attempt', Integer)
    field_goal_made = Column('field_goal_made', Integer)

    def __init__(self, first_name, last_name, id, punt_returns, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.extra_point_attempt = punt_returns['extra_point_attempt']
        self.extra_point_made = punt_returns['extra_point_made']
        self.field_goal_attempt = punt_returns['field_goal_attempt']
        self.field_goal_made = punt_returns['field_goal_made']


class Punts(Base):

    __tablename__ = "punts"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    punts = Column('punts', Integer)
    yards = Column('yards', Integer)
    longest = Column('longest', Integer)

    def __init__(self, first_name, last_name, id, punts, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.punts = punts['punts']
        self.yards = punts['yards']
        self.longest = punts['longest']


class Team(Base):

    def __init__(self, nickname, city):
        self.nickname = nickname.lower()
        self.city = city.lower()
        self.record_by_year = {}
        self.stats_by_game = {}

    def add_stats_from_game(self, stats):
        game = stats.game.to_string()
        if game not in self.stats_by_game:
            self.stats_by_game[game] = stats
        else:
            print("stats already here for this game!")

    def to_string(self):
        return city+" "+nickname


class TeamPassing(Base):
    __tablename__ = "team_passing"

    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    completions = Column('completions', Integer)
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    interceptions = Column('interceptions', Integer)
    sacked = Column('sacked', Integer)
    sack_yards = Column('sack_yards', Integer)

    def __init__(self, first_name, last_name, id, passing, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.completions = passing['completions']
        self.attempts = passing['attempts']
        self.yards = passing['yards']
        self.touchdowns = passing['touchdowns']
        self.interceptions = passing['interceptions']
        self.sacked = passing['sacked']
        self.sack_yards = passing['sack_yards']


class TeamRushing(Base):
    __tablename__ = "team_rushing"

    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)

    def __init__(self, first_name, last_name, id, rushing, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame

        self.attempts = rushing['attempts']
        self.yards = rushing['yards']
        self.touchdowns = rushing['touchdowns']


class TeamFumbles(Base):

    __tablename__ = "team_fumbles"

    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    fumbles = Column('fumbles', Integer)
    lost = Column('lost', Integer)

    def __init__(self, first_name, last_name, id, fumbles, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.fumbles = fumbles['fumbles']
        self.lost = fumbles['lost']


class Penalties(Base):

    __tablename__ = "penalties"

    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    penalties = Column('penalties', Integer)
    yards = Column('yards', Integer)

    def __init__(self, first_name, last_name, id, penalties, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.penalties = penalties['penalties']
        self.yards = penalties['yards']


class Downs(Base):

    __tablename__ = "downs"

    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('nflgame.id'))
    first_downs = Column('first_downs', Integer)
    third_down_conversions = Column('third_down_conversions', Integer)
    third_down_attempts = Column('third_down_attempts', Integer)
    fourth_down_conversions = Column('fourth_down_conversions', Integer)
    fourth_down_attempts = Column('fourth_down_attempts', Integer)
    time_of_posession = Column('time_of_posession', Interval)

    def __init__(self, first_name, last_name, id, downs, NFLGame):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.id = id
        self.NFLGame = NFLGame
        self.first_downs = downs['first_downs']
        self.third_down_conversions = downs['third_down_conversions']
        self.third_down_attempts = downs['third_down_attempts']
        self.fourth_down_conversions = downs['fourth_down_conversions']
        self.fourth_down_attempts = downs['fourth_down_attempts']
        self.time_of_posession = downs['time_of_posession']
