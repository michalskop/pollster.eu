'''Estimation of probabilities'''

import datapackage
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
betfair_dp = datapackage.DataPackage(settings.betfair_dp_url)

# read candidates' info
with open(dir_path + "candidates.json") as fin:
    candidates = json.load(fin)

# get last odds
last_date = ''
tipsport_odds = []
for row in tipsport_dp.resources[0].data:
    if row['date'] > last_date:
        last_date = row['date']
        tipsport_odds = []
    if row['date'] == last_date:
        tipsport_odds.append(row)

last_date = ''
fortuna_odds = []
for row in fortuna_dp.resources[0].data:
    if row['date'] > last_date:
        last_date = row['date']
        fortuna_odds = []
    if row['date'] == last_date:
        fortuna_odds.append(row)

last_date = ''
betfair_odds = []
for row in betfair_dp.resources[0].data:
    if row['date'] > last_date:
        last_date = row['date']
        betfair_odds = []
    if row['date'] == last_date:
        betfair_odds.append(row)


# get candidate by identifier
def candidate_by_identifier(column, value):
    for candidate in candidates:
        try:
            if candidate[column] == value:
                return candidate
        except:
            nothing = None
    return None

# prepare inverses of odds, note new candidates
news = {
    "fortuna": 0,
    "tipsport": 0,
    "betfair": 0,
    "image": 0
}
tipsport_exclude = [1, 48]
for row in tipsport_odds:
    if row['identifier'] not in tipsport_exclude:
        candidate = candidate_by_identifier('tipsport_identifier', row['identifier'])
        if candidate:
            row['odds'] = float(row['odds'])
            candidate['tipsport_odds'] = row['odds']
            candidate['tipsport_odds_inverse'] = 1 / row['odds']
        else:
            new_candidate = {
                "name": row['title'],
                "abbreviation": row['title'],
                "tipsport_identifier": row['identifier']
            }
            new_candidate['tipsport_odds'] = None
            new_candidate['tipsport_odds_inverse'] = 0
            candidates.append(new_candidate)
            news['tipsport'] += 1

for row in fortuna_odds:
    candidate = candidate_by_identifier('fortuna_identifier', row['identifier'])
    if candidate:
        row['odds'] = float(row['odds'])
        candidate['fortuna_odds'] = row['odds']
        candidate['fortuna_odds_inverse'] = 1 / row['odds']
    else:
        new_candidate = {
            "name": row['title'],
            "abbreviation": row['title'],
            "fortuna_identifier": row['identifier']
        }
        new_candidate['fortuna_odds'] = None
        new_candidate['fortuna_odds_inverse'] = 0
        candidates.append(new_candidate)
        news['fortuna'] += 1

for row in betfair_odds:
    candidate = candidate_by_identifier('betfair_identifier', row['identifier'])
    if candidate:
        try:
            row['odds'] = float(row['odds'])
            if row['odds'] >= float(row['available_to_back_0']) and row['odds'] <= float(row['available_to_lay_0']):
                candidate['betfair_odds'] = row['odds']
                candidate['betfair_odds_inverse'] = 1 / row['odds']
                candidate['betfair_probability'] = candidate['betfair_odds_inverse']
        except:
            nothing = None
    else:
        new_candidate = {
            "name": row['title'],
            "abbreviation": row['title'],
            "betfair_identifier": row['identifier']
        }
        new_candidate['betfair_odds'] = None
        new_candidate['betfair_odds_inverse'] = 0
        new_candidate['betfair_probability'] = 0
        candidates.append(new_candidate)
        news['betfair'] += 1

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
    try:
        candidate['probability'] = (candidate['tipsport_probability'] + candidate['fortuna_probability'] + candidate['betfair_probability']) / 3
    except:
        candidate['probability'] = (candidate['tipsport_probability'] + candidate['fortuna_probability']) / 2

# recalibrate to 1
total_sum = 0
for candidate in candidates:
    total_sum += candidate['probability']
for candidate in candidates:
    candidate['probability'] = candidate['probability'] / total_sum

# save the file
with open(dir_path + "candidates_estimated.json", "w") as fout:
    json.dump(sorted(candidates, key=itemgetter('probability'), reverse=True), fout)

# find missing images in TOP12
for i in range(0, 12):
    candidate = sorted(candidates, key=itemgetter('probability'), reverse=True)[i]
    try:
        candidate['image']
    except:
        news['image'] += 1

# save news
news_string = ""
for k in news:
    if news[k] > 0:
        news_string = news_string + "new " + k + ": " + str(news[k]) + ","
with open(dir_path + "news.txt", "w") as fout:
    fout.write(news_string)
