import urllib.request
import bs4 as bs
import re
import sqlite3
from queue import Queue
from threading import Thread
import threading
import time

# Initiating timer for crawl
start_time = time.time()
# Connecting to database	
conn = sqlite3.connect('Cobalt_Blue1.db')
c = conn.cursor()

# Database functions
def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS Scraped_data(id INTEGER PRIMARY KEY, url TEXT, company TEXT, sentiment TEXT, post_date TEXT, price REAL, content TEXT, date_scraped TEXT)")
	
def data_entry(item):
	c.executemany("INSERT INTO Scraped_data (url) VALUES (?)", (item))
	conn.commit()
	
def select_existing_url():
	c.execute("SELECT url FROM Scraped_data")
	existing_urls = c.fetchall()
	return existing_urls
	
global wanted_links
wanted_links = []
global crawled_urls
crawled_urls = []
# Main function for threading.
def main_func(i, q):
	
	page_count = 1
	turn_page = True

	# Main loop - looping through available urls to crawl posts.
	while len(url_list) != len(crawled_urls):
		url = q.get()
		#counter += 1
		#print(counter)
		print("Connecting to: " + str(url))
		
		# Checking whether its not the first page of the forum. Adjusting page count if its not.
		if url.endswith(('page-2', 'page-3', 'page-4', 'page-5', 'page-6', 'page-7', 'page-8', 'page-9')):
			page_num = url[-1:]
			page_count = int(page_num)

		# Attempting to access web page
		try:
			request = urllib.request.Request(url,None,headers)
			response = urllib.request.urlopen(request)
			sauce = response.read()
			print("Request Success!")
		except Exception as e:
			print("Request Failure: " + str(e))

		# Convert to soup
		soup = bs.BeautifulSoup(sauce, 'lxml')
		soupPretty = soup.prettify("utf-8")
		
		# Searching and acquiring wanted urls, also flagging whether to go to next page by hitting cralwed.
		h3 = soup.find_all('h3')
		links = re.findall(r'<a href="(.*?)\"', str(h3))
		for wanted in links:
			wanted = "https://hotcopper.com.au/" + str(wanted)
			if re.findall(r'page-', str(wanted)):
				if wanted not in crawled_list:
					crawled_list.append(wanted)
					wanted = wanted,
					wanted_links.append(wanted)
				else:
					print("URL already crawled!")
					
		if 	len(wanted_links) == 0:
			turn_page = False
			print("No more wanted links! ")
		# Adding next page to url_list if it hasnt been crawled yet.
		if turn_page:
			page_count += 1
			if url.endswith(('page-2', 'page-3', 'page-4', 'page-5', 'page-6', 'page-7', 'page-8', 'page-9')):
				url = url[:-7]
				url_list.append(url + "/page-" + str(page_count))
				print("Added new URL to URL list")
			elif url.endswith('page-10'):
				print()
				print("End of the line..")
				pass	
			else:	
				url_list.append(url + "/page-" + str(page_count))
				print("Added new URL to URL list")
		
		crawled_urls.append(url)
		turn_page = True
		page_count = 1
		print("URL list: " + (str(len(url_list))))
		print("Crawled: " + str(len(crawled_urls)))
		print("Wanted: " + str(len(wanted_links)))
		print()
		q.task_done()
		
#Create table if it doesnt exist
create_table()

data_lock = threading.Lock()
#Starting URL and headers for access
start_url = "https://hotcopper.com.au/asx/"
headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',} 

# Importing company prefix list
with open("D:/Desktop/Code/Cobalt Blue/update1.txt") as f:
	prefix_list = f.readlines()
	prefix_list = [x.strip() for x in prefix_list]

# Creating url list
url_list = []
for prefix in prefix_list:
	url_list.append(start_url + str(prefix))
	
# Importing already crawled urls and adding to crawled list. Toggle text_files for .txt copy.
crawled_list = []
text_files = False
if text_files:
	try:
		with open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt") as f:
			crawled_list = f.readlines()
		crawled_list = [x.strip() for x in crawled_list] 
		crawled_list = list(set(crawled_list))	
	except Exception as e:
		print('IMPORTING CRAWLED URLS ERROR! ' + str(e))
try:
	test_list = select_existing_url()
	for existing in test_list:
		crawled_list.append(existing[0])
except Exception as e:
	print('IMPORTING CRAWLED URLS ERROR! ' + str(e))

# Setting up queue for threading.
q = Queue()
num_threads = 10

# Setting threaded workers to point at main function.
for i in range(num_threads):
	worker = Thread(target=main_func, args=(i, q,))
	worker.setDaemon(True)
	worker.start()
	
	
while len(url_list) != len(crawled_urls):
	for url in url_list:
		if url not in crawled_urls:
			q.put(url)
	q.join()
#if len(url_list) != len(crawled_urls):

data_entry(wanted_links)

# Prints out text backup doccument if text_files is set to True.
if text_files:
	for item in wanted_links:
		if text_files:
			saveFile = open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt", 'a')
			saveFile.write(str(item[0]) + "\n")
			saveFile.close()

c.close()
conn.close()

# Crawl time 
finish_time = time.time()
total_time = finish_time - start_time
print("Crawl took: " + str(total_time))