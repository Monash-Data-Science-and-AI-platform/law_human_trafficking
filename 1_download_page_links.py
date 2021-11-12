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

opts = Options()
# opts.add_argument(" — headless") # Uncomment if the headless version needed
# opts.binary_location = "D:/source/___/chromedriver.exe"

# Set the location of the webdriver
chrome_driver = "D:/source/___/chromedriver.exe"
print(chrome_driver)
# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)



# main_url = 'https://sherloc.unodc.org/cld//v3/sherloc/cldb/search.html?lng=en#?c=%7B%22filters%22:%5B%7B%22fieldName%22:%22en%23__el.caseLaw.crimeTypes_s%22,%22value%22:%22Trafficking%20in%20persons%22%7D%5D,%22sortings%22:%22%22%7D'
main_url = 'https://sherloc.unodc.org/cld//v3/sherloc/cldb/search.html?lng=en#?c=%7B%22filters%22:%5B%7B%22fieldName%22:%22en%23__el.caseLaw.crimeTypes_s%22,%22value%22:%22Trafficking%20in%20persons%22%7D%5D,%22sortings%22:%22%22%7D'
# page = requests.get(main_url)
driver.get(main_url)

SCROLL_PAUSE_TIME = 0.5
scroll_times = 100000
no_scroll_count = 0
# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_count = 0
while scroll_count < scroll_times:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        no_scroll_count += 1
        if no_scroll_count > 10:
            break
    else:
        no_scroll_count = 0
    last_height = new_height
    scroll_count += 1


soup_main = bs.BeautifulSoup(driver.page_source)
# soup_main = bs.BeautifulSoup(page.text, "html.parser")
soup_main = soup_main.find('div', 'row topSpace20')
panels = soup_main.find_all('div', attrs={'class':'animated fadeIn new result-row ng-scope'})
print(len(panels))
all_panels = pd.DataFrame()
for p in panels:
    url = p.find('a')['href']
    url = 'https://sherloc.unodc.org/cld/'+url[6:]
    name = url.split('/')[-1].split('.html?')[0]
    name = '{:04d}'.format(len(all_panels.index)) + '_' + str(name)
    all_panels = all_panels.append({'name':str(name), 'page_link':url}, ignore_index=True)
    # print(url)

all_panels.to_csv('dataset.csv')
#
#     # URL = "https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/nam/2020/s_v_pretorius_cc_22018_2020_nahcmd_507.html?lng=en&tmpl=sherloc"
#     # URL = 'https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/cze/2012/17_t_62010.html?lng=en&tmpl=sherloc'
#     page = requests.get(url)
#     folder_location = 'D:/Desktop/pdfs'
#
#     soup= bs.BeautifulSoup(page.text, "html.parser")
#     for link in soup.select("a[href$='.pdf']"):
#         #Name the pdf files using the last portion of each link which are unique in this case
#         filename = os.path.join(folder_location,link['href'].split('/')[-1])
#         with open(filename, 'wb') as f:
#             f.write(requests.get(urljoin(url,link['href'])).content)
#
#         print('downloaded')





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




