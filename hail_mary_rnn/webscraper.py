import os
import re
from io import StringIO
import requests
import pandas as pd
from get_or_create import get_or_create
from models import *
from bs4 import BeautifulSoup, Comment
from time import sleep
from datetime import datetime, timedelta
from database import session, Base, engine

HEADERS = {
    'user-agent': 'Daniel Foster/daniel.a.foster@gmail.com/Doing a home project'}


def get_all_game_urls(year, week, link_text):
    url_base = 'https://www.pro-football-reference.com'
    links = []

    sleep(3)
    res = requests.get(url_base+'/years/'+str(year) +
                       '/week_'+str(week)+'.htm', headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    for a in soup.find_all('a'):
        if a.text == link_text:
            links.append((url_base+a['href'], week))
            print("got url: "+url_base+a['href'])
    return links


def get_game_page(url):
    res = requests.get(url, headers=HEADERS)  # gets content of URL
    soup = BeautifulSoup(res.text, "html.parser")

    return soup


def get_row_value_where(df, out_col, where_col, s):
    value = df[out_col].where(df[where_col] == s).dropna().tolist()[0]
    return value


def scrape_game_info(parsed_html):
    title = parsed_html.find('title').get_text().split('|')[0]

    game_info_div = parsed_html.find(id="all_game_info")
    comment = game_info_div.find(string=lambda text: isinstance(text, Comment))
    game_info = BeautifulSoup(comment, "html.parser")
    game_info_df = pd.read_html(
        StringIO(game_info.prettify()), header=0, flavor='bs4')[0]

    box_score = parsed_html.find(
        'div', {"class": "linescore_wrap"}).find('table').prettify()
    box_score_df = pd.read_html(StringIO(box_score))[0]

    info = parsed_html.find('div', {'class': 'scorebox_meta'})
    info_divs = info.find_all('div')

    date = info_divs[0].get_text() + ' ' + \
        info_divs[1].get_text().split(' ')[-1]

    return title, game_info_df, box_score_df, date


def parse_game_info(title, game_info_df, box_score_df, date, week, away_team_abbrev, home_team_abbrev):
    #teams and date
    date = datetime.strptime(date, "%A %b %d, %Y %I:%M%p")
    teams = title.split('-')[0]
    away_team_fullname, home_team_fullname = teams.split(
        ' at ')[0], teams.split(' at ')[1].strip()
    home_nickname = home_team_fullname.split(' ')[-1].lower()
    home_city = ' '.join(home_team_fullname.split(' ')[:-1]).lower()
    home_team = get_or_create(
        session, Team, nickname=home_nickname, city=home_city, abbrev=home_team_abbrev)

    away_nickname = away_team_fullname.split(' ')[-1].lower()
    away_city = ' '.join(away_team_fullname.split(' ')[:-1]).lower()
    away_team = get_or_create(
        session, Team, nickname=away_nickname, city=away_city, abbrev=away_team_abbrev)
    game_info = {'home_team': home_team, 'away_team': away_team, 'date': date}

    # game info
    try:
        won_toss = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Won Toss')
    except:
        won_toss = None
    try:
        roof = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Roof')
    except:
        roof = None
    try:
        surface = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Surface')
    except:
        surface = None
    try:
        t = datetime.strptime(get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Duration'), "%H:%M")
        duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    except:
        duration = None
    try:
        attendance = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Attendance')
    except:
        attendance = None
    try:
        vegas_line = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Vegas Line')
        vegas_line_num = re.sub(r'[^\d\+-]|49ers', '', vegas_line)
    except:
        vegas_line = None
        vegas_line_num = None
    if vegas_line_num == '':
        vegas_line_num = None
        vegas_line = re.sub(r'[^\w\s]+', '', vegas_line).strip()
    try:
        over_under = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Over/Under')
        over_under_num = float(over_under.split()[0])
        over_under = re.sub('/W+', '', over_under)
    except:
        over_under = None
        over_under_num = None

    game_info = {**game_info, "won_toss": won_toss, "roof": roof, "surface": surface, "duration": duration,
                 "vegas_line": vegas_line, "vegas_line_num": vegas_line_num, "over_under": over_under, "over_under_num": over_under_num, "week": week}
    try:
        weather = get_row_value_where(
            game_info_df, 'Game Info.1', 'Game Info', 'Weather').split(',')
        for item in weather:
            key = re.sub('\d+', '', item).strip().split(' ')
            if 'humidity' in key:
                key = 'humidity'
            elif 'chill' in key:
                key = 'wind_chill'
            elif 'mph' in key or 'no' in key:
                key = 'wind'
            else:
                key = key[0]
            value = re.sub('\D+', '', item).strip()
            game_info[key] = value

    except:
        pass
    # scoring
    home_first = int(get_row_value_where(
        box_score_df, '1', 'Unnamed: 1',  home_team_fullname))
    away_first = int(get_row_value_where(
        box_score_df, '1', 'Unnamed: 1',  away_team_fullname))

    home_second = int(get_row_value_where(
        box_score_df, '2', 'Unnamed: 1',  home_team_fullname))
    away_second = int(get_row_value_where(
        box_score_df, '2', 'Unnamed: 1',  away_team_fullname))

    home_third = int(get_row_value_where(
        box_score_df, '3', 'Unnamed: 1',  home_team_fullname))
    away_third = int(get_row_value_where(
        box_score_df, '3', 'Unnamed: 1',  away_team_fullname))

    home_fourth = int(get_row_value_where(
        box_score_df, '4', 'Unnamed: 1',  home_team_fullname))
    away_fourth = int(get_row_value_where(
        box_score_df, '4', 'Unnamed: 1',  away_team_fullname))

    home_final = int(get_row_value_where(
        box_score_df, 'Final', 'Unnamed: 1',  home_team_fullname))
    away_final = int(get_row_value_where(
        box_score_df, 'Final', 'Unnamed: 1',  away_team_fullname))

    game_info['home_first'] = home_first
    game_info['home_second'] = home_second
    game_info['home_third'] = home_third
    game_info['home_fourth'] = home_fourth
    game_info['home_final'] = home_final

    game_info['away_first'] = away_first
    game_info['away_second'] = away_second
    game_info['away_third'] = away_third
    game_info['away_fourth'] = away_fourth
    game_info['away_final'] = away_final

    if ('OT' in box_score_df.columns):
        home_OT = int(get_row_value_where(
            box_score_df, 'OT', 'Unnamed: 1',  home_team_fullname))
        away_OT = int(get_row_value_where(
            box_score_df, 'OT', 'Unnamed: 1',  away_team_fullname))

        game_info['home_ot'] = home_OT
        game_info['away_ot'] = away_OT
    if ('OT2' in box_score_df.columns):
        home_OT2 = int(get_row_value_where(
            box_score_df, 'OT2', 'Unnamed: 1',  home_team_fullname))
        away_OT2 = int(get_row_value_where(
            box_score_df, 'OT2', 'Unnamed: 1',  away_team_fullname))
        game_info['home_ot2'] = home_OT2
        game_info['away_ot2'] = away_OT2

    game_info['game'] = home_team_fullname+"_vs_"+away_team_fullname+"_week_" + \
        str(game_info['week'])+"_"+date.strftime("%m%d%Y")

    game = get_or_create(session, Game, **game_info)

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
        first_name = fullname[0]
        last_name = ' '.join(fullname[1:])
    return first_name, last_name


def get_player_stats_offense(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)
    id_num = str(row['id'])
    team_abbrev = row['tm']

    passing = {"completions": row['cmp'], "attempts": row['att'], "yards": row['yds'],
               "touchdowns": row['td'], "interceptions": row['int'], "sacked": row['sk'], "sack_yards": row['yds1'], "longest": row['lng'], "qb_rating": row['rate']}

    rushing = {"attempts": row['att1'], "yards": row['yds2'],
               "touchdowns": row['td1'], "longest": row['lng1']}

    receiving = {"targeted": row['tgt'], "receptions": row['rec'], "yards": row['yds3'],
                 "touchdowns": row['td2'], "longest": row['lng2']}

    return first_name, last_name, team_abbrev, passing, rushing, receiving, id_num


def get_player_stats_defense(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)
    id_num = str(row['id'])
    team_abbrev = row['tm']

    secondary = {"interceptions": row['int'], "passes_defended": row['pd'],
                 "yards": row['yds'], "longest": row['lng'], "touchdowns": row['td']}

    tackles = {"sacks": row['sk'], "combined": row['comb'], "solo": row['solo'],
               "assists": row['ast'], "tackles_for_loss": row['tfl'], "qb_hits": row['qbhits']}

    fumbles = {"forced": row['ff'], "recovered": row['fr'],
               "touchdowns": row['td1'], "yards": row['yds1']}

    return first_name, last_name, team_abbrev, secondary, tackles, fumbles, id_num


def get_player_stats_kicking(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)
    id_num = str(row['id'])
    team_abbrev = row['tm']

    kicks = {"extra_points_made": row['xpm'], "extra_point_attempts": row['xpa'],
             "fg_made": row['fgm'], "fg_attempts": row['fga']}

    punts = {"punts": row['pnt'], "yards": row['yds'],
             "yards": row['yp'], "longest": row['lng']}

    return first_name, last_name, team_abbrev, kicks, punts, id_num


def get_player_stats_returns(row):
    fullname = row['player'].split(' ')
    first_name, last_name = split_name(fullname)
    id_num = str(row['id'])
    team_abbrev = row['tm']

    kick_returns = {"returns": row['rt'], "yards": row['yds'],
                    "yards_per_return": row['yrt'], "longest": row['lng'], "touchdowns": row['td']}

    punt_returns = {"returns": row['ret'], "yards": row['yds1'],
                    "yards_per_return": row['yr'], "longest": row['lng1'], "touchdowns": row['td1']}

    return first_name, last_name, team_abbrev, kick_returns, punt_returns, id_num


def read_table(parsed_html, div_id, extra_headers=False, table_in_comment=False, comment_out_of_div=False, get_urls=False, clean_column_names=True):
    if table_in_comment:
        if comment_out_of_div:
            comments = parsed_html.find_all(string=lambda text: isinstance(text,Comment))
            for comment in comments:
                table = BeautifulSoup(comment, "html.parser")
                div = table.find(id=div_id)
                if div is not None:
                    table = div.find('table')
                    break
        else:    
            div = parsed_html.find(id=div_id)
            comment = div.find(string=lambda text: isinstance(text, Comment))
            table = BeautifulSoup(comment, "html.parser")
    else:
        table = parsed_html.find(id=div_id)
    if extra_headers:
        try:
            remove_extra_table_headers(table)
        except:
            pass
    df = pd.read_html(StringIO(table.prettify()), header=0, flavor='bs4')[0]
    df.columns = df.columns.str.replace(
        re.compile(r'\W'), '', regex=True).str.lower()
    if clean_column_names:
        df['id'] = [re.sub('\D', '', a['href'])
                    for a in table.find_all('a')]
        df.fillna(0, inplace=True)
    if get_urls:
        df['url'] = [a['href'] for a in table.find_all('a')]

    return df


def scrape_player_stats(parsed_html):
    try:
        home_positions_df = read_table(
            parsed_html, "all_home_starters", table_in_comment=True)
    except:
        home_positions_df = None
    try:
        away_positions_df = read_table(
            parsed_html, "all_vis_starters", table_in_comment=True)
        positions_df = pd.concat([home_positions_df, away_positions_df])
    except:
        away_positions_df = None
        positions_df = None

    offense_df = read_table(parsed_html, "player_offense", extra_headers=True)
    defense_df = read_table(parsed_html, "all_player_defense",
                            extra_headers=True, table_in_comment=True)
    kicking_df = read_table(parsed_html, "all_kicking",
                            extra_headers=True, table_in_comment=True)
    try:
        returns_df = read_table(parsed_html, "all_returns",
                                extra_headers=True, table_in_comment=True)
    except:
        returns_df = None
    return offense_df, defense_df, kicking_df, returns_df, positions_df


def parse_player_stats(offense_df, defense_df, kicking_df, returns_df, game):
    for index, row in offense_df.iterrows():
        first_name, last_name, team_abbrev, passing, rushing, receiving, id_num = get_player_stats_offense(
            row)
        identifier = first_name+last_name+id_num
        if game.home_team.abbrev == team_abbrev:
            team = game.home_team
        elif game.away_team.abbrev == team_abbrev:
            team = game.away_team

        player = get_or_create(
            session, Player, first_name=first_name, last_name=last_name, identifier=identifier)

        player_rushing = Rushing(
            **rushing, player_rushing=player, game_player_rushing=game, team_player_rushing=team)
        player_passing = Passing(
            **passing, player_passing=player, game_player_passing=game, team_player_passing=team)
        player_receiving = Receiving(
            **receiving, player_receiving=player, game_player_receiving=game, team_player_receiving=team)

        session.add(player_rushing)
        session.add(player_passing)
        session.add(player_receiving)
        session.commit()

    for index, row in defense_df.iterrows():
        first_name, last_name, team_abbrev, secondary, tackles, fumbles, id_num = get_player_stats_defense(
            row)
        identifier = first_name+last_name+id_num
        if game.home_team.abbrev == team_abbrev:
            team = game.home_team
        elif game.away_team.abbrev == team_abbrev:
            team = game.away_team

        player = get_or_create(
            session, Player, first_name=first_name, last_name=last_name, identifier=identifier)

        player_secondary = Secondary(
            **secondary, player_secondary=player, game_player_secondary=game, team_player_secondary=team)
        player_tackles = Tackles(
            **tackles, player_tackles=player, game_player_tackles=game, team_player_tackles=team)
        player_fumbles = Fumbles(
            **fumbles, player_fumbles=player, game_player_fumbles=game, team_player_fumbles=team)

        session.add(player_secondary)
        session.add(player_tackles)
        session.add(player_fumbles)
        session.commit()

    for index, row in kicking_df.iterrows():
        first_name, last_name, team_abbrev, kicks, punts, id_num = get_player_stats_kicking(
            row)
        identifier = first_name+last_name+id_num
        if game.home_team.abbrev == team_abbrev:
            team = game.home_team
        elif game.away_team.abbrev == team_abbrev:
            team = game.away_team
        player = get_or_create(
            session, Player, first_name=first_name, last_name=last_name, identifier=identifier)

        player_kicks = Kicks(**kicks, player_kicks=player,
                             game_player_kicks=game, team_player_kicks=team)
        player_punts = Punts(**punts, player_punts=player,
                             game_player_punts=game, team_player_punts=team)

        session.add(player_kicks)
        session.add(player_punts)
        session.commit()
    if returns_df is not None:
        for index, row in returns_df.iterrows():
            first_name, last_name, team_abbrev, kick_returns, punt_returns, id_num = get_player_stats_returns(
                row)

            identifier = first_name+last_name+id_num
            if game.home_team.abbrev == team_abbrev:
                team = game.home_team
            elif game.away_team.abbrev == team_abbrev:
                team = game.away_team
            player = get_or_create(
                session, Player, first_name=first_name, last_name=last_name, identifier=identifier)

            player_kick_returns = KickReturns(
                **kick_returns, player_kick_returns=player, game_player_kick_returns=game, team_player_kick_returns=team)
            player_punt_returns = PuntReturns(
                **punt_returns, player_punt_returns=player, game_player_punt_returns=game, team_player_punt_returns=team)

            session.add(player_kick_returns)
            session.add(player_punt_returns)
            session.commit()


def scrape_team_stats(parsed_html):
    team_stats = parsed_html.find(string=re.compile(r'id="team_stats"'))
    df = pd.read_html(StringIO(team_stats), flavor='bs4')[0]
    away_team_abbrev, home_team_abbrev = tuple(df.columns)[1:]
    df.columns = ["stat", "away", "home"]

    return df, away_team_abbrev, home_team_abbrev


def parse_team_stats(team_df, game):
    for team in ['home', 'away']:
        first_downs = get_row_value_where(team_df, team, 'stat', "First Downs")
        team_rush_stats = re.sub(r'--+', '-', get_row_value_where(
            team_df, team, 'stat', "Rush-Yds-TDs")).split('-')

        team_sack_stats = re.sub(r'--+', '-', get_row_value_where(
            team_df, team, 'stat', "Sacked-Yards")).split('-')

        team_pass_stats = re.sub(
            r'--+', '-', get_row_value_where(team_df, team, 'stat', "Cmp-Att-Yd-TD-INT")).split('-')

        team_fumbles = re.sub(r'--+', '-', get_row_value_where(
            team_df, team, 'stat', "Fumbles-Lost")).split('-')
        team_penalties = re.sub(r'--+', '-', get_row_value_where(
            team_df, team, 'stat', "Penalties-Yards")).split('-')
        team_third_downs = re.sub(
            r'--+', '-', get_row_value_where(team_df, team, 'stat', "Third Down Conv.")).split('-')
        team_fourth_downs = re.sub(
            r'--+', '-', get_row_value_where(team_df, team, 'stat', "Fourth Down Conv.")).split('-')

        first_downs = get_row_value_where(team_df, team, 'stat', "First Downs")

        t = datetime.strptime(get_row_value_where(
            team_df, team, 'stat', "Time of Possession"), "%M:%S")
        possession = timedelta(minutes=t.minute, seconds=t.second)

        rushes, rush_yds, rush_tds = tuple(team_rush_stats)
        completions, attempts, pass_yds, pass_tds, interceptions = tuple(
            team_pass_stats)
        sacks, sack_yds = tuple(team_sack_stats)
        fumbles, fumbles_lost = tuple(team_fumbles)

        penalties, penalty_yds = tuple(team_penalties)

        third_down_attempts, third_down_conv = tuple(
            team_third_downs)

        fourth_down_attempts, fourth_down_conv = tuple(team_fourth_downs
                                                       )

        passing = {"completions": completions, "attempts": attempts, "yards": pass_yds,
                   "touchdowns": pass_tds, "interceptions": interceptions, "sacked": sacks, "sack_yards": sack_yds}

        rushing = {"attempts": rushes, "yards": rush_yds,
                   "touchdowns": rush_tds}

        fumbles = {"fumbles": fumbles, "lost": fumbles_lost}

        penalties = {"penalties": penalties, "yards": penalty_yds}

        downs = {"first_downs": first_downs, "third_down_conversions": third_down_conv, "third_down_attempts": third_down_attempts, "fourth_down_conversions": fourth_down_conv, "fourth_down_attempts": fourth_down_attempts,
                 "time_of_posession": possession}

        if team == 'home':
            team = game.home_team
        else:
            team = game.away_team
        # if session.query(Team).filter_by(nickname=team.nickname).first() == None:
        #     session.add(team)

        team_passing = TeamPassing(
            **passing, team_passing=team, game_team_passing=game)
        team_rushing = TeamRushing(
            **rushing, team_rushing=team, game_team_rushing=game)
        team_fumbles = TeamFumbles(
            **fumbles, team_fumbles=team, game_team_fumbles=game)

        penalties = Penalties(
            **penalties, team_penalties=team, game_team_penalties=game)
        downs = Downs(**downs, team_downs=team, game_team_downs=game)

        session.add(team_passing)
        session.add(team_rushing)
        session.add(team_fumbles)
        session.add(penalties)
        session.add(downs)

    session.commit()


def process_page(url):
    parsed_html = get_game_page(url)
    team_df, away_team_abbrev, home_team_abbrev = scrape_team_stats(
        parsed_html)
    title, game_info_df, box_score_df, date = scrape_game_info(parsed_html)
    game = parse_game_info(title, game_info_df, box_score_df,
                           date, week, away_team_abbrev, home_team_abbrev)
    offense_df, defense_df, kicking_df, returns_df, positions_df = scrape_player_stats(
        parsed_html)
    parse_team_stats(
        team_df, game)
    parse_player_stats(
        offense_df, defense_df, kicking_df, returns_df, game)


if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    PLAYERS = {}
    TEAMS = {}
    year_range = range(2000, 2023)
    week_range = range(1, 18)
    for year in year_range:
        for week in week_range:
            urls = get_all_game_urls(year, week, "Final")
            game_num = 0
            for url, week in urls:
                sleep(3)
                print(url)
                print("game_index: ", game_num)
                game_num += 1
                process_page(url)
# get positions for players other than starters
# build database
