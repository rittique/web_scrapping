from TikTokApi import TikTokApi
from playwright.sync_api import sync_playwright
import json
import asyncio
import os
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

# Step 1: Load JSON files and parse proxy information
def load_proxies_from_json(directory):
    proxies = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = Path(directory) / file_name
            with open(file_path, 'r') as file:
                try:
                    # Load JSON data
                    data = json.load(file)
                    # Access the proxies array within the JSON structure
                    if 'proxies' in data:
                        proxies.extend(data['proxies'])
                except json.JSONDecodeError as e:
                    print(f"Error loading {file_name}: {e}")
    return proxies

# Step 2: Filter the proxies
def filter_proxies(proxies, max_timeout=500, required_anonymity="elite"):
    filtered_proxies = []
    for proxy in proxies:
        # Extract fields from the nested structure
        ip_data = proxy.get('ip_data', {})
        # Check for anonymity, if proxy is alive, and if the average timeout is below threshold
        if proxy['alive'] and proxy['average_timeout'] <= max_timeout and proxy['anonymity'] == required_anonymity:
            filtered_proxies.append({
                "ip": ip_data.get('countryCode', 'unknown'),  # IP Address from ip_data
                "port": proxy.get('port', 'unknown'),  # Port is assumed to be part of the proxy object
                "protocols": proxy.get('protocols', ['http']),  # Default to HTTP if protocols aren't listed
                "anonymity": proxy['anonymity'],
                "country": ip_data.get('country', 'unknown'),  # Country from ip_data
                "isp": ip_data.get('isp', 'unknown'),  # ISP from ip_data
                "average_timeout": proxy['average_timeout']  # Include the average timeout for performance
            })
    return filtered_proxies

# Step 3: Select a random proxy from the list
def get_random_proxy(filtered_proxies):
    proxy_data = random.choice(filtered_proxies)

    # Extract the first protocol (you can adapt this if multiple protocols are used)
    protocol = proxy_data.get('protocols', ['http'])[0]  # Default to 'http' if no protocol is specified
    
    # Check if the protocol is supported
    if protocol not in ['http', 'https', 'socks5']:
        print(f"Skipping unsupported protocol: {protocol}")
        return None

    # Return formatted proxy information
    return {
        "server": f"{protocol}://{proxy_data['ip']}:{proxy_data['port']}",
        "username": "",  # Set if proxy requires authentication
        "password": ""   # Set if proxy requires authentication
    }

# Step 4: Use the proxy in Playwright
def get_ms_token_with_proxy(proxy):
    with sync_playwright() as p:
        try:
            # Launch browser with the selected proxy
            browser = p.chromium.launch(proxy={
                "server": proxy["server"],
                "username": proxy.get("username", ""),
                "password": proxy.get("password", "")
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
            print(f"Error occurred while using proxy {proxy['server']}: {e}")
            return None    

async def trending_videos():
    api = TikTokApi()  # Instantiate the TikTokApi object
    await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
    
    async for video in api.trending.videos(count=30):
        print(video)
        print(video.as_dict)

async def get_hashtag_videos(name):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        tag = api.hashtag(name=name)
        async for video in tag.videos(count=30):
            print(video)
            print(video.as_dict)

async def user_example():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user("therock")
        user_data = await user.info()
        print(user_data)

        async for video in user.videos(count=30):
            print(video)
            print(video.as_dict)

        async for playlist in user.playlists():
            print(playlist)

# Main Execution
if __name__ == "__main__":
    # Specify the directory where your JSON files are located
    json_directory = "./tiktokAnalytics/"

    # Load all proxies from JSON files
    proxies = load_proxies_from_json(json_directory)

    # Check if proxies are available
    if proxies:
        # Get a random proxy
        proxy = get_random_proxy(proxies)

        # Use the proxy to get the ms_token
        ms_token = get_ms_token_with_proxy(proxy)
        print("Final ms_token:", ms_token)
    else:
        print("No proxies found in the specified directory.")

    asyncio.run(user_example())

"""
def get_ms_token():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set headless=True for no browser UI
        context = browser.new_context()

        # Open a new page
        page = context.new_page()

        # Go to TikTok website (login may be required)
        page.goto("https://www.tiktok.com")

        # Wait for page to load, adjust wait time as necessary
        page.wait_for_timeout(5000)

        # Get the ms_token from cookies or local storage
        # For cookies
        cookies = context.cookies()
        for cookie in cookies:
            if cookie['name'] == 'msToken':
                ms_token = cookie['value']
                print("ms_token:", ms_token)
                return ms_token

        # Alternatively, check local storage
        ms_token = page.evaluate("localStorage.getItem('msToken')")
        print("ms_token:", ms_token)
        
        # Close the browser
        browser.close()
"""
    


    
