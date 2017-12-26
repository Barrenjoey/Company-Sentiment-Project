import urllib.request
import bs4 as bs
import re
import sqlite3
'''
This is the web crawler used to find the wanted urls on the hotcopper website. The crawler
searches by company prefix, and automatically adds the next page of the forum to the url list
if they havent already been crawled before. Crawled entries are imported at the start, and
wanted urls will then be saved to a database, with the option of text file backups.
'''
#Connecting to database and creating cursor
conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

# Database functions
def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS Scraped_data(id INTEGER PRIMARY KEY, url TEXT, company TEXT, sentiment TEXT, post_date TEXT, price REAL, content TEXT, date_scraped TEXT)")
	#8 categories
	
def data_entry(item):
	c.execute("INSERT INTO Scraped_data (url) VALUES (?)", (item,))
	conn.commit()
	
def select_existing_url():
	c.execute("SELECT url FROM Scraped_data")
	existing_urls = c.fetchall()
	return existing_urls
	
#Create table if it doesnt exist
create_table()

#Starting URL and headers for access
start_url = "https://hotcopper.com.au/asx/"
headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',} 

# Importing company prefix list
with open("D:/Desktop/Code/Cobalt Blue/prefix_list.txt") as f:
	prefix_list = f.readlines()
	prefix_list = [x.strip() for x in prefix_list]

# Creating url list
url_list = []
for prefix in prefix_list:
	url_list.append(start_url + str(prefix))
	
#Importing already crawled urls and adding to crawled list. Toggle text_files for .txt copy.
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
	
# Declared variables
wanted_links = []
crawled_urls = []
page_count = 1
turn_page = True
counter = 0

# Main loop - looping through available urls to crawl posts.
while len(url_list) != len(crawled_urls):
	for url in url_list[6000:]:
		counter += 1
		print(counter)
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
					wanted_links.append(wanted)
					crawled_list.append(wanted)
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
				#url_list.append(url + "/page-" + str(page_count))
				print("Added new URL to URL list")
			elif url.endswith('page-10'):
				print()
				print("End of the line..")
				pass	
			else:	
				#url_list.append(url + "/page-" + str(page_count))
				print("Added new URL to URL list")
		
		crawled_urls.append(url)
		turn_page = True
		page_count = 1
		print("URL list: " + (str(len(url_list))))
		print("Crawled: " + str(len(crawled_urls)))
		print("Wanted: " + str(len(wanted_links)))
		print()
		
# Saving wanted urls to database and optional text file.
		for item in wanted_links:
			data_entry(item)
			if text_files:
				saveFile = open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt", 'a')
				saveFile.write(str(item) + "\n")
				saveFile.close()
		wanted_links = []
		
	
c.close()
conn.close()
# Known bug - Not getting author created thread posts.
