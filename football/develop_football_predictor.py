"""
Data here: http://static.pfref.com/years/2015/passing.htm


"""
from database import DBSession
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from collections import namedtuple
from sklearn.cross_validation import train_test_split
from statistics import mean, median
import numpy as np

columns = [col[1] for col in DBSession.get_column('football_view')]
Football = namedtuple(
    'Football',
    ' '.join(columns)
)


def load_football_obj(row):
    row_dict = {col: row[idx] for (idx, col) in enumerate(columns)}
    return Football(**row_dict)


def remove_columns(data, columns_to_remove):
    FootallReduced = namedtuple(
        'FootballReduced',
        ' '.join([
            col for col in data[0]._fields
            if col not in columns_to_remove])
    )
    data_to_return = []
    for point in data:
        row_dict = {col: getattr(point, col) for col in FootallReduced._fields}
        data_to_return.append(FootallReduced(**row_dict))
    return data_to_return


def load_data():
    return [
        load_football_obj(row)
        for row in
        DBSession.query('select * from football_view')
    ]


def dict_vectorize(data):
    dict_vect = DictVectorizer()
    X = dict_vect.fit_transform(data)
    return np.nan_to_num(X.toarray())


def featurize_columns(data, columns_to_featurize):
    data_to_featurize = [
        {'col': getattr(point, col) for col in columns_to_featurize}
        for point in data
    ]
    featurized_data = dict_vectorize(data_to_featurize)
    data = remove_columns(data, columns_to_featurize)
    new_data = []
    for idx, row in enumerate(data):
        initial_row = np.array([getattr(row, field) for field in row._fields])
        new_data.append(np.concatenate([initial_row, featurized_data[idx]]))
    return new_data


def split_into_output_and_input(all_data):
    output = [point.Yards for point in all_data]
    return all_data, output


def train_model(x_data, y_data, estimators, depth):
    model = GradientBoostingRegressor(loss='ls', n_estimators=estimators, max_depth=depth)
    model = RandomForestRegressor(n_estimators=estimators)
    from sklearn.svm import SVR
    model = LinearRegression()
    model.fit(x_data, y_data)
    return model


def compute_base_error(y_data):
    base_prediction = mean(y_data)
    return mean((base_prediction - point)**2 for point in y_data)**.5


if __name__ == '__main__':
    data = load_data()
    x_data, y_data = split_into_output_and_input(data)
    print('Base Error: {}'.format(compute_base_error(y_data)))
    x_data = remove_columns(x_data, ['Yards', 'Description'])
    x_data = featurize_columns(x_data, ['PlayType', 'Formation', 'PassType'])
    trn_X, val_x, trn_y, val_y = train_test_split(x_data, y_data, test_size=.3)
    for attr in ['Yards', 'Description', 'PlayType', 'Formation', 'PassType']:
        columns.remove(attr)
    params = [
        # (25, 3),
        # (25, 6),
        # (25, 10),
        # (50, 2),
        # (50, 3),
        # (50, 4),
        (50, 5),
        # (50, 6)
        # (50, 10),
        # (100, 3),
        # (100, 6),
        # (100, 10),
        # (200, 3),
        # (200, 6),
        # (200, 10),
    ]
    for est, depth in params:
        print('\nParameters: {}, {}'.format(est, depth))
        model = train_model(trn_X, trn_y, est, depth)
        print('Model Error: {}\n'.format(mean((val_y[idx] - point)**2
              for idx, point in enumerate(model.predict(val_x)))**.5))
        feats = {col: model.feature_importances_[idx] for idx, col in enumerate(columns)}
        for key, val in feats.items():
            print("{}: {}".format(key, val))
    import pdb; pdb.set_trace()

