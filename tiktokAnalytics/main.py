import requests
from concurrent.futures import ThreadPoolExecutor
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
from proxies import fetch_proxies_from_db
from TikTokApi import TikTokApi
from playwright.sync_api import sync_playwright
import json
import asyncio
import os
import random
from pathlib import Path
from playwright.sync_api import sync_playwright
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc

def init_driver_with_proxy(proxy):
    # Set up Chrome options
    chrome_options = Options()

    # Configure proxy for Chrome
    proxy_obj = Proxy()
    proxy_obj.proxy_type = ProxyType.MANUAL
    proxy_obj.http_proxy = proxy
    proxy_obj.ssl_proxy = proxy
    chrome_options.proxy = proxy_obj

    # Initialize undetected_chromedriver without using 'executable_path'
    service = Service("/System/Volumes/Data/Users/rittique/.cache/selenium/chromedriver/mac-arm64/129.0.6668.70/chromedriver")
    driver = uc.Chrome(service=service, options=chrome_options)

    # Visit google.com
    driver.get('https://www.google.com')

    return driver

# Function to get ms_token from TikTok using a working proxy
def get_ms_token(working_proxies):
    if not working_proxies:
        print("No working proxies available.")
        return None
    
    # Choose a random proxy from the working list
    proxy = random.choice(working_proxies)
    print(f"Using proxy: {proxy}")
    
    # Set up Selenium with the selected proxy
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    chrome_options.add_argument('--headless')  # Run in headless mode for no GUI
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service("/System/Volumes/Data/Users/rittique/.cache/selenium/chromedriver/mac-arm64/129.0.6668.70/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to TikTok
        driver.get("https://www.tiktok.com")
        
        # Wait for the page to load
        time.sleep(5)  # Adjust as necessary for your connection speed

        # Retrieve the cookies
        cookies = driver.get_cookies()

        # Extract the ms_token from the cookies
        for cookie in cookies:
            if cookie['name'] == 'msToken':
                print(f"ms_token found: {cookie['value']}")
                return cookie['value']
    
    except Exception as e:
        print(f"Error while trying to retrieve ms_token: {e}")
    
    finally:
        # Quit the browser
        driver.quit()
    
    return None

def get_ms_token_with_proxy(proxies):
    if not proxies:
        print("No working proxies available.")
        return None
    
    # Choose a random proxy from the working list
    proxy = random.choice(proxies)
    print(f"Using proxy: {proxy}")
    with sync_playwright() as p:
        try:
            # Launch browser with the selected proxy
            browser = p.chromium.launch(proxy={
                "server": proxy
            }, headless=True)  # Set headless=True for no browser UI

            # Create a new browser context
            context = browser.new_context()

            # Open a new page and navigate to TikTok
            page = context.new_page()
            page.goto("https://www.tiktok.com")
            
            # Wait for page to load, adjust wait time as necessary
            page.wait_for_timeout(5000)

            # Get the ms_token from cookies or local storage
            cookies = context.cookies()
            ms_token = None
            for cookie in cookies:
                if cookie['name'] == 'msToken':
                    ms_token = cookie['value']
                    print("ms_token:", ms_token)
                    break

            # Close the browser
            browser.close()
            return ms_token

        except Exception as e:
            print(f"Error occurred while using proxy {proxy}: {e}")
            return None

if __name__ == "__main__":
    # Fetch proxies from the GitHub URL
    proxies = fetch_proxies_from_db()
    
    # Check proxies if we successfully fetched them
    if proxies:
        # Get ms_token using a working proxy
        proxy = random.choices(proxies)
        init_driver_with_proxy(proxy)
    else:
        print("No proxies to fetch ms_token.")
