from selenium import webdriver
import bs4 as bs
import numpy as np
import pandas as pd
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import pickle


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




