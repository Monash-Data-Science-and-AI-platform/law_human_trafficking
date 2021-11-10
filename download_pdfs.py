from selenium import webdriver
import bs4 as bs
import numpy as np
import pandas as pd
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


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
soup_main = bs.BeautifulSoup(driver.page_source)
# soup_main = bs.BeautifulSoup(page.text, "html.parser")
soup_main = soup_main.find('div', 'row topSpace20')
panels = soup_main.find_all('div', attrs={'class':'animated fadeIn new result-row ng-scope'})
# print(panels)
for p in panels:
    url = p.find('a')['href']
    url = 'https://sherloc.unodc.org/cld/'+url[6:]
    print(url)

    # URL = "https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/nam/2020/s_v_pretorius_cc_22018_2020_nahcmd_507.html?lng=en&tmpl=sherloc"
    # URL = 'https://sherloc.unodc.org/cld/case-law-doc/traffickingpersonscrimetype/cze/2012/17_t_62010.html?lng=en&tmpl=sherloc'
    page = requests.get(url)
    folder_location = 'D:/Desktop/pdfs'

    soup= bs.BeautifulSoup(page.text, "html.parser")
    for link in soup.select("a[href$='.pdf']"):
        #Name the pdf files using the last portion of each link which are unique in this case
        filename = os.path.join(folder_location,link['href'].split('/')[-1])
        with open(filename, 'wb') as f:
            f.write(requests.get(urljoin(url,link['href'])).content)

        print('downloaded')

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




