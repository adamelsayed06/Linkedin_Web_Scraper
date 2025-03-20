from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# auto install chrome driver

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://www.linkedin.com/login")

time.sleep(5) # wait for page to load 5s

username = driver.find_element(By.ID, "username") # <input id="username"> on linkedin website, searches for this tag
username.send_keys(USERNAME) # enters username

password = driver.find_element(By.ID, "password") # <input id="password"> on linkedin website, searches for this tag
password.send_keys(PASSWORD) # enters password

driver.find_element(By.XPATH, "//button[@type='submit']").click() #find button with type submit (login button) and clicks it