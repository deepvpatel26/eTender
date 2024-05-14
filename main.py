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
# import google.cloud
# from firebase_admin import credentials, firestore
#Initialize Firebase

firebaseConfig = {
  "apiKey": "AIzaSyBca_j5rUCse7lyr-ydlSWt2UUIMFNJjqc",
  "authDomain": "app-tender.firebaseapp.com",
  "databaseURL": "https://app-tender-default-rtdb.firebaseio.com",
  "projectId": "app-tender",
  "storageBucket": "app-tender.appspot.com",
  "messagingSenderId": "261067565740",
  "appId": "1:261067565740:web:df9bd5499dba4e1eb44d09",
  "measurementId": "G-PWS7B0ER1D"
};
firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()


def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

driver.get("https://etenders.gov.in/eprocure/app;jsessionid=27BC7A64F887FDF6F74CA97EE7DFE34A.geps1?page=FrontEndTendersByLocation&service=page")


city = 'Mumbai' # declare your city 

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
res = ''
eleSelected = False

while res == '' or str(eleSelected) == "True":
    with open('mycapthca.png', 'wb') as file:
        file.write(driver.find_element(By.XPATH,"//img[@id='captchaImage']").screenshot_as_png)

    inputElement = driver.find_element(By.NAME,"Location")
    inputElement.send_keys(city)
    code = pytesseract.image_to_string(r'mycapthca.png')
    res = ''.join(ch for ch in code if ch.isalnum())
    inputElement = driver.find_element(By.NAME,"captchaText")
    inputElement.send_keys(res)
    
    if res != '':
        folder = driver.find_element(By.XPATH,"//input[@id='submit']")
        folder.click()
        eleSelected= check_exists_by_xpath("//*[@id='content']/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr/td/span/b")
        if str(eleSelected) == "True":
            
            driver.get("https://etenders.gov.in/eprocure/app;jsessionid=27BC7A64F887FDF6F74CA97EE7DFE34A.geps1?page=FrontEndTendersByLocation&service=page")
            continue
        break
    else:
        driver.get("https://etenders.gov.in/eprocure/app;jsessionid=27BC7A64F887FDF6F74CA97EE7DFE34A.geps1?page=FrontEndTendersByLocation&service=page")
  

# rows = driver.find_elements_by_xpath("//*[@class='list_table']/tbody/tr")
rows = driver.find_elements(by=By.XPATH, value="//*[@class='list_table']/tbody/tr")
# continue_link = driver.find_element_by_tag_name('a')
continue_link = driver.find_element(by=By.TAG_NAME, value='a')
elem = driver.find_elements(by=By.XPATH, value="//*[@href]")
# elem = driver.find_elements_by_xpath("//*[@href]")
#x = str(continue_link)
#print(continue_link)
list =[]

for i in range(0,len(rows)):
    list.append(elem)

arr = []
for index in range(0,len(rows)):
    # str = str(index     
    l=driver.find_elements(By.XPATH,"//*[@class='list_table']/tbody/tr["+str(index)+"]/td")
    for i in l:
        arr.append(i.text)

np_arr = np.array(arr)

# arr = []
# for index in range(0,len(rows)):
#     # str = str(index     
#     l=driver.find_elements(By.XPATH,"//*[@class='list_table']/tbody/tr["+str(index)+"]/td")
#     for i in l:
#         arr.append(i.text)

np_arr = np.array(arr)
np_arr = np_arr.reshape(len(rows)-1,6)
df = pd.DataFrame(np_arr)

np_arr = np.array(arr)
np_arr = np_arr.reshape(len(rows)-1,6)

df = pd.DataFrame(np_arr)
df = df.rename(columns=df.iloc[0])
df = df.drop(df.index[0])

df.rename(columns = {'e-Published Date':'e Published Date',
                     'Title and Ref.No./Tender ID':'Title and Ref No TenderID',
                     }, inplace = True)

df["Tender_ID"] = None


for j in range(1, df.shape[0]+1):
    t = ""
    i=2
    l = len(df["Title and Ref No TenderID"][j])
    while df["Title and Ref No TenderID"][j][l-i] != "[":
        t = df["Title and Ref No TenderID"][j][l-i] + t
        i = i + 1
        df["Tender_ID"][j] = t

html1 = driver.page_source
k=0
for i in range(1,df.shape[0]+1):
  if i == 1:
    s = ""
    l = html1.find("DirectLink_0") + 52
    while html1[l] != ">" :
        s = s + html1[l] 
        l = l + 1
  else:
    path = "DirectLink_0" + "_" + str(k)   
    s = ""
    l = html1.find(path) + 54
    while html1[l] != ">" :
        s = s + html1[l] 
        l = l + 1
    k = k + 1


  s = "https://etenders.gov.in" + s
  s = s.replace("amp;","")
  s = s[:-1]
  
  print(df['e Published Date'][i])
  data={"e Published Date":df['e Published Date'][i],
        "Closing Date":df['Closing Date'][i], 
        "Opening Date":df['Opening Date'][i],
        "Title and Ref No TenderID": df['Title and Ref No TenderID'][i],
        "Organisation Chain":df['Organisation Chain'][i],
        "DirectLink":s,
        "TenderId":df["Tender_ID"][i]}
  # print(db.child("e-procure-"+city).push(data)) #unique key is generated

  #create a table in mongo db


# Connect to MongoDB server
client = MongoClient('mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/')
# mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/
# Select database
db = client['Etender']  # Replace 'your_database_name' with your actual database name
# Create a new collection (table)
collection = db['E_tender_Mumbai']  # Replace 'your_collection_name' with your desired collection name

# Convert DataFrame records to dictionary format
records = df.to_dict(orient='records')

# Insert records into the collection
collection.insert_many(records)

