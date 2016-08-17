import pickle
import numpy as np


if __name__ == '__main__':
    # with open('mlb/reccomendation_system_data', 'rb') as f:
    #     data = pickle.load(f)

    # import pdb; pdb.set_trace()
    import os
    os.system(
        """
        ipython mlb/gather_mlb_data.py
        """  # noqa
    )
    os.system(
        """
        ipython mlb/gather_batter_vs_pitcher_data.py
        """  # noqa
    )
