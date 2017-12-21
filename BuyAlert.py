import sqlite3
import datetime
'''
This is an alert tool i created to search over each company from the database and
create an alert if certain coniditons are met, buy_ratio and volume_strength. The 
search can be altered to a set time period, however the tools main use is for 
short time periods such as 1-10 days.
'''
# Set the period of time you want to analyse - in days
time_period = 10

# Set wanted ratio and volume for alert
buy_ratio = 0.8
volume_strength = 0.5

# Dates
date = datetime.datetime.today()
#date = date - datetime.timedelta(days=time_period)
past_date = date - datetime.timedelta(days=time_period)

conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

def select_scraped_data(prefix):
	c.execute("SELECT post_date, sentiment FROM Scraped_data WHERE company=?", (prefix,))
	data = c.fetchall()
	return data

# Importing company prefix list
with open("D:/Desktop/Code/Cobalt Blue/prefix_list.txt") as f:
	prefix_list = f.readlines()
	prefix_list = [x.strip() for x in prefix_list]

# Loop through company prefix
alerts = {}
for prefix in prefix_list[0:50]:
	try:
		#prefix = 'ABV'	#Mute this to run all of list and change above line
		print("Analysing: " + prefix)
		data = select_scraped_data(prefix)
		
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
		volume = 0
		buy, sell, hold = 0, 0, 0
		for item in clean_data:	
			#print(item)
			volume += 1
			if item[1] == 'Buy':
				buy += 1
			elif item[1] == 'Sell':
				sell += 1
			elif item[1] == 'Hold':
				hold += 1
		
		# Buy/sell ratio
		ratio = (buy - sell) / (buy + sell + hold)
		
		# Volume ratio
		volume_ratio = volume / time_period

		#Add alert if conditions met
		if ratio >= buy_ratio and volume_ratio >= volume_strength:
			alerts[prefix] = [ratio, volume_ratio]
			
		print("Volume: " + str(volume))
		print("Volume Strength: " + str(volume_ratio))
		print("Buy: " + str(buy))
		print("Sell: " + str(sell))
		print("Hold: " + str(hold))
		print("Buy ratio: " + str(ratio))	
		print()
		ratio = 0
		
	except Exception as e:
		print("Error: Main loop fail! " + str(e))
		
print()
print("ALERTS: " + str(len(alerts)))
print()
for alert in alerts:
	print(alert)
	info = alerts.get(alert)
	print ("Buy Ratio: " + str(info[0]))
	print ("Volume Ratio: " + str(info[1]))
	print()
#print("Alerts:" + str(alerts))	

c.close()
conn.close()
