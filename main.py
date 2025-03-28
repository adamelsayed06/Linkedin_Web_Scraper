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
import psycopg2

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
    "human-centered design", "empathy-driven design", "barrier-free access",
    "IAAP Certified", "Section 508", "Trusted Tester", 
    "European Accessibility Act (EAA) Compliance", "PDF remediation", 
    "A11y audits", "Accessibility SME (Subject matter expert)"
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

#TODO: find element name
def extract_name():
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser") 
    
    name = soup.find('div', class_="jGartttxmtrDzkrUUMcDSSWGJxlJixOGnZIHk")
    
    return name.get_text(strip=True)

#TODO: find specific element names
def extract_job_title():
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser") 
    
    desired_titles = ["Web Developer", "UX Designer", "UI Designer", "Software Engineer", "Software Developer", "Front End Developer", "UIUX Accessibility", "Software Accessibility", "Accessibility Tester"]
    
    headline = soup.find('div', class_="text-body-medium break-words")
    most_recent_job = soup.find()
    
    headline = headline.get_text(strip=True)
    most_recent_job = most_recent_job.get_text(strip=True)
    
    #job not found or not in desired titles
    if(headline is None or most_recent_job is None or headline not in desired_titles or most_recent_job not in desired_titles):
        return ""
    else: #return desired title
        if headline in desired_titles:
            for title in desired_titles:
                if title in headline:
                    return title
        elif most_recent_job in desired_titles:
            for title in desired_titles:
                if title in most_recent_job:
                    return title
    #maybe change to a try-catch?


#TODO: implement
def extract_skills(profile_url):
    
    '''REFERENCE
    open_profile_and_scroll(profile_url + "details/skills/")
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser")
    skills = soup.find('ul', class_="JqmyCNHukZleLyGJMVErdOZaZFoDArjDs")
    '''
    pass

def clean_data(data):
    cleaned_data = []
    for dataItem in data: #['accessibility', 'nope']
        dataItem = re.sub(r'[\n\t]+', ' ', dataItem)
        dataItem = re.sub(r'[^a-zA-Z ]', '', dataItem).strip().lower()
        
        for keyword in ACCESSIBILITY_KEYWORDS:
            if keyword.lower() in dataItem:
                cleaned_data.append(dataItem)
                break #avoid duplicates
    cleaned_data = list(set(cleaned_data)) #remove duplicates 
    return cleaned_data

#returns lists of new profiles to loop through
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
       
    return profiles
    
if __name__ == "__main__":
    '''
    main flow:
    1. login to linkedin --  login()
    2. get list of profiles -- get_new_profiles()
    3. open each profile and scroll to bottom -- open_profile_and_scroll()
    4. extract headline & most recent job title
    5. categorize into one of the following titles:  
    Web Developer, UX Designer, UI Designer, Software Engineer, Software Developer, Front End Developer, UIUX Accessibility, Software Accessibility, and Accessibility Tester
    6. Extract skills from profile
    7. Compare keywords for matches in ACCESSIBILITY_KEYWORDS
    8. Take matched keywords and add to database
    '''
    
    login()
    open_profile_and_scroll("https://www.linkedin.com/in/adam-elsayed-9b0162245/")
    profiles = get_new_profiles(10) 
    for profile in profiles:
        name = extract_name(profile)
        job_title = extract_job_title(profile)
        if job_title == "":
            continue
        skills = extract_skills(profile) #returns array of skills
        skills = clean_data(skills) #Take skills and remove anything that's not one of the ACCESSIBILITY_KEYWORDS
        #TODO: add name, job_title, and accessibility skills to database and anti-bot detection
        
    
        