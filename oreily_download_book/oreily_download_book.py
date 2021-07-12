#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml

from pathlib import Path
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import pyautogui
from bs4 import BeautifulSoup
from icecream import ic


# paths
CHROME_DRIVER_PATH = Path("/home/jolitp/Applications/chromedriver")
DOWNLOADS_FOLDER_PATH = Path("/home/jolitp/Downloads/")
CWD = Path(os.getcwd())

# setup driver
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_extension("./ext.zip")
DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=CHROME_OPTIONS)
DRIVER.maximize_window()


# login information
EMAIL = "libed17686@advew.com"
PASSWORD = "h3dg3h0g"


# region login_oreilly() ================================================ login_oreilly()
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
# endregion login_oreilly() --------------------------------------------- login_oreilly()


# region go_to_book_page(...) ===================================== go_to_book_page(...)
def go_to_book_page(url: str):
    time.sleep(3)
    DRIVER.get(url)
    # save_page("./book_main_page.html")

    page_source = DRIVER.page_source

    soup = BeautifulSoup(page_source, "lxml")
    list_of_h5s = soup.find_all("h5")
    for index, chapter_tag in enumerate(list_of_h5s):
        chapter_tag : str = str(chapter_tag)
        soup = BeautifulSoup(chapter_tag, "lxml")
        for element in soup.findAll("a"):
            link = element.get("href")
            full_link = "https://learning.oreilly.com" + link
            title = element.text
            chapter_order = index + 1

            data = {
                "title" : title,
                "link" : full_link,
                "order" : chapter_order
            }

            ic(data)

        ...
    ...
# endregion go_to_book_page(...) ---------------------------------- go_to_book_page(...)


# region save_page(...) ================================================= save_page(...)
def save_page(file_path:Path):
    ext_btn_img = "./ext_btn.png"
    ext_btn_pos = pyautogui.locateCenterOnScreen(ext_btn_img)
    ic(ext_btn_pos)
    pyautogui.click(ext_btn_pos)

    time.sleep(.5)

    ext_pin_btn_img = "./ext_pin_btn.png"
    ext_pin_btn_pos = pyautogui.locateCenterOnScreen(ext_pin_btn_img)
    ic(ext_pin_btn_pos)
    pyautogui.click(ext_pin_btn_pos)

    time.sleep(.5)

    pyautogui.click(ext_btn_pos)

    time.sleep(.5)

    ext_save_btn_img = "./ext_save_btn.png"
    ext_save_btn_pos = pyautogui.locateCenterOnScreen(ext_save_btn_img)
    ic(ext_save_btn_pos)
    pyautogui.click(ext_save_btn_pos)

    time.sleep(1)

    ext_continue_save_btn_img = "./continue_save_btn.png"
    ext_continue_save_btn_pos = pyautogui.locateCenterOnScreen(ext_continue_save_btn_img)
    ic(ext_continue_save_btn_pos)
    pyautogui.click(ext_continue_save_btn_pos)

    time.sleep(2)

    page_title = DRIVER.title
    ic(page_title)

    saved_file_path = DOWNLOADS_FOLDER_PATH / "{}.html".format(page_title)
    ic(saved_file_path)

    src = saved_file_path
    dst = CWD / "0_{}.html".format(page_title)
    ic(src)
    ic(dst)

    os.rename(src, dst)
    ...
# endregion save_page(...) ---------------------------------------------- save_page(...)


# region main() ================================================================= main()
def main():
    login_oreilly()
    url = "https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
    go_to_book_page(url)
    ...
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    main()
    # test_re()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
