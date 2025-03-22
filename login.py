from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import time

load_dotenv()

USERNAME = os.getenv("LINKEDIN_USERNAME")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# auto install chrome driver
chrome_opts = ChromeOptions() 
chrome_opts.add_experimental_option("detach", True)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_opts)


def login():
    driver.get("https://www.linkedin.com/login")

    time.sleep(5) # wait for page to load 5s

    username = driver.find_element(By.ID, "username") # <input id="username"> on linkedin website, searches for this tag
    username.send_keys(USERNAME) # enters username
    
    time.sleep(2)

    password = driver.find_element(By.ID, "password") # <input id="password"> on linkedin website, searches for this tag
    password.send_keys(PASSWORD) # enters password
    
    time.sleep(2)

    driver.find_element(By.XPATH, "//button[@type='submit']").click() #find button with type submit (login button) and clicks it

def open_profile_and_scroll(profile_url):
    driver.get(profile_url) # opens your profile
    time.sleep(5) # wait for page to load 5s
    
    #scrolls to the bottom of the page
    start = time.time()
    while time.time() - start < 5: #scrolls for 5 seconds
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def extract_data(profile_url):
    headline = driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]").text #headline element
    description = driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/div").text #description element
    
    open_profile_and_scroll(profile_url + "details/skills/") #opens skills section of profile
    skills = driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]").text
    
    return [headline, skills, description]
    
    
    
if __name__ == "__main__":
    login()
    open_profile_and_scroll("mock-profile-url")