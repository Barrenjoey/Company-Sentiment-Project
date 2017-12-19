import urllib.request
import bs4 as bs
import datetime
import re
import sqlite3

#Connecting to database and creating cursor
conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

# Database functions
def data_entry():
	c.execute("UPDATE Scraped_data SET company=?, sentiment=?, post_date=?, price=?, date_scraped=? WHERE url=?", (prefix, sentiment, post_date, price, date, url))
	conn.commit()
	
def select_urls():
	c.execute("SELECT url FROM Scraped_data WHERE date_scraped IS NULL")
	urls = c.fetchall()
	return urls

# Date
date = datetime.date.today()

# Headers for authentication
headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',} 

# Collecting urls from database to scrape
scrape_list = select_urls()

# Declared variables
counter = 0
sentiment = ""
content = "content"
for url in scrape_list[0:]:
	url = url[0]
	counter += 1
	print(counter)
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
		print("Error getting price! ")

	# Gathering post date
	try:
		post_date = soup.findAll("dl", {"class": "ctrlUnit"})
		post_date = re.findall(r'(\d+/\d+/\d+)', str(post_date))
		post_date = post_date[0]
	except Exception as e:
		print("Error getting post date! " + str(e))
		
	# Data entry	
	data_entry()	
	
	# Resetting Variables
	price = ''
	sentiment = ''
	prefix = ''
	post_date = ''
	
c.close()
conn.close()
