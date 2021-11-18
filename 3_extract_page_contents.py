import bs4 as bs
import numpy as np
import pandas as pd
import os
import time
import pickle
import keywords
import re


load_path = 'D:/datasets/law_human_trafficking/page_html/'

df = pd.read_csv('dataset links.csv',index_col=0)

df[['facts_summary', 'legal_reasons',
    'acts', 'means', 'purpose', 'form', 'imprisonment',
    'sector',
    'country', 'decision_date', 'legal_system', 'latest_court_ruling',
    'charge', 'court', 'victims', 'defendants', 'pdf_link']] = '-'

for i in range(len(df.index)):
    name = df.loc[i,'name']
    page_link = df.loc[i,'page_link']
    # print(page_link)
    f = open(os.path.join(load_path, name+'.html'), 'r', encoding='utf8')
    soup = bs.BeautifulSoup(f, 'html.parser')

    # try:
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
    df = keywords.extract_and_search(df, i, soup)

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
    df.loc[i, 'charge'] = '\n=================================\n'.join(charges)

    ## court
    a = soup.find('div', class_='proceeding_court_title fieldFullWidth')
    if a is not None:
        b = a.find('div', class_='value')
        if b is not None:
            df.loc[i, 'court'] = b.text.strip('\n')


    ## victims


    ## defendants


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

        # print(df.loc[i, 'charge'])
    # a = soup.find_all('div', class_='legislationStatusCode fieldFullWidth')
    # # print(len(a))
    # if len(a):
    #     legislations = []
    #     for b in a:
    #         c = b.find('div', class_='value')
    #         d = c.find_all('p')
    #         legislation = []
    #         for e in d:
    #             legislation.append(e.text)
    #         legislations.append('\n'.join(legislation))
    #
    #     df.loc[i,'legislation'] = '\n\n'.join(legislations)
    #     # print('///', df.loc[i,'legislation'])



    # except Exception as e:
    #     print(page_link)
    #     print(e)
    #     print('---------------------------------')

    # if i==5:
    #     break

# print(df)
df.to_csv('dataset.csv')

# for html_file in os.listdir(load_path):
#     f = open(os.path.join(load_path,html_file),'r', encoding='utf8')
#     soup = bs.BeautifulSoup(f, 'html.parser')
#     # print(soup)
#     case_law_content = soup.find('div', class_='countryNoHighlight field')
#     # x = case_law_content.find_all('div', class_='countryNoHighlight field ')
#     print(case_law_content)