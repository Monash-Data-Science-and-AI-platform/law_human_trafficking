import bs4 as bs
import numpy as np
import pandas as pd
import os
import time
import pickle
import keywords
import re


df = pd.read_csv('dataset extract.csv',index_col=0)

df.insert(1, column='serious_crime', value='-')
df.insert(1, column='victims_type', value='-')
df.insert(1, column='meet_criteria', value='-')

stats = {
    'imprisonment': {
        'no info': 0,
        'any has serious crime': 0,
        'all no serious crime': 0
    },
    'victims_type':{
        'all children': 0,
        'all adult': 0,
        'mix': 0,
        'unknown': 0,
        '-': 0
    }
}

for i in range(len(df.index)):
    # check if all victims children -> can ignore means
    victims = df.loc[i, 'victims']
    if victims != '-':
        child = re.search('Child', victims, re.IGNORECASE)
        adult = re.search('Male', victims, re.IGNORECASE) or re.search('Female', victims, re.IGNORECASE)
        unknown = re.search('\? \?', victims, re.IGNORECASE)
        if child and not adult and not unknown:
            df.loc[i, 'victims_type'] = 'all children'
        elif child and adult:
            df.loc[i, 'victims_type'] = 'mix'
        elif not child and adult and not unknown:
            df.loc[i, 'victims_type'] = 'all adult'
        else:
            df.loc[i, 'victims_type'] = 'unknown'

    # check if imprisonment >= 4 years
    imprisonment = df.loc[i, 'imprisonment']
    life = re.search('life', imprisonment, re.IGNORECASE)
    if life:
        df.loc[i, 'serious_crime'] = 'Yes'
    else:
        terms = re.findall('(\d+) year', imprisonment)
        for y in terms:
            if int(y) >= 4:
                df.loc[i, 'serious_crime'] = 'Yes'
                break

    if imprisonment == '-':
        stats['imprisonment']['no info'] += 1
    elif df.loc[i, 'serious_crime'] == 'Yes':
        stats['imprisonment']['any has serious crime'] += 1
    else:
        stats['imprisonment']['all no serious crime'] += 1


    # check if case meets criteria for human trafficking
    acts = (df.loc[i, 'acts'] != '-')
    means = (df.loc[i, 'means'] != '-')
    purpose = (df.loc[i, 'purpose'] != '-')
    form = re.search('Transnational', df.loc[i, 'form'], re.IGNORECASE) and \
           re.search('Organized Criminal Group', df.loc[i, 'form'], re.IGNORECASE)

    if acts and purpose and form and (means or df.loc[i, 'victims_type'] == 'all children') \
        and (df.loc[i, 'serious_crime'] == 'Yes'):
        df.loc[i, 'meet_criteria'] = 'Yes'

for measure in stats['victims_type']:
    stats['victims_type'][measure] = (df.loc[:, 'victims_type']==measure).sum()
print('total cases', len(df.index))
print('meet_criteria', np.sum(df.loc[:, 'meet_criteria'] == 'Yes'))
for field in stats:
    total = 0
    for measure in stats[field]:
        print(field, ':', measure, '=', stats[field][measure])
        total += stats[field][measure]
    print(field, ':', 'total', '=', total)

df.to_csv('dataset analysed.csv')
