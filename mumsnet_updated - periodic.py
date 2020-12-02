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
from datetime import datetime

#request html information from website
def gethtml(url):

    """
    The purpose of this function is to get the html from the webpage and then return the text.
    If the request fails, the function prints "failed" 
    arguments:
    url -- this is the url of the website
    """
    try:
        #define custom HTTP header 
        headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
            }
        #request the html document with a timeout time of 30 seconds
        r = requests.get(url,headers = headers,timeout = 30)
        #check if the request was successful 
        r.raise_for_status
        #change the encoding to suitable one
        r.encoding = "utf-8"
        #return the text
        return(r.text)
    except:
        print("connection failed")
        
def get_chat_page(sub_topic_url,chat_page):
    #cocantenation of subtopic url and "?pg=" and the chat page number in string form to get the url for each page
    sub_topic_url_with_page = sub_topic_url + "?pg=" + str(chat_page)
    #gets the html document for each page
    sub_topic_web_with_page = gethtml(sub_topic_url_with_page)
    #parses through the html document
    sub_topic_soup_with_page = BeautifulSoup(sub_topic_web_with_page,"html.parser")
    #extracts all the different chats (discussions) on the current subtopic webpage
    chats = sub_topic_soup_with_page.find("table",id = "threads",class_ = "thread_list").find_all("tr")
    print("Start processing " + str(chat_page) + " out of " + str(chat_pages) + " pages of \"" + sub_topic_name + "\" sub topic")
    return(chats)

#get dialogues from web chat page
def get_texts(chat_soup_taken,dialogue_name):
    """
     This function goes through each chat web page and gets the chat web page and gets all the questions by users
     on that web page. Each post is a question
    arguments:
    chat_soup_taken -- this is the web page of a chat or discussion
    """
    terminating = 0
    #extracts a list of all the posts from the Talk page or that chat web page
    post_list = chat_soup_taken.find("div",id = "posts").find_all("div",class_ = "post")
    post_number = len(post_list)
    for post_loop in range(post_number-1,-1,-1):
        post = post_list[post_loop]
        #gest the username of the poster
        poster = post.find("span",class_ = "nick").string
        #gets the time of the poster
        post_time = post.find("span",class_ = "post_time").string
        post_time_reformatted = post_time.strip().split(" ")[1] + " " + post_time.strip().split(" ")[2]
        post_time_datetime = datetime.strptime(post_time_reformatted,"%d-%b-%y %H:%M:%S")
        if post_time_datetime <= time_point:
            if post_loop == post_number-1:
                terminating = 1
                return(terminating)
            break
        #defines empty string to append the post message on that chat
        post_message = ""
        #finds the actual post message
        p_list = post.find("div",class_ = "talk-post").find_all("p")
        #iterates the message to check if it is none and if it is not, clean up the message from not needed characters
        for p in p_list:
            if p.attrs != {}:
                pass
            else:
                #removes unncessary characters and replaces with empty string
                one_p = str(p).replace("<p>","").replace("</p>","").replace("<br/>"," ").replace("<strong>","").replace("</strong>","").replace("<wbr/>","").strip()
                #removes unncessary characters and replaces with empty string with regular expression and converts r/ into a line break
                one_p = re.sub(r"<img.+?/>","",one_p)
                #removes unncessary characters and replaces with empty string with regular expression and converts r/ into a line break
                one_p = re.sub(r"Here's a link to our.+?</a>","",one_p)
                one_p = re.sub(r"<a.+?</a>","",one_p)
                #updates the empty string defined earlier
                post_message += one_p
        #updates the topic names list
        topic_name_result_list.append(topic_name)
        #updates the subtopic names list
        sub_topic_name_result_list.append(sub_topic_name)
        #updates the chat names list
        dialogue_name_result_list.append(dialogue_name)
        #updates the poster names list
        poster_result_list.append(poster)
        #updates the post times list
        post_time_result_list.append(post_time)
        #updates the post messages list
        post_message_result_list.append(post_message)
    return(terminating)

def get_chat_content(chat):
    #gets the link from the chat page
    chat_url = "https://www.mumsnet.com/Talk/" + chat.find("h2",class_ = "standard-thread-title").find("a")["href"].strip()
    #gets the html document of the chat page
    chat_web = gethtml(chat_url)
    #parses the html document
    chat_soup = BeautifulSoup(chat_web,"lxml")
    #gets the number of pages the chat has
    dialogue_pages = int(chat_soup.find("div",class_ = "pages").find("p").string.strip().split("\t")[0].strip().split(" ")[-1])
    #gets the name of the current chat or discussion in the subtopic 
    dialogue_name = BeautifulSoup(str(chat_soup.find("div",id = "thread_title").find("h1",class_ = "thread_name")).replace("<wbr/>",""),"lxml").string.strip()
    #we iterate through each page, get the url for the dialogue page and then extract the html document and parse it 
    for dialogue_page in range(dialogue_pages,0,-1):
        #get the url for the current chat page
        if dialogue_page == 1:
            chat_url_with_pages = chat_url
            chat_soup_with_pages = chat_soup
        else:
            chat_url_with_pages = chat_url + "?pg=" + str(dialogue_page)
            #get the html document of that page
            chat_web_with_pages = gethtml(chat_url_with_pages)
            #parse the html document
            chat_soup_with_pages = BeautifulSoup(chat_web_with_pages,"lxml")
        #calls the get_texts functions to get the different comments by the mumsnet users in that chat page
        terminating = get_texts(chat_soup_with_pages,dialogue_name)
        if terminating == 1:
            break

def into_database(topic_name_result_list,
                  sub_topic_name_result_list,
                  dialogue_name_result_list,
                  poster_result_list,
                  post_time_result_list,
                  post_message_result_list):
    #stores lists in a dictionary
    result_dataframe = {
                        "topic_name":topic_name_result_list,
                        "sub_topic_name":sub_topic_name_result_list,
                        "dialogue_name":dialogue_name_result_list,
                        "poster":poster_result_list,
                        "post_time":post_time_result_list,
                        "post_message":post_message_result_list
                        }
    #transforms the dictionary into a dataframe
    result_dataframe = pd.DataFrame(result_dataframe)
    #writes sub_topic_name record as a table to the SQL database and insert rows into the table for every new sub_topic
    result_dataframe.to_sql(sub_topic_name,con,if_exists = "append",index = False)

#creates a connection object to a database called kami.db
con = sqlite3.connect(r'C:\Users\William\Desktop\kami\kami.db')
#the url which we will be scraping from
mumsnet_base_url = "https://www.mumsnet.com/Talk"
#calling the gethtml function to get the html text
mumsnet_base_web = gethtml(mumsnet_base_url)
#parses the html text and stores in a variable
mumsnet_base_soup = BeautifulSoup(mumsnet_base_web,"html.parser")
#selects all the main topics ranging from being a parent from to becoming a parent
topics = mumsnet_base_soup.find("div",id = "categories").find_all("div",class_ = "category")
#selects a topic from all the main topics, so we change this to select topics!!!
topics_selection = topics[1:2]
#specify the time point and all posts posted after the timepoint specified will be clooected
#format datetime(year, month, date, hour, minute)
time_point = datetime(2020, 10, 6, 00, 00)

for topic in topics_selection:
    #extracts the text from the name of talk topic such as Becoming a Parent etc. and strips the last character from the text
    topic_name = topic.find("div",class_ = "category_name_link").string.strip()
    #extracts all the subtopics from the topic chosen, but it is still in html form
    sub_topic_list = topic.find("div",class_ = "category_topics_all").find("ul").find_all("li")
    print("Start processing \"" + topic_name + "\" topic")
    #selects a subtopic from the list of subtopics and then parses through it to receive the text 
    for sub_topic in sub_topic_list[8:9]:#change here to select sub topics!!!!
        end = 0
        #extracts the text of the subtopic and strips the last character
        sub_topic_name = sub_topic.find("a").string.strip()
        #cocantenation with subtopic link to extract the subtopic url
        sub_topic_url = "https://www.mumsnet.com/" + sub_topic.find("a")["href"].strip()
        print("Start processing \"" + sub_topic_name + "\" sub topic")
        #get the html document for the page of the subtopic url
        sub_topic_web = gethtml(sub_topic_url)
        #parses the html document 
        sub_topic_soup = BeautifulSoup(sub_topic_web,"html.parser")
        #get the number of chatpages in the subtopic webpage
        chat_pages = int(sub_topic_soup.find("div",class_ = "talk_bar_bottom thread_pages").find("p").string.strip().split(" ")[-1])
        #iterate throught each chatpage for the specific subtopic and 
        for chat_page in range(1,chat_pages+1):
            chat_index = 0
            chats = get_chat_page(sub_topic_url,chat_page)
            #iterates through each chat and creates a list for each one
            for chat in chats:
                #a list of all the main topic names for each chat
                topic_name_result_list = []
                #a list of all the subtopic names for each chat
                sub_topic_name_result_list = []
                #a list of all the chat names
                dialogue_name_result_list = []
                #a list of all the poster names for each chat
                poster_result_list = []
                #a list of all the poster posting times for each chat
                post_time_result_list = []
                #a list of all the posts(messages) for each chat
                post_message_result_list = []
                #if the chat is empty or there is no discussion around that topic, don't do anything
                if chat.attrs != {} or chat.find("th") != None:
                    pass
                #if not, then try the follwing
                else:
                    try:
                        #keeps track of the chat pages crawled
                        chat_index += 1
                        last_post_time = chat.find("span",class_ = "la_time").string.strip().replace("/","-")
                        last_post_time_datetime = datetime.strptime(last_post_time, '%d-%m-%y %H:%M')
                        if last_post_time_datetime > time_point:
                            get_chat_content(chat)
                        else:
                            end = 1
                            break
                        print("finished chat " + str(chat_index) + " on page " + str(chat_page))
                    except:
                        #if the above does not work, then print failed
                        print("failed chat " + str(chat_index) + " on page " + str(chat_page))
                into_database(topic_name_result_list,
                              sub_topic_name_result_list,
                              dialogue_name_result_list,
                              poster_result_list,
                              post_time_result_list,
                              post_message_result_list)
            print("finished " + str(chat_page) + " out of " + str(chat_pages) + " pages of \"" + sub_topic_name + "\" sub topic")
            if end == 1:
                break
con.close()





















