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


options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

driver.get("https://etenders.gov.in/eprocure/app;jsessionid=27BC7A64F887FDF6F74CA97EE7DFE34A.geps1?page=FrontEndTendersByLocation&service=page")



try:
    with open('E:\Automated_web\captchaimg\mycapthca.png', 'wb') as file:
        file.write(driver.find_element(By.XPATH,"//img[@id='captchaImage']").screenshot_as_png)

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    code = pytesseract.image_to_string(r'E:\Automated_web\captchaimg\mycapthca.png')
    res = ''.join(ch for ch in code if ch.isalnum())
    print (res)


    inputElement = driver.find_element(By.NAME,"Location")
    inputElement.send_keys('Surat')


    inputElement = driver.find_element(By.NAME,"captchaText")
    inputElement.send_keys(res)

    folder = driver.find_element(By.XPATH,"//input[@id='submit']")
    folder.click()

except:
    print("not good")