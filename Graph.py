import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

'''

'''
# Set the period of time you want to analyse - in days
time_period = 10

# Set wanted ratio and volume for alert
buy_ratio = 0.8
volume_strength = 0.2

# Dates
date = datetime.datetime.today()
#date = date - datetime.timedelta(days=time_period)
past_date = date - datetime.timedelta(days=time_period)
# print(date)
# print(past_date)

conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

def select_scraped_data(prefix):
	c.execute("SELECT post_date, sentiment FROM Scraped_data WHERE company=?", (prefix,))
	data = c.fetchall()
	return data

# Set companys to graph by prefix eg COB
prefix_list = ['ABU']

# Loop through company prefix
for prefix in prefix_list:
	print("Analysing: " + prefix)
	data = select_scraped_data(prefix)
	
	# Declaring x,y coord variables for graph
	x = []
	y = []
	
	# Converting to datestamp to sort by date
	date_data = []
	clean_data = []
	for item in data:
		item = list(item)
		item[0] = datetime.datetime.strptime(item[0], "%d/%m/%y")
		date_data.append(item)	
		
	# Sorting and converting back to wanted date format. Also cutting unwanted dates.
	date_data.sort()
	for item in date_data:
		if item[0] > past_date:
			item[0] = item[0].strftime('%d-%m-%Y')
			clean_data.append(item)
	
	# Getting volume and sentiment
	volume, sentiment = 0, 0
	buy, sell, hold = 0, 0, 0
	for item in clean_data:
		print(item)
		x.append(item[0])
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
				sentiment -= 0.5
			elif sentiment < 1:
				sentiment += 0.5
		y.append(sentiment)
		
	# Buy/sell ratio
	ratio = (buy - sell) / (buy + sell + hold)
	
	# Volume ratio
	volume_ratio = volume / time_period
		
	print("Volume: " + str(volume))
	print("Volume Strength: " + str(volume_ratio))
	print("Buy: " + str(buy))
	print("Sell: " + str(sell))
	print("Hold: " + str(hold))
	print("Buy ratio: " + str(ratio))
	print("Sentiment Score: " + str(sentiment))
	ratio = 0
print()


# Setting graph format - change between months/days and set fmt to %m or %d
#months = mdates.MonthLocator()
days = mdates.DayLocator()
fmt = mdates.DateFormatter('%d')

# Converting back to datetime to graph
x = [datetime.datetime.strptime(d,'%d-%m-%Y').date() for d in x]

# Plotting coords
fig, ax = plt.subplots()
ax.plot(x, y, label='Sentiment')

# Setting x axis format
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(fmt)

# Graphing info
plt.xlabel('Time')
plt.ylabel('Sentiment Score')
plt.title(str(prefix) + ' Sentiment')
plt.legend()
plt.show()


c.close()
conn.close()
