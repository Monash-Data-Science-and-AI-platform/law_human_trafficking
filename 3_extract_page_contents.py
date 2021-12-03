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
    'charge', 'court', 'victims', 'defendants', 'defendants_detail', 'pdf_link']] = '-'

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
            # if i in faulty_cases:
            #     legal_reasons = legal_reasons.replace('\n',' || ')
            #     legal_reasons = legal_reasons.replace(',', ';')
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
df.to_csv('dataset extract.csv')

# for html_file in os.listdir(load_path):
#     f = open(os.path.join(load_path,html_file),'r', encoding='utf8')
#     soup = bs.BeautifulSoup(f, 'html.parser')
#     # print(soup)
#     case_law_content = soup.find('div', class_='countryNoHighlight field')
#     # x = case_law_content.find_all('div', class_='countryNoHighlight field ')
#     print(case_law_content)