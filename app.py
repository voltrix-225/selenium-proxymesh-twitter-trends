from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import uuid
import time
import os

# Load environment variables
load_dotenv()

# Set up Flask
app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['twitter_trends']
collection = db['trends']

# ProxyMesh setup
PROXY_URL = os.getenv('PROXY_URL')
PROXY_CREDENTIALS = os.getenv('PROXY_CREDENTIALS')

# Selenium setup
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument(f'--proxy-server={PROXY_URL}')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def fetch_trending_topics():
    service = Service('./chromedriver/chromedriver')  # Replace with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Log in to Twitter
        driver.get('https://twitter.com/login')
        time.sleep(10)

        username = driver.find_element(By.NAME, 'session[username_or_email]')
        password = driver.find_element(By.NAME, 'session[password]')

        username.send_keys(os.getenv('TWITTER_USERNAME'))
        password.send_keys(os.getenv('TWITTER_PASSWORD'))
        password.send_keys(Keys.RETURN)

        time.sleep(10)

        # Fetch trends from "What's Happening"
        trends_section = driver.find_element(By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]")
        trends = trends_section.find_elements(By.XPATH, ".//span[contains(@class, 'css-')]")[:5]
        trending_topics = [trend.text for trend in trends if trend.text]

        # Get current IP address from the proxy
        driver.get('https://api.ipify.org')
        current_ip = driver.find_element(By.TAG_NAME, 'body').text

        # Store data in MongoDB
        record = {
            "_id": str(uuid.uuid4()),
            "trend1": trending_topics[0] if len(trending_topics) > 0 else "",
            "trend2": trending_topics[1] if len(trending_topics) > 1 else "",
            "trend3": trending_topics[2] if len(trending_topics) > 2 else "",
            "trend4": trending_topics[3] if len(trending_topics) > 3 else "",
            "trend5": trending_topics[4] if len(trending_topics) > 4 else "",
            "timestamp": datetime.datetime.now().isoformat(),
            "ip_address": current_ip
        }
        collection.insert_one(record)

        return record
    finally:
        driver.quit()
        os.remove('System32')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = fetch_trending_topics()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
