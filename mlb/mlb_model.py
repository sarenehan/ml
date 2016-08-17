from database import DBSession
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.feature_extraction import DictVectorizer
import statsmodels.api as sm
from statistics import mean
import pandas as pd
import numpy as np
from collections import namedtuple


columns = [col[1] for col in DBSession.get_column('batting_formatted')]
MlbBatter = namedtuple(
    'Batter',
    ' '.join(columns)
)


def load_batter_obj(row):
    row_dict = {col: row[idx] for (idx, col) in enumerate(columns)}
    return MlbBatter(**row_dict)


def remove_columns(data, columns_to_remove):
    global columns
    MlbReduced = namedtuple(
        'MlbBatterReduced',
        ' '.join([
            col for col in data[0]._fields
            if col not in columns_to_remove])
    )
    data_to_return = []
    for point in data:
        row_dict = {col: getattr(point, col) for col in MlbReduced._fields}
        data_to_return.append(MlbReduced(**row_dict))
    # Remove these columns from the global column list
    for col in columns_to_remove:
        columns.remove(col)
    return data_to_return


def load_data():
    columns_to_remove = [
        'is_starter',
        'last_game_was_bad',
        'last_game_last_month',
        'last_week_season',
        'last_month_season'
    ]
    rows = [
        load_batter_obj(row)
        for row in
        DBSession.query('select * from batting_formatted')
    ]
    return remove_columns([
        row for row in rows
        if row.average_points > 4
        and row.is_starter
        and row.previous_games_count > 20
    ], columns_to_remove)


def split_into_output_and_input(all_data, output_column='points'):
    global columns
    output = [point.points for point in all_data]
    x_data = remove_columns(all_data, [output_column])
    return x_data, output


def compute_rmse(predictions, actual):
    diffs_sq = [
        (pred - actual[idx])**2
        for idx, pred in enumerate(predictions)
    ]
    return mean(diffs_sq) ** .5


def compute_base_error(x_data, y_data):
    predictions = [point.average_points for point in x_data]
    return compute_rmse(predictions, y_data)


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


def make_verbose_model(x_data, y_data):
    x_data = sm.add_constant(x_data)
    data_frame = pd.DataFrame(x_data)
    data_frame.columns = ['Intercept'] + columns
    model = sm.OLS(pd.Series(y_data), data_frame).fit()
    print(model.summary())
    print('Model Error: {}'.format(
        compute_rmse(model.predict(data_frame), y_data)))


def make_model(x_data, y_data):
    trn_X, val_x, trn_y, val_y = train_test_split(x_data, y_data, test_size=.3)
    model = GradientBoostingRegressor(n_estimators=300)
    # model = SVR()
    # model = RandomForestRegressor(n_estimators=500)
    # model = LinearRegression()
    model.fit(trn_X, trn_y)
    print('Model Error: {}'.format(compute_rmse(model.predict(val_x), val_y)))
    # analyzer_error(model, x_data, y_data)


def analyzer_error(model, x_data, y_data):
    model.fit(x_data, y_data)
    residual_data = [
        (abs(y_data[idx] - point), idx)
        for idx, point in enumerate(model.predict(x_data))
    ]
    x_points = [point[1] for point in residual_data]
    y_points = [point[0] for point in residual_data]
    import plotly.plotly as py
    import plotly.graph_objs as go
    py.sign_in('sarenehan', 'kbdx1l9r2x')
    trace = go.Scatter(
        x=x_points,
        y=y_points,
        mode='markers'
    )

    data = [trace]

    # Plot and embed in ipython notebook!
    py.plot(data, filename='basic-scatter')


if __name__ == '__main__':
    all_data = load_data()
    x_data, y_data = split_into_output_and_input(all_data)
    print('Base Error: {}'.format(compute_base_error(x_data, y_data)))
    make_model(x_data, y_data)
    make_verbose_model(x_data, y_data)
