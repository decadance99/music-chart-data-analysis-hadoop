#!/usr/bin/python3.6
import pandas as pd
from selenium import webdriver
from time import sleep
from subprocess import PIPE, Popen
import subprocess

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("./chromedriver", chrome_options=options)
driver = webdriver.Chrome("./chromedriver.exe")
driver.implicitly_wait(20)
driver.get('https://www.genie.co.kr/chart/top200')
sleep(5)

date = str(driver.find_element_by_css_selector("span[id*='inc_date']").text)
time = str(driver.find_element_by_css_selector("span[id*='inc_time']").text)
filename = date.translate({ord(i): None for i in '.'}) + '-' + time.translate({ord(i): None for i in':'}) + '.json'

points = []
i = 1
try:
    while (i != 6):
        s3 = "icon-chart ranking-" + str(i)
        item = driver.find_element_by_css_selector("span[class*='" + s3 + "']")
        point = ''.join(filter(lambda x: x.isdigit(), item.get_attribute('style')))
        points.append(point)
        i += 1
except TimeoutError:
    print('Too long')

points2 = sorted(points, key=int)
print(points2)

titles = []
artists = []
lyricses = []
for i in range(1,6):
    titem = driver.find_element_by_css_selector("table[class*='list-wrap'] tr.list:nth-of-type(" + str(i) + ")")
    title = titem.find_element_by_css_selector("a[class*='title ellipsis']").text
    artist = titem.find_element_by_css_selector("a[class*='artist ellipsis']").text
    titem.find_element_by_css_selector("a[class*='btn-basic btn-info']").click()
    sleep(3)
    lyrics = driver.find_element_by_css_selector("pre[id*='pLyrics'] p").text
    driver.execute_script("window.history.go(-1)")
    sleep(3)
    titles.append(title)
    artists.append(artist)
    lyricses.append(lyrics)

info = pd.DataFrame(list(zip(titles, artists, lyricses, points2)), columns=['Title', 'Artist', 'Lyrics', 'Points'])
info.to_json(filename, orient='records', force_ascii=False)
hdfspath = "/user/maria_dev/chart5/" + filename

put = subprocess.Popen(["hadoop", "fs", "-put", filename, hdfspath], stdin=PIPE, bufsize=-1)
put.communicate()

driver.quit()
