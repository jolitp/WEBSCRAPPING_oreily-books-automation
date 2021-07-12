#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui

from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from icecream import ic


# setup driver
chromedriver_path = Path("/home/jolitp/Applications/chromedriver")
driver = webdriver.Chrome(chromedriver_path)
driver.maximize_window()

# login information
EMAIL = "libed17686@advew.com"
PASSWORD = "h3dg3h0g"

# def login_oreilly():

#     ...

# def main():

# 	...

# if __name__ == '__main__':
#     main()

# open site
# driver.get("https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/")
driver.get("https://learning.oreilly.com/")
# get email filed element and insert email
email_field = driver.find_element_by_xpath("//input[@name='email']")
email_field.clear()
email_field.send_keys(EMAIL)
time.sleep(.1)

# get password field element and insert password
password_field = driver.find_element_by_xpath("//input[@name='password']")
password_field.clear()
password_field.send_keys(PASSWORD)
time.sleep(.3)
password_field.send_keys(Keys.ENTER)







time.sleep(3)
driver.get("https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/")












