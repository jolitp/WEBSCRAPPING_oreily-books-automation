#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui

from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from icecream import ic


# setup driver
CHROME_DRIVER_PATH = Path("/home/jolitp/Applications/chromedriver")
DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH)
DRIVER.maximize_window()

# login information
EMAIL = "libed17686@advew.com"
PASSWORD = "h3dg3h0g"

def login_oreilly():
    # open site
    DRIVER.get("https://learning.oreilly.com/")
    # get email filed element and insert email
    email_field = DRIVER.find_element_by_xpath("//input[@name='email']")
    email_field.clear()
    email_field.send_keys(EMAIL)
    time.sleep(.1)

    # get password field element and insert password
    password_field = DRIVER.find_element_by_xpath("//input[@name='password']")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # wait for sign in button to be clickable
    time.sleep(.3)
    password_field.send_keys(Keys.ENTER)

def go_to_book_page(url: str):
    time.sleep(3)
    DRIVER.get(url)
    ...

def main():
    login_oreilly()
    url = "https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
    go_to_book_page(url)
    ...

if __name__ == '__main__':
    main()
















