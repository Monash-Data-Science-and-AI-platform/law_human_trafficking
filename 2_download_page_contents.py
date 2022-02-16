'''
This script visits each case's webpage and saves the html.
'''

import pandas as pd
import requests
import os


save_path = 'D:/datasets/law_human_trafficking/page_html/'
if not os.path.isdir(save_path):
    os.makedirs(save_path)

df = pd.read_csv('dataset links.csv')


for i in range(len(df.index)):
    name = df.loc[i,'name']
    page_link = df.loc[i,'page_link']
    page = requests.get(page_link)
    f = open(os.path.join(save_path, str(name)+'.html'), 'wb')
    f.write(page.content)

    print(i, name)




