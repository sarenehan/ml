"""
This script generates the matrix used for collaborative filtering
"""


from database import DBSession
import numpy as np
from collections import defaultdict


def load_player_ids(player_id_name):
    """
    Returns a list of distinct player ids
    """
    return np.array([
        point[0] for point in DBSession.query(
            'select distinct({}) from batter_vs_pitcher'.format(
                player_id_name)
        )
    ])


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
    np.save('mlb/reccomendation_system_data', data, allow_pickle=False)


def remove_nan_players(player_array, player_ids, axis):
    """
    Returns player_array and player_ids with players with no non-null
    stats removed.

    Axis denotes batters or pitchers.
        axis = 0 denotes batters
        axis = 1 denotes pitchers
    """
    a_axis_length = player_array.shape[0]
    b_axis_length = player_array.shape[1]
    if axis == 0:
        indeces_to_delete = [
            idx for idx in range(a_axis_length)
            if sum(np.isnan(player_array[idx])) == b_axis_length
        ]
    else:
        indeces_to_delete = [
            idx for idx in range(b_axis_length)
            if sum(np.isnan(player_array[:, idx])) == a_axis_length
        ]
    index_offset = 0
    for index in indeces_to_delete:
        eff_index = index - index_offset
        player_array = np.delete(player_array, eff_index, axis)
        player_ids = np.delete(player_ids, eff_index)
        index_offset += 1
    return player_array, player_ids


def generate_numpy_array(count_cutoff=10):
    """
    Saves an array of batters vs pitchers

    TODO: preserve the batter and pitcher ids
    """
    batter_ids = load_player_ids('batter_id')
    pitcher_ids = load_player_ids('pitcher_id')

    batter_vs_pitcher_dict = load_batter_vs_pitcher_averages()
    player_array = np.zeros((len(batter_ids), len(pitcher_ids)))
    b_idx = 0
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
    # player_array, batter_ids = remove_nan_players(
    #     player_array, batter_ids, axis=0)
    # player_array, batter_ids = remove_nan_players(
    #     player_array, pitcher_ids, axis=1)
    shape = np.shape(player_array)

    count = sum(
        [shape[0] - point for point in sum(np.isnan(
            player_array))])
    total_count = shape[0] * shape[1]
    print('Count: {}'.format(count))
    print('Shape: {}'.format(shape))
    print('Percentage: {}'.format(100 * (count / total_count)))
    return player_array, batter_ids, pitcher_ids


if __name__ == '__main__':
    matrix, batter_ids, pitcher_ids = generate_numpy_array()
    save_data(matrix)
    np.save('mlb/pitcher_ids', pitcher_ids)
    np.save('mlb/batter_ids', batter_ids)
