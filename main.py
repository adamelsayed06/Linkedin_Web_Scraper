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
import re
import json

load_dotenv()

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
    driver.get(profile_url) # opens your profile
    time.sleep(5) # wait for page to load 5s
    
    #scrolls to the bottom of the page
    start = time.time()
    while time.time() - start < 5: #scrolls for 5 seconds
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

'''
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
'''

#returns lists of new profiles to loop through, update class name
def get_new_accessibility_profiles(count):
    '''
    Have group URL of accessibility professionals, scroll through page and look for see more results button, if there click it
    and scroll to bottom of page, then extract headlines and profile URLs, from the headline determines if they are accessibility professionals
    and adds URL to list of profiles to return NOT WORKING YET
    '''
    profiles = []
    open_profile_and_scroll("https://www.linkedin.com/groups/4512178/members/")
        
    for _ in range(count):
        source = driver.page_source 
        soup = BeautifulSoup(source, "html.parser")
        
        start = time.time()
        while time.time() - start < 5:  # Scrolls for 5 seconds
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Find and click "See More Results" button if present
        show_more_button = [] # code to find button 
        
        if show_more_button:
            try:
                print("button found")
                show_more_button.click()
                time.sleep(2)  # Wait for new profiles to load
            except Exception as e:
                print(f"Error clicking 'See More Results' button: {e}")
        
        # Find headlines and profile URLs
        headlines = soup.find_all('div', class_=["artdeco-entity-lockup__subtitle", "ember-view"])
        profile_urls = soup.find_all('a', class_=["ember-view", "ui-conditional-link-wrapper", "ui-entity-action-row__link"])
        
        if not headlines or not profile_urls:
            print("No headlines or profile URLs found")
            continue
        
        # Process profiles
        for i in range(len(headlines)):
            headline_text = headlines[i].get_text(strip=True)
            profile_url = profile_urls[i]['href'] if 'href' in profile_urls[i].attrs else None
            
            if profile_url and isAccessibilityProfessional(headline_text):
                if profile_url not in profiles:  # Avoid duplicates
                    profiles.append(profile_url)  # Ensure only strings are added
    
    return profiles

def get_new_software_profiles(count):
    pass
#tested, and working
def isSoftwareProfessional(job_title):
    
    software_professional_titles = [
        "Web Developer", "UX Designer", "UI Designer", 
        "Software Engineer", "Software Developer", 
        "Front End Developer", "Backend Developer", 
        "Full Stack Developer", "Mobile App Developer", 
        "DevOps Engineer", "Data Scientist", 
        "Machine Learning Engineer", "Cloud Engineer", "Data Engineer",
        "Software Architect", "SWE", "SDE", "ML Engineer"
    ]
    
    return job_title in software_professional_titles

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
    ROOT_URL = "" #PLACEHOLDER
    login()
    open_profile_and_scroll(ROOT_URL)
    for profile in profiles:
        open_profile_and_scroll(profile)
        name = extract_name()
        job_title = extract_job_title()
        if isSoftwareProfessional(job_title):
            skills = extract_skills(profile) #MAKE SURE TO CLEAN DATA

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
        
if __name__ == "__main__":
    login()
    print(get_new_accessibility_profiles(3))
    '''
    login()
    ROOT_URL = "https://www.linkedin.com/in/adam-elsayed-9b0162245/"  # Replace with your LinkedIn profile URL
    open_profile_and_scroll(ROOT_URL)
    profiles = get_new_profiles(10)
    for profile in profiles:
        print(profile)
        open_profile_and_scroll(profile)
        name = extract_name()
        print(name)
    '''
'''
main flow:
1. login to linkedin --  login()
2. get list of profiles -- get_new_accessibility_profiles, get_new_software_profiles => at this point we know they are accessibility/software professionals from the headline.
3. open each profile, extract name, job title, and skills
4. put into JSON
3. open each new profile and extract analytics
5. Based on titles they are either accessibility or software professionals, so categorize:  
Web Developer, UX Designer, UI Designer, Software Engineer, Software Developer, Front End Developer, UIUX Accessibility, Software Accessibility, and Accessibility Tester
6. Extract skills from profile
7. Add skills to JSON
8. Compare to ACCESSIBILITY_KEYWORDS

TODO: test getting new profiles, 
'''



