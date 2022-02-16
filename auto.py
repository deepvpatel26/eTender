from pandas import options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from PIL import Image, ImageFilter
import pytesseract
import requests
import lxml.html as lh
import base64
import pandas as pd
from soaplib.core.service import soap
from selenium.webdriver.common.by import By
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\deepv\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\local-packages\Python38\site-packages\pytesseract"


website_link = "https://etenders.gov.in/eprocure/app"

options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
driver.get(website_link)
# driver.get("https://etenders.gov.in/eprocure/app;jsessionid=6B8CE0299858583680A01B01549035CF.geps1?page=FrontEndTendersByLocation&service=page")


    
folder = driver.find_element_by_xpath("//a[@title='Tenders by Location']")
folder.click()


inputElement = driver.find_element_by_name("Location")
inputElement.send_keys('Surat')


with open('E:\Automated_web\captchaimg\mycapthca.png', 'wb') as file:
    file.write(driver.find_element_by_xpath("//img[@id='captchaImage']").screenshot_as_png)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
code = pytesseract.image_to_string(r'E:\Automated_web\captchaimg\mycapthca.png')
res = ''.join(ch for ch in code if ch.isalnum())



inputElement = driver.find_element_by_name("captchaText")
inputElement.send_keys(res)



folder = driver.find_element_by_xpath("//input[@id='submit']")
folder.click()






table = soap.find_all('table')[0] 
df = pd.read_html(str(table))
print( tabulate(df[0], headers='keys', tablefmt='psql') )





