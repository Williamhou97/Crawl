# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 15:42:27 2020

@author: William
"""

from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import pandas as pd
import json

def gethtml(url):
    try:
        headers = {
        "subscription-key": "654f0605eaf6498fabb6b57247b399c7"
            }
        r = requests.get(url,headers = headers,timeout = 30)
        r.raise_for_status
        r.encoding = r.apparent_encoding
        return(r.text)
    except:
        print("connection failed")

def get_name_dataframe(href_json):
    url_list = []
    name_list = []
    description_list = []
    keywords_list = []
    
    try:
        url = href_json["url"]
    except:
        url = None
        
    try:
        name = href_json["name"]
    except:
        name = None
        
    try:
        description = href_json["description"]
    except:
        description = None
    
    try:
        keyword_original = href_json["keywords"]
        keywords = ""
        for keyword in keyword_original:
            keywords = keywords + keyword + ","
        keywords = keywords.strip(",")
    except:
        keywords = None
    
    url_list.append(url)
    name_list.append(name)
    description_list.append(description)
    keywords_list.append(keywords)
    
    data_name_dict = {
        "url":url_list,
        "name":name_list,
        "description":description_list,
        "keywords":keywords_list
        }
    data_name = pd.DataFrame(data_name_dict)
    return(data_name)


href = gethtml("https://api.nhs.uk/conditions/cholesteatoma/")
href_json = json.loads(href)

data_name = get_name_dataframe(href_json)

#!!
content_list = href_json["mainEntityOfPage"]
try:
    url = href_json["url"]
except:
    url = None
    
try:
    name = href_json["name"]
except:
    name = None

url_list = []
name_list = []
headline_list = []
text_message_list = []

for content in content_list:
    headline = content["text"]
    sections = content["mainEntityOfPage"]
    if sections != []:
        text_message = ""
        for section in sections:
            if len(section) == 5:
                text_message += section["text"].replace("<p>","").replace("</p>"," ").replace("<b>","").replace("</b>",r"\n").replace("<h2>","").replace("</h2>"," ")
            elif len(section) == 9:
                text_message += section["url"]
                text_message += r"\n"
            text_message = text_message.strip()
        url_list.append(url)
        name_list.append(name)
        headline_list.append(headline)
        text_message_list.append(text_message)

data_content_dict = {
    "url":url_list,
    "name":name_list,
    "headline":headline_list,
    "text_message":text_message_list
    }
data_content = pd.DataFrame(data_content_dict)










