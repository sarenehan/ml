from database import DBSession
import numpy as np
from collections import defaultdict
import pickle


def load_player_ids(player_id_name):
    """
    Returns a list of distinct player ids
    """
    return [
        point[0] for point in DBSession.query(
            'select distinct({}) from batter_vs_pitcher'.format(
                player_id_name)
        )
    ]


def load_batter_vs_pitcher_averages():
    """
    Returns dictionary in the format:
    {batter_id: {pitcher_id: (avg_batter_points, count)}}
    """
    batter_dict = defaultdict(dict)
    data = DBSession.query(
        """
        select batter_id, avg(batter_points), pitcher_id, count(*)
        from batter_vs_pitcher
        group by pitcher_id, batter_id
        """
    )
    for batter_id, avg_points, pitcher_id, count in data:
        batter_dict[batter_id][pitcher_id] = (avg_points, count)
    return batter_dict


def save_data(data):
    """
    Pickles the data
    """
    with open('mlb/reccomendation_system_data', 'wb') as f:
        pickle.dump(data, f)


def generate_numpy_array(count_cutoff=5):
    batter_ids = load_player_ids('batter_id')
    pitcher_ids = load_player_ids('pitcher_id')
    batter_vs_pitcher_dict = load_batter_vs_pitcher_averages()

    player_array = np.zeros((len(batter_ids), len(pitcher_ids)))

    for b_idx, batter_id in enumerate(batter_ids):
        for p_idx, pitcher_id in enumerate(pitcher_ids):
            try:
                b_avg, count = batter_vs_pitcher_dict[batter_id][pitcher_id]
            except KeyError:
                count = 0
            if count > count_cutoff:
                player_array[b_idx][p_idx] = b_avg
            else:
                player_array[b_idx][p_idx] = None
    save_data(player_array)


if __name__ == '__main__':
    generate_numpy_array()
