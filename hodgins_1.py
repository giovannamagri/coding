from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import csv

webdriver_path = '/path/to/geckodriver'

main_url = "https://hodginshalls.hibid.com/catalog/452895/halls--fine-wine-and-spirits?ipp=250"

wines = []
seen_urls = set()


firefox_options = Options()
driver = webdriver.Firefox(service=Service(executable_path=webdriver_path), options=firefox_options)

try:
    driver.get(main_url)
    time.sleep(2)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    auction_date_element = soup.find("div", class_="col").find_all("p")[0].text
    auction_date = auction_date_element.replace("Data", "").replace("\n", "").replace("\t", "")

    anchors = soup.find_all('a', href=True)
    urls_to_scrape = [anchor['href'] for anchor in anchors if anchor['href'].startswith("/lot/")]

    for url in urls_to_scrape:
        full_url = "https://hodginshalls.hibid.com" + url

        if full_url in seen_urls:
            continue  # Skip processing if URL has been seen before
        seen_urls.add(full_url)
        
        # Open the secondary URL 
        driver.get(full_url)
        time.sleep(5)
        page_source = driver.page_source
        
        wine_soup = BeautifulSoup(page_source, 'html.parser')
        
        content = wine_soup.find_all("tr", class_="row ng-star-inserted")
        wine_lot = content[0].text.replace("Lotto", "").replace("\n", "").replace("\t", "")
        
        
        wine_content = content[1].text
        if "Quantità" in wine_content:
            wine_quantity = wine_content.replace("x", "").replace("Quantità", "").replace("\n", "").replace("\t", "")
            price_estimate = content[2].text.replace("\n", "").replace("\t", "").replace("Stima", "")
        elif "Stima" in wine_content:
            wine_quantity = "1"
            price_estimate = wine_content.replace("\n", "").replace("\t", "").replace("Stima", "")
        else:
            wine_quantity = "N/A"
            price_estimate = "N/A"
        wine_name = wine_soup.find("div", class_="text-pre-line").text.replace("\n", "").replace("\t", "")
        wine_price = wine_soup.find("span", class_="lot-price-realized").text
        


        # Append data to the wines list
        wines.append({
            "Auction Date": auction_date,
            "Wine Lot": wine_lot,
            "Wine Name": wine_name,
            "Quantity": wine_quantity,
            "Price Estimate": price_estimate,
            "Price": wine_price
        })

    filename = "hodgins.csv"
    fieldnames = ["Auction Date", "Wine Lot", "Wine Name", "Quantity", "Price Estimate", "Price"]
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)  
        
        writer.writerows(wines)
    print("Data saved to", filename)

finally:
    driver.quit()
