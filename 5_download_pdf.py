import numpy as np
import pandas as pd
import os
import time
import pickle
import keywords
import re
import requests

save_path = 'D:/datasets/law_human_trafficking/pdfs/'
if not os.path.isdir(save_path):
    os.makedirs(save_path)

df = pd.read_csv('dataset analysed.csv',index_col=0)
df['pdf_status'] = '-'
for i in range(len(df.index)):
    urls = df.loc[i, 'pdf_link']
    if urls != '-':
        urls = urls.split(' \n')
        for u in urls:
            if u[-4:] == '.pdf':
                folder_name = df.loc[i, 'name']
                case_path = os.path.join(save_path, folder_name)
                pdf_name = u.split('/')[-1]
                pdf_name = pdf_name.replace('%20','_')
                pdf_name = pdf_name.replace('%', '_')
                pdf_path = os.path.join(case_path, pdf_name)
                if not os.path.isfile(pdf_path):
                    try:
                        pdf = requests.get(u).content
                        if not os.path.isdir(case_path):
                            os.makedirs(case_path)
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf)
                        df.loc[i, 'pdf_status'] = 'saved'
                        print(i, 'downloaded', pdf_name)
                    except:
                        df.loc[i, 'pdf_status'] = 'ERROR'
                        print(i, 'ERROR', pdf_name)
                else:
                    df.loc[i, 'pdf_status'] = 'saved'
                    print(i, 'exists', pdf_name)

df.to_csv('dataset analysed.csv')
# # URL = "https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/nam/2020/s_v_pretorius_cc_22018_2020_nahcmd_507.html?lng=en&tmpl=sherloc"
# # URL = 'https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/cze/2012/17_t_62010.html?lng=en&tmpl=sherloc'
# page = requests.get(URL)
# folder_location = 'D:/Desktop/pdfs'
#
# soup = bs.BeautifulSoup(page.text, "html.parser")
# for link in soup.select("a[href$='.pdf']"):
#     # Name the pdf files using the last portion of each link which are unique in this case
#     filename = os.path.join(folder_location, link['href'].split('/')[-1])
#     with open(filename, 'wb') as f:
#         f.write(requests.get(urljoin(URL, link['href'])).content)