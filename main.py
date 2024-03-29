import logging
import os
import sqlite3 as sqlite
from queue import Queue
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm


class NMCScraper():
	def __init__(self) -> None:
		logging.getLogger('WDM').setLevel(logging.NOTSET)
		self.driver = self.setupBrowser()
		clearConsole()
		self.setupDatabase()
		self.startURL = self.urlInput()
		if self.startURL:
			self.start()
		else:
			fprint("Something went wrong! Contact JCMS#0557 on Discord")

	def setupBrowser(self) -> None:
		options = Options()
		options.add_argument("log-level=3")
		options.add_extension("./3.4.2_0.crx")
		return webdriver.Chrome(ChromeDriverManager().install(), options=options)

	def setupDatabase(self) -> None:
		"""
		Sets up Database
		"""
		self.connection = sqlite.connect("NameMC.db", check_same_thread=False)
		cur = self.connection.cursor()
		try:
			cur.execute("CREATE TABLE Account(Name, uuID, prevNames)")
		except sqlite.OperationalError as e:
			pass
		cur.close()

	def urlInput(self) -> str:
		"""
		Prompts the user for a URL

		Returns:
				str: URL from User
		"""
		fprint("Please provide a start URL (A link to a Profile)")
		if self.testURL(url := input("==> ")):
			return url.rstrip().lstrip()
		else:
			clearConsole()
			fprint("Input is not a valid NameMC Profile URL (make sure its not smth like 'de.namemc.com')")
			return self.urlInput()

	def testURL(self, url) -> bool:
		"""
		Takes a URL as String and tests for NameMC Profile structure

		Args:
				URL (str): URL

		Returns:
				bool: If the given URL has NameMC Structure or not
		"""
		# Sample URL: https://namemc.com/profile/JustCallMeSimon.1
		if url.rstrip().lstrip().startswith("https://namemc.com/profile/"):
			MCname = url.replace("https://namemc.com/profile/", "").split(".")
			return True if len(MCname[0]) in range(3, 17) else False
		else:
			return False


	def start(self) -> None:
		fprint("Starting...")
		toBeCrawled = Queue(0)
		Name, uuID, prevNames, newURLS = self.crawlURL(self.startURL, toBeCrawled)
		self.addAccount(Name, uuID, prevNames)
		#Start actual process
		if newURLS:
			for url in tqdm(newURLS,desc="Adding URLS to Queue",ascii=True):
				toBeCrawled.put(url)
		else:
			fprint("Profile does not link to further Profiles. Please Choose a Profile with Followers/Following")
		while toBeCrawled:
			nextURL = toBeCrawled.get()
			self.resetDriver()
			try:
				Name, uuID, prevNames, newURLS = self.crawlURL(nextURL,toBeCrawled)
				self.addAccount(Name, uuID, prevNames)
			except (ValueError, TypeError):
				pass

	def crawlURL(self, url, Queue):
		try:
			self.driver.get(url)
		except TimeoutException:
			return
		try:
			username = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[1]/div[1]/h1'))).text
			uuid = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[3]'))).text
			prevNamesList = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div[1]/div[5]/div[2]'))).text.split("\n")
		except TimeoutException:
			try:
				uuid = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]'))).text
				prevNamesList = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div[1]/div[4]/div[2]'))).text.split("\n")
			except TimeoutException:
				return
		except Exception as e:
			fprint("Something went wrong! Contact JCMS#0557 on Discord (1)")
			fprint(e)
		if username == "PlaceHolderUsernameBeLike":
			username = str(prevNamesList[-1]).split(" ")[1]
		clearConsole()
		fprint(f"Links in Queue: {Queue.qsize()} \n")
		fprint(f"""Username: {username}
[NMCS] - UUID: {uuid}
[NMCS] - Previous Names (if not none):""")
		# Process the prev Names Data
		OriginalName = str(prevNamesList[-1]).split(" ")[1]
		del prevNamesList[-1]
		prevNames = {OriginalName: "Original"}
		for nameLine, dateLine in zip(prevNamesList[::2], prevNamesList[1::2]):
			OldName = str(nameLine).split(" ")[1]
			tempDate = dateLine.replace("• ", "").split(" ")
			Date = str(f"{tempDate[0]},{tempDate[1]}")
			prevNames[OldName] = Date
			fprint(f"> {OldName} - {Date}")

		self.resetDriver()

		#following
		newURLS = []
		try:
			self.driver.get(f"{url}/following")
		except TimeoutException:
			pass
		try:
			following = WebDriverWait(self.driver,1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
			for nameLine, _ in zip(following[::2], following[1::2]):
				followsName = str(nameLine).split(" ")[1]
				newURLS.append(f"https://namemc.com/profile/{followsName}")

			pages = WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[1]/ul/li[1]/a'))).text.split("(")[1].replace(")","")
			pages = round(float(pages) / 50)
			try:
				for page in tqdm(range(2,pages + 1),desc="Gathering Follows",ascii=True):
					try:
						self.resetDriver()
						self.driver.get(f"{url}/following?sort=date:desc&page={page}")
						following = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
						for nameLine, _ in zip(following[::2], following[1::2]):
							followsName = str(nameLine).split(" ")[1]
							newURLS.append(f"https://namemc.com/profile/{followsName}")
					except TimeoutException:
						continue
			except:
				pass

		except TimeoutException:
			pass
		fprint(f"Follows: {len(newURLS)} People")

		self.resetDriver()

		#followers
		try:
			self.driver.get(f"{url}/followers")
		except TimeoutException:
			pass
		try:
			follows = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
			for nameLine, _ in zip(follows[::2], follows[1::2]):
				followingName = str(nameLine).split(" ")[1]
				newURLS.append(f"https://namemc.com/profile/{followingName}")

			pages = WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[1]/ul/li[2]/a'))).text.split("(")[1].replace(")","")
			pages = round(float(pages) / 50)
			try:
				for page in tqdm(range(2,pages + 1),desc="Gathering Followers",ascii=True):
					try:
						self.resetDriver()
						self.driver.get(f"{url}/followers?sort=date:desc&page={page}")
						followers = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
						for nameLine, _ in zip(followers[::2], followers[1::2]):
							followerName = str(nameLine).split(" ")[1]
							newURLS.append(f"https://namemc.com/profile/{followerName}")
					except TimeoutException:
						continue
			except:
				pass

		except TimeoutException:
			pass
		fprint(f"Followed by: {len(newURLS)} People")


		fprint(f"Linked People (new URLS): {len(newURLS)}")
		return username, uuid, prevNames, newURLS


	def resetDriver(self) -> None:
		"""
		Deletes Cookies
		"""
		self.driver.delete_all_cookies()
		sleep(1)

	def addAccount(self, name, uuID, prevNames) -> None:
		"""
		Adds Account Details to Database

		Args:
			name (str): Name of Account
			uuID (string): UUID of Account
			prevNames (dict): Dictionary of Old Names with Timestamp
		"""
		cur = self.connection.cursor()
		cur.execute(f'INSERT INTO Account VALUES(?,?,?)', (str(name), str(uuID), str(prevNames)))
		self.connection.commit()
		cur.close()

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
	os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
	scraper = NMCScraper()
