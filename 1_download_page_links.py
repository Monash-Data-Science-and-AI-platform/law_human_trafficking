'''
This script uses a selenium webdriver to visit the unodc website and scans for all the relevant cases.
It only provides a unique case name and saves the page url, but does not download the html yet.
'''

import bs4 as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()

# Set the location of the webdriver
chrome_driver = "D:/source/___/chromedriver.exe"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)


main_url = 'https://sherloc.unodc.org/cld//v3/sherloc/cldb/search.html?lng=en#?c=%7B%22filters%22:%5B%7B%22fieldName%22:%22en%23__el.caseLaw.crimeTypes_s%22,%22value%22:%22Trafficking%20in%20persons%22%7D%5D,%22sortings%22:%22%22%7D'

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











