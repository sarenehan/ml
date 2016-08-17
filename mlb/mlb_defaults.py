BATTER_POINTS = {
    'd': 5,
    't': 8,
    'hr': 10,
    'rbi': 2,
    'r': 2,
    'bb': 2,
    'hbp': 2,
    'sb': 5,
}

SINGLE_POINTS = 3

PITCHER_POINTS = {
    # This is innnings pitched. Innings_pitched = outs / 3,
    # and 2.25 points are given for each inning pitched
    'out': 2.25 / 3,
    'so': 2,
    'win': 4,
    'er': -2.0,
    'h': -0.6,
    'bb': -0.6,
}

BATTER_POINTS_VS_PITCHER = {
    'single': 3,
    'double': 5,
    'triple': 8,
    'home run': 10,
    'walk': 2,
    'hit by pitch': 2,
}
