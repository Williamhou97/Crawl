# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 19:56:06 2020

@author: William
"""

import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

def sleep_awhile():
    time.sleep(5)

def to_end():
    js="var q=document.documentElement.scrollTop=100000"  
    driver.execute_script(js)  
    
def check_height():
    height_now = driver.execute_script("return document.documentElement.scrollHeight")
    return(height_now)

con = sqlite3.connect('C:\\Users\\William\\Desktop\\kami\\kami.db')

chrome_options = Options()
chrome_options.add_argument('lang=en_GB')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)

driver.get("https://www.youtube.com/c/channelmum/videos")
sleep_awhile()

page = 1
height_old = check_height()

while True:
    to_end()
    sleep_awhile()
    height_new = check_height()
    print("finished page " + str(page))
    page += 1
    if height_old == height_new:
        print("now we are at the end of the page!")
        break
    else:
        height_old = height_new
        print("not end yet")

playlist_html = driver.page_source
playlist_soup = BeautifulSoup(playlist_html,"html.parser")

video_list_parent = playlist_soup.find("div",id = "items",class_ = "style-scope ytd-grid-renderer")
video_list = video_list_parent.find_all("ytd-grid-video-renderer",class_ = "style-scope ytd-grid-renderer")

video_url_list = []

for video in video_list:
    video_url = video.find("a",id = "thumbnail",class_ = "yt-simple-endpoint inline-block style-scope ytd-thumbnail")["href"]
    video_url = "https://www.youtube.com/" + video_url
    video_url_list.append(video_url)

video_index = 1

for video_home_url in video_url_list[0:50]:
    video_name_list = []
    num_of_view_list = []
    upload_time_list = []
    video_description_text_list = []
    video_subtitle_text_list = []
    video_url_result_list = []
    
    print("start working on video " + str(video_index) + " out of " + str(len(video_url_list)))
    video_index += 1
    driver.get(video_home_url)
    sleep_awhile()
    click_list = driver.find_elements_by_css_selector("[aria-label = 'More actions']")
    for click in click_list:
        try:
            click.click()
            break
        except:
            pass
    sleep_awhile()
    try:
        driver.find_element_by_css_selector(".style-scope ytd-menu-service-item-renderer").click()
    except:
        print("video " + str(video_index-1) + " out of " + str(len(video_url_list)) + " doesn't have subtitle")
        continue
    sleep_awhile()
    video_home_web = driver.page_source
    video_home_soup = BeautifulSoup(video_home_web,"html.parser")
    try:
        try:
            video_name = video_home_soup.find("yt-formatted-string",class_ = "style-scope ytd-video-primary-info-renderer").string.strip()
        except:
            video_name = video_home_soup.find("yt-formatted-string",class_ = "style-scope ytd-video-primary-info-renderer").find("span",class_ = "style-scope yt-formatted-string").string.strip()
        num_of_view = video_home_soup.find("span",class_ = "short-view-count style-scope yt-view-count-renderer").string.strip()
        upload_time = video_home_soup.find("div",id = "date",class_ = "style-scope ytd-video-primary-info-renderer").find("yt-formatted-string",class_ = "style-scope ytd-video-primary-info-renderer").string.strip()
        video_description_list = video_home_soup.find("yt-formatted-string",class_ = "content style-scope ytd-video-secondary-info-renderer").contents
        video_description_text = ""
        for video_description in video_description_list:
            if video_description.name == "span":
                video_description_text += video_description.string.replace("\n"," ").strip() + " "
            elif video_description.name == "a":
                video_description_text += video_description["href"].split("q=")[-1].replace("%3A",":").replace("%2F","/").split("&v=")[0].split("&event=")[0] +" "
        video_subtitle_text = ""
        video_subtitle_list = video_home_soup.find("ytd-transcript-body-renderer",class_ = "style-scope ytd-transcript-renderer").find_all("div",class_ = "cue-group style-scope ytd-transcript-body-renderer")
        for video_subtitle in video_subtitle_list:
            video_subtitle_text_one = video_subtitle.find("div",class_ = "cue style-scope ytd-transcript-body-renderer").string.strip() + ". "
            video_subtitle_text += video_subtitle_text_one
        
        video_name_list.append(video_name)
        num_of_view_list.append(num_of_view)
        upload_time_list.append(upload_time)
        video_description_text_list.append(video_description_text)
        video_subtitle_text_list.append(video_subtitle_text)
        video_url_result_list.append(video_home_url)
        
        result_data = {
                        "video_name":video_name_list,
                        "video_url":video_url_result_list,
                        "num_of_view":num_of_view_list,
                        "upload_time":upload_time_list,
                        "video_description_text":video_description_text_list,
                        "video_subtitle_text":video_subtitle_text_list
            }
        
        result_data = pd.DataFrame(result_data)
        result_data.to_sql("channel mum",con,if_exists = "append",index = False)
        print("finished video " + str(video_index-1) + " out of " + str(len(video_url_list)))
    except:
        pass

driver.close()
con.close()


