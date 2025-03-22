from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
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
    #TODO: fix this function, XPATHs not found -- use BS4???
    source = driver.page_source #get source code of loaded page
    soup = BeautifulSoup(source, "html.parser") #parse source code with BS4 and default parser
    
    name = soup.find('div', class_="jGartttxmtrDzkrUUMcDSSWGJxlJixOGnZIHk") #name element
    headline = soup.find('div', class_="text-body-medium break-words") #headline element
    description = soup.find('div', class_="RinVMSOWRtYXwYvTNDaswJSYyXBbKjzFFUWQ full-width t-14 t-normal t-black display-flex align-items-center") #description element
    #note that there may be weird characters needs to be cleaned
    
    #open & parse skills tab
    open_profile_and_scroll(profile_url + "detail/skills/")
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser")
    skills = soup.find('div', class_="scaffold-finite-scroll__content")
   

    if headline or description or name or skills is None:
        return "ERROR"
    else:
        return [name.get_text(strip=True), headline.get_text(strip=True), description.get_text(strip=True), skills.get_text(strip=True)]
    #maybe change to a try-catch?
    
    
    
    
    
if __name__ == "__main__":
    login()
    open_profile_and_scroll("https://www.linkedin.com/in/adam-elsayed-9b0162245/")
    data = extract_data("https://www.linkedin.com/in/adam-elsayed-9b0162245/")
    print(data)