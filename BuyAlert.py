import sqlite3
import datetime
'''
This is an alert tool i created to search over each company from the database and
create an alert if certain coniditons are met, buy_strength and volume_strength. The 
search can be altered to a set time period, however the tools main use is for 
short time periods such as 1-10 days.
'''
# Set the period of time you want to analyse - in days
time_period = 10

# Set wanted ratio and volume for alert. Buy strength in %
buy_strength = 85
volume_strength = 10

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

# Use this to search for selected companys, mute to scan all companies.	
prefix_list = ['AB1']

# Loop through company prefix
alerts = {}
counter = 0
for prefix in prefix_list[0:]:
	try:
		counter += 1
		print("Scanned: " + str(counter))
		print("Analysing: " + prefix + " for past " + str(time_period) + " days")
		data = select_scraped_data(prefix)

		# Converting to datestamp to sort by date and then sorting chronologically.
		date_data = []
		clean_data = []
		for item in data:
			item = list(item)
			item[0] = datetime.datetime.strptime(item[0], "%d/%m/%y")
			date_data.append(item)	
		date_data.sort()
		
		# Getting historical average of volume and sentiment.
		volume_total = 0
		buy_total, sell_total, hold_total, none_total = 0, 0, 0, 0
		for item in date_data:	
			#print(item)
			volume_total += 1
			if item[1] == 'Buy':
				buy_total += 1
			elif item[1] == 'Sell':
				sell_total += 1
			elif item[1] == 'Hold':
				hold_total += 1
			elif item[1] == 'None':
				none_total += 1
				
		# Getting whole time period.
		first_date = date_data[0]
		first_date = first_date[0]
		last_date = date_data[-1]
		last_date = last_date[0]
		whole_period = str(last_date - first_date)
		whole_period = int(whole_period.split()[0])

		# Buy/sell historical average
		ratio_average = ((buy_total) / (buy_total + sell_total + hold_total))*100
		ratio_average = round(ratio_average, 2)
		
		# Volume historical avergae
		volume_average = round(volume_total / whole_period, 1)
		
		# Sorting and converting back to wanted date format. Also cutting unwanted dates.
		for item in date_data:
			if item[0] > past_date:
				item[0] = item[0].strftime('%d-%m-%Y')
				clean_data.append(item)
		
		# Getting volume and sentiment (For selected time period)
		volume = 0
		buy, sell, hold, none = 0, 0, 0, 0
		for item in clean_data:	
			#print(item)
			volume += 1
			if item[1] == 'Buy':
				buy += 1
			elif item[1] == 'Sell':
				sell += 1
			elif item[1] == 'Hold':
				hold += 1
			elif item[1] == 'None':
				none += 1
				
		# Buy/sell ratio (For selected time period)
		ratio = ((buy) / (buy + sell + hold))*100
		ratio = round(ratio, 2)
		
		# Volume ratio (For selected time period)
		volume_ratio = volume / time_period

		#Add alert if conditions met
		if ratio >= buy_strength and volume_ratio >= volume_strength:
			alerts[prefix] = [ratio, volume_ratio]
		
		print("Buy Average: " + str(ratio_average) + "%")
		print("Volume Average " + str(volume_average) + " posts per day")
		print("Volume: " + str(volume))
		print("Buy: " + str(buy))
		print("Sell: " + str(sell))
		print("Hold: " + str(hold))
		print("None: " + str(none))
		print("Buy Strength: " + str(ratio) + "%")
		print("Volume Strength: " + str(volume_ratio) + " posts per day")	
		print()
		ratio = 0
		
	except Exception as e:
		print("No data in that time period! - " + str(e))

# Displaying alerts		
print()
print("ALERTS: " + str(len(alerts)))
print()
for alert in alerts:
	print(alert)
	info = alerts.get(alert)
	print("Buy Strength: " + str(info[0]) + "%")
	print("Volume Strength: " + str(info[1]) + " posts per day")
	print()

c.close()
conn.close()