Scoring rules: https://www.draftkings.com/help/mlb

Player data: http://panz.io/mlbgame/#mlbgame.player_stats

Schema: less /usr/local/lib/python2.7/site-packages/mlbgame/statmap.py

Look into pitcher game_score attribute. USE THIS INSTEAD OF FANTASY POINTS.

Featurize predicted pitcher performance

Draftkings rules: http://www.highya.com/draftkings-reviews

Make sure that using date > date is never the same day

Ensure that dates arent imported as strings
(update batting set date = date(date);
sqlite> update pitching set date = date(date);)

Decide what to do when there is no data from the last week

How does a player do early in a season vs late in a season

Integrate all pitchers into feature space

Score batter based on how well he performed against quality of pitcher / pitcher throwing arm

Figure out how to deal with injuries

Use confidence intervals to estimate a risk

Stadium: http://espn.go.com/fantasy/baseball/story/_/page/mlbdk2k16_parkfactors/which-parks-most-least-favorable-fantasy-baseball-hitters-pitchers-mlb
Other Source: http://espn.go.com/mlb/stats/parkfactor
"Park Factors"

Which team is expected to win / by how much

Use this data: Events: http://panz.io/mlbgame/events.m.html
-Use the pitcher style

Predict who will pitch in the next game as relief pitcher, etc

Player Vs This pitcher specifically: an Alternating least squares problem.

If a player has been performing poorly recently and they are good historically,
then they may be expected to perform better in the next game: ie: 1 - (career_average / month_avg)

For historical pitcher performance, make sure the pitcher was the starting pitcher

Autoregressive Integrated Moving Average (ARIMA): http://stackoverflow.com/questions/31690134/python-statsmodels-help-using-arima-model-for-time-series