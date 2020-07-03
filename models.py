from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, Date, String, Interval
from sqlalchemy.orm import relationship
from database import Base


from datetime import datetime


class NFLGame(Base):
    __tablename__ = "game"

    # main columns
    id = Column('id', Integer, primary_key=True)
    game = Column('game', String, unique=True)
    home_team = Column('home_team', String, unique=True)
    away_team = Column('away_team', String, unique=True)
    date = Column('date', Date)

    # relationships
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


class Player(Base):

    __tablename__ = "player"

    # main columns
    id = Column('id', Integer, primary_key=True)
    identifier= Column('identifier', String, unique=True)
    first_name = Column('game', String)
    last_name = Column('home_team', String)

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
        self.id = first_name+last_name+id
        self.position = []


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
    sacked_yds = Column('sacked_yds', Integer)
    longest = Column('longest', Integer)
    qb_rating = Column('qb_rating', Float)

    def __init__(self, passing):

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

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, rushing):
        self.attempts = rushing['attempts']
        self.yards = rushing['yards']
        self.touchdowns = rushing['touchdowns']
        self.longest = rushing['longest']


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

    def __init__(self, receiving):
        self.receptions = receiving['receptions']
        self.targeted = ['targeted']
        self.yards = ['yards']
        self.touchdowns = ['touchdowns']
        self.longest = ['longest']


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

    def __init__(self, secondary):
        self.interceptions = secondary['interceptions']
        self.passes_defended = secondary['passes_defended']
        self.yards = secondary['yards']
        self.touchdowns = secondary['touchdowns']
        self.longest = secondary['longest']


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

    def __init__(self, tackles):
        self.sacks = tackles['sacks']
        self.combined = tackles['combined']
        self.solo = tackles['solo']
        self.assists = tackles['assists']
        self.tackles_for_loss = tackles['tackles_for_loss']
        self.qb_hits = tackles['qb_hits']


class Fumbles(Base):

    __tablename__ = "fumbles"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    forced = Column('forced', Integer)
    recovered = Column('recovered', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)

    def __init__(self, fumbles):
        self.forced = fumbles['forced']
        self.recovered = fumbles['recovered']
        self.yards = fumbles['yards']
        self.touchdowns = fumbles['touchdowns']


class PuntReturns(Base):

    __tablename__ = "punt_returns"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, punt_returns):
        self.returns = punt_returns['returns']
        self.yards = punt_returns['yards']
        self.touchdowns = punt_returns['touchdowns']
        self.longest = punt_returns['longest']


class KickReturns(Base):

    __tablename__ = "kick_returns"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    returns = Column('returns', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)
    longest = Column('longest', Integer)

    def __init__(self, kick_returns):
        self.returns = kick_returns['returns']
        self.yards = kick_returns['yards']
        self.touchdowns = kick_returns['touchdowns']
        self.longest = kick_returns['longest']


class Kicks(Base):

    __tablename__ = "kicks"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    extra_point_attempt = Column('extra_point_attempt', Integer)
    extra_point_made = Column('extra_point_made', Integer)
    field_goal_attempt = Column('field_goal_attempt', Integer)
    field_goal_made = Column('field_goal_made', Integer)

    def __init__(self, punt_returns):
        self.extra_point_attempt = punt_returns['extra_point_attempt']
        self.extra_point_made = punt_returns['extra_point_made']
        self.field_goal_attempt = punt_returns['field_goal_attempt']
        self.field_goal_made = punt_returns['field_goal_made']


class Punts(Base):

    __tablename__ = "punts"

    id = Column('id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    punts = Column('punts', Integer)
    yards = Column('yards', Integer)
    longest = Column('longest', Integer)

    def __init__(self, punts):
        self.punts = punts['punts']
        self.yards = punts['yards']
        self.longest = punts['longest']


class Team(Base):
    __tablename__ = "team"
    id = Column('id', Integer, primary_key=True)
    nickname = Column('nickname', String, unique=True)
    city = Column('city', String)

    def __init__(self, team):

        nickname = team.split(' ')[-1]
        city = ' '.join(team.split(' ')[:-1])

        self.nickname = nickname.lower()
        self.city = city.lower()


class TeamPassing(Base):
    __tablename__ = "team_passing"

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

    def __init__(self, passing):
        self.completions = passing['completions']
        self.attempts = passing['attempts']
        self.yards = passing['yards']
        self.touchdowns = passing['touchdowns']
        self.interceptions = passing['interceptions']
        self.sacked = passing['sacked']
        self.sack_yards = passing['sack_yards']


class TeamRushing(Base):
    __tablename__ = "team_rushing"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    attempts = Column('attempts', Integer)
    yards = Column('yards', Integer)
    touchdowns = Column('touchdowns', Integer)

    def __init__(self, rushing):
        self.attempts = rushing['attempts']
        self.yards = rushing['yards']
        self.touchdowns = rushing['touchdowns']


class TeamFumbles(Base):

    __tablename__ = "team_fumbles"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    fumbles = Column('fumbles', Integer)
    lost = Column('lost', Integer)

    def __init__(self, fumbles):
        self.fumbles = fumbles['fumbles']
        self.lost = fumbles['lost']


class Penalties(Base):

    __tablename__ = "penalties"

    id = Column('id', Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    game_id = Column(Integer, ForeignKey('game.id'))
    penalties = Column('penalties', Integer)
    yards = Column('yards', Integer)

    def __init__(self, penalties):
        self.penalties = penalties['penalties']
        self.yards = penalties['yards']


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

    def __init__(self, downs):
        self.first_downs = downs['first_downs']
        self.third_down_conversions = downs['third_down_conversions']
        self.third_down_attempts = downs['third_down_attempts']
        self.fourth_down_conversions = downs['fourth_down_conversions']
        self.fourth_down_attempts = downs['fourth_down_attempts']
        self.time_of_posession = downs['time_of_posession']
