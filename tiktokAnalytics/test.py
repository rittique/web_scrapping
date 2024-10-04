import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from requests.auth import HTTPProxyAuth
import undetected_chromedriver as uc
import time
# List of proxies in the format: IP:PORT:USERNAME:PASSWORD
valid_proxies = [
    '198.23.239.134:6540:hxmlpejz:sa6vhuse1ftb',
    '207.244.217.165:6712:hxmlpejz:sa6vhuse1ftb',
    '107.172.163.27:6543:hxmlpejz:sa6vhuse1ftb',
    '173.211.0.148:6641:hxmlpejz:sa6vhuse1ftb',
    '161.123.152.115:6360:hxmlpejz:sa6vhuse1ftb',
    '216.10.27.159:6837:hxmlpejz:sa6vhuse1ftb',
    '167.160.180.203:6754:hxmlpejz:sa6vhuse1ftb',
    '154.36.110.199:6853:hxmlpejz:sa6vhuse1ftb',
    '45.151.162.198:6600:hxmlpejz:sa6vhuse1ftb',
    '206.41.172.74:6634:hxmlpejz:sa6vhuse1ftb'
]

# Select a random proxy
proxy_str = random.choice(valid_proxies)

# Extract IP, port, username, and password from the proxy string
proxy_ip, proxy_port, proxy_user, proxy_pass = proxy_str.split(":")

### Part 1: Using Selenium with Proxy ###

# Configure Chrome WebDriver options
chrome_options = Options()

# Set the proxy server without credentials in the URL (for Chrome)
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = f"{proxy_ip}:{proxy_port}"
proxy.ssl_proxy = f"{proxy_ip}:{proxy_port}"

# Add the proxy to ChromeOptions
chrome_options.add_argument(f'--proxy-server=http://{proxy_ip}:{proxy_port}')

# Path to your ChromeDriver (ensure it’s correctly installed)
#webdriver_service = Service(executable_path='/path/to/chromedriver')

# Start WebDriver with proxy settings
driver = uc.Chrome(options=chrome_options)

# Handle proxy authentication via HTTP headers using JavaScript
def proxy_authenticate(username, password):
    auth_script = f'''
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "http://ipinfo.io/json", true, "{username}", "{password}");
    xhr.setRequestHeader("Proxy-Authorization", "Basic " + btoa("{username}:{password}"));
    xhr.send();
    '''
    driver.execute_script(auth_script)

# Authenticate the proxy using username and password
proxy_authenticate(proxy_user, proxy_pass)

# Now try visiting a website
try:
    driver.get("http://ipinfo.io/json")  # You can visit any website you want
    time.sleep(10)
    print("Selenium: Visited the website successfully!")
except Exception as e:
    print(f"Selenium: Error occurred: {e}")
finally:
    driver.quit()  # Close the browser


### Part 2: Using requests with Proxy ###

# Prepare the proxy dictionary for requests
proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
}

# Optionally, you can use HTTPProxyAuth for some proxy setups
auth = HTTPProxyAuth(proxy_user, proxy_pass)

# Make a GET request using the proxy
try:
    response = requests.get("http://ipinfo.io/json", proxies=proxies, timeout=10)
    if response.status_code == 200:
        print("Requests: Successfully accessed the website!")
        print(response.json())
    else:
        print(f"Requests: Failed with status code {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Requests: Error occurred: {e}")
