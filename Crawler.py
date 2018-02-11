import urllib.request
import bs4 as bs
import re
import sqlite3
from queue import Queue
from threading import Thread
import subprocess
import time
'''
This is the web crawler used to find the wanted urls on the hotcopper website. The crawler
searches by company prefix, and automatically adds the next page of the forum to the url list
if they havent already been crawled before. Crawled entries are imported at the start, and
wanted urls will then be saved to a database, with the option of text file backups. The crawler
is threaded to access pages, with 1 data insert at the end for faster and optimal performance.
'''

class Crawler():

	# SET prefix list location:
	list_location = "D:/Desktop/Code/Cobalt Blue/prefix_list1.txt"

	# Initiating timer for crawl
	start_time = time.time()

	# Declaring the 2 main variables
	global wanted_links
	wanted_links = []
	global crawled_urls
	crawled_urls = []

	def __init__(self):
		# Connecting to database
		self.conn = sqlite3.connect('Cobalt_Blue.db')
		self.c = self.conn.cursor()

		# Create table if it doesnt exist
		self.create_table()

		# Starting URL and headers for url access
		start_url = "https://hotcopper.com.au/asx/"
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7', }

		# Importing company prefix list
		with open(self.list_location) as f:
			prefix_list = f.readlines()
			prefix_list = [x.strip() for x in prefix_list]

		# Creating url list
		self.url_list = []
		for prefix in prefix_list:
			self.url_list.append(start_url + str(prefix))

		# Importing already crawled urls and adding to crawled list. Toggle text_files for .txt copy.
		self.crawled_list = []
		text_files = False
		if text_files:
			try:
				with open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt") as f:
					self.crawled_list = f.readlines()
				self.crawled_list = [x.strip() for x in self.crawled_list]
				self.crawled_list = list(set(self.crawled_list))
			except Exception as e:
				print('IMPORTING CRAWLED URLS ERROR! ' + str(e))
		try:
			temp_list = self.select_existing_url()
			for existing in temp_list:
				self.crawled_list.append(existing[0])
		except Exception as e:
			print('IMPORTING CRAWLED URLS ERROR! ' + str(e))

		# Setting up queue for threading.
		q = Queue()
		num_threads = 3

		# Setting threaded workers to point at main function.
		for i in range(num_threads):
			worker = Thread(target=self.main_func, args=(i, q,))
			worker.setDaemon(True)
			worker.start()

		# Putting the urls in the queue while running until no urls are left to crawl.
		while len(self.url_list) != len(crawled_urls):
			for url in self.url_list:
				if url not in crawled_urls:
					q.put(url)
			q.join()

		# Data entry for wanted links, 1 insert for whole list.
		try:
			self.data_entry(wanted_links)
			print("Added " + str(len(wanted_links)) + "URL's to the database!")
			print()
		except Exception as e:
			print("Data entry error: " + str(e))

		# Prints out text backup doccument if text_files is set to True.
		if text_files:
			for item in wanted_links:
				if text_files:
					saveFile = open("D:/Desktop/Code/Cobalt Blue/wanted_urls.txt", 'a')
					saveFile.write(str(item[0]) + "\n")
					saveFile.close()

		# Closing database connection
		self.c.close()
		self.conn.close()

		# Starting Scraper
		print("Starting Scraper!")
		subprocess.call(['python', 'Cobalt_Scraper.py'])

		# Crawl time
		finish_time = time.time()
		total_time = finish_time - self.start_time
		print("Crawl time: " + str(round(total_time, 2)))

	# Database functions
	def create_table(self):
		self.c.execute("CREATE TABLE IF NOT EXISTS Scraped_data(id INTEGER PRIMARY KEY, url TEXT, company TEXT, sentiment TEXT, post_date TEXT, price REAL, content TEXT, date_scraped TEXT)")

	def data_entry(self, item):
		self.c.executemany("INSERT INTO Scraped_data (url) VALUES (?)", (item))
		self.conn.commit()

	def select_existing_url(self):
		self.c.execute("SELECT url FROM Scraped_data")
		existing_urls = self.c.fetchall()
		return existing_urls



	# Main function for threading.
	def main_func(self, i, q):
		page_count = 1
		turn_page = True
		# Main loop - looping through available urls to crawl posts.
		while len(self.url_list) != len(crawled_urls):
			# Getting url from queue
			url = q.get()
			print("Worker " + str(i) + " connecting to: " + str(url))

			# Checking whether its not the first page of the forum. Adjusting page count if its not.
			if url.endswith(('page-2', 'page-3', 'page-4', 'page-5', 'page-6', 'page-7', 'page-8', 'page-9')):
				page_num = url[-1:]
				page_count = int(page_num)

			# Attempting to access web page
			try:
				request = urllib.request.Request(url, None, self.headers)
				response = urllib.request.urlopen(request)
				sauce = response.read()
				print("Request Success!")
			except Exception as e:
				print("Request Failure: " + str(e))

			# Convert to soup
			soup = bs.BeautifulSoup(sauce, 'lxml')

			# Searching and acquiring wanted urls, also flagging whether to go to next page by hitting cralwed.
			h3 = soup.find_all('h3')
			links = re.findall(r'<a href="(.*?)\"', str(h3))
			for wanted in links:
				wanted = "https://hotcopper.com.au/" + str(wanted)
				if re.findall(r'page-', str(wanted)):
					if wanted not in self.crawled_list:
						self.crawled_list.append(wanted)
						wanted = wanted,
						wanted_links.append(wanted)
					else:
						turn_page = False
						#print("URL already crawled!")

			# Adding additional urls to crawl if turn_page hasn't been triggered by already crawled urls.
			if turn_page:
				page_count += 1
				if url.endswith(('page-2', 'page-3', 'page-4', 'page-5', 'page-6', 'page-7', 'page-8', 'page-9')):
					temp_url = url[:-7]
					self.url_list.append(temp_url + "/page-" + str(page_count))
					print("Added new URL to URL list")
				elif url.endswith('page-10'):
					print()
					print("End of the line..")
					pass
				else:
					self.url_list.append(url + "/page-" + str(page_count))
					print("Added new URL to URL list")

			crawled_urls.append(url)
			turn_page = True
			page_count = 1
			print("URL list: " + (str(len(self.url_list))))
			print("Crawled: " + str(len(crawled_urls)))
			print("Wanted: " + str(len(wanted_links)))
			print()
			q.task_done()
