import urllib.request
import bs4 as bs
import datetime
import re
import time
# Date
date = datetime.date.today()

#Starting URL and headers for access
start_url = "https://hotcopper.com.au/asx/"
headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',} 

#Importing company prefix list
with open("D:/Desktop/Code/Cobalt Blue/prefix_list.txt") as f:
	prefix_list = f.readlines()
	prefix_list = [x.strip() for x in prefix_list]

#Importing already crawled urls and adding to crawled list.
crawled_list = []
try:
	with open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt") as f:
		crawled_list = f.readlines()
	crawled_list = [x.strip() for x in crawled_list] 
	crawled_list = list(set(crawled_list))	
except Exception as e:
	print('IMPORTING CRAWLED URLS ERROR! ' + str(e))

# Creating url list
url_list = []
for prefix in prefix_list:
	url_list.append(start_url + str(prefix))

page_count = 1
turn_page = True
# Main loop - looping through available urls to crawl posts.
for url in url_list[0:5]:
	print("URL list: " + (str(len(url_list))))
	print("Connecting to: " + str(url))
	
	# Checking whether its not the first page of the forum. Adjusting page count if its not.
	if url.endswith(('page-2', 'page-3', 'page-4', 'page-5', 'page-6', 'page-7', 'page-8', 'page-9')):
		page_num = url[-1:]
		page_count += int(page_num)
		print(page_count)
	
	# Attempting to access web page
	try:
		request = urllib.request.Request(url,None,headers)
		response = urllib.request.urlopen(request)
		sauce = response.read()
		print("Request Success!")
	except Exception as e:
		print("Request Failure: " + e)

	# Convert to soup
	soup = bs.BeautifulSoup(sauce, 'lxml')
	soupPretty = soup.prettify("utf-8")

	# Save the soup to text file for debugging
	saveFile = open("D:/Desktop/Code/Cobalt Blue/soup.txt", 'wb')
	saveFile.write(soupPretty)
	saveFile.close()
	
	# Searching and acquiring wanted urls, also flagging whether to go to next page by hitting cralwed.
	h3 = soup.find_all('h3')
	links = re.findall(r'<a href="(.*?)\"', str(h3))
	wanted_links = []
	for wanted in links:
		if re.findall(r'page-', str(wanted)):
			if wanted not in wanted_links:
				if wanted not in crawled_list:
					wanted_links.append(wanted)
				else:
					turn_page = False
					
	# Adding next page to url_list if it hasnt been crawled yet.
	if turn_page:
		page_count += 1
		url_list.append(url + "/page-" + str(page_count))
		print("Added new URL to URL list")
		
	# Saving wanted
	for item in wanted_links:
		saveFile = open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt", 'a')
		saveFile.write(str(item) + "\n")
		saveFile.close()
	print()

#appending to url_list will only work if it runs until the end. Need to add it to a file for importing?

'''
import bs4 as bs
import urllib.request
import re
import datetime
import os
import sqlite3

date = datetime.date.today()
#Date of today and yesterday
today = datetime.datetime.now()
today = today.day
#Month - text
month = datetime.datetime.now()
month_int = month.month
month = month.strftime("%B")

#Starting Url and declared variables etc..
start_url = "http://money.cnn.com/"
spider_list = []
crawled_list = []
scrape_list = []
scrapeD_list = []
crawler_url = ""
http_scan = re.compile('http')
video_scan = re.compile('/video/')
money_scan = re.compile('http://money.cnn.com/')
index_scan = re.compile('index.html?')
loop_counter = 0
mainLoop = True

#Test URL, exception if error
try:
	sauce = urllib.request.urlopen(start_url).read()
except Exception as e:			
	print(str(e))
	
#Converting website html to Beautiful Soup	
sauce = urllib.request.urlopen(start_url).read()
soup =	bs.BeautifulSoup(sauce, 'lxml')
#print(soup)
#Importing already crawled urls and adding to crawled list.
try:
	with open("D:/Desktop/Code/Web Crawler/" + month + "/_CRAWLED_MONEY_URLS.txt") as f:
		crawled_list = f.readlines()
	crawled_list = [x.strip() for x in crawled_list] 
	crawled_list = list(set(crawled_list))	
	#print(crawled_list)
except Exception as e:
	print('IMPORTING CRAWLED URLS ERROR! ' + str(e))
#Importing already scraped urls	
try:
	with open("D:/Desktop/Code/Web Crawler/" + month + "/_CNN_MONEY_URLS.txt") as f:
		scrapeD_list = f.readlines()
	scrapeD_list = [x.strip() for x in scrapeD_list] 
	scrapeD_list = list(set(scrapeD_list))	
	# print(scrapeD_list)
	# print(len(scrapeD_list))
except Exception as e:
	print('IMPORTING SCRAPE URLS ERROR! ' + str(e))	

#Finding all the url links on the page, removing http links, adding starting_url and adding to list.
def url_finder():
	for link in soup.find_all('a'):
		new_url = link.get('href')
#Searching for money website at start of url and adding to url list		
		tt = re.findall(money_scan, str(new_url))
		kk = re.findall(http_scan, str(new_url))
		if len(tt) > 0:
			if new_url not in spider_list:
				spider_list.append(new_url)
				#print(new_url)
#Searching for http (other sites) and only adding urls that dont have http.				
		elif len(kk) == 0:	
			new_url = start_url + str(new_url)
			if new_url not in spider_list:
				spider_list.append(new_url)
				#print(new_url)
		else:
			pass
#Taking wanted urls from spider_list to scrape_list.
def wanted_urls():
	for url in spider_list:
		zz = re.findall(index_scan, str(url))
		if url.endswith('index.html'):
			jj = re.findall(video_scan, str(url))
			if len(jj) <= 0:
				if url not in scrape_list and url not in scrapeD_list:
					scrape_list.append(url)
					print(url)	
		elif len(zz) > 0:
			if url not in scrape_list and url not in scrapeD_list:
				scrape_list.append(url)
				print(url)
url_finder()
wanted_urls()
#print(scrape_list[0])

#Looping through url list, looking for more urls and adding wanted urls to scrape list. Runs until
#every url has been crawled.
while mainLoop:
	for url in spider_list[0:5]:
		# if spider_list.index == 5:
			# break
		if url not in crawled_list:
			print("Trying URL: ", url)
			loop_counter += 1
			print(loop_counter)
			crawler_url = url
			try:
				sauce = urllib.request.urlopen(crawler_url).read()
			except Exception as e:			
				print(str(e))		
#Converting website html to Beautiful Soup	
			try:
				sauce = urllib.request.urlopen(crawler_url).read()
				soup =	bs.BeautifulSoup(sauce, 'lxml')
			except Exception as e:
				print("FAILED!!SOUP: ",url)
				print(str(e))
			try:
				url_finder()
			except Exception as e:
				print("FAILED!!1: "+ url)
				print(str(e))
			try:	
				wanted_urls()
			except Exception as e:
				print("FAILED!!2: "+ url)
				print(str(e))
#Adding crawled url to crawled list and checking whether the loop needs to end.		
			crawled_list.append(url)
			if len(spider_list) == len(crawled_list):
				mainLoop = False
			print("Spider: ",len(spider_list))
			print("Scrape: ",len(scrape_list))
			print("Crawled: ", len(crawled_list))
	break
# print(spider_list)
print("Spider: ",len(spider_list))
#print(scrape_list)
print("Scrape: ",len(scrape_list))

#Creating crawled text file to stop later crawls of same thing.
saveFile = open("D:/Desktop/Code/Web Crawler//" + month + '/_CRAWLED_MONEY_URLS.txt', 'w')
saveFile.close()
for item in crawled_list:
	saveFile = open("D:/Desktop/Code/Web Crawler//" + month + '/_CRAWLED_MONEY_URLS.txt', 'a')		
	saveFile.write(str(item) + "\n")
	saveFile.close()

#Saving scrape url text file for scraping.
for item in scrape_list:
	saveFile = open("D:/Desktop/Code/Web Crawler//" + month + '/_CNN_MONEY_URLS.txt', 'a')		
	saveFile.write(str(item) + "\n")
	saveFile.close()
	

# jo = []
# for h in spider_list:
	# if h not in scrape_list:
		# jo.append(h)
		# print(h)
# print(len(jo))	
'''	
