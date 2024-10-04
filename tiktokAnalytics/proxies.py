import requests
from concurrent.futures import ThreadPoolExecutor
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sqlite3
import time

# Function to fetch the proxy list from GitHub
def fetch_proxies_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        proxies = response.text.splitlines()
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch proxies: {e}")
        return []

# Function to test if a single proxy works
def check_proxy(proxy):
    test_urls = [
        'https://httpbin.org/ip',
        'https://api.ipify.org',
        'https://www.google.com',
        'https://www.example.com'
    ]
    
    for test_url in test_urls:
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(test_url, proxies=proxies, timeout=5)

            if response.status_code == 200:
                return True  # Return True if the proxy works
        except requests.exceptions.RequestException:
            return False  # Return False if there's an error

    return False  # Return False if no test URL was successful

# Function to check proxies concurrently and return working proxies
def check_proxies_concurrently(proxies, max_workers=10):
    working_proxies = []  # List to hold working proxies
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_proxy, proxies))
    
    # Filter proxies based on results
    for proxy, result in zip(proxies, results):
        if result:
            working_proxies.append(proxy)
    
    return working_proxies

# Function to save working proxies to SQLite database
def save_proxies_to_db(proxies, db_name='proxies.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS working_proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proxy TEXT NOT NULL
    )
    ''')
    
    # Insert proxies into the table
    for proxy in proxies:
        cursor.execute('INSERT INTO working_proxies (proxy) VALUES (?)', (proxy,))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(proxies)} working proxies to the database.")

def fetch_proxies_from_db(db_name='proxies.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT proxy FROM working_proxies')
    proxies = cursor.fetchall()
    conn.close()
    return [proxy[0] for proxy in proxies]


if __name__ == "__main__":
    # GitHub URL where the proxy list is located
    url = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
    
    # Fetch proxies from the GitHub URL
    proxies = fetch_proxies_from_github(url)
    
    # Check proxies if we successfully fetched them
    if proxies:
        working_proxies = check_proxies_concurrently(proxies)
        print("\nWorking Proxies:")
        for proxy in working_proxies:
            print(proxy)

        # Save working proxies to the database
        save_proxies_to_db(working_proxies)
        print("Proxies Saved to Database.")

    else:
        print("No proxies to check.")
