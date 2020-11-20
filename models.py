from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, Date, String, Interval
from sqlalchemy.orm import relationship
from database import Base


from datetime import datetime


class Game(Base):
    __tablename__ = "game"
    print('created game table')
    # main columns
    id = Column('id', Integer, primary_key=True)
    game = Column('game', String, unique=True)
    home_team = Column('home_team', String, unique=True)
    away_team = Column('away_team', String, unique=True)
    date = Column('date', Date)

    # relationships
    passing = relationship('Passing', backref='game_player_passing')
    rushing = relationship('Rushing', backref='game_player_rushing')
    receiving = relationship('Receiving', backref='game_player_receiving')
    secondary = relationship('Secondary', backref='game_player_secondary')
    tackles = relationship('Tackles', backref='game_player_tackles')
    fumbles = relationship('Fumbles', backref='game_player_fumbles')
    punt_returns = relationship('PuntReturns', backref='game_player_punt_returns')
    kick_returns = relationship('KickReturns', backref='game_player_kick_returns')
    punts = relationship('Punts', backref='game_player_punts')
    kicks = relationship('Kicks', backref='game_player_kicks')
    team_passing = relationship('TeamPassing', backref='game_team_passing')
    team_rushing = relationship('TeamRushing', backref='game_team_rushing')
    team_fumbles = relationship('TeamFumbles', backref='game_team_fumbles')
    penalties = relationship('Penalties', backref='game_team_penalties')
    downs = relationship('Downs', backref='game_team_downs')

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

        self.home_final = scores['home_scoring']['final']
        self.home_first = scores['home_scoring']['1']
        self.home_second = scores['home_scoring']['2']
        self.home_third = scores['home_scoring']['3']
        self.home_fourth = scores['home_scoring']['4']
        if game_info['ot']:
            self.home_ot = scores['home_scoring']['ot']
        if game_info['ot2']:
            self.home_ot2 = scores['home_scoring']['ot2']

        self.away_final = scores['away_scoring']['final']
        self.away_first = scores['away_scoring']['1']
        self.away_second = scores['away_scoring']['2']
        self.away_third = scores['away_scoring']['3']
        self.away_fourth = scores['away_scoring']['4']
        if game_info['ot']:
            self.away_ot = scores['away_scoring']['ot']
        if game_info['ot2']:
            self.away_ot = scores['away_scoring']['ot2']

        self.won_toss = game_info['won_toss']
        self.roof = game_info['roof']
        self.surface = game_info['surface']
        self.duration = game_info['duration']
        self.vegas_line = game_info['vegas_line']
        self.vegas_line_num = game_info['vegas_line_num']
        self.over_under = game_info['over_under']
        self.over_under_num = game_info['over_under_num']
        self.week = game_info['week']
        self.game = home_team+"_vs_"+away_team+"_week_" + \
            str(game_info['week'])+"_"+date.strftime("%m%d%Y")

    def to_string(self):
        return self.home_team+"_vs_"+self.away_team+"_week_"+str(self.game_info['week'])+"_"+self.date.strftime("%m%d%Y")

# Player based objects


class Player(Base):

    __tablename__ = "player"

    # main columns
    id = Column('id', Integer, primary_key=True)
    identifier = Column('identifier', String, unique=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)

    passing = relationship('Passing', backref='player_passing')
    rushing = relationship('Rushing', backref='player_rushing')
    receiving = relationship('Receiving', backref='player_receiving')
    secondary = relationship('Secondary', backref='player_secondary')
    tackles = relationship('Tackles', backref='player_tackles')
    fumbles = relationship('Fumbles', backref='player_fumbles')
    punt_returns = relationship('PuntReturns', backref='player_punt_returns')
    kick_returns = relationship('KickReturns', backref='player_kick_returns')
    punts = relationship('Punts', backref='player_punts')
    kicks = relationship('Kicks', backref='player_kicks')


class Passing(Base):
    __tablename__ = "passing"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    completions = Column('completions', Integer)
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    interceptions = Column('interceptions', Integer)
    sacked = Column('sacked', Integer)
    sack_yards = Column('sack_yards', Integer)
    longest = Column('longest', Integer)
    qb_rating = Column('qb_rating', Float)


class Rushing(Base):
    __tablename__ = "rushing"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

class Receiving(Base):

    __tablename__ = "receiving"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    receptions = Column('receptions', Integer)
    targeted = Column('targeted', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

class Secondary(Base):

    __tablename__ = "secondary"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    interceptions = Column('interceptions', Integer)
    passes_defended = Column('passes_defended', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

class Tackles(Base):

    __tablename__ = "tackles"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    sacks = Column('sacks', Integer)
    combined = Column('combined', Integer)
    solo = Column('solo', Integer)
    assists = Column('assists', Integer)
    tackles_for_loss = Column('tackles_for_loss', Integer)
    qb_hits = Column('qb_hits', Integer)


class Fumbles(Base):

    __tablename__ = "fumbles"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    forced = Column('forced', Integer)
    recovered = Column('recovered', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)


class PuntReturns(Base):

    __tablename__ = "punt_returns"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    yards_per_return = Column('yards_per_return', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)


class KickReturns(Base):

    __tablename__ = "kick_returns"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    yards_per_return = Column('yards_per_return', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)


class Kicks(Base):

    __tablename__ = "kicks"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    extra_point_attempts = Column('extra_point_attempts', Integer)
    extra_points_made = Column('extra_points_made', Integer)
    fg_attempts = Column('fg_attempts', Integer)
    fg_made = Column('fg_made', Integer)


class Punts(Base):

    __tablename__ = "punts"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    punts = Column('punts', Integer)
    yards = Column('yards', Integer)
    longest = Column('longest', Integer)

# Team based objects


class Team(Base):
    __tablename__ = "team"

    # main columns
    id = Column('id', Integer, primary_key=True)
    nickname = Column('nickname', String, unique=True)
    city = Column('city', String)

    # relationships
    team_passing = relationship('TeamPassing', backref='team_passing')
    team_rushing = relationship('TeamRushing', backref='team_rushing')
    team_fumbles = relationship('TeamFumbles', backref='team_fumbles')
    penalties = relationship('Penalties', backref='team_penalties')
    downs = relationship('Downs', backref='team_downs')

    def __init__(self, team):

        nickname = team.split(' ')[-1]
        city = ' '.join(team.split(' ')[:-1])

        self.nickname = nickname.lower()
        self.city = city.lower()


class TeamPassing(Base):
    __tablename__ = "team_passing"
    # main columns
    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    completions = Column('completions', Integer)
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    interceptions = Column('interceptions', Integer)
    sacked = Column('sacked', Integer)
    sack_yards = Column('sack_yards', Integer)

class TeamRushing(Base):
    __tablename__ = "team_rushing"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)

class TeamFumbles(Base):

    __tablename__ = "team_fumbles"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    fumbles = Column('fumbles', Integer)
    lost = Column('lost', Integer)

class Penalties(Base):

    __tablename__ = "penalties"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    penalties = Column('penalties', Integer)
    yards = Column('yards', Integer)


class Downs(Base):

    __tablename__ = "downs"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    first_downs = Column('first_downs', Integer)
    third_down_conversions = Column('third_down_conversions', Integer)
    third_down_attempts = Column('third_down_attempts', Integer)
    fourth_down_conversions = Column('fourth_down_conversions', Integer)
    fourth_down_attempts = Column('fourth_down_attempts', Integer)
    time_of_posession = Column('time_of_posession', Interval)
