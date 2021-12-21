# options = webdriver.ChromeOptions()
# prefs = {'profile.default_content_setting_values': {'notifications': 2}}
# options.add_experimental_option('prefs', prefs)
# options.add_argument("disable-infobars")
# driver = webdriver.Chrome(options=options)
# driver.get("https://www.youtube.com/user/twappledaily/videos")

# 前面可能要先載一些東西
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import requests
import os
import json
import pandas as pd

options = webdriver.ChromeOptions()
prefs = {'profile.default_content_setting_values': {'notifications': 2}}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable-infobars")
driver = webdriver.Chrome(options=options)
driver.get("https://www.youtube.com/user/udntv/videos")
driver.maximize_window()


# 設定爬取多少 新聞量
for x in range(1):
    driver.execute_script("window.scrollBy(0, 1000)")
    time.sleep(3)

# 拿取新聞網址
soup = BeautifulSoup(driver.page_source, 'lxml')
url_filter = "/watch?v="
links = []
for a in soup.find_all('a', href=True):
	if url_filter not in a['href']:
		pass
	else:
		url = a['href'].replace('/watch?v=', '')
		if url not in links:
			links.append(url)

# 拿取youtube 影片資訊
# 每個人api 不一樣 我剛上傳沒注意到就被google 警告了
base_url = "https://www.googleapis.com/youtube/v3/"
part='snippet,contentDetails,statistics,status'
api_key = '' 

d = []
for i in range(len(links)):
	video_id = links[i]
	path = f'videos?part={part}&id={video_id}'
	api_url = f"{base_url}{path}&key={api_key}"

	r = requests.get(api_url)
	if r.status_code == requests.codes.ok:
	    info_data = r.json()

	data_item = info_data['items'][0]

	info = {
	    # 'channelId': data_item['snippet']['channelId'],      
	    'channelTitle': data_item['snippet']['channelTitle'],
	    'title': data_item['snippet']['title'],
	    'publishedAt': data_item['snippet']['publishedAt'],
	    # 'description': data_item['snippet']['description'],
	    # 'videoId': data_item['id'],
	    'likeCount': int(data_item['statistics']['likeCount']),
	    # 'dislikeCount': int(data_item['statistics']['dislikeCount']),
	    'commentCount': int(data_item['statistics']['commentCount']),
	    'viewCount':int(data_item['statistics']['viewCount']),
	    'duration': data_item['contentDetails']['duration']
	}	
	d.append(info)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
df = pd.DataFrame(d)



# 拿取youtube 留言資訊
all_comment = []
for i in range(len(links)):
	video_id = links[i]
	part='snippet,replies'
	path = f'commentThreads?part={part}&videoId={video_id}&maxResults=10000'
	api_url = f"{base_url}{path}&key={api_key}"
	r = requests.get(api_url)
	if r.status_code == requests.codes.ok:
	  comment_data = r.json()


	comments = []
	if comment_data == None:
	    comment = None
	elif comment_data != None and 'items' in comment_data:
	    for data_item in comment_data['items']:
	        data_item = data_item['snippet']
	        top_comment = data_item['topLevelComment']
	        comments.append({
	                  'videoId': video_id,
	                  # 'authorChannelId': top_comment['snippet']['authorChannelId']['value'],
	                  # 'authorDisplayName': top_comment['snippet'].get('authorDisplayName', ''),
	                  'textOriginal': top_comment['snippet']['textOriginal'],
	                  'likeCount': int(top_comment['snippet']['likeCount']),
	                  'publishedAt': top_comment['snippet']['publishedAt']
	              })

	    while 'nextPageToken' in comment_data:
	        page_token = comment_data.get('nextPageToken')
	        path = f'commentThreads?part={part}&videoId={video_id}&maxResults=10000&pageToken={page_token}'
	        api_url = f"{base_url}{path}&key={api_key}"
	        r = requests.get(api_url)
	        if r.status_code == requests.codes.ok:
	          comment_data = r.json()
	        else:
	          comment_data = None

	        if comment_data != None and 'items' in comment_data:
	            for data_item in comment_data['items']:
	                data_item = data_item['snippet']
	                top_comment = data_item['topLevelComment']
	                comments.append({
	                          'videoId': video_id,
	                          # 'authorChannelId': top_comment['snippet']['authorChannelId']['value'],
	                          # 'authorDisplayName': top_comment['snippet'].get('authorDisplayName', ''),
	                          'textOriginal': top_comment['snippet']['textOriginal'],
	                          'likeCount': int(top_comment['snippet']['likeCount']),
	                          'publishedAt': top_comment['snippet']['publishedAt']
	                      })
	        if not page_token:
	            break
	all_comment.append(comments)

# 組裝
df['all_comment'] = all_comment
df.to_csv('聯合報.csv', index=False)
print(df.shape)






