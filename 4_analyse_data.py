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
df.insert(1, column='ignore_means', value='-')
df.insert(1, column='meet_criteria', value='-')

for i in range(len(df.index)):
    # check if all victims children -> can ignore means
    victims = df.loc[i, 'victims']
    if victims != '-':
        child = re.search('Child', victims, re.IGNORECASE)
        adult = re.search('Male', victims, re.IGNORECASE) or re.search('Female', victims, re.IGNORECASE)
        unknown = re.search('\? \?', victims, re.IGNORECASE)
        if child and not adult and not unknown:
            df.loc[i, 'ignore_means'] = 'Yes'

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

    # check if case meets criteria for human trafficking
    acts = (df.loc[i, 'acts'] != '-')
    means = (df.loc[i, 'means'] != '-')
    purpose = (df.loc[i, 'purpose'] != '-')
    form = re.search('Transnational', df.loc[i, 'form'], re.IGNORECASE) and \
           re.search('Organized Criminal Group', df.loc[i, 'form'], re.IGNORECASE)

    if acts and purpose and form and (means or df.loc[i, 'ignore_means'] == 'Yes') \
        and (df.loc[i, 'serious_crime'] == 'Yes'):
        df.loc[i, 'meet_criteria'] = 'Yes'

print('total cases', len(df.index))
print('meet_criteria', np.sum(df.loc[:, 'meet_criteria'] == 'Yes'))

df.to_csv('dataset analysed.csv')
