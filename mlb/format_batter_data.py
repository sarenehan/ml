from database import DBSession
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from statistics import mean, StatisticsError, mode
from collections import namedtuple
import csv
import numpy as np

batter_columns = [
    col[1].replace('.', '') for col in DBSession.get_column('batting')
]
MlbBatter = namedtuple(
    'Batter',
    ' '.join(batter_columns)
)
pitcher_columns = [
    col[1].replace('.', '') for col in DBSession.get_column('pitching')
]
MlbPitcher = namedtuple(
    'Pitcher',
    ' '.join(pitcher_columns)
)
game_columns = [
    col[1].replace('.', '') for col in DBSession.get_column('games')
]
MlbGame = namedtuple(
    'Games',
    ' '.join(game_columns)
)
batter_ids = np.load('mlb/batter_ids.npy')
pitcher_ids = np.load('mlb/pitcher_ids.npy')
# matrix = np.load('mlb/batter_vs_pitcher_cosine_array.npy')
matrix = np.load('mlb/bvp_data.npy')

batter_v_pitcher_dict = {
    b_id: {
        p_id: matrix[i, j]
        for j, p_id in enumerate(pitcher_ids)
    }
    for i, b_id in enumerate(batter_ids)
}


def load_batter_obj(row):
    """
    Returns a namedtuple object representing a batter for a given
    row
    """
    row_dict = {
        col: row[idx] for (idx, col) in enumerate(batter_columns)}
    return MlbBatter(**row_dict)


def load_pitcher_obj(row):
    """
    Returns a namedtuple object representing a pitcher for a given
    row
    """
    row_dict = {
        col: row[idx] for (idx, col) in enumerate(pitcher_columns)}
    return MlbPitcher(**row_dict)


def load_game_obj(row):
    """
    Returns a MlbGame namedtuple
    """
    row_dict = {
        col: row[idx] for (idx, col) in enumerate(game_columns)
    }
    return MlbGame(**row_dict)


def load_data(table_name, loading_func):
    """
    Loads all of the data into namedtuples from a given table
    """
    return convert_to_datetimes([
        loading_func(row)
        for row in
        DBSession.query('select * from {}'.format(table_name))
    ])


def load_player_dict(players):
    """
    Returns a dictionary of player_id: [Batting] objects
    """
    player_dict = defaultdict(list)
    for player in players:
        player_dict[player.player_id].append(player)
    return player_dict


def load_game_dict(games):
    return {game.game_id: game for game in games}


def convert_to_datetimes(players):
    """
    Turns date strings into datetimes for all players
    """
    new_players = []
    for player in players:
        new_players.append(
            player._replace(
                date=datetime.strptime(player.date.split(' ')[0], '%Y-%m-%d')
            ))
    return new_players


def get_previous_games(date, all_games):
    """
    Returns the games in all_games that occur before a
    certain date
    """
    games = [
        player for player in all_games
        if player.date < date
    ]
    games.sort(key=lambda bat: bat.date, reverse=True)
    return games


def weight_avg_points(games, pitcher_dict):
    numerator = 0
    denominator = 0
    batter_id = games[0].player_id
    for batter_stats in games:
        try:
            pitcher_season_average = mean(
                pitch_game.points for pitch_game in
                pitcher_dict[batter_stats.starting_pitcher_id]
                if pitch_game.date < batter_stats.date
            )
        except (StatisticsError):
            continue
        numerator += (pitcher_season_average * batter_stats.points)
        denominator += 1
    return numerator / denominator


def eliminate_start_of_season(batters, days_to_eliminate=30):
    all_dates = [batter.date for batter in batters]
    start_date = min(all_dates) + timedelta(days=days_to_eliminate)
    return [
        batter for batter in batters if
        batter.date > start_date
    ]


def get_relevant_batters(all_batters):
    relevant_batters = []
    years = set([batter.date.year for batter in all_batters])
    for year in years:
        games_in_year = [
            batter for batter in batters if batter.date.year == year
        ]
        relevant_batters.extend(eliminate_start_of_season(games_in_year))
    return relevant_batters


def compute_winning_pct(games, date_cutoff, team_name):
    """
    Returns wins - losses / (wins + losses)
    """
    wins = len([
        game for game in games if (game.w_team == team_name)
        and game.date.year == date_cutoff.year
        and game.date < date_cutoff
    ])
    loss = len([
        game for game in games if (game.l_team == team_name)
        and game.date.year == date_cutoff.year
        and game.date < date_cutoff
    ])
    return wins / (wins + loss)


def who_will_win(batter, games, game_dict):
    is_home_team = batter.is_home_team
    game_date = batter.date
    if is_home_team:
        player_team = 'home_team'
        opposing_team = 'away_team'
    else:
        player_team = 'away_team'
        opposing_team = 'home_team'
    player_team_name = getattr(game_dict[batter.game_id], player_team)
    opposing_team_name = getattr(game_dict[batter.game_id], opposing_team)
    ptp = compute_winning_pct(
        games, game_date, player_team_name)
    otp = compute_winning_pct(
        games, game_date, opposing_team_name)
    return ptp - otp


def compute_momentum(points):
    x_data = [[x] for x in list(range(len(points)))]
    return LinearRegression().fit(x_data, points).coef_[0]


def mean_points_in_range(games, max_days, min_days, this_game_date):
    return mean(
        player.points for player in games
        if (player.date >= this_game_date - timedelta(days=max_days))
        and (player.date < this_game_date - timedelta(days=min_days))
    )


def format_data(batters, pitchers, games):
    relevant_batters = get_relevant_batters(batters)
    pitcher_dict = load_player_dict(pitchers)
    batter_dict = load_player_dict(batters)
    game_dict = load_game_dict(games)
    batter_rows = []
    for idx, batter in enumerate(relevant_batters):
        if idx % 1000 == 0:
            print('{} of {}'.format(idx, len(relevant_batters)))
        try:
            previous_games = get_previous_games(
                batter.date, batter_dict[batter.player_id])

            if len(previous_games) < 5 or (
                    batter.date - previous_games[5].date).days > 30:
                continue

            is_expected_to_win = who_will_win(batter, games, game_dict)
            last_game = previous_games[0].points
            last_week = mean_points_in_range(previous_games, 7, 0, batter.date)
            last_month = mean_points_in_range(
                previous_games, 30, 7, batter.date)
            season = mean(
                bat.points for bat in previous_games
                if bat.date < batter.date - timedelta(days=30)
            )
            pitcher_season_average = mean(
                pitch_game.points for pitch_game in
                pitcher_dict[batter.starting_pitcher_id]
                if pitch_game.date < batter.date
            )
            batting_position = mode(
                bat.batting_position for bat in previous_games
            )
            try:
                batter_vs_pitcher = batter_v_pitcher_dict[batter.player_id][
                    batter.starting_pitcher_id]
            except KeyError:
                batter_vs_pitcher = 1.0

            batter_rows.append([
                len(previous_games),
                batter.points,
                is_expected_to_win,
                batter.is_home_team,
                batting_position,
                last_game,
                last_week,
                last_month,
                season,
                pitcher_season_average,
                batter.is_starter,
                last_game / max(season, 0.01),
                last_week / max(last_month, 0.01),
                last_week / max(season, 0.01),
                last_month / max(season, 0.01),
                batter_vs_pitcher,
            ])
        except (StatisticsError, IndexError, ZeroDivisionError):
            continue
    return batter_rows


def write_to_csv_and_create_table(batter_rows):
    column_names = [
        'previous_games_count',
        'points',
        'is_expected_to_win',
        'is_home_team',
        'batting_position',
        'last_game_points',
        'last_week_average_points',
        'last_month_average_points',
        'average_points',
        'pitcher_season_avg_points',
        'is_starter',
        'last_game_was_bad',
        'last_game_last_month',
        'last_week_season',
        'last_month_season',
        'batter_vs_pitcher',
    ]
    csv_filename = 'mlb/batter_formatted_rows.csv'
    with open(csv_filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        for row in batter_rows:
            writer.writerow(row)
    DBSession.query('drop table if exists batting_formatted')
    DBSession.upload_from_csv(csv_filename, 'batting_formatted')


if __name__ == '__main__':
    batters = load_data('batting', load_batter_obj)
    pitchers = load_data('pitching', load_pitcher_obj)
    games = load_data('games', load_game_obj)
    batter_rows = format_data(batters, pitchers, games)
    write_to_csv_and_create_table(batter_rows)
