from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os
import json
import re
from webdriver_manager.firefox import GeckoDriverManager
from pymongo import MongoClient

geckodriver_path = '/home/yohannes/Documents/python/geckodriver'
mongodb_uri = 'mongodb://localhost:27017/'
database_name = 'talkwalker_data'

def setup_firefox_service():
    """Set up the Firefox service."""
    if os.path.exists(geckodriver_path):
        return FirefoxService(executable_path=geckodriver_path)
    else:
        return FirefoxService(GeckoDriverManager().install())

def initialize_driver():
    """Initialize the Firefox WebDriver."""
    firefox_service = setup_firefox_service()
    firefox_options = webdriver.FirefoxOptions()
    #firefox_options.add_argument('--headless')  # Run in headless mode
    firefox_options.add_argument("--disable-notifications")
    return webdriver.Firefox(service=firefox_service, options=firefox_options)

def load_cookies(driver, cookies_file):
    """Load cookies from a pickle file and add them to the browser session."""
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print(f"Cookies file {cookies_file} does not exist.")

def scroll_and_collect_divs(driver, scroll_pause_time=3):
    """Scroll down the page to collect all <div> elements with class 'top' until no more new content is loaded."""
    divs_collected = set()  # To store collected divs
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get the initial page height

    while True:  
        divs = driver.find_elements(By.CLASS_NAME, 'top')
        for div in divs:

            post_texts = [span.text.replace('\n', ' ').replace('\r', '').strip() for span in div.find_elements(By.CLASS_NAME, 'tw-entry-text')]
            
            dates = [span.text.replace('\n', ' ').replace('\r', '').strip() for span in div.find_elements(By.CLASS_NAME, 'published.clickable')]
            
          
            social_media_info = [span.text.replace('\n', ' ').replace('\r', '').strip() for span in div.find_elements(By.CLASS_NAME, 'metrics.lower-labels')]
            
            
            profile_images = [img.get_attribute('src') for img in div.find_elements(By.CSS_SELECTOR, 'img.avatar.clickable')]
            post_images = [img.get_attribute('src') for img in div.find_elements(By.CSS_SELECTOR, 'img.thumbnail.clickable')]
            
            if profile_images:
                first_image = profile_images[0]
                profile_images = [first_image] + post_images  
            else:
                profile_images = post_images 
            
            links = [a.get_attribute('href') for a in div.find_elements(By.TAG_NAME, 'a')]
            
            div_info = {
                'text': post_texts,
                'dates': dates,
                'social_media_info': social_media_info,
                'links': links,
                'profile_image': profile_images[0] if profile_images else None,
                'post_images': profile_images[1:] if len(profile_images) > 1 else []
            }
            divs_collected.add(json.dumps(div_info))  


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # Check if the page height has changed after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No new content loaded, stopping scrolling.")
            break  

        last_height = new_height  

    return list(divs_collected) 


def login_and_navigate(driver, login_url, cookies_file):
    """Log in and navigate to the desired page."""
    driver.get(login_url)
    time.sleep(5)
    load_cookies(driver, cookies_file)
    driver.refresh()
    time.sleep(10)

import threading

def get_input_with_timeout(prompt, timeout):
    """Get user input with a timeout."""
    user_input = [None]  # Use a list to modify from inner function
    
    def input_thread():
        user_input[0] = input(prompt)

    thread = threading.Thread(target=input_thread)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print("No input received, defaulting to 'All'.")
        return None  
    return user_input[0]

def interact_with_elements(driver, keyword):
    """Interact with various elements on the page."""
    try:
        
        first_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div/div[2]/div[2]/div/div/section/a[1]/div'))
        )
        first_element.click()
        time.sleep(5)

        
        try:
            pop_up_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button:nth-child(2)'))
            )
            pop_up_button.click()
            time.sleep(2)
        except Exception as e:
            print("The pop-up didn't appear or another issue occurred:", e)

        
        comment_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="tw-container"]/div/div/div/div[2]/div[2]/div[1]/div/div/div/form/div/div/div/pre/code'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", comment_input)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="tw-container"]/div/div/div/div[2]/div[2]/div[1]/div/div/div/form/div/div/div/pre/code'))
        )

        
        comment_input.send_keys(keyword)
        time.sleep(0.5)
        comment_input.send_keys(Keys.ENTER)
        print("Keyword has been sent")
        time.sleep(5)

        
        result_type = get_input_with_timeout("Choose a result type:\n1: All\n2: Negative\n3: Neutral\n4: Positive\n", 5)

        if result_type == '2':
            negative_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-sad.css-ien03w-webfont-icon.p-webfont-icon'))
            )
            negative_element.click()
            time.sleep(5)
        elif result_type == '3':
            neutral_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-neutral.css-ien03w-webfont-icon.p-webfont-icon'))
            )
            neutral_element.click()
            time.sleep(5)
        elif result_type == '4':
            positive_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-smile.css-ien03w-webfont-icon.p-webfont-icon'))
            )
            positive_element.click()
            time.sleep(5)
        else:
            
            print("Defaulting to 'All' results.")
            default_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-results-list.css-1t53cig-webfont-icon.p-webfont-icon'))
            )
            default_element.click()
            print("Clicked the default option.")

        new_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-results-list.css-1t53cig-webfont-icon.p-webfont-icon'))
        )
        new_element.click()
        print("Clicked the new element")
    except Exception as e:
        print("An error occurred while interacting with elements:", e)

def click_influencer_icon(driver):
    """Click the influencer icon."""
    try:
        influencer_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-influencer.css-1t53cig-webfont-icon.p-webfont-icon'))
        )
        influencer_icon.click()
        time.sleep(5)
        print("Influencer icon clicked.")
    except Exception as e:
        print("An error occurred while clicking the influencer icon:", e)

def collect_influencer_data(driver):
    """Collect data from each <tr> element with class 'css-1kidomb' and format it."""
    influencer_data = []
    platform_influencers = []
    other_influencers = []
    
    try:
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.css-1kidomb'))
        )
        
        for row in rows:

            columns = [td.text.replace('\n', ' ').replace('\r', '').strip() for td in row.find_elements(By.TAG_NAME, 'td')]
            icon_classes = [i.get_attribute('class') for i in row.find_elements(By.TAG_NAME, 'i')]

            # The structure of columns is as follows:
            # [name, network, posts, reach, engagement]
            if len(columns) >= 5:
                influencer_info = {
                    "person": columns[0],
                    "network": columns[1],
                    "posts": columns[2],
                    "reach": columns[3],
                    "engagement": columns[4] 
                }

                # Check if any <i> element class contains social media platform keywords
                if any(re.search(r'\b(facebook|twitter|instagram|tiktok|youtube)\b', icon_class, re.IGNORECASE) for icon_class in icon_classes):
                    platform_influencers.append(influencer_info)
                else:
                    other_influencers.append(influencer_info)

        # Combine lists, placing platform-related influencers second
        influencer_data.extend(other_influencers)
        influencer_data.extend(platform_influencers)
        
        print(f"Collected {len(influencer_data)} influencer rows.")

    except Exception as e:
        print("An error occurred while collecting influencer data:", e)
    
    return influencer_data

def scrape_gender_data(driver):
    """Scrape gender-related information and return it."""
    genders = {}
    try:

        gender_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.tw3-icon-gender-signs.css-1t53cig-webfont-icon'))
        )
        gender_button.click()
        time.sleep(3)  

       
        male_data_div = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'chart-info.male-chart-info'))
        )
        male_data = male_data_div.text.strip()
        genders['men'] = male_data

        female_data_div = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'chart-info.female-chart-info'))
        )
        female_data = female_data_div.text.strip()
        genders['women'] = female_data

        print("Gender data scraped successfully.")

    except Exception as e:
        print("An error occurred while scraping gender data:", e)

    return genders

def process_divs(driver, collection_name):
    """
    Collect and process each <div> with class 'top' and add influencer and gender data.
    Update data in MongoDB under an existing document.
    """
    divs_data = []  
    try:

        try:
            divs = scroll_and_collect_divs(driver)
            print(f"Found {len(divs)} div(s) with class 'top'")
            # Convert divs content to JSON
            divs_data = [{'index': i + 1, 'content': json.loads(div)} for i, div in enumerate(divs)]
        except Exception as e:
            print(f"Error occurred during div collection: {e}")
            if divs_data:  # If partial data exists, save it
                client = MongoClient(mongodb_uri)
                db = client[database_name]
                collection = db[collection_name]
                collection.update_one(
                    {'_id': 'default_id'}, 
                    {'$set': {'content': divs_data}}, 
                    upsert=True
                )
                print(f"Partial divs data saved to MongoDB collection '{collection_name}'.")
            return

        # Handle pop-ups if they appear
        try:
            pop_up_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button:nth-child(2)'))
            )
            pop_up_button.click()
            time.sleep(2)
            print("Pop-up handled successfully.")
        except Exception as e:
            print("The pop-up didn't appear or another issue occurred:", e)
            
        try:
            pop_up_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.css-1pyyzld-button.p-button'))
            )
            pop_up_button.click()
            time.sleep(2)
            print("Pop-up handled successfully.")
        except Exception as e:
            print("The pop-up didn't appear or another issue occurred:", e)     


        click_influencer_icon(driver)
        influencers = collect_influencer_data(driver)

        gender_data = scrape_gender_data(driver)

        results = {
            'content': divs_data,
            'influencers': influencers,
            'genders': gender_data
        }

        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        collection = db[collection_name]

        collection.update_one(
            {'_id': 'default_id'},
            {
                '$setOnInsert': {
                    'content': [],
                    'influencers': [],
                    'genders': []
                }
            },
            upsert=True
        )

        existing_doc = collection.find_one({'_id': 'default_id'})
        if not isinstance(existing_doc.get('genders', []), list):
            collection.update_one({'_id': 'default_id'}, {'$set': {'genders': []}})
        if not isinstance(existing_doc.get('content', []), list):
            collection.update_one({'_id': 'default_id'}, {'$set': {'content': []}})
        if not isinstance(existing_doc.get('influencers', []), list):
            collection.update_one({'_id': 'default_id'}, {'$set': {'influencers': []}})

        # Append new data to the document
        collection.update_one(
            {'_id': 'default_id'},
            {
                '$push': {
                    'content': {'$each': divs_data if isinstance(divs_data, list) else []},
                    'influencers': {'$each': influencers if isinstance(influencers, list) else []},
                    'genders': {'$each': gender_data if isinstance(gender_data, list) else []}
                }
            }
        )
        print(f"New data appended to MongoDB collection '{collection_name}' with ID 'default_id'.")

    except Exception as e:
        print("An error occurred while processing divs:", e)

def read_keywords_from_file(file_path):
    """Read keywords from a text file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            keywords = [line.strip() for line in file if line.strip()]
        return keywords
    else:
        print(f"Keyword file {file_path} does not exist.")
        return []

if __name__ == "__main__":
    login_url = 'https://app.talkwalker.com/app/login'
    cookies_file = 'talkwalk_cookies.pkl'
    keywords_file = 'keywords.txt'  
    
    keywords = read_keywords_from_file(keywords_file)
    
    driver = initialize_driver()

    try:
        for keyword in keywords:
            print(f"Processing keyword: {keyword}")
            collection_name = keyword 
            
            # Reload cookies and login process
            driver.get(login_url)
            time.sleep(5)
            load_cookies(driver, cookies_file)
            driver.refresh()
            time.sleep(10)  

            interact_with_elements(driver, keyword)
            time.sleep(5)
            process_divs(driver, collection_name) 
            print(f"Completed processing for keyword: {keyword}")
    
    finally:
        driver.quit()
