from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
import re 
import csv
import sqlite3
import datetime
import time #Used for testing purposes only....
#Sentiment analysis module.
#This module extracts the scraped data from the database, then extracts sentiment based on keywords.
#It then returns the analysed data to a new database, which records instances of mentioned sentiment for that keyword.

#Date
date = datetime.date.today()

#Sqlite database stuff
conn = sqlite3.connect('Sentiment_Analysis.db')
c = conn.cursor()
#Creating Main_DB table if it doesnt exist
def create_table():
	c.execute("CREATE TABLE IF NOT EXISTS Main_DB (id INTEGER PRIMARY KEY, topic TEXT, score INTEGER, article_date TEXT, translated_score TEXT, category TEXT, location TEXT, string_snippet TEXT, source TEXT, url TEXT, date_scraped TEXT, date_analysed TEXT)")	
#Main data entry function to add topics to Main_DB
def data_entry():
	c.execute("INSERT INTO Main_DB (topic, score, article_date, translated_score, category, location, string_snippet, source, url, date_scraped, date_analysed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (topic,upload_score,article_date,'translated','category',location,'string',source,url,date_scraped,date))
	conn.commit()
#Function to add analysed date to crawled_Data to show what has been analysed for future processing.
def date_analysed():
	c.execute("UPDATE Crawled_Data SET date_analysed=? WHERE url=?", (date,url))
	conn.commit()
#Selecting the data to be analysed from the Scraped/Crawled DB
def select_crawled_data():
	c.execute("SELECT * FROM Crawled_Data WHERE date_analysed IS NULL")
	data = c.fetchall()
	return data
#Looks to see if the url exists in the main DB, then deletes if a match.
def select_existing_url():
	c.execute("SELECT url FROM Crawled_Data")
	existing_url = c.fetchall()
	#data = data[0]
	for cell in existing_url:
		cell = cell[0]
		if cell == url:
			delete_existing_url()
		else:
			pass
def delete_existing_url():
	c.execute("SELECT * FROM Main_DB")
	dat = c.fetchall()
	c.execute("DELETE FROM Main_DB WHERE url=?", (url,))
	conn.commit()

create_table()
#Importing data for analysing. Default setting to date_analysed is null from crawled_Data.
select_crawled_data()
data = select_crawled_data()
	
#Importing text list of products
with open("D:/Desktop/Code/Web Crawler/Keywords.txt") as k:
	keyword_list = k.readlines()
#Making lower case.	
keyword_list = [x.lower() for x in keyword_list]
#Stripping \n and whitespace	
keyword_list = [x.strip() for x in keyword_list]
#Importing people names
with open("D:/Desktop/Code/Web Crawler/All_names.txt") as name:
	name_list = name.readlines()
name_list = [x.lower() for x in name_list]	
name_list = [x.strip() for x in name_list]	
#Importing positive word list
with open("D:/Desktop/Code/Web Crawler/positive-words.txt") as p:
	positive_list = p.readlines()	
positive_list = [x.strip() for x in positive_list]
#Importing negative word list
with open("D:/Desktop/Code/Web Crawler/negative-words.txt") as n:
	negative_list = n.readlines()
negative_list = [x.strip() for x in negative_list] 
#Importing phrase list and values for scoring, convert to csv for delimiter, create list and make lower case.
with open("D:/Desktop/Code/Web Crawler/Phrase_scoring.txt") as phr:
	phrase_list = csv.reader(phr, delimiter = ",")
	phrase_list = list(phrase_list)
phrase_list = [[j.lower() for j in i] for i in phrase_list]
#Importing negation phrases.
with open("D:/Desktop/Code/Web Crawler/Phrase_negation.txt") as frase:
	frase_list = frase.readlines()
frase_list = [x.lower() for x in frase_list]	
frase_list = [x.strip() for x in frase_list]	
#print (keyword_list)
#Negation words
NEGATION = r"""
    (
       never|no\s|nothing|nowhere|noone|none|not\s|
       havent|hasnt|hadnt|cant|couldnt|shouldnt|
       wont|wouldnt|dont|doesnt|didnt|isnt|arent|aint|n't
	)"""
NEGATION_RE = re.compile(NEGATION, re.VERBOSE)
#Declaring variables
keywords = []
keyword_linger = []
positives = []
negatives = []
key_sides = ""
key_sides3 = ""
key_sides4 = ""
key_sides5 = ""
score = 0
total_score = 0
scoreDict = {}
nouns = []
full_name = []
fuller_name = []
nameDict = {}
single_name = ""
single_names = []
negate_counter = 0
frase_counter = 0
counter = 0
#print(data)

#Main loop of data entries
for link in data[0:]:
	#Extracting wanted data from crawled db to transfer to sentiment db.
	counter += 1
	url = link[0]
	article_date = link[1]
	source = link[2]
	location = link[3]
	date_scraped = link[6]
	EXAMPLE_TEXT = link[5]
	#EXAMPLE_TEXT = "scottish pacific group is great. southern cross electrical engineering is bad. shopping centres australasia property group is amazing."
	#EXAMPLE_TEXT = "I really love my new Nokia Lumia 1520, but i don't like the screen! However, the image quality is not bad. My Iphone's battery life was really shit. However, the Microsoft phone is terrible. I like Nokia."
	# with open("C:/Users/Jake/Desktop/Web Crawler/July/3#Article.txt") as f:
	# EXAMPLE_TEXT = f.read()
	#Making lower case	
	EXAMPLE_TEXT = EXAMPLE_TEXT.lower()
	#Adding spaces after full stops to filter sentences correctly.
	EXAMPLE_TEXT = re.sub(r'\.', '. ', EXAMPLE_TEXT)
	#Tokenizing
	word_text = word_tokenize(EXAMPLE_TEXT)		#Word Tokenize
	sent_text = sent_tokenize(EXAMPLE_TEXT)		#Sent Tokenize
	#print(word_text)
	#Searching for keywords by sentence then word. 1 and 2 word strings pulled.
	for sent in sent_text:	#Loop through sentences
		print(sent)
		single_sent = word_tokenize(sent)	#Word tokenize for 1 sentence
		tagged = nltk.pos_tag(single_sent)			#Part of Speech tags
		negate = re.findall(NEGATION_RE, sent)
		# namedEnt = nltk.ne_chunk(tagged, binary=True)		#Named entity recognition
		# namedEnt.draw()
#Made changes here from each try/except to under 1 with elif statements.
		for key in single_sent:			#Loop through words of sentence
			if key in keyword_list:
				keywords.append(key)	#Append keywords to list
			key_sides += " " + key		#Key_sides = 2 word products
			key_sides3 += " " + key		#3 word keywords
			key_sides4 += " " + key		#4 word keywords
			key_sides5 += " " + key		#5 word keywords
			try:
				if key_sides in keyword_list:
					keywords.append(key_sides)
				elif key_sides3 in keyword_list:
					keywords.append(key_sides3)
				elif key_sides4 in keyword_list:
					keywords.append(key_sides4)
				elif key_sides5 in keyword_list:
					keywords.append(key_sides5)
			except:
				pass
#Made changes to 4 and 5 word keywords.				
			key_sides5 = key_sides4
			key_sides4 = key_sides3
			key_sides3 = key_sides	
			key_sides = key
	#Searching for Noun phrases to add to keywords list	
		#for word,pos in tagged:
			# if (pos == 'NNP' and word != 'My' and word not in keywords):
				# keywords.append(word)
######################				
	#People Names - Adds name and last name together then adds to keywords if successful. Also adding firstname to keywords.
			# if len(full_name) > 0:
				# if pos == 'NN':
					# full_name.append(word)
					# if len(full_name) == 2:
						# single_name = full_name[1]
						# full_name = full_name[0] + " " + full_name[1]
						# keywords.append(full_name)
						# nameDict[single_name] = full_name
						# fuller_name = full_name
						# full_name = []
				# else:
					# full_name = []
			# if word in name_list:
				# full_name.append(word)
				#keywords.append(word)
######################				
	#Searching for positive words
		for pos in single_sent:
			if pos in positive_list:
				positives.append(pos)
				score += 1
	#Searching for negative words
		for neg in single_sent:
			if neg in negative_list:
				negatives.append(neg)
				score += -1	
	#like negation and trump negation			
		for wrd,ps in tagged:
			if (ps == 'IN' and wrd == 'like'):
				print('like NEGATION!!!!')
				score += -1			
			# if wrd == "donald":
				# score += -1
	#Adding space to no and not to match negation list			
			if wrd == "not" or wrd == "no":
				wrd = wrd + " "	
			#if wrd == 'great'
	#Searching for negating words and turning their polarity by score. Positional counting system for assigning negation.		
			if wrd in negate or negate_counter >= 1:
				negate_counter += 1
				print(negate)
				#print(negate_counter)
				if wrd in positives:
					score += -2
					negate_counter = 0
				elif wrd in negatives:
					score += 2
					negate_counter = 0
				elif negate_counter >= 6 or wrd == '.':
					negate_counter = 0		
	#Phrase scoring. Searching for phrase and then scoring by assigned value. ie. 'expected more' -1 
		for phrases in phrase_list:
			find_phrase = re.findall(phrases[0],sent)
			#print(find_phrase)
			if len(find_phrase) >= 1:
				score += int(phrases[1])
				print(phrases)
				#print(phrases[1])
	#Phrase negation. Negating phrases and turning polarity. ie. 'could have' been better -1 		
		for frase in frase_list:		
			find_frase = re.findall(frase,sent)	
			if len(find_frase) >= 1:
				find_frase = word_tokenize(find_frase[0])
				#print(find_frase)
				for werd in single_sent:
					if werd in find_frase:
						frase_counter += 1
					if frase_counter == len(find_frase):
						if werd in positives:
							print('Phrase_negative: ',frase)
							score += -2
							frase_counter = 0
						elif wrd in negatives:
							print('Phrase_positive: ',find_phrase)
							score += 2
							frase_counter = 0
						elif frase_counter >= 3 or werd == '.':
							frase_counter = 0
								
	#Adding the keyword and score to a dictionary. Checking if keyword in dict, if so it adds the scores, else it creates new entry.		
		for k in keywords:
			if k in scoreDict:
				y = scoreDict.get(k)
				scoreDict[k] = y + score
			else:	
				scoreDict[k] = score
###################################				
#Scoring single word names to match with full name. Only does this if full name is not in sentence as well.				
		# for word in single_sent:		
			# if word in nameDict:
				# if len(fuller_name) == 0:
					# single_names.append(word)
					# z = nameDict.get(word)
					# try:
						# s = scoreDict.get(z)
						# scoreDict[z] = s + score
					# except:	
						# pass	
#####################################						
	#Assigning pos/neg words to previous sentence keyword		
		if score != 0 and len(keywords) == 0 and len(scoreDict) != 0:
			for l in keyword_linger:
				x = scoreDict.get(l)
				scoreDict[l] = score + x
		#print(negate)	
		print("Sentence score: ",score)
		print ("Positive Words: ",positives)
		print ("Negative Words: ",negatives)
		print("Keywords: ",keywords)
		#print("Names: ", single_names, score)
		#print(tagged)
		print(" ")
		keyword_linger = keywords
		keywords = []
		total_score = total_score + score
		score = 0
		positives = []
		negatives = []
		negate = []
		single_names = []
		fuller_name = []
	print(scoreDict)
	print("Total Score: ",total_score)
	print(counter)
	#print(nameDict)
	#Data entry - Checking existing url and updating.
	date_analysed()
	select_existing_url()
	for topic in scoreDict:
		upload_score = scoreDict[topic]
		data_entry()	
	scoreDict = {}
	total_score = 0	
	nameDict = {}
	print("##########################################")
	print("\n")
	
c.close()
conn.close()

