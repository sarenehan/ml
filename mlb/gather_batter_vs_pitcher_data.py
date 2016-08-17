"""
events = mlbgame.events.game_events(game_id)
"""
from database import DBSession
import csv
import mlbgame
from collections import defaultdict
from mlb.mlb_defaults import BATTER_POINTS_VS_PITCHER

fieldnames = [
    'pitcher_id',
    'batter_id',
    'batter_points',
    'inning',
    'side',
]
filename = 'mlb/batter_vs_pitcher_data.csv'
events = defaultdict(int)
key_error_count = 0


def load_game_ids():
    """Returns all of the game ids in the database"""
    return [
        point[0] for point in
        DBSession.query('select distinct(game_id) from batting')
    ]


def write_row_to_csv(row_dictionary, fieldnames=fieldnames, filename=filename):
    """
    Writes a dictionary row to a csv
    """
    # Lack of row dictionary indicates header should be written
    if not row_dictionary:
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(filename, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(row_dictionary)


def get_batter_points(at_bat, inning, side, prev_points, team_ident):
    """
    Returns the number of points a batter gained in a given at bat
    """
    global key_error_count
    event = at_bat['event'].lower()
    if 'out' in event:
        return 0
    batter_points = BATTER_POINTS_VS_PITCHER.get(event)
    if batter_points is None:
        return None
    if event == 'home run':
        batter_points += 2
    try:
        rbi = int(at_bat[team_ident]) - prev_points
    except KeyError:
        key_error_count += 1
        rbi = 0
    batter_points += 2 * rbi
    return batter_points


def get_row_dictionary(at_bat, inning, side, prev_points, team_ident):
    """
    Generates the row dictionary in the format expected by the csv file
    """
    batter_points = get_batter_points(
        at_bat, inning, side, prev_points, team_ident)
    if batter_points is None:
        return
    row_dict = {
        'batter_points': batter_points,
        'inning': int(inning),
        'side': side,
        'batter_id': int(at_bat['batter']),
        'pitcher_id': int(at_bat['pitcher'])
    }
    write_row_to_csv(row_dict)


def gather_data(game_ids):
    """
    Top level function for writing data to the csv file. Creates a row
    for each at bat.
    """
    for idx, game_id in enumerate(game_ids):
        print('{} of {}'.format(idx, len(game_ids)))
        try:
            game_events = mlbgame.events.game_events(game_id)
        except:
            continue
        home_team_points = 0
        away_team_points = 0
        for inning in sorted(game_events.keys(), key=lambda ev_: int(ev_)):
            for side in game_events[inning]:
                for at_bat in game_events[inning][side]:
                    if side == 'top':
                        get_row_dictionary(
                            at_bat,
                            inning,
                            side,
                            away_team_points,
                            'away_team_runs')
                        try:
                            away_team_points = int(
                                at_bat['away_team_runs'])
                        except KeyError:
                            continue
                    else:
                        get_row_dictionary(
                            at_bat,
                            inning,
                            side,
                            home_team_points,
                            'home_team_runs')
                        try:
                            home_team_points = int(
                                at_bat['home_team_runs'])
                        except KeyError:
                            continue


def create_tables():
    DBSession.query('drop table if exists batter_vs_pitcher')
    DBSession.upload_from_csv(filename, 'batter_vs_pitcher')


if __name__ == '__main__':
    game_ids = load_game_ids()
    write_row_to_csv(None)
    gather_data(game_ids)
    create_tables()
