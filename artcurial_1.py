import re
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import json
import time
import csv

#this code: uses selenium to get inside the dinamically loaded website, does the login procedure automatically, gets the json data and extract the info needed from there. Finally, prints everything in a csv file. 
driver = webdriver.Firefox()

# Define the cookies and accept
cookies = [
    {
        'name': 'oas-node-sid',
        'value': 's%3A9lzOSanys3Is0qzJqRjUcj-uRrrHQ1kM.l2%2BDCzSCrfBsqNiMCgfccrrcv88ycwwMOycyZEsPxxY',
        
    },
]

driver.add_cookie

driver.get("https://www.invaluable.com/catalog/8l4o2m9915?page=1&size=540")
cookies = driver.get_cookies()

accept_cookies_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonAccept")
accept_cookies_button.click()

# do the login automatically 
login_button = driver.find_element(By.CSS_SELECTOR, "button.emailOnlyLogin")
login_button.click()
time.sleep(3)

email_input = driver.find_element(By.ID, "emailLoginModal")
email_input.send_keys("gertjan@verdickt.eu")

password_input = driver.find_element(By.ID, "passwordLoginModal")
password_input.send_keys("7d_kgkFs6R6DGDk")

login_submit_button = driver.find_element(By.ID, "loginBtn")
login_submit_button.click()
time.sleep(5)

page_source = driver.page_source
driver.quit()

# find json data in page source
json_text = page_source.split("window.__APP_INITIAL_STATE__ = ")[1].split(" window.__isShowV2Page__")[0].strip()
json_pattern = json.loads(json_text)

wine_lots = []
wine_names = []
wine_prices = []
price_estimates = []
auction_dates = []
lot_references = []
super_category_names = []
object_ids = []


# Create a CSV file
with open('artcurial_invaluable.csv', mode='a', newline='') as csv_file:
    fieldnames = ['Auction Date', 'Lot', 'Lot Reference', 'Name', 'Super Category Name', 'Object ID', 'Price (HKD)', 'Estimate (Low-High HKD)']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    for result in json_pattern['resultsState']['rawResults']:
        for hit in result['hits']:
            lot_number = hit['lotNumber']
            lot_title = hit['lotTitle']
            price_result = hit['priceResult']
            estimate_low = hit['estimateLow']
            estimate_high = hit['estimateHigh']
            auction_date = hit['dateTimeLocal']
            lot_reference = hit['lotRef']
            super_category_name = hit['supercategoryName']
            object_id = hit['objectID']

            writer.writerow({
                'Lot': lot_number,
                'Name': lot_title,
                'Price (HKD)': f'{price_result} HKD',
                'Estimate (Low-High HKD)': f'{estimate_low}-{estimate_high} HKD',
                'Auction Date': auction_date,
                'Lot Reference': lot_reference,
                'Super Category Name': super_category_name,
                'Object ID': object_id
            })
