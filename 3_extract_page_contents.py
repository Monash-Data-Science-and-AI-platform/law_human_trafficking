'''
This script loads the saved html for each page/case and extracts various content from the html.
The extracted information is stored in respective columns in the dataframe and saved as csv.
'''


import bs4 as bs
import numpy as np
import pandas as pd
import os
import time
import pickle
import keywords
import re
import json
import copy

load_path = 'D:/datasets/law_human_trafficking/page_html/'

df = pd.read_csv('dataset links.csv',index_col=0)

# keyword_definitions contains all keywords of interest to search for.
# sorted by theme (acts, means, purpose)
# each theme is a dict of keywords and (as a list) the variants of each keyword that is accepted.
keyword_definitions = json.load(open('keywords.json','r'))

# bad_cases contains the cleaned version of website content that had unusual characters that could not be read
bad_cases = json.load(open('bad_cases.json','r'))

df[['facts_summary', 'legal_reasons',
    'acts', 'means', 'purpose', 'form_transnational', 'form_organised', 'imprisonment',
    'sector',
    'country', 'decision_date', 'legal_system', 'latest_court_ruling',
    'charge', 'court', 'victims', 'defendants', 'defendants_detail', 'pdf_link']] = '-'

# all_keywords collects all keywords from the keywords section on the website, duplicates included
all_keywords = {
    "acts": [],
    "means": [],
    "purpose": [],
    "form": []
}

# keyword_count keeps track of the number of times a keyword appears on the website keyword section. Only counts exact matches.
keyword_count = copy.deepcopy(keyword_definitions)

# init keyword_count to 0
for theme in keyword_count:
    for keyword in keyword_count[theme]:
        keyword_count[theme][keyword] = 0

# for each case (row in the dataframe)
for i in range(len(df.index)):
    name = df.loc[i,'name']
    page_link = df.loc[i,'page_link']
    f = open(os.path.join(load_path, name+'.html'), 'r', encoding='utf8')
    soup = bs.BeautifulSoup(f, 'html.parser')

    ## facts_summary
    a = soup.find('div', class_='factSummary')
    if a is not None:
        b = a.find_all('p')
        if b is not None:
            facts_summary = ''
            for c in b:
                facts_summary += c.text
                if len(c.text) > 2:
                    facts_summary += ' \n '
            if i in [53]:
                facts_summary = 'ERROR'
            df.loc[i, 'facts_summary'] = facts_summary

    ## legal_reasons
    a = soup.find('div', class_='legalReasoning field line')
    if a is not None:
        b = a.find('div', {'class':'value'})
        if b is not None:
            c = b.find_all('p')
            legal_reasons = ''
            for d in c:
                legal_reasons += d.text
                if len(d.text) > 2:
                    legal_reasons += ' \n '
            df.loc[i, 'legal_reasons'] = legal_reasons

    ## keywords
    df = keywords.extract_and_search(keyword_definitions, bad_cases, df, i, soup, all_keywords, keyword_count)


    ## imprisonment
    terms = []
    for a in soup.find_all('div', class_='termOfImprisonment field'):
        b = a.find('div', class_='value')
        if b is not None:
            terms.append(re.sub(r'\W+', ' ', b.text))
    if len(terms):
        df.loc[i, 'imprisonment'] = ' | '.join(terms)

    ## country
    for a in soup.find('div', class_='countryNoHighlight field'):
        for b in a.find('a'):
            df.loc[i,'country'] = str(b)

    ## decision_date
    for a in soup.find_all('div', class_='proceeding_decisionDate field'):
        for b in a.find('div', {'class':'value'}):
            df.loc[i,'decision_date'] = str(b)

    ## legal_system
    for a in soup.find_all('div', class_='legalSystem field'):
        for b in a.find('div', {'class':'value'}):
            df.loc[i,'legal_system'] = str(b)

    ## latest_court_ruling
    for a in soup.find_all('div', class_='presentCourt field'):
        for b in a.find('div', {'class':'value'}):
            df.loc[i,'latest_court_ruling'] = str(b)

    ## charge (legislation, charge, verdict)
    a = soup.find_all('div', class_='charge')
    charges = []
    for b in a:
        charges.append(b.text)
    full_charge = '\n=================================\n'.join(charges)
    if i in [633, 911]:
        full_charge = 'ERROR'
    df.loc[i, 'charge'] = full_charge

    ## court
    a = soup.find('div', class_='proceeding_court_title fieldFullWidth')
    if a is not None:
        b = a.find('div', class_='value')
        if b is not None:
            df.loc[i, 'court'] = b.text.strip('\n')


    ## victims
    # victims are stored in the format gender_age_country.
    # if a field is missing, it is filled with '?', e.g. female_?_australia
    # multiple victims are separated by '|'
    a = soup.find('div', class_='victimsPlaintiffs')
    if a is not None:
        persons = a.find_all('div', class_='person')
        if persons is not None:
            victims = []
            for c in persons:
                gender = '?'
                age = '?'
                nation = '?'
                d = c.find_all('div', class_='age field line')
                if d is not None:
                    for e in d:
                        f = e.find('div', class_='label')
                        if f is not None:
                            if f.text == 'Gender: ':
                                gender = e.find('div', class_='value').text
                            elif f.text == 'Age: ':
                                age = e.find('div', class_='value').text
                d = c.find('div', class_='name field line')
                if d is not None:
                    e = d.find('div', class_='value')
                    if e is not None:
                        nation = e.text
                        nation = nation.replace(' / ', '-').strip(' \n\t')
                        nation = re.sub("\s+", " ", nation)
                victims.append('_'.join([gender,age,nation]))
            df.loc[i, 'victims'] = ' | '.join(victims)

    ## defendants
    # defendants are stored in the format gender_age_country.
    # if a field is missing, it is filled with '?', e.g. female_?_australia
    # multiple defendants are separated by '|'
    a = soup.find('div', class_='defendantsRespondents')
    if a is not None:
        df.loc[i, 'defendants_detail'] = a.text
        persons = a.find_all('div', class_='person')
        if persons is not None:
            defendants = []
            for p in persons:
                gender = '?'
                nation = '?'
                age = '?'
                q = p.find_all('div', class_='name field line')
                if q is not None:
                    for r in q:
                        label = r.find('div', class_='label')
                        if label is not None:
                            if label.text == 'Gender: ':
                                gender = r.find('div', class_='value').text
                            elif label.text == 'Nationality: ':
                                nation = r.find('div', class_='value').text
                                nation = nation.replace(' / ', '-').strip(' \n\t')
                                nation = re.sub("\s+", " ", nation)

                q = p.find('div', class_='age field line')
                if q is not None:
                    age = q.find('div', class_='value').text

                defendants.append('_'.join([gender,age,nation]))
            df.loc[i, 'defendants'] = ' | '.join(defendants)





    ## pdf_link
    a = soup.find('div', class_='sources')
    links = []
    if a is not None:
        b = a.find_all('p')
        if b is not None:

            for c in b:
                d = c.find('a', href=True)
                if d is not None:
                    links.append(d['href'])

    if len(links):
        df.loc[i, 'pdf_link'] = ' \n'.join(links)


df.to_csv('dataset extract.csv')

# print all unique keywords found from the website
for key in all_keywords:
    print('###', key, '###')
    s = set(all_keywords[key])
    for u in s:
        print(u)

# print each keyword and its number of occurrences
for theme in keyword_count:
    for keyword in keyword_count[theme]:
        print(keyword, keyword_count[theme][keyword])
