import re
import json
import copy

'''
extract_and_search extracts values for the following fields: 'acts', 'means', 'purpose', 'form', 'sector'.
For 'acts', 'means', 'purpose':
It searchers for keywords defined in keywords.json in 2 locations: the keyword field in the html, and in the text.
'keyword_definitions' is a dictionary structured as keyword_definitions[theme][keywords][variant]
If a keyword is found exactly in keyword field, flag = 'K'
Else if a keyword variant is found, flag = 'k'
If a keyword is found exactly in text, flag = 'T'
Else if a keyword variant is found, flag = 't'

'sector' is copied as is.
'form' is split into two columns: form_transnational (transnational vs internal), form_organised (organised crime)
'''

def extract_and_search(keyword_definitions, bad_cases, df, i, soup, all_keywords, keyword_count):

    flags = copy.deepcopy(keyword_definitions)
    for theme in flags:
        for keyword in flags[theme]:
            flags[theme][keyword] = ''


    ## search keywords in keyword fields
    a = soup.find_all('div', class_='keywordCategory field')
    if a is not None:
        for b in a: # for each theme on the webpage
            # identify theme and extract keywords
            keyword_label = b.find('div', class_='label')

            if keyword_label is not None:
                keyword_label = keyword_label.text
                values = b.find_all('div', class_='value')
                values_list = []
                for v in values:
                    values_list.append(v.text)

                theme = None
                if keyword_label == 'Acts:':
                    theme = 'acts'
                    all_keywords['acts'] += values_list
                elif keyword_label == 'Means:':
                    theme = 'means'
                    all_keywords['means'] += values_list
                elif keyword_label == 'Purpose of Exploitation:':
                    theme = 'purpose'
                    all_keywords['purpose'] += values_list
                elif keyword_label == 'Form of Trafficking:':
                    theme = 'form'
                    all_keywords['form'] += values_list
                elif keyword_label == 'Sector in which exploitation takes place:':
                    theme = 'sector'

                if theme == 'sector':
                    df.loc[i, theme] = ' | '.join(values_list)
                elif theme == 'form':
                    for v in values_list:
                        if re.search('transnational', v, re.IGNORECASE) or re.search('internal', v, re.IGNORECASE):
                            df.loc[i, 'form_transnational'] = v
                        if re.search('Organized', v, re.IGNORECASE):
                            df.loc[i, 'form_organised'] = v
                elif theme is not None:
                    for keyword in keyword_definitions[theme]:
                        in_keywords = False
                        for v in values_list:
                            if re.search(keyword, v, re.IGNORECASE):
                                flags[theme][keyword] += 'K' # if found in keyword section, mark as capital K
                                in_keywords = True
                                break
                        if in_keywords:
                            keyword_count[theme][keyword] += 1

                        # if original keyword not found, search for variants
                        if not in_keywords:
                            for variant in keyword_definitions[theme][keyword]:
                                for v in values_list:
                                    if re.search(variant, v, re.IGNORECASE):
                                        flags[theme][keyword] += 'k' # if variant found in keyword section, mark as lowercase k
                                        in_keywords = True
                                        break
                                if in_keywords:
                                    break

    ## search keywords in text (only facts_summary and legal_reasons)
    facts_summary = df.loc[i, 'facts_summary']
    if i == 53:
        facts_summary = bad_cases['53']['facts_summary']

    legal_reasons = df.loc[i, 'legal_reasons']

    for theme in keyword_definitions:
        for keyword in keyword_definitions[theme]:
            in_text = False
            if re.search(keyword, facts_summary, re.IGNORECASE) or \
                    re.search(keyword, legal_reasons, re.IGNORECASE):
                flags[theme][keyword] += 'T' # if found in text, mark as capital T
                in_text = True
            # if original keyword not found, search for variants
            if not in_text:
                for variant in keyword_definitions[theme][keyword]:
                    if re.search(variant, facts_summary, re.IGNORECASE) or \
                            re.search(variant, legal_reasons, re.IGNORECASE):
                        flags[theme][keyword] += 't' # if variant found in text, mark as lowercase t
                        in_text = True
                        break

    ## process flags and write to dataframe
    for theme in flags:
        matches = []
        for keyword in flags[theme]:
            if len(flags[theme][keyword]):
                matches.append('['+flags[theme][keyword]+']'+keyword)

        if len(matches):
            df.loc[i, theme] = ' | '.join(matches)

    return df