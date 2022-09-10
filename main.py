import sqlite3 as sqlite
import bs4 as bs
import os
from queue import Queue

class NMCScraper():
	def __init__(self) -> None:
		#Database stuff
		dbCode = self.setupDatabase() #dbCode should be a status code
		#Url Stuff
		self.startURL = self.urlInput()
		if self.startURL:
			self.start()

	def setupDatabase(self) -> int:
		"""
		Check the status of he Database and return a status code 

		Returns:
			int: status code
		"""
		pass

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
		# Sample URL: https://namemc.com/profile/JustCallMeSimon
		if url.startswith("https://namemc.com/profile/"):
			MCname = url.replace("https://namemc.com/profile/","").split(".")
			if len(MCname[0]) in range(3,17):

				#TODO and only upper lower and number

				return True
			else:
				False
		else:
			return False

	def start(self):
		toBeCrawled = Queue(0)
		#initial crawl of first Page
		newURLS,Name,prevNames,uuID,uuID2 = self.crawlURL(self.startURL)
		#add all new urls into q
		#loop through bla bla bla

	def crawlURL(URL):
		#do beautifulsoup shits... i alr wanna die
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