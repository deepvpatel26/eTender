from msilib.schema import Class
from pandas import options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from PIL import Image, ImageFilter
import pytesseract
import base64
import urllib
import pytesseract  
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import pyrebase
import pandas as pd
import csv
import time
from pymongo import MongoClient
from selenium.common.exceptions import NoSuchElementException

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def store_to_mongo_new(df, city):
    city = city.lower()
    # Connect to MongoDB server
    client = MongoClient('mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/')
    # Select database
    db = client['Etender']  # Replace 'your_database_name' with your actual database name
    # Create a new collection (table)
    collection_name = f'E_tender_{city}'
    print(collection_name)
    collection = db[collection_name]
    #check if collection already exists
    if collection_name in db.list_collection_names():
        print(f"Collection {collection_name} already exists.")
    # Get existing Tender IDs from the collection
    existing_tender_ids = set(collection.distinct("Tender_ID"))
    print(existing_tender_ids)
    # Filter DataFrame to exclude existing Tender IDs
    new_records = df[~df['Tender_ID'].isin(existing_tender_ids)]

    if not new_records.empty:
        # Convert new records DataFrame to dictionary format
        new_records_dict = new_records.to_dict(orient='records')
        # Insert new records into the collection
        collection.insert_many(new_records_dict)
        print(f"New records inserted into {collection_name}.")
    else:
        print(f"No new records to insert into {collection_name}.")

def scrape_tender_data(city):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    with webdriver.Chrome(options=options) as driver:
        try:
            driver.get("https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByLocation&service=page")

            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
            res = ''
            eleSelected = False

            while res == '' or str(eleSelected) == "True":
                with open('mycapthca.png', 'wb') as file:
                    file.write(driver.find_element(By.XPATH, "//img[@id='captchaImage']").screenshot_as_png)

                inputElement = driver.find_element(By.NAME, "Location")
                inputElement.send_keys(city)
                code = pytesseract.image_to_string(r'mycapthca.png')
                res = ''.join(ch for ch in code if ch.isalnum())
                inputElement = driver.find_element(By.NAME, "captchaText")
                inputElement.send_keys(res)

                if res != '':
                    folder = driver.find_element(By.XPATH, "//input[@id='submit']")
                    folder.click()
                    eleSelected = check_exists_by_xpath(driver, "//*[@id='content']/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr/td/span/b")
                    if str(eleSelected) == "True":
                        driver.get("https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByLocation&service=page")
                        continue
                    break
                else:
                    driver.get("https://etenders.gov.in/eprocure/app;jsessionid=27BC7A64F887FDF6F74CA97EE7DFE34A.geps1?page=FrontEndTendersByLocation&service=page")

            rows = driver.find_elements(by=By.XPATH, value="//*[@class='list_table']/tbody/tr")
            elem = driver.find_elements(by=By.XPATH, value="//*[@href]")

            arr = []
            for index in range(0, len(rows)):
                l = driver.find_elements(By.XPATH, "//*[@class='list_table']/tbody/tr[" + str(index) + "]/td")
                for i in l:
                    arr.append(i.text)

            np_arr = np.array(arr)
            np_arr = np_arr.reshape(len(rows) - 1, 6)

            df = pd.DataFrame(np_arr)
            df = df.rename(columns=df.iloc[0])
            df = df.drop(df.index[0])
            if 'Title and Ref.No./Tender ID' in df:
                df['Tender_ID'] = df['Title and Ref.No./Tender ID'].str.split('[').str[-1]
                df['Tender_ID'] = df['Tender_ID'].str.replace(']', '')
            return df

        except Exception as e:
            print("An error occurred:", e)
            #return empty dataframe with columns [S.No,e-Published Date,Closing Date,Opening Date,Title and Ref.No./Tender ID,Organisation Chain,Tender_ID]
            return pd.DataFrame(columns=['S.No', 'e-Published Date', 'Closing Date', 'Opening Date', 'Title and Ref.No./Tender ID', 'Organisation Chain', 'Tender_ID'])
# Example usage:
# city = 'Rajkot'
# tender_data = scrape_tender_data(city)