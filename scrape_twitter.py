from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
import uuid
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb+srv://guganclg:Mx4FD6BGybN63JkB@cluster0.5dxve.mongodb.net/test?retryWrites=true&w=majority"
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["twitter_scraper"]
collection = db["trending_topics"]

TWITTER_USERNAME = '@hs1067'
TWITTER_PASSWORD = 'Gugan2004$'

def scrape_twitter():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Opening Twitter login page...")
        driver.get("https://twitter.com/login")
        wait = WebDriverWait(driver, 20)

        #  Log in to Twitter
        try:
            print("Attempting to log in...")
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            username_field.send_keys(TWITTER_USERNAME)
            username_field.send_keys(Keys.RETURN)

            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(TWITTER_PASSWORD)
            password_field.send_keys(Keys.RETURN)
            print("Logged in successfully.")
        except Exception as login_error:
            print(f"Error during login: {login_error}")
            raise Exception("Failed to log in to Twitter. Check credentials or page structure.")

        #  Wait for trending topics to load
        try:
            print("Waiting for trending topics to load...")
            trending_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//span[@dir='ltr']")
                )
            )
            
            print("Trending topics loaded.")

            # Extract only the top 5 trending topics
            trends = [
                element.text.strip()
                for element in trending_elements[:5]
                if element.text.strip()
            ]
            print(f"Extracted trends: {trends}")
        except Exception as wait_error:
            print(f"Error while waiting for trending topics: {wait_error}")
            print("Page source for debugging:")
            print(driver.page_source)
            raise Exception("Failed to load trending topics. Check page structure or increase wait time.")

        #  Save results to MongoDB
        try:
            unique_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now()
            record = {
                "_id": unique_id,
                "trends": trends,
                "timestamp": timestamp.isoformat()
            }
            collection.insert_one(record)
            print("Data saved to MongoDB.")
        except Exception as db_error:
            print(f"Error saving to MongoDB: {db_error}")
            raise Exception("Failed to save data to MongoDB.")

        return record

    except Exception as main_error:
        print(f"Error during scraping: {main_error}")
        raise main_error

    finally:
        driver.quit()
        print("Closed WebDriver.")
