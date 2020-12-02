# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 13:38:00 2020

@author: William
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import sqlite3
import re

#request html information from website
def gethtml(url):
    try:
        headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
            }
        r = requests.get(url,headers = headers,timeout = 30)
        r.raise_for_status
        r.encoding = "utf-8"
        return(r.text)
    except:
        print("failed")

#get dialogues from web chat page
def get_texts(chat_soup_taken):
    post_list = chat_soup_taken.find("div",id = "posts").find_all("div",class_ = "post")
    for post in post_list:
        poster = post.find("span",class_ = "nick").string
        post_time = post.find("span",class_ = "post_time").string
        post_message = ""
        p_list = post.find("div",class_ = "talk-post").find_all("p")
        for p in p_list:
            if p.attrs != {}:
                pass
            else:
                one_p = str(p).replace("<p>","").replace("</p>","").replace("<br/>"," ").replace("<strong>","").replace("</strong>","").replace("<wbr/>","").strip()
                one_p = re.sub(r"<img.+?/>","",one_p)
                one_p = re.sub(r"Here's a link to our.+?</a>","",one_p)
                post_message += one_p
        topic_name_result_list.append(topic_name)
        sub_topic_name_result_list.append(sub_topic_name)
        dialogue_name_result_list.append(dialogue_name)
        poster_result_list.append(poster)
        post_time_result_list.append(post_time)
        post_message_result_list.append(post_message)

con = sqlite3.connect('C:\\Users\\William\\Desktop\\kami\\kami.db')
mumsnet_base_url = "https://www.mumsnet.com/Talk"

mumsnet_base_web = gethtml(mumsnet_base_url)
mumsnet_base_soup = BeautifulSoup(mumsnet_base_web,"html.parser")

topics = mumsnet_base_soup.find("div",id = "categories").find_all("div",class_ = "category")
#change here to select topics!!!!
topics_selection = topics[0:1]



for topic in topics_selection:
    topic_name = topic.find("div",class_ = "category_name_link").string.strip()
    sub_topic_list = topic.find("div",class_ = "category_topics_all").find("ul").find_all("li")
    print("Start processing \"" + topic_name + "\" topic")
    for sub_topic in sub_topic_list[0:1]:#change here to select sub topics!!!!
        sub_topic_name = sub_topic.find("a").string.strip()
        sub_topic_url = "https://www.mumsnet.com/" + sub_topic.find("a")["href"].strip()
        print("Start processing \"" + sub_topic_name + "\" sub topic")
        sub_topic_web = gethtml(sub_topic_url)
        sub_topic_soup = BeautifulSoup(sub_topic_web,"html.parser")
        chat_pages = int(sub_topic_soup.find("div",class_ = "talk_bar_bottom thread_pages").find("p").string.strip().split(" ")[-1])
        for chat_page in range(1,chat_pages+1):
            sub_topic_url_with_page = sub_topic_url + "?pg=" + str(chat_page)
            sub_topic_web_with_page = gethtml(sub_topic_url_with_page)
            sub_topic_soup_with_page = BeautifulSoup(sub_topic_web_with_page,"html.parser")
            chats = sub_topic_soup_with_page.find("table",id = "threads",class_ = "thread_list").find_all("tr")
            chat_index = 0
            print("Start processing " + str(chat_page) + " out of " + str(chat_pages) + " pages of \"" + sub_topic_name + "\" sub topic")
            for chat in chats:
                topic_name_result_list = []
                sub_topic_name_result_list = []
                dialogue_name_result_list = []
                poster_result_list = []
                post_time_result_list = []
                post_message_result_list = []
                if chat.attrs != {}:
                    pass
                else:
                    try:
                        chat_url = "https://www.mumsnet.com/Talk/" + chat.find("h2",class_ = "standard-thread-title").find("a")["href"].strip()
                        chat_index += 1
                        chat_web = gethtml(chat_url)
                        chat_soup = BeautifulSoup(chat_web,"lxml")
                        dialogue_pages = int(chat_soup.find("div",class_ = "pages").find("p").string.strip().split("\t")[0].strip().split(" ")[-1])
                        dialogue_name = BeautifulSoup(str(chat_soup.find("div",id = "thread_title").find("h1",class_ = "thread_name")).replace("<wbr/>",""),"lxml").string.strip()
                        if dialogue_pages == 1:
                            get_texts(chat_soup)
                            print("finished chat " + str(chat_index) + " on page " + str(chat_page))
                        else:
                            for dialogue_page in range(1,dialogue_pages+1):
                                chat_url_with_pages = chat_url + "?pg=" + str(dialogue_page)
                                chat_web_with_pages = gethtml(chat_url_with_pages)
                                chat_soup_with_pages = BeautifulSoup(chat_web_with_pages,"lxml")
                                get_texts(chat_soup_with_pages)
                            print("finished chat " + str(chat_index) + " on page " + str(chat_page))
                    except:
                        try:
                            chat.find("th").string.strip()
                        except:
                            print("failed chat " + str(chat_index) + " on page " + str(chat_page))
                result_dataframe = {
                                    "topic_name":topic_name_result_list,
                                    "sub_topic_name":sub_topic_name_result_list,
                                    "dialogue_name":dialogue_name_result_list,
                                    "poster":poster_result_list,
                                    "post_time":post_time_result_list,
                                    "post_message":post_message_result_list
                                    }
                result_dataframe = pd.DataFrame(result_dataframe)
                result_dataframe.to_sql(sub_topic_name,con,if_exists = "append",index = False)
            print("finished " + str(chat_page) + " out of " + str(chat_pages) + " pages of \"" + sub_topic_name + "\" sub topic")
























