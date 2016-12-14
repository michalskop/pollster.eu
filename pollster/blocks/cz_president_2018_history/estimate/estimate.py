'''Estimation of probabilities'''

import copy
import csv
import datapackage
import datetime
import dateutil.parser
import json
from operator import itemgetter
import os
import settings

# get path
try:
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
except:
    dir_path = ""

# read datapackages
tipsport_dp = datapackage.DataPackage(settings.tipsport_dp_url)
fortuna_dp = datapackage.DataPackage(settings.fortuna_dp_url)

# read candidates' info
with open(dir_path + settings.candidates_path + "candidates.json") as fin:
    candidates = json.load(fin)

# get candidate by identifier
def candidate_by_identifier(column,value):
    for candidate in candidates:
        try:
            if candidate[column] == value:
                return candidate
        except:
            nothing = None
    return None

# dates for interval
since = dateutil.parser.parse(settings.since)
until = datetime.datetime.now()
oneday = since
history = {}
while oneday < until:
    # get last odds till oneday
    last_date = ''
    tipsport_odds = []
    for row in tipsport_dp.resources[0].data:
        if (row['date'] > last_date) and (row['date'] < oneday.isoformat()):
            last_date = row['date']
            tipsport_odds = []
        if row['date'] == last_date:
            tipsport_odds.append(row)

    last_date = ''
    fortuna_odds = []
    for row in fortuna_dp.resources[0].data:
        if (row['date'] > last_date) and (row['date'] < oneday.isoformat()):
            last_date = row['date']
            fortuna_odds = []
        if row['date'] == last_date:
            fortuna_odds.append(row)

    # prepare inverses of odds, note new candidates
    news = {
        "color": ""
    }
    tipsport_exclude = [1, 48]
    for row in tipsport_odds:
        if row['identifier'] not in tipsport_exclude:
            candidate = candidate_by_identifier('tipsport_identifier',row['identifier'])
            if candidate:
                row['odds'] = float(row['odds'])
                candidate['tipsport_odds'] = row['odds']
                candidate['tipsport_odds_inverse'] = 1/row['odds']
            else:
                new_candidate = {
                    "name":row['title'],
                    "abbreviation":row['title'],
                    "tipsport_identifier": row['identifier']
                }
                new_candidate['tipsport_odds'] = None
                new_candidate['tipsport_odds_inverse'] = 0
                candidates.append(new_candidate)
                news['tipsport'] += 1

    for row in fortuna_odds:
        candidate = candidate_by_identifier('fortuna_identifier',row['identifier'])
        if candidate:
            row['odds'] = float(row['odds'])
            candidate['fortuna_odds'] = row['odds']
            candidate['fortuna_odds_inverse'] = 1/row['odds']
        else:
            new_candidate = {
                "name":row['title'],
                "abbreviation":row['title'],
                "fortuna_identifier": row['identifier']
            }
            new_candidate['fortuna_odds'] = None
            new_candidate['fortuna_odds_inverse'] = 0
            candidates.append(new_candidate)
            news['fortuna'] += 1

    # calculate probabilities based on odds
    tipsport_sum = 0
    fortuna_sum = 0
    for candidate in candidates:
        try:
            tipsport_sum += candidate['tipsport_odds_inverse']
        except:
            nothing = None
        try:
            fortuna_sum += candidate['fortuna_odds_inverse']
        except:
            nothing = None
    for candidate in candidates:
        try:
            candidate['tipsport_probability'] = candidate['tipsport_odds_inverse'] / tipsport_sum
        except:
            candidate['tipsport_probability'] = 0
        try:
            candidate['fortuna_probability'] = candidate['fortuna_odds_inverse'] / fortuna_sum
        except:
            candidate['fortuna_probability'] = 0

    # estimate probabilities
    for candidate in candidates:
        if tipsport_sum > 0:
            candidate['probability'] = round((candidate['tipsport_probability'] + candidate['fortuna_probability']) / 2 * 1000)/1000
        else:
            candidate['probability'] = round(candidate['fortuna_probability'] * 1000)/1000

    for candidate in candidates:
        try:
            history[candidate['name']]
        except:
            history[candidate['name']] = []
        c = copy.deepcopy(candidate)
        c['date'] = oneday.strftime('%Y-%m-%d')
        history[candidate['name']].append(c)

    oneday += datetime.timedelta(1)

# select only those over threshold
selected_history = []
for k in history:
    selected = False
    for row in history[k]:
        if row['probability'] > settings.minimum:
            selected = True
            break
    if selected:
        for row in history[k]:
            selected_history.append(row)

# save the file
with open(dir_path + "candidates_estimated.csv","w") as fout:
    csvw = csv.writer(fout)
    csvw.writerow(['date','value','name','color'])
    for row in selected_history:
        try:
            row['color']
        except:
            row['color'] = '#666'
            news['color'] = 'missing color(s)'
        if row['probability'] > 0:
            csvw.writerow([row['date'],row['probability'],row['abbreviation'],row['color']])

# save news
with open(dir_path + "news.txt","w") as fout:
    fout.write(news['color'])
