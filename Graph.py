import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

'''
This is a simple tool i made to create a plot graph with the data from the database. You can
manually enter the prefix's of the companys you want to look at in the prefix_list and it 
will use all the data it can in the database corresponding to that prefix. This tool is used
to determine the sentiment score and volume over a chosen period of time.
'''
# Set the period of time you want to analyse - in days
time_period = 20

# Dates
date = datetime.datetime.today()
#date = date - datetime.timedelta(days=time_period)
past_date = date - datetime.timedelta(days=time_period)

conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

def select_scraped_data(prefix):
	c.execute("SELECT post_date, sentiment, price FROM Scraped_data WHERE company=?", (prefix,))
	data = c.fetchall()
	return data

# Set companys to graph by prefix eg COB
prefix_list = ['4DS']

# Loop through company prefix
graph = True
previous_item = [past_date]
for prefix in prefix_list:
	try:
		print("Analysing: " + prefix + " for past " + str(time_period) + " days")
		data = select_scraped_data(prefix)
		
		# Declaring x,y coord variables for graph
		x = []
		y = []
		x2 = []
		y2 = []
		
		# Converting to datestamp to sort by date
		date_data = []
		clean_data = []
		for item in data:
			item = list(item)
			item[0] = datetime.datetime.strptime(item[0], "%d/%m/%y")
			date_data.append(item)	
			
		# Sorting dates and saving wanted dates in new list.
		date_data.sort()
		for item in date_data:
			if item[0] > past_date:
				clean_data.append(item)
		
		# Getting volume and sentiment
		volume, sentiment = 0, 0
		buy, sell, hold, none = 0, 0, 0, 0
		for item in clean_data:
			print(item)
			volume += 1
			if item[1] == 'Buy':
				buy += 1
				sentiment += 1
			elif item[1] == 'Sell':
				sell += 1
				sentiment -= 1
			elif item[1] == 'Hold':
				hold += 1
				if sentiment > 1:
					sentiment -= 1
				elif sentiment < -1:
					sentiment += 1
			elif item[1] == 'None':
				none += 1
		# Sorting dates to plot only end of day figure and decaying sentiment for time without posts.
			if item[0] > previous_item[0]:
				#print(item)
				# Finding days between posts and decaying sentiment at 0.25/day if no post.
				sent_decay = item[0] - previous_item[0]
				sent_decay = str(sent_decay)
				sent_decay = sent_decay[0:2]
				sent_decay = int(sent_decay)
				sent_decay = sent_decay/4
				print(sent_decay)
				if sentiment > 1 and sent_decay > 0.25:
					if sentiment >= sent_decay:
						sentiment -= sent_decay
					else:
						sentiment = 0

		# Converting date format for graphing and appending to coords.
				new_date = item[0].strftime('%d-%m-%Y')
				x.append(new_date)
				x2.append(new_date)
				y.append(sentiment)
				y2.append(item[2])
				previous_item = item

		# Buy/sell ratio
		ratio = ((buy - sell) / (buy + sell + hold + none))*100
		ratio = round(ratio, 2)
		# Volume ratio
		volume_ratio = round(volume / time_period, 1)
			
		print("Volume: " + str(volume))
		print("Buy: " + str(buy))
		print("Sell: " + str(sell))
		print("Hold: " + str(hold))
		print("None: " + str(none))
		print("Buy strength: " + str(ratio) + "%")
		print("Volume Strength: " + str(volume_ratio) + " posts per day")
		print("Sentiment Score: " + str(sentiment))
		ratio = 0
		volume_ratio = 0
		
	except Exception as e:
		print("Error - No data in that time period!")
		print(e)
		graph = False
print()

if graph:
	# Setting graph format - change between months/days and set fmt to %m or %d
	#months = mdates.MonthLocator()
	days = mdates.DayLocator()
	fmt = mdates.DateFormatter('%d')

	# Converting back to datetime to graph
	x = [datetime.datetime.strptime(d,'%d-%m-%Y').date() for d in x]
	x2 = [datetime.datetime.strptime(d,'%d-%m-%Y').date() for d in x2]

	# Plotting coords
	fig, ax = plt.subplots()
	ax2 = ax.twinx()
	ax.plot(x, y, label='Sentiment', color='r')
	ax.set_xlabel('Time (days)')
	ax.set_ylabel('Sentiment Score')
	ax2.plot(x2, y2, label='Price', color='b')
	ax2.set_ylabel("Price at Post")
	
	# Getting legends for graph
	handles, labels = ax.get_legend_handles_labels()
	ax.legend(handles, labels, loc='center left')
	# Setting x axis format
	ax.xaxis.set_major_locator(days)
	ax.xaxis.set_major_formatter(fmt)
	
	# Graphing info
	plt.title(str(prefix) + ' Sentiment')
	plt.legend()
	plt.show()

# Closing database connections
c.close()
conn.close()