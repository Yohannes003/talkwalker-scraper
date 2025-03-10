from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pickle
import time

firefox_options = webdriver.FirefoxOptions()
firefox_service = FirefoxService(GeckoDriverManager().install())
driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
driver.get("https://app.talkwalker.com/app/login")

username = "email"
password = "pass"

time.sleep(30)
# Locate the username input field and input the username
username_input = driver.find_element(By.XPATH, '//*[@id="tw-container"]/div/div/div/div/main/div/div/form/div[1]/div[1]/div/input')
username_input.send_keys(username)

# Click the next button
next_button = driver.find_element(By.XPATH, '//*[@id="next-button"]')
next_button.click()

time.sleep(2)  # Wait for the password field to appear

# Locate the password input field and input the password
password_input = driver.find_element(By.XPATH, '//*[@id="tw-container"]/div/div/div/div/main/div/div/form/div[1]/div[2]/div/input')
password_input.send_keys(password)

# Click the login button
login_button = driver.find_element(By.XPATH, '//*[@id="login-button"]')
login_button.click()
time.sleep(10)
# Save cookies (overwrite if the file exists)
with open("talkwalk_cookies.pkl", "wb") as f:
    pickle.dump(driver.get_cookies(), f)
driver.quit()

#mimitib231@polatrix.com
#//*[@id="tw-container"]/div/div/div/div/main/div/div/form/div[1]/div[1]/div/input
#//*[@id="tw-container"]/div/div/div/div/main/div/div/form/div[1]/div[2]/div/input
#//*[@id="login-button"]
