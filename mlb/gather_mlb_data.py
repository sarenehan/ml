import mlbgame
import csv
from database import DBSession
from mlb_defaults import (
    BATTER_POINTS,
    SINGLE_POINTS,
    PITCHER_POINTS
)

batter_filename = 'mlb/batter_data.csv'
pitcher_filename = 'mlb/pitcher_data.csv'
game_filename = 'mlb/games.csv'
batter_fieldnames = [
    'date',
    'player_id',
    'name',
    'position',
    'points',
    'position',
    'at_bats',
    'batting_position',
    'batting_average',
    'is_starter',
    'is_home_team',
    'starting_pitcher_id',
    'season_hits',
    'season_rbi',
    'game_id',
]
pitcher_fieldnames = [
    'date',
    'player_id',
    'full_name',
    'name',
    'points',
    'is_starting_pitcher',
    'is_home_team',
    'game_id',
]
game_fieldnames = [
    'away_team_errors',
    'away_team_hits',
    'l_pitcher_wins',
    'game_status',
    'home_team_runs',
    'sv_pitcher',
    'l_pitcher',
    'w_pitcher_wins',
    'l_team',
    'sv_pitcher_saves',
    'w_pitcher',
    'away_team',
    'game_league',
    'l_pitcher_losses',
    'date',
    'game_start_time',
    'home_team_errors',
    'home_team',
    'game_id',
    'w_team',
    'game_type',
    'w_pitcher_losses',
    'away_team_runs',
    'home_team_hits'
]


def load_all_games(years=range(2009, 2016)):
    all_games = []
    for year in years:
        all_games.extend(mlbgame.games(year))
    return mlbgame.combine_games(all_games)


def write_row_to_csv(row_dictionary, fieldnames, filename):
    # Lack of row dictionary indicates header should be written
    if not row_dictionary:
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(filename, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(row_dictionary)


def batter_points(player_stats):
    """
    Given a BatterStats object, compute the number of fantasy points.
    """
    points_no_singles = sum(
        getattr(player_stats, attribute) * points
        for attribute, points in BATTER_POINTS.items()
    )
    # Singles must be extrapolated
    singles = (
        player_stats.h -
        player_stats.t -
        player_stats.d -
        player_stats.hr
    )
    return points_no_singles + (singles * SINGLE_POINTS)


def pitcher_points(player_stats):
    """
    Given a PitcherStats object, compute the number of fantasy points.

    NOTE: data for hit by pitch is available, which subtracts
    0.6 points for each one. Consider attempting to extrapolate this
    from the player data.
    """
    # Change 'true' / 'false' to 1 / 0
    try:
        player_stats.win = int(bool(player_stats.win))
    except AttributeError:
        player_stats.win = 0
    points = sum(
        getattr(player_stats, attribute) * points
        for attribute, points in PITCHER_POINTS.items()
    )
    # Complete game
    if player_stats.out >= 27:
        points += 2.5
        # Complete game shutout
        if player_stats.r == 0:
            points += 2.5
        # No hitter
        if player_stats.h == 0:
            points += 5
    return points


def get_starting_pitcher_id(pitchers):
    pitchers.sort(key=lambda pitcher: pitcher.out)
    return pitchers[-1].id


def format_pitcher_data(pitchers, game, is_home):
    starting_pitcher_id = get_starting_pitcher_id(pitchers)
    for pitcher in pitchers:
        player_dict = {
            'date': game.date,
            'player_id': pitcher.id,
            'full_name': pitcher.name,
            'name': pitcher.name,
            'points': pitcher_points(pitcher),
            'is_starting_pitcher': pitcher.id == starting_pitcher_id,
            'is_home_team': is_home,
            'game_id': game.game_id
        }
        write_row_to_csv(player_dict, pitcher_fieldnames, pitcher_filename)


def format_batter_data(batting, pitching, game, home_batting):
    global player_error_count
    starting_pitcher_id = get_starting_pitcher_id(pitching)
    for player in batting:
        try:
            player_dict = {
                'date': game.date,
                'player_id': player.id,
                'name': player.name,
                'points': batter_points(player),
                'at_bats': player.ab,
                'position': player.pos,
                'batting_position': round(player.bo / 100),
                'batting_average': player.avg,
                'is_starter': player.bo % 100 == 0,
                'is_home_team': home_batting,
                'starting_pitcher_id': starting_pitcher_id,
                'season_hits': player.s_h,
                'season_rbi': player.s_rbi,
                'game_id': game.game_id,
            }
        except AttributeError:
            player_error_count += 1
            continue
        write_row_to_csv(player_dict, batter_fieldnames, batter_filename)


def format_game_data(game):
    game_dict = {
        'away_team_errors': game.away_team_errors,
        'away_team_hits': game.away_team_hits,
        'l_pitcher_wins': game.l_pitcher_wins,
        'game_status': game.game_status,
        'home_team_runs': game.home_team_runs,
        'sv_pitcher': game.sv_pitcher,
        'l_pitcher': game.l_pitcher,
        'w_pitcher_wins': game.w_pitcher_wins,
        'l_team': game.l_team,
        'sv_pitcher_saves': game.sv_pitcher_saves,
        'w_pitcher': game.w_pitcher,
        'away_team': game.away_team,
        'game_league': game.game_league,
        'l_pitcher_losses': game.l_pitcher_losses,
        'date': game.date,
        'game_start_time': game.game_start_time,
        'home_team_errors': game.home_team_errors,
        'home_team': game.home_team,
        'game_id': game.game_id,
        'w_team': game.w_team,
        'game_type': game.game_type,
        'w_pitcher_losses': game.w_pitcher_losses,
        'away_team_runs': game.away_team_runs,
        'home_team_hits': game.home_team_hits,
    }
    write_row_to_csv(game_dict, game_fieldnames, game_filename)


def gather_player_data(all_games):
    global game_error_count
    for game in all_games:
        try:
            player_stats = mlbgame.player_stats(game.game_id)
        except ValueError:
            game_error_count += 1
            continue
        try:
            format_game_data(game)
        except:
            continue
        try:
            format_batter_data(
                player_stats['home_batting'],
                player_stats['away_pitching'],
                game,
                home_batting=True)
        except:
            continue
        try:
            format_batter_data(
                player_stats['away_batting'],
                player_stats['home_pitching'],
                game,
                home_batting=False)
        except:
            continue
        try:
            format_pitcher_data(
                player_stats['home_pitching'],
                game,
                True)
        except:
            continue
        try:
            format_pitcher_data(
                player_stats['home_pitching'],
                game,
                False)
        except:
            continue


def create_tables():
    DBSession.query('drop table if exists batting')
    DBSession.query('drop table if exists pitching')
    DBSession.query('drop table if exists games')
    DBSession.upload_from_csv(batter_filename, 'batting')
    DBSession.upload_from_csv(pitcher_filename, 'pitching')
    DBSession.upload_from_csv(game_filename, 'games')
    DBSession.query(
        """delete from batting where game_id in
        (select game_id from games where away_team in
         (select away_team from games group by away_team having count(*) < 10)
        )
        """)
    DBSession.query(
        """delete from pitching where game_id in
        (select game_id from games where away_team in
         (select away_team from games group by away_team having count(*) < 10)
        )
        """)
    DBSession.query(
        """delete from games where game_id in
        (select game_id from games where away_team in
         (select away_team from games group by away_team having count(*) < 10))
        )
        """)

player_error_count = 0
game_error_count = 0

if __name__ == '__main__':
    import time
    start = time.time()
    write_row_to_csv(None, batter_fieldnames, batter_filename)
    write_row_to_csv(None, pitcher_fieldnames, pitcher_filename)
    write_row_to_csv(None, game_fieldnames, game_filename)
    all_games = load_all_games()
    gather_player_data(all_games)
    stop = time.time()
    print('Took {} seconds'.format(int(stop - start)))
    print('Player error count: {}'.format(player_error_count))
    print('Game error count: {}'.format(game_error_count))
    create_tables()
