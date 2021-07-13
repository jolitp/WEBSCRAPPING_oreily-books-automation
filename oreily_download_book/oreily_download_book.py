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
DRIVER = None


# login information
EMAIL = "libed17686@advew.com"
PASSWORD = "h3dg3h0g"

book_chapter_links = []


# region setup_driver() ================================================== setup_driver()
def setup_driver():
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_extension("./ext.zip")

    global DRIVER
    DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=CHROME_OPTIONS)
    DRIVER.maximize_window()
    ...
# endregion setup_driver() ----------------------------------------------- setup_driver()


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

    # save_page(url)

    time.sleep(1)
    page_source = DRIVER.page_source

    soup = BeautifulSoup(page_source, "lxml")
    list_of_h5s = soup.find_all("h5")

    links_to_visit = []
    for chapter_tag in list_of_h5s:
        chapter_tag : str = str(chapter_tag)
        soup = BeautifulSoup(chapter_tag, "lxml")
        for element in soup.findAll("a"):
            link = element.get("href")
            full_link = "https://learning.oreilly.com" + link
            links_to_visit.append(full_link)

    # testing for one page first
    link_to_test = links_to_visit[2]

    DRIVER.get(link_to_test)

    set_text_style()

    for link_to_visit in links_to_visit:
        # ic(link_to_visit)
        ...
    ...

# endregion go_to_book_page(...) ---------------------------------- go_to_book_page(...)


# region set_text_style() ========================================= set_text_style()
def set_text_style():
    cog_light_img = "./img/cog_light.png"
    cog_light_pos = pyautogui.locateCenterOnScreen(cog_light_img)
    ic(cog_light_pos)
    pyautogui.click(cog_light_pos)

    time.sleep(.5)

    text_options_large_text_img = "./img/text_options_large_text.png"
    text_options_large_text_pos = pyautogui \
        .locateCenterOnScreen(text_options_large_text_img)
    ic(text_options_large_text_pos)
    pyautogui.click(text_options_large_text_pos)

    time.sleep(.5)

    text_options_small_borders_img = "./img/text_options_small_borders.png"
    text_options_small_borders_pos = pyautogui \
        .locateCenterOnScreen(text_options_small_borders_img)
    ic(text_options_small_borders_pos)
    pyautogui.click(text_options_small_borders_pos)

    time.sleep(.5)

    text_options_dark_mode_img = "./img/text_options_dark_mode.png"
    text_options_dark_mode_pos = pyautogui \
        .locateCenterOnScreen(text_options_dark_mode_img)
    ic(text_options_dark_mode_pos)
    pyautogui.click(text_options_dark_mode_pos)

    time.sleep(.5)

    text_options_close_img = "./img/text_options_close.png"
    text_options_close_pos = pyautogui \
        .locateCenterOnScreen(text_options_close_img)
    ic(text_options_close_pos)
    pyautogui.click(text_options_close_pos)
    ...
# endregion set_text_style() ----------------------------------------- set_text_style()


# region save_page(...) ================================================= save_page(...)
def save_page(url):
    ext_btn_img = "./img/ext_btn.png"
    ext_btn_pos = pyautogui.locateCenterOnScreen(ext_btn_img)
    ic(ext_btn_pos)
    pyautogui.click(ext_btn_pos)

    time.sleep(.5)

    ext_pin_btn_img = "./img/ext_pin_btn.png"
    ext_pin_btn_pos = pyautogui.locateCenterOnScreen(ext_pin_btn_img)
    ic(ext_pin_btn_pos)
    pyautogui.click(ext_pin_btn_pos)

    time.sleep(.5)

    pyautogui.click(ext_btn_pos)

    time.sleep(.5)

    ext_save_btn_img = "./img/ext_save_btn.png"
    ext_save_btn_pos = pyautogui.locateCenterOnScreen(ext_save_btn_img)
    ic(ext_save_btn_pos)
    pyautogui.click(ext_save_btn_pos)

    time.sleep(1)

    ext_continue_save_btn_img = "./img/continue_save_btn.png"
    ext_continue_save_btn_pos = pyautogui.locateCenterOnScreen(ext_continue_save_btn_img)
    ic(ext_continue_save_btn_pos)
    pyautogui.click(ext_continue_save_btn_pos)

    time.sleep(2)

    page_title = DRIVER.title
    ic(page_title)

    book_folder_path = CWD / page_title
    if not os.path.isdir(book_folder_path):
        os.mkdir(book_folder_path)
    saved_file_path = DOWNLOADS_FOLDER_PATH / f"{page_title}.html"
    ic(saved_file_path)

    src = saved_file_path
    index = len(book_chapter_links)
    dst = book_folder_path / f"{index}_{page_title}.html"
    ic(src)
    ic(dst)

    os.rename(src, dst)

    book_chapter_links.append(url)

# endregion save_page(...) ---------------------------------------------- save_page(...)


# region main() ================================================================= main()
def main():
    setup_driver()
    login_oreilly()
    url = "https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
    go_to_book_page(url)
    ...
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    main()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
