'''
This script downloads the pdf files associated with each case, if available.
'''
import pandas as pd
import os
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
