from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

from utils.loginInfo import loadSavedLogin

class InstagramPathViewer:
    def __init__(self, path):
        self.path = path
        self.username, self.password = loadSavedLogin()
        self.driver = self.setupDriver()
        self.wait = WebDriverWait(self.driver, 12)
        self.instagram_url = "https://www.instagram.com/"

    def setupDriver(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver

    def findFirst(self, locators, timeout=10):
        """Try locators quickly without stacking long waits."""
        end = time.time() + timeout
        while time.time() < end:
            for by, value in locators:
                elements = self.driver.find_elements(by, value)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            return element
                    except Exception:
                        continue
            time.sleep(0.2)
        raise TimeoutException(f"Could not find any of: {locators}")

    def dismissIfPresent(self, xpaths, timeout=1.5):
        for xpath in xpaths:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                return True
            except TimeoutException:
                continue
        return False

    def login(self):
        self.driver.get(f"{self.instagram_url}accounts/login/")

        self.dismissIfPresent([
            "//button[contains(., 'Allow all')]",
            "//button[contains(., 'Accept all')]",
            "//button[contains(., 'Accept')]",
            "//button[contains(., 'Allow')]",
        ], timeout=1)

        # Instagram login now uses email/pass but we're keeping username/password as fallback
        username_input = self.findFirst([
            (By.NAME, "email"),
            (By.NAME, "username"),
        ], timeout=8)
        password_input = self.findFirst([
            (By.NAME, "pass"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ], timeout=5)

        username_input.clear()
        username_input.send_keys(self.username)
        password_input.clear()
        password_input.send_keys(self.password)

        self.findFirst([
            (By.XPATH, "//div[@role='button' and contains(., 'Log in')]"),
            (By.XPATH, "//button[contains(., 'Log in')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
        ], timeout=5).click()

        # Wait until we leave the login page
        WebDriverWait(self.driver, 15).until(
            lambda d: "accounts/login" not in d.current_url
        )
        self.dismissIfPresent([
            "//button[contains(., 'Not Now')]",
            "//div[@role='button' and contains(., 'Not Now')]",
        ], timeout=2)
        self.dismissIfPresent([
            "//button[contains(., 'Not Now')]",
            "//div[@role='button' and contains(., 'Not Now')]",
        ], timeout=2)

    def goToStartingProfile(self):
        self.driver.get(f"{self.instagram_url}{self.path[0]}/")
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(., 'following') or contains(., 'Following')]")
            )
        )

    def clickFollowing(self):
        # New Instagram UI uses href="#", so now we match by visible text, not /following
        following_link = self.findFirst([
            (By.XPATH, "//a[contains(., 'following')]"),
            (By.XPATH, "//a[contains(., 'Following')]"),
            (By.XPATH, "//*[contains(@href, '/following')]"),
        ], timeout=8)
        following_link.click()
        self.findFirst([
            (By.CSS_SELECTOR, "input[aria-label='Search input']"),
            (By.CSS_SELECTOR, "input[placeholder='Search']"),
            (By.XPATH, "//*[@role='dialog']//input"),
        ], timeout=8)

    def searchFollowing(self, username):
        search_box = self.findFirst([
            (By.CSS_SELECTOR, "input[aria-label='Search input']"),
            (By.CSS_SELECTOR, "input[placeholder='Search']"),
            (By.XPATH, "//*[@role='dialog']//input"),
        ], timeout=5)
        search_box.clear()
        search_box.send_keys(username)
        time.sleep(1.2)

    def goToFollowingProfile(self, username):
        self.driver.get(f"{self.instagram_url}{username}/")
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//header | //main")
            )
        )

    def showPath(self):
        self.login()
        self.goToStartingProfile()

        for user in self.path[1:]:
            self.clickFollowing()
            self.searchFollowing(user)
            self.goToFollowingProfile(user)

        time.sleep(5) # wait b4 exiting
        self.driver.quit()
