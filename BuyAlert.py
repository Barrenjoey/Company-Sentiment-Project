import sqlite3
import datetime
'''
This is an alert tool i created to search over each company from the database and
create an alert if certain conditions are met, buy_strength and volume_strength. The 
search can be altered to a set time period, however the tools main use is for 
short time periods such as 1-10 days.
'''
# Set the period of time you want to analyse - in days
time_period = 5
# Set wanted ratio and volume for alert. Buy strength in %
buy_strength = 70
buy_strength_month = 70
volume_strength_low = 2
volume_strength_high = 40
desired_volatility = 8

# Set price difference condition for alert in % (percent of current price below monthly average)
priceDifference = 8

# Dates
date = datetime.datetime.today()
#date = date - datetime.timedelta(days=15)
past_date = date - datetime.timedelta(days=time_period)
past_month = date - datetime.timedelta(days=30)
past_monthStr = past_month.strftime('%Y-%m-%d')
dateStr = date.strftime('%Y-%m-%d')
print("Date: " + str(date))
print("Past Date: " + str(past_date))
print("Past Month: " + str(past_month))
#print(dateStr)
print()
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
prefix_list = ['TKF']

previous = False
if previous:
	with open("D:/Desktop/Alerts 13-2.txt") as f:
		alreadyBought = f.readlines()
		alreadyBought = [x.strip() for x in alreadyBought]
#print(alreadyBought)
# Loop through company prefix
alerts = {}
underValueAlert = {}
newAlerts = {}
counter = 0
gainersList = []
for prefix in prefix_list[0:]:
	try:
		counter += 1
		print("Scanned: " + str(counter))
		print("Alerts: " + str(len(alerts)))
		print("Analysing: " + prefix + " for past " + str(time_period) + " days")
		# Importing sentiment data
		data = select_scraped_data(prefix)
		# Converting to datestamp to sort by date and then sorting chronologically.
		date_data = []
		clean_data = []
		month_data = []
		for item in data:
			item = list(item)
			item[0] = datetime.datetime.strptime(item[0], "%d/%m/%y")
			date_data.append(item)
		date_data.sort()
	except Exception as e:
		print("Error importing data - " + str(e))
		continue
	'''
	Pricing
	'''
	minPrice = 100
	maxPrice = 0
	try:
		# Importing price data
		priceData = select_price_data(prefix)
		# Sorting data
		priceData.sort()
		# Getting prices for the past month
		monthPrices = []
		for val in priceData:
			if val[0] > past_monthStr:
				if val[0] <= dateStr:
					monthPrices.append(val)
					# Getting volatility from min and max prices
					if val[2] < minPrice and val[2] > 0:
						minPrice = val[2]
					if val[3] > maxPrice:
						maxPrice = val[3]
		volatility = ((maxPrice - minPrice) / minPrice)*100
		volatility = round(volatility, 2)
		# print(minPrice)
		# print(maxPrice)
		# Working out the average price for the past month
		monthPriceAverage = 0
		for price in monthPrices:
			monthPriceAverage += price[1]
		monthPriceAverage = round(monthPriceAverage/len(monthPrices), 3)
		# Getting current price from last entry
		currentPrice = monthPrices[-1]
		currentPrice = currentPrice[1]
		#print(currentPrice)
		# Converting price difference to string to convert to float
		if priceDifference >= 10:
			priceDifference2 = "0." + str(priceDifference)
		elif priceDifference < 10:
			priceDifference2 = "0.0" + str(priceDifference)
		priceDifference2 = float(priceDifference2)
		# Figuring out the desired price difference from the chosen percentage at start of script.
		wantedPriceDiff = (priceDifference2 * monthPriceAverage)
		wantedPriceDiff = round(monthPriceAverage - wantedPriceDiff, 4)
		#print(wantedPriceDiff)
		currentDifAverage = ((monthPriceAverage - currentPrice)/monthPriceAverage)*100
		currentDifAverage = round(currentDifAverage, 2)
		#print(currentDifAverage)
		'''
		Gainers of the Month
		'''
		lastMonthsPrice = monthPrices[0]
		lastMonthsPrice = lastMonthsPrice[1]
		monthlyGain = ((currentPrice - lastMonthsPrice)/lastMonthsPrice)*100
		monthlyGain = round(monthlyGain, 2)
		if monthlyGain > 500:
			print("Possible dead stock")
			continue
		if monthlyGain > 0:
			trend = "Up!"
			if len(gainersList) < 7:
				gainersList.append([prefix, monthlyGain])
			else:
				for i, x in enumerate(gainersList):
					if monthlyGain > x[1]:
						del gainersList[i]
						gainersList.append([prefix, monthlyGain])
						break		
		else:
			trend = "Down"
	except Exception as e:
		print("No price data - " + str(e))
		currentPrice, wantedPriceDiff, currentDifAverage, monthlyGain, trend = 0, 0, 0, 0, None
	'''
	Total historical data as averages. (vol/buy)
	
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
	'''
	Data for the past month. (30 days)
	'''
	try:
		# Converting date format and removing items not in the past month and chosen time period.
		for item in date_data:
			if item[0] <= date:
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
	except Exception as e:
		print("Error getting monthly data - " + str(e))
		month_ratio, month_volume = 0, 0
	'''
	Data for the chosen time period. ie 10 days.
	'''	
	try:
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
	except Exception as e:
		print("No data for chosen time period - " + str(e))
		ratio, volume_ratio = 0, 0
		
	#Add alert if conditions met
	if month_ratio >= buy_strength_month:
		if ratio >= buy_strength:
			if volume_strength_low < volume_ratio < volume_strength_high:
				if currentPrice <= wantedPriceDiff and currentPrice != 0:
					if volatility >= desired_volatility:
						alerts[prefix] = [ratio, volume_ratio, month_ratio, month_volume, monthPriceAverage, currentPrice, currentDifAverage, volatility]
						if previous:
							if prefix not in alreadyBought:
								newAlerts[prefix] = [ratio, volume_ratio]
	
	if currentPrice <= (wantedPriceDiff * 0.9) and currentPrice > 0.015:
		underValueAlert[prefix] = [ratio, volume_ratio, month_ratio, month_volume, monthPriceAverage, currentPrice, currentDifAverage]
	print()					
	print("########  SENTIMENT  #########")
	print("Volume: " + str(volume), ", Buy: " + str(buy), ", Sell: " + str(sell), ", Hold: " + str(hold), ", None: " + str(none))
	print("Buy Strength: " + str(ratio) + "%")
	print("Volume Strength: " + str(round(volume_ratio, 1)) + " posts per day", )
	print("Monthly Buy Average: " + str(month_ratio) + "%")
	print("Monthly Vol Average: " + str(month_volume) + " posts per day")
	print()
	print("########  PRICING  #########")
	print("Current Price: $" + str(currentPrice))
	print("Month Price Avg: $" + str(monthPriceAverage))
	print("% Below Avg: " + str(currentDifAverage) + '%')
	print("Volatility: " + str(volatility) + '%')
	print("Trending " + str(trend))
	print()
	print("############################################################")
	

print("Top Gainers:")
print(gainersList)
# Displaying alerts
print()
print("Price Alerts: " + str(len(underValueAlert)))
print()
for priceAlert in underValueAlert:
	print(priceAlert)
	info2 = underValueAlert.get(priceAlert)
	print("Current Price: $" + str(round(info2[5], 3)))
	print("Monthly Price Average: $" + str(round(info2[4], 3)))
	print("Price is: " + str(info2[6]) + '% below average')
	print()
print()
print("ALERTS: " + str(len(alerts)))
print()
for alert in alerts:
	print(alert)
	info = alerts.get(alert)
	print("Buy Strength: " + str(round(info[0], 2)) + "%")
	print("Volume Strength: " + str(round(info[1], 2)) + " posts per day")
	print("Monthly Buy Average: " + str(round(info[2], 2)) + "%")
	print("Monthly Volume Average " + str(round(info[3], 2)) + " posts per day")
	print("Current Price: $" + str(round(info[5], 3)))
	print("Monthly Price Average: $" + str(round(info[4], 3)))
	print("Price is: " + str(info[6]) + '% below average')
	print("Volatility: " + str(info[7]) + '%')
	print()
print()
'''
print("NEW ALERTS: " + str(len(newAlerts)))
for alert in newAlerts:
	print(alert)
	info = newAlerts.get(alert)
	print("Buy Strength: " + str(round(info[0], 2)) + "%")
	print("Volume Strength: " + str(round(info[1], 2)) + " posts per day")
	#print("Buy Average: " + str(round()))
	print()
'''
c.close()
conn.close()

saveFile = open("D:/Desktop/previousAlerts.txt", 'w')
saveFile.close()
for item in alerts:
	saveInfo = alerts.get(item)
	payLoad = (item + '\nBuy Str: ' + str(saveInfo[0]) + '%\nVol Str: ' + str(saveInfo[1])
	+ '\nCurrent Price: $' + str(saveInfo[5]) + '\nPrice Avg: $' + str(saveInfo[4]) + '\nPrice Dif: '
	+ str(saveInfo[6]) + '%\nVolatility: ' + str(saveInfo[7]) + '%\n')
	saveFile = open("D:/Desktop/previousAlerts.txt", 'a')
	saveFile.write(str(payLoad) + '\n')
	saveFile.close()