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
import random
import json

load_dotenv()
'''
MAIN LOGIC:
We use get_new_accessibility_profiles & get_new_software_profiles to get a few thousand urls.
Then we loop through each url, open the profile, extract name & job title,
check based on job title if they are accessibility or software professionals, 
if they're neither skip them, otherwise extract skills and add analytics
to their respective JSON files.
'''
#TODO: error handling, find swe urls, and bot detection
# bot detection => human like behavior, pause 30 seconds between extractions of each profile, human like login,
# rotating proxies and user agents.

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
chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_opts.add_experimental_option("useAutomationExtension", False)
chrome_opts.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_opts)

# tested and works
def login():
    driver.get("https://www.linkedin.com/login")

    time.sleep(5) # wait for page to load 5s

    username = driver.find_element(By.ID, "username") # <input id="username"> on linkedin website, searches for this tag
    username.send_keys(os.getenv("LINKEDIN_USERNAME")) # sends your username to the input field
    time.sleep(2)

    password = driver.find_element(By.ID, "password") # <input id="password"> on linkedin website, searches for this tag
    password.send_keys(os.getenv("LINKEDIN_PASSWORD")) # sends your password to the input field
    
    time.sleep(2)

    driver.find_element(By.XPATH, "//button[@type='submit']").click() #find button with type submit (login button) and clicks it

# tested and works
def open_profile_and_scroll(profile_url):
    # implement error handling for invalid URLs
    driver.get(profile_url) # opens your profile
    time.sleep(random.randint(3,5)) # wait for page to load 5s
    
    #scrolls to the bottom of the page
    start = time.time()
    end = random.randint(4,8)
    while time.time() - start < end: #scrolls for 4-8 seconds
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# tested and works
def extract_name():
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser") 
    
    # Search for the <h1> element with multiple classes
    name = soup.find('h1', class_=["noXxUHDdDzsoAtzfoMtCjNImbKnWKSCtAsU", 
                                   "inline", "t-24", "v-align-middle", "break-words"])

    if name is None:
        print("ERROR: Name element not found")
        return ""
    
    return name.get_text(strip=True)

'''
Extracts headline from profile page, but still needs to be compared against
accessibility and software professional titles, before being added to JSON
tested and works
'''
def extract_job_title():
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser") 
    
    headline = soup.find('div', class_="text-body-medium break-words")
    # example: Data Engineering Intern @Stantec | Research Assistant @Brooklyn College
    
    headline = headline.get_text(strip=True)
    
    #job not found or not in desired titles
    try:
        if(headline is None or headline == ""):
            print("ERROR: Headline not found or empty")
            return ""
        else: #return desired title
            return headline
    except Exception as e:
        print(f"Error extracting job title: {e}")
        return ""

 #works and tested
def extract_skills(profile_url):
    # Navigate to the skills section of the profile
    open_profile_and_scroll(profile_url + "details/skills/")
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser")
    
    # Find all <li> elements with the desired class
    li_elements = soup.find_all('li', class_="pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column")
    
    skills = []
    for li in li_elements:
        # Find the <div> within the <li> element with the specific class
        div = li.find('div', class_="display-flex flex-row justify-space-between")
        if div:
            skill_text = div.get_text(strip=True)
            # Truncate the skill text to half its length
            truncated_skill = skill_text[:len(skill_text) // 2]
            skills.append(truncated_skill)
    
    return skills

#returns lists of new profiles to loop through, update class name
def get_new_accessibility_profiles():
    '''
    WORKING BUT I NEED TO SCROLL THROUGH THE PAGE TO GET ALL PROFILES
    this will give us a list of like 1000 profiles each of which we can scrape
    # open_profile_and_scroll("https://www.linkedin.com/groups/4512178/members/")
    '''
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    profiles = [] 
    open_profile_and_scroll("https://www.linkedin.com/groups/4512178/members/")
    time.sleep(10) # wait for me to scroll through page for 10 seconds CHANGE THIS
    source = driver.page_source 
    soup = BeautifulSoup(source, "html.parser") 
    urls = soup.find_all('a', class_=["ember-view", "ui-conditional-link-wrapper", "ui-entity-action-row__link"])
    for url in urls:
        print(f"url: {url['href']}")
    
    for i in range(len(urls)):
        url = urls[i]['href'] # get the href attribute of the a tag
        if "linkedin.com" in url: # gets rid of the weird urls like linkedin.com/acessibility
            continue
        else:
            url = "https://www.linkedin.com" + url # add the base URL to the profile URL
        profiles.append(url)
    
    add_to_json("accessibility_profile_URLS.json", {"profile_URLS": profiles}) 
    # for now we can just add it to a JSON file and then loop through the JSON file to extract data

def get_new_software_profiles(count):
    pass
#tested, and working
def isSoftwareProfessional(job_title):
    
    #right now its checking if something like Data Engineering Intern @Stantec is in the list of software professional titles
    # to fix, we should loop through the titles, and see if job_title contains any of the titles in the list
    
    software_professional_titles = [
        "Web Developer", "UX Designer", "UI Designer", 
        "Software Engineer", "Software Developer", 
        "Front End Developer", "Backend Developer", 
        "Full Stack Developer", "Mobile App Developer", 
        "DevOps Engineer", "Data Scientist", 
        "Machine Learning Engineer", "Cloud Engineer", "Data Engineer",
        "Software Architect", "SWE", "SDE", "ML Engineer"
    ]
    
    for title in software_professional_titles:
        if title.lower() in job_title.lower(): #e.g. "Software Engineer" in "Software Engineer at Company"
            return True
    return False

# tested and working
def isAccessibilityProfessional(job_title):
    for keyword in ACCESSIBILITY_KEYWORDS:
        if keyword.lower() in job_title.lower():
            return True
        
    return False
    
#tested and working, just make sure we're converting profile_data to proper JSON format
def add_to_json(filename, profile_data):
    
    with open(filename, "r+") as file: # open file in read and write mode
        try:
            data = json.load(file) # load existing data
            data.append(profile_data) # append new profile data
            file.seek(0) # move the cursor to the beginning of the file to prevent corruption
            json.dump(data, file, indent=4) # write updated data back to file
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            data = []
    
    time.sleep(2)

def main():
    '''
    ROOT_URL = "" #PLACEHOLDER
    login()
    open_profile_and_scroll(ROOT_URL)
    for profile in profiles:
        open_profile_and_scroll(profile)
        name = extract_name()
        job_title = extract_job_title()
        if isSoftwareProfessional(job_title):
            skills = extract_skills(profile) #MAKE SURE TO CLEAN DATA
            # make all elements of skills unique
            skills = list(set(skills)) # remove duplicates

            profile_data = {
                "name": name,
                "job_title": job_title,
                "skills": skills
            }

            add_to_json("software_professionals.json", profile_data) #add to software professionals JSON
        
        elif isAccessibilityProfessional(job_title):
            skills = extract_skills(profile) #MAKE SURE TO CLEAN DATA
            profile_data = {
                "name": name,
                "job_title": job_title,
                "skills": skills
            }
            add_to_json("accessibility_professionals.json", profile_data) #add to accessibility professionals JSON
        
        else:
            continue
    '''
        
if __name__ == "__main__":
    login()
    get_new_accessibility_profiles()
    ''' # TESTING WITH HARDCODED PROFILES
    listOfProfileURLS = [
        "https://www.linkedin.com/in/adam-elsayed-9b0162245/", # swe profile
        "https://www.linkedin.com/in/adam-elsayed-5a7781357/", # profile with no headline
        "https://www.linkedin.com/in/jorge-d-robles/", # swe profile
        "https://www.linkedin.com/in/amywolfemls/", # accessibility profile
        "https://www.linkedin.com/in/john-w-moyler-29549014/" # neither swe or accessibility profile
    ]
    login()
    for profile in listOfProfileURLS:
        open_profile_and_scroll(profile)
        name = extract_name()
        job_title = extract_job_title()
        # CHECK IF ACCESSIBILITY PROFESSIONAL FIRST => THEN SOFTWARRE PROFESSIONAL
        if isSoftwareProfessional(job_title):
            print(f"{name} is a software professional with job title: {job_title}")
            skills = extract_skills(profile)
            skills = list(set(skills)) # remove duplicates
            print(f"Skills: {skills}")
            profile_data = {
                "name": name,
                "job_title": job_title,
                "skills": skills
            }
            add_to_json("software_professionals.json", profile_data) #add to software professionals JSON
        elif isAccessibilityProfessional(job_title):
            print(f"{name} is an accessibility professional with job title: {job_title}")
            skills = extract_skills(profile)
            print(f"Skills: {skills}")
            profile_data = {
                "name": name,
                "job_title": job_title,
                "skills": skills
            }
            add_to_json("accessibility_professionals.json", profile_data) #add to accessibility professionals JSON
    '''
    # tmrw let's write up the getting software professionals bit, and get all accessibility urls (scroll for 30 mins), get all software urls



