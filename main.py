from selenium import webdriver
import undetected_chromedriver as uc
import requests

#driver = uc.Chrome()

with open("valid_proxies.txt", "r") as f:
    proxies = f.read().split("\n")
        
        
sites_to_check = ["https://books.toscrape.com/",
         "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
         "https://books.toscrape.com/catalogue/category/books/romance_8/index.html"]

counter = 0

for site in sites_to_check:
    try:
        print(f"Using {proxies[counter]}")

        res = requests.get(site, proxies={"http": proxies[counter],
                                        "https": proxies[counter]})
        
        print(res.status_code)
        print(res.text)

    except:
        print("failed")

    finally:
        counter+=1