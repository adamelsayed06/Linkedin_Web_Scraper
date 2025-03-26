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
import re

load_dotenv()

USERNAME = os.getenv("LINKEDIN_USERNAME")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
ACCESSIBILITY_KEYWORDS = {
    "accessibility", "a11y", "wcag", "screen reader", "assistive technology",
    "inclusive design", "universal design", "alt text", "aria", "captioning",
    "closed captions", "color contrast", "cognitive accessibility",
    "disability inclusion", "web accessibility", "usability", "ada compliance",
    "digital accessibility expert", "accessibility engineer", "accessibility specialist",
    "UX accessibility consultant", "web accessibility developer", "ADA compliance officer",
    "disability advocate", "human-centered design specialist", "accessibility consultant",
    "usability expert", "voiceover", "JAWS", "NVDA", "TalkBack", "braille displays",
    "semantic HTML", "keyboard navigation", "digital equality", "assistive UX",
    "social model of disability", "equity and accessibility", "neurodiversity", 
    "human-centered design", "empathy-driven design", "barrier-free access"
}

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
    source = driver.page_source #get source code of loaded page
    soup = BeautifulSoup(source, "html.parser") #parse source code with BS4 and default parser
    
    name = soup.find('div', class_="jGartttxmtrDzkrUUMcDSSWGJxlJixOGnZIHk") #name element
    headline = soup.find('div', class_="text-body-medium break-words") #headline element
    description = soup.find('div', class_="RinVMSOWRtYXwYvTNDaswJSYyXBbKjzFFUWQ full-width t-14 t-normal t-black display-flex align-items-center") #description element
    #note that there may be weird characters needs to be cleaned
    
    #open & parse skills tab
    open_profile_and_scroll(profile_url + "details/skills/")
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser")
    skills = soup.find('ul', class_="JqmyCNHukZleLyGJMVErdOZaZFoDArjDs") 
    #remove numbers and word endorsemenets, keep places of employment/titles could give info for accessibility skills

    if headline or description or name or skills is None:
        return "ERROR"
    else:
        return [name.get_text(strip=True), headline.get_text(strip=True), description.get_text(strip=True), skills.get_text(strip=True)]
    #maybe change to a try-catch?

def clean_data(data):
    #remove any unwanted characters/info from data and make it all a string
    cleaned_data = ""
    for dataItem in data:
        dataItem = re.sub(r'[\n\t]+', ' ', dataItem)
        dataItem = re.sub(r'[^a-zA-Z0-9 ]', '', dataItem)
        cleaned_data += dataItem
    return cleaned_data

#@param data: string
#@return list of strings
def extract_keywords(data):
    #TODO: rewrite with fuzzy search instead of spacy -- don't just want exact matches
    pass

def get_new_profiles(count):
    profiles = []
    
    for i in range(count):
        source = driver.page_source 
        soup = BeautifulSoup(source, "html.parser")
        divs = soup.find_all('div', class_="display-flex flex-row justify-space-between")
        
        for div in divs:
            a_tag = div.find('a')
            if a_tag:
                profiles.append(a_tag['href'])
            else:
                print("ERROR: No a tag found")
        open_profile_and_scroll(a_tag['href']) #only scrolls last element -> potential optimization
        
    #initialize array of profiles -> get all profiles on the right and add to array -> open each profile and scroll -> get new profiles -> repeat count time
    
if __name__ == "__main__":
    
    
    #base case, runs through first profile
    
    login()
    open_profile_and_scroll("https://www.linkedin.com/in/adam-elsayed-9b0162245/")
    profiles = get_new_profiles(10) 
    for profile in profiles:
        data = extract_data(profile)
        cleaned_data = clean_data(data)
        keywords = extract_keywords(cleaned_data)
        #add name + keywords to postgres database