import os
import sqlite3 as sqlite
from queue import Queue

import bs4 as bs
import requests


class NMCScraper():
	def __init__(self) -> None:
		#Database stuff
		self.setupDatabase() #dbCode should be a status code
		#Url Stuff
		self.startURL = self.urlInput()
		if self.startURL:
			self.start()

	def setupDatabase(self) -> None:
		"""
		Sets up Database
		"""
		self.connection = sqlite.connect("NameMC.db", check_same_thread=False)
		cur = self.connection.cursor()
		try:
			cur.execute("CREATE TABLE Account(Name, uuID, uuID2, prevNames)")
		except sqlite.OperationalError as e:
			fprint(e)
		cur.close()

	def addAccount(self,name, uuID, uuID2, prevNames):
		cur = self.connection.cursor()
		cur.execute(f'INSERT INTO Account VALUES({name},{uuID},{uuID2},{prevNames})')
		self.connection.commit()
		cur.close()

	def urlInput(self) -> str:
		"""
		Prompts the user for a URL

		Returns:
			str: URL from User
		"""
		fprint("Please provide a start URL (A link to a Profile)")
		if self.testURL(url := input("==> ")):
			return url
		else:
			clearConsole()
			fprint("Input is not a valid NameMC Profile URL")
			self.urlInput()

	def testURL(self,url) -> bool:
		"""
		Takes a URL as String and tests for NameMC Profile structure

		Args:
			URL (str): URL

		Returns:
			bool: If the given URL has NameMC Structure or not
		"""
		# Sample URL: https://namemc.com/profile/JustCallMeSimon.1
		if url.startswith("https://namemc.com/profile/"):
			MCname = url.replace("https://namemc.com/profile/","").split(".")
			return True if len(MCname[0]) in range(3,17) else False
		else:
			return False

	def start(self):
		toBeCrawled = Queue(0)
		newURLS,Name,prevNames,uuID,uuID2 = self.crawlURL(self.startURL)
		self.addAccount(Name,uuID,uuID2,prevNames)

		# Note to self, this is 3 AM Code (not really but still) fix tomorrow

		for url in newURLS:
			if url not in toBeCrawled:
				toBeCrawled.put(url)
		while toBeCrawled:
			nextURL = toBeCrawled.get()
			newURLS,Name,prevNames,uuID,uuID2 = self.crawlURL(next)

	def crawlURL(URL):
		#do beautifulsoup shits... i alr wanna die. Update: thinking about bs4 shits still wants me to commit non alive.
		pass


def fprint(text) -> None:
	"""
	Takes a Message and adds a prefix before printing

	Args:
		text (any): Object that should be printed
	"""
	print(f"[NMCS] - {str(text)}")

def clearConsole() -> None:
	"""
	Clears the console
	"""
	os.system('cls' if os.name=='nt' else 'clear')

if __name__ == "__main__":
	scraper = NMCScraper()
