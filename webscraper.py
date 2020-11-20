import os
import re
import sys
import requests
import pandas as pd
from models import *
from bs4 import BeautifulSoup, Comment
from time import sleep
from datetime import datetime, timedelta
from database import session, Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

HEADERS = {
    'user-agent': 'Daniel Foster/daniel.a.foster@gmail.com/Doing a home project'}


def get_all_game_urls(year_range, week_range):
    url_base = 'https://www.pro-football-reference.com'
    links = []
    for i in year_range:
        for j in week_range:
            sleep(3)
            res = requests.get(url_base+'/years/'+str(i) +
                               '/week_'+str(j)+'.htm', headers=HEADERS)
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all('a', text="Final"):
                links.append((url_base+a['href'], j))
    return links


def get_game_page(url):
    res = requests.get(url, headers=HEADERS)  # gets content of URL
    soup = BeautifulSoup(res.text, "html.parser")

    return soup


def get_row_value_where(df, out_col, where_col, s):
    return df[out_col].where(df[where_col] == s).dropna().tolist()[0]


def scrape_game_info(parsed_html):
    title = parsed_html.find('title').get_text().split('|')[0]

    game_info_div = parsed_html.find(id="all_game_info")
    comment = game_info_div.find(text=lambda text: isinstance(text, Comment))
    game_info = BeautifulSoup(comment, "html.parser")
    game_info_df = pd.read_html(
        game_info.prettify(), header=0, flavor='bs4')[0]

    box_score = parsed_html.find(
        'div', {"class": "linescore_wrap"}).find('table').prettify()
    box_score_df = pd.read_html(box_score)[0]

    info = parsed_html.find('div', {'class': 'scorebox_meta'})
    info_divs = info.find_all('div')

    date = info_divs[0].get_text() + ' ' + \
        info_divs[1].get_text().split(' ')[-1]

    return title, game_info_df, box_score_df, date


def parse_game_info(title, game_info_df, box_score_df, date, week):
    #teams and date
    date = datetime.strptime(date, "%A %b %d, %Y %I:%M%p")
    teams = title.split('-')[0]
    home_team, away_team = teams.split(
        ' at ')[0], teams.split(' at ')[1].strip()

    # game info
    won_toss = get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Won Toss')
    roof = get_row_value_where(game_info_df, 'Game Info.1', 'Game Info', 'Roof')
    surface = get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Surface')
    t = datetime.strptime(get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Duration'), "%H:%M")
    duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    try:
        weather = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Weather').split(',')
        weather_dict = {}
        for item in weather:
            key = re.sub('\d+', '', item).strip()
            value = re.sub('\D+', '', item).strip()
            weather_dict[key] = value

    except:
        weather = None
        weather_dict = None
    attendance = get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Attendance')
    vegas_line = get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Vegas Line')
    vegas_line_num = re.sub('[^\d\+-]', '', vegas_line)
    vegas_line = re.sub('[^\w\s]+', '', vegas_line).strip()
    over_under = get_row_value_where(
        game_info_df, 'Game Info.1', 'Game Info', 'Over/Under')
    over_under_num = float(over_under.split()[0])
    over_under = re.sub('/W+', '', over_under)
    game_info = {"won_toss": won_toss, "roof": roof, "surface": surface, "duration": duration,
                 "weather": weather, "vegas_line": vegas_line, "vegas_line_num": vegas_line_num, "over_under": over_under, "over_under_num": over_under_num, "week": week}

    # scoring
    home_first = int(get_row_value_where(
        box_score_df, '1', 'Unnamed: 1',  home_team))
    away_first = int(get_row_value_where(
        box_score_df, '1', 'Unnamed: 1',  away_team))

    home_second = int(get_row_value_where(
        box_score_df, '2', 'Unnamed: 1',  home_team))
    away_second = int(get_row_value_where(
        box_score_df, '2', 'Unnamed: 1',  away_team))

    home_third = int(get_row_value_where(
        box_score_df, '3', 'Unnamed: 1',  home_team))
    away_third = int(get_row_value_where(
        box_score_df, '3', 'Unnamed: 1',  away_team))

    home_fourth = int(get_row_value_where(
        box_score_df, '4', 'Unnamed: 1',  home_team))
    away_fourth = int(get_row_value_where(
        box_score_df, '4', 'Unnamed: 1',  away_team))

    home_final = int(get_row_value_where(
        box_score_df, 'Final', 'Unnamed: 1',  home_team))
    away_final = int(get_row_value_where(
        box_score_df, 'Final', 'Unnamed: 1',  away_team))

    if ('OT' in box_score_df.columns):
        OT = True
        home_OT = int(get_row_value_where(
            box_score_df, 'OT', 'Unnamed: 1',  home_team))
        away_OT = int(get_row_value_where(
            box_score_df, 'OT', 'Unnamed: 1',  away_team))
        home_score = {'1': home_first, '2': home_second, '3': home_third,
                      '4': home_fourth, 'ot': home_OT, 'final': home_final}
        away_score = {'1': away_first, '2': away_second, '3': away_third,
                      '4': away_fourth, 'ot': away_OT, 'final': away_final}
        if ('OT2' in box_score_df.columns):
            OT2 = True
            home_OT2 = int(get_row_value_where(
                box_score_df, 'OT2', 'Unnamed: 1',  home_team))
            away_OT2 = int(get_row_value_where(
                box_score_df, 'OT2', 'Unnamed: 1',  away_team))
            home_score['ot2'] = home_OT2
            away_score['ot2'] = away_OT2
    else:
        OT = False
        OT2 = False
        home_score = {'1': home_first, '2': home_second,
                      '3': home_third, '4': home_fourth, 'final': home_final}
        away_score = {'1': away_first, '2': away_second,
                      '3': away_third, '4': away_fourth, 'final': away_final}

    scores = {"home_scoring": home_score, "away_scoring": away_score}
    game_info['ot'] = OT
    game_info['ot2'] = OT2

    game = NFLGame(home_team, away_team, date, scores, game_info)
    session.add(game)
    session.commit() 

    return game

def remove_extra_table_headers(table):
    for tr in table.find_all('tr', {"class": "over_header"}):
        tr.decompose()
    table.find('tr', {"class": "thead"}).decompose()


def split_name(fullname):
    if len(fullname) == 2:
        first_name = fullname[0]
        last_name = fullname[1]
    else:
        last_name = fullname[-1]
        first_name = ' '.join(fullname[0:len(fullname-1)])
    return first_name, last_name


def get_player_stats_offense(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)

    passing = {"completions": row['cmp'], "attempts": row['att'], "yards": row['yds'],
               "touchdowns": row['td'], "interceptions": row['int'], "sacked": row['sk'], "sack_yards": row['yds1'], "longest": row['lng'], "qb_rating": row['rate']}

    rushing = {"attempts": row['att1'], "yards": row['yds2'],
               "touchdowns": row['td1'], "longest": row['lng1']}

    receiving = {"targeted": row['tgt'], "receptions": row['rec'], "yards": row['yds3'],
                 "touchdowns": row['td2'], "longest": row['lng2']}

    return first_name, last_name, passing, rushing, receiving


def get_player_stats_defense(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)

    secondary = {"interceptions": row['int'], "passes_defended": row['pd'],
                 "yards": row['yds'], "longest": row['lng'], "touchdowns": row['td']}

    tackles = {"sacks": row['sk'], "combined": row['comb'], "solo": row['solo'],
               "assists": row['ast'], "tackles_for_loss": row['tfl'], "qb_hits": row['qbhits']}

    fumbles = {"forced": row['ff'], "recovered": row['fr'],
               "touchdowns": row['td1'], "yards": row['yds1']}

    return first_name, last_name, secondary, tackles, fumbles


def get_player_stats_kicking(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)

    kicks = {"extra_points_made": row['xpm'], "extra_point_attempts": row['xpa'],
             "fg_made": row['fgm'], "fg_attempts": row['fga']}

    punts = {"punts": row['pnt'], "yards": row['yds'],
             "yds_per_punt": row['yp'], "longest": row['lng']}

    return first_name, last_name, kicks, punts


def get_player_stats_returns(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)
    kick_returns = {"returns": row['rt'], "yards": row['yds'],
                    "yds_per_return": row['yrt'], "longest": row['lng'], "touchdowns": row['td']}

    punt_returns = {"returns": row['ret'], "yards": row['yds1'],
                    "yds_per_return": row['yr'], "longest": row['lng1'], "touchdowns": row['td1']}

    return first_name, last_name, kick_returns, punt_returns


def read_table(parsed_html, div_id, extra_headers=False, table_in_comment=False, get_urls=False):
    if table_in_comment:
        div = parsed_html.find(id=div_id)
        comment = div.find(text=lambda text: isinstance(text, Comment))
        table = BeautifulSoup(comment, "html.parser")
    else:
        table = parsed_html.find(id=div_id)
    if extra_headers:
        remove_extra_table_headers(table)
    df = pd.read_html(table.prettify(), header=0, flavor='bs4')[0]
    df.columns = df.columns.str.replace(
        re.compile(r'\W'), '').str.lower()
    df['id'] = [re.sub('\D', '', a['href'])
                for a in table.find_all('a')]
    df.fillna(0, inplace=True)
    if get_urls:
        df['url'] = [a['href'] for a in table.find_all('a')]

    return df


def scrape_player_stats(parsed_html):

    home_positions_df = read_table(
        parsed_html, "all_home_starters", table_in_comment=True)
    away_positions_df = read_table(
        parsed_html, "all_vis_starters", table_in_comment=True)
    positions_df = pd.concat([home_positions_df, away_positions_df])
    offense_df = read_table(parsed_html, "player_offense", extra_headers=True)
    defense_df = read_table(parsed_html, "all_player_defense",
                            extra_headers=True, table_in_comment=True)
    kicking_df = read_table(parsed_html, "all_kicking",
                            extra_headers=True, table_in_comment=True)
    returns_df = read_table(parsed_html, "all_returns",
                            extra_headers=True, table_in_comment=True)

    return offense_df, defense_df, kicking_df, returns_df, positions_df


def parse_player_stats(offense_df, defense_df, kicking_df, returns_df, game):
    for index, row in offense_df.iterrows():
        first_name, last_name, passing, rushing, receiving = get_player_stats_offense(
            row)
        player = Player(first_name, last_name, str(row['id']))
        q = session.query(Player).filter_by(identifier = player.identifier).scalar()
        if not q:
            session.add(player)

        player_rushing = Rushing(rushing, player=player, game=game)
        player_passing = Passing(passing, player=player, game=game)
        player_receiving = Receiving(receiving, player=player, game=game)

        session.add(player_rushing)
        session.add(player_passing)
        session.add(player_receiving)

    for index, row in defense_df.iterrows():
        first_name, last_name, secondary, tackles, fumbles = get_player_stats_defense(
            row)
        player = Player(first_name, last_name, str(row['id']))

        q = session.query(Player).filter_by(identifier = player.identifier).scalar()
        if not q:
            session.add(player)

        player_secondary = Secondary(secondary, player=player, game=game)
        player_tackles = Tackles(tackles, player=player, game=game)
        player_fumbles = Fumbles(fumbles, player=player, game=game)

        session.add(player_secondary)
        session.add(player_tackles)
        session.add(player_fumbles)

    for index, row in kicking_df.iterrows():
        first_name, last_name, kicks, punts = get_player_stats_kicking(row)
        player = Player(first_name, last_name, str(row['id']))

        q = session.query(Player).filter_by(identifier = player.identifier).scalar()
        if not q:
            session.add(player)

        player_kicks = Kicks(kicks, player=player, game=game)
        player_punts = Punts(punts, player=player, game=game)

        session.add(player_kicks)
        session.add(player_punts)

    for index, row in returns_df.iterrows():
        first_name, last_name, kick_returns, punt_returns = get_player_stats_returns(
            row)
        player = Player(first_name, last_name, str(row['id']))

        q = session.query(Player).filter_by(identifier = player.identifier).scalar()
        if not q:
            session.add(player)

        player_kick_returns = KickReturns(kick_returns, player=player, game=game)
        player_punt_returns = PuntReturns(punt_returns, player=player, game=game)

        session.add(player_kick_returns)
        session.add(player_punt_returns)

    session.commit()


def scrape_team_stats(parsed_html):
    offense = parsed_html.find(string=re.compile(r'id="team_stats"'))
    df = pd.read_html(offense, header=None, flavor='bs4')[0]
    df.columns = ["stat", "home", "away"]
    return df


def parse_team_stats(team_df, home_team, away_team, game):
    for team in ['home', 'away']:
        first_downs = get_row_value_where(team_df, team, 'stat', "First Downs")
        rushes, rush_yds, rush_tds = tuple(get_row_value_where(
            team_df, team, 'stat', "Rush-Yds-TDs").split('-'))
        completions, attempts, pass_yds, pass_tds, interceptions = tuple(
            get_row_value_where(team_df, team, 'stat', "Cmp-Att-Yd-TD-INT").split('-'))
        sacks, sack_yds = tuple(get_row_value_where(
            team_df, team, 'stat', "Sacked-Yards").split('-'))
        fumbles, fumbles_lost = tuple(get_row_value_where(
            team_df, team, 'stat', "Fumbles-Lost").split('-'))
        turnovers = get_row_value_where(team_df, team, 'stat', "Turnovers")
        penalties, penalty_yds = tuple(get_row_value_where(
            team_df, team, 'stat', "Penalties-Yards").split('-'))
        third_down_attempts, third_down_conv = turnovers = tuple(
            get_row_value_where(team_df, team, 'stat', "Third Down Conv.").split('-'))
        fourth_down_attempts, fourth_down_conv = turnovers = tuple(
            get_row_value_where(team_df, team, 'stat', "Fourth Down Conv.").split('-'))
        t = datetime.strptime(get_row_value_where(
            team_df, team, 'stat', "Time of Possession"), "%M:%S")
        possession = timedelta(minutes=t.minute, seconds=t.second)

        passing = {"completions": completions, "attempts": attempts, "yards": pass_yds,
                   "touchdowns": pass_tds, "interceptions": interceptions, "sacked": sacks, "sack_yards": sack_yds}

        rushing = {"attempts": rushes, "yards": rush_yds,
                   "touchdowns": rush_tds}

        fumbles = {"fumbles": fumbles, "lost": fumbles_lost}

        penalties = {"penalties": penalties, "yards": penalty_yds}

        downs = {"first_downs": first_downs, "third_down_conversions": third_down_conv, "third_down_attempts": third_down_attempts, "fourth_down_conversions": fourth_down_conv, "fourth_down_attempts": fourth_down_attempts,
                 "time_of_posession": possession}

        
        if team == 'home':
            team = Team(home_team)

        if team == 'away':
            team = Team(away_team)
            
        if  session.query(Team).filter_by(nickname = team.nickname).first() == None:
            session.add(team)

        team_passing = TeamPassing(passing, team=team, game=game)
        team_rushing = TeamRushing(rushing, team=team, game=game)
        team_fumbles = TeamFumbles(fumbles, team=team, game=game)

        penalties = Penalties(penalties, team=team, game=game)
        downs = Downs(downs, team=team, game=game)

        session.add(team_passing)
        session.add(team_rushing)
        session.add(team_fumbles)
        session.add(penalties)
        session.add(downs)

    session.commit()


def process_page(url):
    parsed_html = get_game_page(url)
    title, game_info_df, box_score_df, date = scrape_game_info(parsed_html)
    game = parse_game_info(title, game_info_df, box_score_df, date, week)
    offense_df, defense_df, kicking_df, returns_df, positions_df = scrape_player_stats(
        parsed_html)
    team_df = scrape_team_stats(parsed_html)
    parse_team_stats(
        team_df, game.home_team, game.away_team, game)
    parse_player_stats(
        offense_df, defense_df, kicking_df, returns_df, game)


if __name__ == '__main__':
    PLAYERS = {}
    TEAMS = {}
    year_range = range(2000, 2001)
    week_range = range(1, 2)
    urls = get_all_game_urls(year_range, week_range)

    for url, week in urls[1:2]:
        sleep(3)
        print(url)
        process_page(url)
# get positions for players other than starters
# build database

