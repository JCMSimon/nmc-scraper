import os
import sqlite3 as sqlite
import time
from queue import Queue

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class NMCScraper():
    def __init__(self) -> None:
        # Selenium Stuff
        self.chrome_options = Options()
        self.chrome_options.add_argument("log-level=3")
        self.chrome_options.add_extension("3.4.2_0.crx")
        self.restartDriver()
        # Database stuff
        self.setupDatabase()
        # Url Stuff
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
            cur.execute("CREATE TABLE Account(Name, uuID, uuID_nh, prevNames)")
        except sqlite.OperationalError as e:
            fprint(e)
        cur.close()

    def addAccount(self, name, uuID, uuID_nh, prevNames):
        cur = self.connection.cursor()
        cur.execute(
            f'INSERT INTO Account VALUES({name},{uuID},{uuID_nh},{prevNames})')
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

    def testURL(self, url) -> bool:
        """
        Takes a URL as String and tests for NameMC Profile structure

        Args:
                URL (str): URL

        Returns:
                bool: If the given URL has NameMC Structure or not
        """
        # Sample URL: https://namemc.com/profile/JustCallMeSimon.1
        if url.startswith("https://namemc.com/profile/"):
            MCname = url.replace("https://namemc.com/profile/", "").split(".")
            return True if len(MCname[0]) in range(3, 17) else False
        else:
            return False

    def start(self):
        toBeCrawled = Queue(0)
        newURLS, Name, prevNames, uuID, uuID_nh = self.crawlURL(self.startURL)
        self.addAccount(Name, uuID, uuID_nh, prevNames)

        # Note to self, this is 3 AM Code (not really but still) fix tomorrow

        for url in newURLS:
            if url not in toBeCrawled:
                toBeCrawled.put(url)
        while toBeCrawled:
            nextURL = toBeCrawled.get()
            Name, uuID, uuID_nh, prevNames, newURLS = self.crawlURL(nextURL)

    def crawlURL(self, url):
        self.driver.get(url)
        Name = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '/html/body/main/div[1]/div[1]/h1'))).text
        try:
            uuID = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[3]'))).text
            uuID_nh = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[2]/div[2]/div[2]/div[3]'))).text
            prevNamesList = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[5]/div[2]'))).text.split("\n")
        except TimeoutException:
            uuID = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]'))).text
            uuID_nh = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[1]/div[2]/div[2]/div[3]'))).text
            prevNamesList = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div[1]/div[4]/div[2]'))).text.split("\n")
        except Exception as e:
            fprint("ERROR Please provide text below to JCMS#0557 on Discord")
            fprint(e)
        ##############################################
        self.restartDriver()
        ##############################################
        self.driver.get(f"{url}/following")
        try:
            follows = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
            newURLS = []
            for nameLine, followLine in zip(prevNamesList[::2], prevNamesList[1::2]):
                Name = str(nameLine).split(" ")[1]
                newURLS.append(f"https://namemc.com/profile/{Name}")
        except TimeoutException:
            pass
        ##############################################
        self.restartDriver()
        ##############################################
        self.driver.get(f"{url}/followers")
        try:
            follows = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/main/div[2]/div/div/table/tbody'))).text.encode("ascii", "ignore").decode().split("\n")
            for nameLine, followLine in zip(prevNamesList[::2], prevNamesList[1::2]):
                Name = str(nameLine).split(" ")[1]
                newURLS.append(f"https://namemc.com/profile/{Name}")
        except TimeoutException:
            pass
        OriginalName = str(prevNamesList[-1]).split(" ")[1]
        del prevNamesList[-1]
        prevNames = {OriginalName: "Original"}
        for nameLine, dateLine in zip(prevNamesList[::2], prevNamesList[1::2]):
            Name = str(nameLine).split(" ")[1]
            preDate = dateLine.replace("• ", "").split(" ")
            Date = str(f"{preDate[0]},{preDate[1]}")
            prevNames[Name] = Date
        fprint(f"""Summary:
Scraped Account > {Name}
Previous Names ({len(prevNames)}) > {prevNames}
UUIDS > {uuID},{uuID_nh}
New URL's ({len(newURLS)}) > {newURLS}
		""")
        time.sleep(100000)
        # return Name, uuID, uuID_nh, prevNames, newURLS

    def restartDriver(self):
        # Listen i know this is disgusting but Cloudflare is focking my bottom if i dont do this
        try:
            self.driver.close()
        except:
            pass
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.chrome_options)
        self.driver.minimize_window()


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
