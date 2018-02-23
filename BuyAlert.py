import sqlite3
import datetime
'''
This is an alert tool i created to search over each company from the database and
create an alert if certain coniditons are met, buy_strength and volume_strength. The 
search can be altered to a set time period, however the tools main use is for 
short time periods such as 1-10 days.
'''
# Set the period of time you want to analyse - in days
time_period = 8

# Set wanted ratio and volume for alert. Buy strength in %
buy_strength = 80
volume_strength_low = 4
volume_strength_high= 30

# Dates
date = datetime.datetime.today()
#date = date - datetime.timedelta(days=time_period)
past_date = date - datetime.timedelta(days=time_period)
past_month = date - datetime.timedelta(days=30)
past_monthStr = past_month.strftime('%Y-%m-%d')
print(past_monthStr)
conn = sqlite3.connect('Cobalt_Blue.db')
c = conn.cursor()

def select_scraped_data(prefix):
	c.execute("SELECT post_date, sentiment FROM Scraped_data WHERE company=?", (prefix,))
	data = c.fetchall()
	return data
	
def select_price_data(company):
	c.execute("SELECT date, price, price_low, price_high FROM Prices WHERE company=?", (company,))
	priceData = c.fetchall()
	return priceData
	
# Importing company prefix list
with open("D:/Desktop/Code/Cobalt Blue/prefix_list.txt") as f:
	prefix_list = f.readlines()
	prefix_list = [x.strip() for x in prefix_list]

# Use this to search for selected companys, mute to scan all companies.	
prefix_list = ['COB']

previous = False
if previous:
	with open("D:/Desktop/Alerts 13-2.txt") as f:
		alreadyBought = f.readlines()
		alreadyBought = [x.strip() for x in alreadyBought]
#print(alreadyBought)
# Loop through company prefix
alerts = {}
newAlerts = {}
counter = 0
for prefix in prefix_list[0:]:
	try:
		counter += 1
		print("Scanned: " + str(counter))
		print("Analysing: " + prefix + " for past " + str(time_period) + " days")
		data = select_scraped_data(prefix)
		priceData = select_price_data(prefix)
		print(len(priceData))
		print(priceData)
		priceData.sort()
		print()
		print(priceData)
		## Sorting done.
		## Work out price average over month
		monthPrices = []
		for val in priceData:
			if val[0] > past_monthStr:
				monthPrices.append(val)
		print(monthPrices)
		monthPriceAverage = 0
		for price in monthPrices:
			monthPriceAverage += price[1]
		monthPriceAverage = monthPriceAverage/len(monthPrices)
		print(len(monthPrices))
		print(monthPriceAverage)

			
		## Alert if current price is 7-10%+ below average price?

		# Converting to datestamp to sort by date and then sorting chronologically.
		date_data = []
		clean_data = []
		month_data = []
		for item in data:
			item = list(item)
			item[0] = datetime.datetime.strptime(item[0], "%d/%m/%y")
			date_data.append(item)	
		date_data.sort()
		'''
		Total historical data as averages. (vol/buy)
		'''
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
		'''
		Data for the past month. (30 days)
		'''
		# Converting date format and removing items not in the past month and chosen time period.
		for item in date_data:
			if item[0] > past_month:
				if item[0] > past_date:
					item[0] = item[0].strftime('%d-%m-%Y')
					month_data.append(item)
					clean_data.append(item)
				else:
					item[0] = item[0].strftime('%d-%m-%Y')
					month_data.append(item)
		
		volume_month = 0
		buy_month, sell_month, hold_month, none_month = 0, 0, 0, 0
		for item in month_data:	
			#print(item)
			volume_month += 1
			if item[1] == 'Buy':
				buy_month += 1
			elif item[1] == 'Sell':
				sell_month += 1
			elif item[1] == 'Hold':
				hold_month += 1
			elif item[1] == 'None':
				none_month += 1
				
		# Buy/sell ratio (For past month)
		month_ratio = ((buy_month) / (buy_month + sell_month + hold_month))*100
		month_ratio = round(month_ratio, 2)
		
		# Volume ratio (For past month)
		month_volume = round(volume_month / 30, 2)

		'''
		Data for the chosen time period. ie 10 days.
		'''		
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
		if ratio >= buy_strength:
			if volume_strength_low < volume_ratio < volume_strength_high:
				alerts[prefix] = [ratio, volume_ratio, month_ratio, month_volume]
				if previous:
					if prefix not in alreadyBought:
						newAlerts[prefix] = [ratio, volume_ratio]
		
		print("Volume: " + str(volume))
		print("Buy: " + str(buy))
		print("Sell: " + str(sell))
		print("Hold: " + str(hold))
		print("None: " + str(none))
		print("Buy Strength: " + str(ratio) + "%")
		print("Volume Strength: " + str(volume_ratio) + " posts per day")	
		print("Monthly Buy Average: " + str(month_ratio) + "%")
		print("Monhly Volume Average " + str(month_volume) + " posts per day")
		# print("Current Price: $" + str(currentPrice))
		print("Month Price Average: $" + str(monthPriceAverage))
		print()
		ratio = 0
		
	except Exception as e:
		print("Main script error! - " + str(e))
		
# Displaying alerts
print()
print("ALERTS: " + str(len(alerts)))
print()
for alert in alerts:
	print(alert)
	info = alerts.get(alert)
	print("Buy Strength: " + str(round(info[0], 2)) + "%")
	print("Volume Strength: " + str(round(info[1], 2)) + " posts per day")
	print("Monthly Buy Average: " + str(round(info[2], 2)) + "%")
	print("Monhly Volume Average " + str(round(info[3], 2)) + " posts per day")
	#print("Current Price: $" + str(currentPrice))
	print("Month Price Average: $" + str(monthPriceAverage))
	print()
print()
print("NEW ALERTS: " + str(len(newAlerts)))
for alert in newAlerts:
	print(alert)
	info = newAlerts.get(alert)
	print("Buy Strength: " + str(round(info[0], 2)) + "%")
	print("Volume Strength: " + str(round(info[1], 2)) + " posts per day")
	#print("Buy Average: " + str(round()))
	print()
	
c.close()
conn.close()

saveFile = open("D:/Desktop/previousAlerts.txt", 'w')
saveFile.close()
for item in alerts:
	saveFile = open("D:/Desktop/previousAlerts.txt", 'a')
	saveFile.write(str(item) + '\n')
	saveFile.close()