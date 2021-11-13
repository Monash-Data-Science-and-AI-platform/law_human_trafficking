import re

'''
extract_and_search extracts values for the following fields: 'acts', 'means', 'purpose', 'form', 'sector'.
'acts', 'means', 'purpose', 'form' are only recorded if the words match exactly the definition of trafficking.
'sector' is copied as is.
'''
def extract_and_search(df, i, soup, text_to_search):
    definitions = {
        'acts': ['recruitment', 'transportation', 'transfer', 'harbouring', 'receipt'],
        'means': ['threat or use of force or other forms of coercion', 'abduction', 'fraud', 'deception',
                    'abuse of power or a position of vulnerability', 'giving or receiving of payments or benefits'],
        'purpose': ['exploitation of the prostitution of others or other forms of sexual exploitation',
                      'forced labour or services', 'slavery or practices similar to slavery',
                      'servitude', 'removal of organs'],
        'form': ['transnational', 'organized criminal group']
    }
    # definitions = {
    #     'acts': ['recruitment', 'transportation', 'transfer', 'harbouring', 'receipt'],
    #     'means': ['threat or use of force or other forms of coercion', 'abduction', 'fraud', 'deception',
    #                 'abuse of power or a position of vulnerability', 'giving or receiving of payments or benefits'],
    #     'purpose': ['exploitation of the prostitution of others or other forms of sexual exploitation',
    #                   'forced labour or services', 'slavery or practices similar to slavery',
    #                   'servitude', 'removal of organs'],
    #     'form': ['transnational']
    # }

    a = soup.find_all('div', class_='keywordCategory field')
    if a is not None:
        for b in a:
            keyword_label = b.find('div', class_='label')

            if keyword_label is not None:
                keyword_label = keyword_label.text
                values = b.find_all('div', class_='value')
                values_list = []
                for v in values:
                    values_list.append(v.text)

                key = None
                if keyword_label == 'Acts:':
                    key = 'acts'
                elif keyword_label == 'Means:':
                    key = 'means'
                elif keyword_label == 'Purpose of Exploitation:':
                    key = 'purpose'
                elif keyword_label == 'Form of Trafficking:':
                    key = 'form'
                elif keyword_label == 'Sector in which exploitation takes place:':
                    key = 'sector'

                if key == 'sector':
                    df.loc[i, key] = ' | '.join(values_list)
                elif key is not None:
                    matches = []
                    for k in definitions[key]:
                        in_keywords = False
                        in_text = False
                        for v in values_list:
                            if re.search(k, v, re.IGNORECASE):
                                in_keywords = True

                        if re.search(k, df.loc[i, 'facts_summary'], re.IGNORECASE) or \
                            re.search(k, df.loc[i, 'legal_reasons'], re.IGNORECASE):
                            in_text = True

                        if in_text or in_keywords:
                            kk = k
                            if in_text:
                                kk = '@' + kk
                            if in_keywords:
                                kk = '#' + kk

                            matches.append(kk)

                    if len(matches):
                        df.loc[i, key] = ' | '.join(matches)

                        # print(matches, df.loc[i, key])

    return df