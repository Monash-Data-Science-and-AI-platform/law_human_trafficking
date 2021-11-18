import re
import json
import copy

'''
extract_and_search extracts values for the following fields: 'acts', 'means', 'purpose', 'form', 'sector'.
For 'acts', 'means', 'purpose':
It searchers for keywords defined in keywords.json in 2 locations: the keyword field in the html, and in the text.
'definitions' is a dictionary structured as definitions[theme][keywords][variant]
If a keyword is found exactly in keyword field, flag = 'K'
Else if a keyword variant is found, flag = 'k'
If a keyword is found exactly in text, flag = 'T'
Else if a keyword variant is found, flag = 't'

'form' and 'sector' is copied as is.
'''

def extract_and_search(df, i, soup):
    definitions = json.load(open('keywords.json','r'))
    flags = copy.deepcopy(definitions)
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
                elif keyword_label == 'Means:':
                    theme = 'means'
                elif keyword_label == 'Purpose of Exploitation:':
                    theme = 'purpose'
                elif keyword_label == 'Form of Trafficking:':
                    theme = 'form'
                elif keyword_label == 'Sector in which exploitation takes place:':
                    theme = 'sector'

                if theme == 'sector' or theme == 'form':
                    df.loc[i, theme] = ' | '.join(values_list)
                elif theme is not None:
                    matches = []

                    for keyword in definitions[theme]:
                        in_keywords = False
                        for v in values_list:
                            if re.search(keyword, v, re.IGNORECASE):
                                flags[theme][keyword] += 'K'
                                in_keywords = True
                                break
                        # if original keyword not found, search for variants
                        if not in_keywords:
                            for variant in definitions[theme][keyword]:
                                for v in values_list:
                                    if re.search(variant, v, re.IGNORECASE):
                                        flags[theme][keyword] += 'k'
                                        in_keywords = True
                                        break
                                if in_keywords:
                                    break

    ## search keywords in text
    for theme in definitions:
        for keyword in definitions[theme]:
            in_text = False
            if re.search(keyword, df.loc[i, 'facts_summary'], re.IGNORECASE) or \
                    re.search(keyword, df.loc[i, 'legal_reasons'], re.IGNORECASE):
                flags[theme][keyword] += 'T'
                in_text = True
            # if original keyword not found, search for variants
            if not in_text:
                for variant in definitions[theme][keyword]:
                    if re.search(variant, df.loc[i, 'facts_summary'], re.IGNORECASE) or \
                            re.search(variant, df.loc[i, 'legal_reasons'], re.IGNORECASE):
                        flags[theme][keyword] += 't'
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



            #     for v in values_list:
            #         if re.search(k, v, re.IGNORECASE):
            #             in_keywords = True
            #
            #     if re.search(k, df.loc[i, 'facts_summary'], re.IGNORECASE) or \
            #         re.search(k, df.loc[i, 'legal_reasons'], re.IGNORECASE):
            #         in_text = True
            #
            #     if in_text or in_keywords:
            #         kk = k
            #         if in_text:
            #             kk = '@' + kk
            #         if in_keywords:
            #             kk = '#' + kk
            #
            #         matches.append(kk)
            #
            # if len(matches):
            #     df.loc[i, key] = ' | '.join(matches)

            # print(matches, df.loc[i, key])

    return df