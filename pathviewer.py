from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.loginInfo import loadSavedLogin

class InstagramPathViewer:
    def __init__(self, path):
        self.path = path
        self.username, self.password = loadSavedLogin()
        self.driver = self.setupDriver()
        self.instagram_url = "https://www.instagram.com/"

    def setupDriver(self):
        service = Service(executable_path="chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        return driver

    def login(self):
        self.driver.get(self.instagram_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(self.username)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(self.password)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button'))).click()
        time.sleep(10)  # Wait to be logged in

    def goToStartingProfile(self):
        self.driver.get(f"{self.instagram_url}{self.path[0]}") # first person in list is starting user
        time.sleep(2)

    def clickFollowing(self):
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))).click()
        time.sleep(3)  # wait for following results


    def searchFollowing(self, username):
        search_box = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[3]/div/div/input'))
        )
        search_box.send_keys(username)
        time.sleep(2)  # wait for search results

    def goToFollowingProfile(self, username):
        self.driver.get(f"{self.instagram_url}{username}")
        time.sleep(2)

    def showPath(self):
        self.login()
        self.goToStartingProfile()

        for user in self.path[1:]:
            self.clickFollowing()
            self.searchFollowing(user)
            self.goToFollowingProfile(user)

        time.sleep(10) # wait before exiting
        self.driver.quit()

# viewer = InstagramPathViewer(['jayz', 'beyonce'])
# viewer.showPath()