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
