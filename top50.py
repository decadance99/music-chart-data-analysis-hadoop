#!/usr/bin/python3.6
import requests
import pandas as pd
from selenium import webdriver
from time import sleep
from konlpy.tag import Okt
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager, rc
from wordcloud import WordCloud
from subprocess import PIPE, Popen
import subprocess
import datetime

data = pd.DataFrame(columns=['Title', 'Artist', 'Lyrics'])
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("./chromedriver", chrome_options=options)
driver.implicitly_wait(20)
driver.get('http://mw.genie.co.kr/')
driver.find_element_by_css_selector("a[href*='chart']").click()
sleep(1)

for i in range(0,49):
    song = driver.find_elements_by_css_selector("div[class='info']")[i]
    title = song.find_element_by_css_selector("a[href*='songInfo']").click()
    if i == 0 : driver.find_element_by_css_selector("a[class*='later']").click()
    title = driver.find_element_by_css_selector("h2[class*='title']").text
    artist = driver.find_element_by_css_selector("a[href*='artistInfo']").text
    lyrics = driver.find_element_by_css_selector("section[class='lyrics']").textz
    data.loc[i] = [title, artist, lyrics]
    driver.execute_script("window.history.go(-1)")
    #driver.implicitly_wait(5)

file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M") + ".json"
hdfspath = "/user/maria_dev/chart50" + file_name

info = pd.DataFrame(data, columns=['Title', 'Artist', 'Lyrics', 'Points'])
info.to_json(file_name, orient='records', force_ascii=False)

put = subprocess.Popen(["hadoop", "fs", "-put", file_name, hdfspath], stdin=PIPE, bufsize=-1)
put.communicate()

driver.quit()
