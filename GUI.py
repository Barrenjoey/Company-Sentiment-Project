import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import *
import sqlite3
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import Cobalt_Graphs
import Cobalt_Crawler
import multiprocessing

plt.style.use('bmh')
# Main class for initialising GUI window.
class CobaltBlue(tk.Tk):
	
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		#tk.Tk.geometry(self, '830x640+150+150')
		# App icon
		tk.Tk.iconbitmap(self, default="image/update.ico")
		
		# App title
		tk.Tk.wm_title(self, "Cobalt Blue")
		
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		
		self.frames = {}
		
		# Add new pages to tuple here.
		for F in (UpdatePage, GraphPage, AlertPage):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky='nsew')
		
		self.show_frame(UpdatePage)
		
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()

# Update page for app. Will act as apps homescreen. Also inherits from tk.Frame
class UpdatePage(tk.Frame):
	
	def __init__(self, parent, controller):
		# Initializing frames for the page.
		mainFrame = tk.Frame.__init__(self, parent)
		buttonFrame = tk.Frame(self)
		infoboxFrame = tk.Frame(self)
		scheduleFrame = tk.Frame(self)
		scheduleFrame2 = tk.Frame(self)
		updateFrame = tk.Frame(self)

		# Creating the title label
		self.titleImage = tk.PhotoImage(file="image/Title.png")
		title = tk.Label(self, image=self.titleImage)
		# Packing in title
		title.pack()

		#Packing in button frame
		buttonFrame.pack(in_=mainFrame)
		
		# Buttons to navigate between pages.
		self.image1 = tk.PhotoImage(file="image/update.png")
		self.image2 = tk.PhotoImage(file="image/Graph.png")
		self.image3 = tk.PhotoImage(file="image/Alert.png")
		button1 = tk.Button(self, text="Update", image=self.image1, width=120, height=120,
		compound='top', command=lambda: controller.show_frame(UpdatePage))
		button1.grid(in_=buttonFrame, row=2, column=0, padx=5, pady=10)
		button2 = tk.Button(self, text="Graphs", image=self.image2, width=120, height=120,
		compound='top', command=lambda: controller.show_frame(GraphPage))
		button2.grid(in_=buttonFrame, row=2, column=1, padx=5, pady=10)
		button3 = tk.Button(self, text="Alerts", image=self.image3, width=120, height=120,
		compound='top', command=lambda: controller.show_frame(AlertPage))
		button3.grid(in_=buttonFrame, row=2, column=2, padx=5, pady=10)

		# UPDATE DATABASE	(LEFT)
		# Title
		label = tk.Label(self, text="Update Database", padx=10, pady=10, font=("Helvetica", 16))
		label.pack(in_=updateFrame, anchor='n')
		self.updateButton = tk.Button(self, text="Update Database", image=self.image1, width=120, height=120,
		compound='top', command=self.update_database)
		self.updateButton.pack(in_=updateFrame, padx=10, pady=10)

		# Packing updateframe into infoboxframe
		updateFrame.grid(in_=infoboxFrame, row=1, column=1)

		# INFO BOX	(CENTER)
		# Creating info box widget
		infoBox = Text(self, width=50, height=25, padx=10, pady=10)
		infoBox.grid(in_=infoboxFrame, row=1, column=2, rowspan=10)

		# SCHEDULE WIDGETS	(RIGHT)
		# Title
		label2 = tk.Label(self, text="Schedule Update", padx=10, pady=10, font=("Helvetica", 16), anchor='n')
		label2.pack(in_=scheduleFrame, anchor='n')

		# Radio Buttons
		var = IntVar()
		radio1 = Radiobutton(self, text="Update Hourly", variable=var, value=1, font=("Arial", 12))
		radio1.pack(in_=scheduleFrame, anchor='w', padx=10, pady=5)
		radio2 = Radiobutton(self, text="Update Daily", variable=var, value=2, font=("Arial", 12))
		radio2.pack(in_=scheduleFrame, anchor='w', padx=10, pady=5)

		# Time Box widget
		timeValues = ('9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm')
		var2 = StringVar()
		timeSelect = Spinbox(self, values=timeValues, textvariable=var2, width=8, wrap='true', font=("Arial", 10))
		timeSelect.pack(in_=scheduleFrame, anchor='w', padx=10, pady=10)

		# scheduleButton
		self.image4 = tk.PhotoImage(file="image/schedule.png")
		scheduleButton = Button(self, text="Schedule Update", image=self.image4, width=120, height=80,
		compound='top', command=lambda: controller.show_frame(UpdatePage))
		scheduleButton.pack(in_=scheduleFrame2, anchor='w', padx=10, pady=20)

		# Placing schedule frame in infobox frame to grid place it
		scheduleFrame.grid(in_=infoboxFrame, row=1, column=3)
		scheduleFrame2.grid(in_=infoboxFrame, row=2, column=3)

		# Packing in infobox frame to mainframe
		infoboxFrame.pack(in_=mainFrame)

	def update_database(self):
		# Starts new process to update database
		p2 = multiprocessing.Process(target=Cobalt_Crawler.Crawler)
		p2.start()
		# Greys out button
		self.updateButton['state'] = 'disabled'
