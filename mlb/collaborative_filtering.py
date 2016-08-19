"""
tutorial:
http://bugra.github.io/work/notes/2014-04-19/alternating-least-squares-method-
for-collaborative-filtering/
"""

import numpy as np
import pandas as pd


def load_data():
	return pd.DataFrame(np.load('mlb/reccomendation_system_data'))


def changes_nulls_to_zeros(data):
	pass
