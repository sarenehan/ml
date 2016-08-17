from bs4 import BeautifulSoup
import csv
import urllib.request
from database import DBSession

mapping = {'Arizona': 'ARI',
           'Atlanta': 'ATL',
           'Baltimore': 'BAL',
           'Buffalo': 'BUF',
           'Carolina': 'CAR',
           'Chicago': 'CHI',
           'Cincinnati': 'CIN',
           'Cleveland': 'CLE',
           'Dallas': 'DAL',
           'Denver': 'DEN',
           'Detroit': 'DET',
           'Green Bay': 'GB',
           'Houston': 'HOU',
           'Indianapolis': 'IND',
           'Jacksonville': 'JAC',
           'Kansas City': 'KC',
           'Miami': 'MIA',
           'Minnesota': 'MIN',
           'New England': 'NE',
           'New Orleans': 'NO',
           'New York Giants': 'NYG',
           'New York Jets': 'NYJ',
           'Oakland': 'OAK',
           'Philadelphia': 'PHI',
           'Pittsburgh': 'PIT',
           'San Diego': 'SD',
           'San Francisco': 'SF',
           'Seattle': 'SEA',
           'St. Louis': 'STL',
           'Tampa Bay': 'TB',
           'Tennessee': 'TEN',
           'Washington': 'WAS'}

page = urllib.request.urlopen('http://static.pfref.com/years/2014/opp.htm')
soup = BeautifulSoup(page.read())
data = soup.find_all('tr')
data = [point.text[1:] for point in data][:34]
fields = data[1].split(' ')
fields = [fields[0]] + ['City', 'Mascot'] + fields[2:]
fields = fields[:-1]
fields.append('Team_Abbr')
data = [point.split(' ')[:-1] for point in data[1:]]

good_data = []
for row in data:
    if row[0] == fields[0]:
        continue
    if 'York' in row:
        if 'Giants' in row:
            row = [row[0], 'New York Giants'] + row[3:]
        else:
            row = [row[1], 'New York Jets'] + row[3:]
    elif len(row) == 30:
        city = row[1] + ' ' + row[2]
        row = [row[0], city] + row[3:]
    row_dict = {fields[idx]: value for (idx, value) in enumerate(row)}
    row_dict['Team_Abbr'] = mapping[row[1]]
    good_data.append(
        {fields[idx]: value for (idx, value) in enumerate(row)}
    )

output_file_name = 'data/defense_data.csv'

with open(output_file_name, 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fields)
    writer.writeheader()
    for row in good_data:
        writer.writerow(row)


DBSession.upload_from_csv(output_file_name, 'defense')
