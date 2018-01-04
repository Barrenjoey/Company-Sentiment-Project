import urllib.request
import bs4 as bs
import datetime
import re
import sqlite3
import time
import threading
from threading import Thread
from queue import Queue
'''
This is the scraper script that grabs the urls gathered by the crawler and then extracts
the wanted content from each url. The data obtained is the sentiment, date, company and 
price at post. The gathered data is then used to update the database. The script uses threading
to maximize speed and also just 1 database entry to prevent database locking.
'''
# SET the amount of urls to crawl eg 5000
scrape_amount = 5000

# Initiating timer for crawl
start_time = time.time()
#Connecting to database and creating cursor
conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

# Database functions
def data_entry(item):
	c.executemany("UPDATE Scraped_data SET company=?, sentiment=?, post_date=?, price=?, date_scraped=? WHERE url=?", (item))
	conn.commit()
	
def select_urls():
	c.execute("SELECT url FROM Scraped_data WHERE date_scraped IS NULL")
	urls = c.fetchall()
	return urls

# Declaring main list for database update
global update_list
update_list = []
def main_func(i, q):
	while len(update_list) != scrape_amount:
		# Getting url from queue
		url = q.get()
		print("Connecting to: " + str(url))
		
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

		# Save the soup to text file for debugging
		saveFile = open("D:/Desktop/Code/Cobalt Blue/soup.txt", 'wb')
		saveFile.write(soupPretty)
		saveFile.close()
		
		# Gathering sentiment data from post
		data = soup.findAll("div", {"class": "message-user-metadata message-user-metadata-sentiment"})
		if re.findall(r'Buy', str(data)):
			sentiment = "Buy"
		elif re.findall(r'Sell', str(data)):
			sentiment = "Sell"
		elif re.findall(r'Hold', str(data)):
			sentiment = "Hold"
		elif re.findall(r'None', str(data)):
			sentiment = "None"
		else:
			print("Error getting sentiment! ")
			
		# Gathering company prefix
		try:
			prefix = re.findall(r'<strong>(.*)\(ASX\)', str(data)) 
			prefix = [x.strip() for x in prefix]
			prefix = prefix[0]
		except Exception as e:
			print("Error getting company prefix! " + str(e))

		# Gathering price at posting and converting to dollar.cents
		try:
			if re.findall(r'\$', str(data)):
				price = re.findall(r'\$(\d+\.\d+)', str(data))
				price = price[0]
			elif re.findall(r'¢', str(data)):
				price = re.findall(r'(\d+\.\d+)¢', str(data))
				price = float(price[0])
				price = round(price/100,3)	
		except Exception as e:
			price = None
			print("Error getting price! ")

		# Gathering post date
		try:
			post_date = soup.findAll("dl", {"class": "ctrlUnit"})
			post_date = re.findall(r'(\d+/\d+/\d+)', str(post_date))
			post_date = post_date[0]
		except Exception as e:
			print("Error getting post date! " + str(e))
		
		# Updating the list for database entry.
		if prefix:
			try:
				update_tup = (prefix, sentiment, post_date, price, date, url)
				print(update_tup)
				update_list.append(update_tup)
			except:
				print("Error appending to update list, not updating! ")
		else:
			print("Post gone! Not updating.")
		print("Update list: " + str(len(update_list)))
		
		# Resetting Variables
		price = ''
		sentiment = ''
		prefix = ''
		post_date = ''
		
		# Task finished for thread
		q.task_done()

# Date
date = datetime.date.today()

# Headers for authentication
headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',} 

# Collecting urls from database to scrape
scrape_list = select_urls()

# Setting up queue for threading.
q = Queue()
num_threads = 30

# Setting threaded workers to point at main function.
for i in range(num_threads):
	worker = Thread(target=main_func, args=(i, q,))
	worker.setDaemon(True)
	worker.start()		
	
# Putting the desired urls into the queue for scraping.	
for url in scrape_list[70:scrape_amount]:
	q.put(url[0])
q.join()

# Data entry
try:
	data_entry(update_list)	
except Exception as e:	
	print("Error - Data entry! " + str(e))

# Closing database connection
c.close()
conn.close()

# Crawl time 
finish_time = time.time()
total_time = finish_time - start_time
print("Scrape time: " + str(total_time))