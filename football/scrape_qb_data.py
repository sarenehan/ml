from bs4 import BeautifulSoup
import csv
import urllib.request
from database import DBSession

page = urllib.request.urlopen('http://static.pfref.com/years/2014/passing.htm')
soup = BeautifulSoup(page.read())
data = soup.find_all('tr')
data = [point.text[1:].replace('*', '').replace('+', '') for point in data]
fields = data[0].split(' ')
fields = [fields[0]] + ['First_Name', 'Last_Name'] + fields[2:]
fields = fields[:-1]
data = [point.split(' ')[:-1] for point in data]

good_data = []

for row in data:
    if row[0] == fields[0]:
        continue
    good_data.append(
        {fields[idx]: value for (idx, value) in enumerate(row)}
    )

output_file_name = 'data/qb_data.csv'

with open(output_file_name, 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fields)
    writer.writeheader()
    for row in good_data:
        writer.writerow(row)


DBSession.upload_from_csv(output_file_name, 'quarterback')
