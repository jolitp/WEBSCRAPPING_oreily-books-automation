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
book_name : str = ""


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


# region get_book_chapter_links() ============================= get_book_chapter_links()
def get_book_chapter_links(page_source) -> list:
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
    return links_to_visit

# endregion get_book_chapter_links() --------------------------- get_book_chapter_links()


# region go_to_book_page(...) ===================================== go_to_book_page(...)
def go_to_book_page(url: str):
    time.sleep(3)
    DRIVER.get(url)

    page_source = DRIVER.page_source
    global book_name
    book_name = DRIVER.title

    links_to_visit = get_book_chapter_links(page_source)

    save_page(url)

    time.sleep(1)

    # testing for one page first
    link_to_test = links_to_visit[2]

    DRIVER.get(link_to_test)

    hide_toc_img = "./img/hide_toc_dark.png"
    hide_toc_pos = pyautogui \
        .locateCenterOnScreen(hide_toc_img)
    # ic(hide_toc_pos)
    if hide_toc_pos:
        pyautogui.click(hide_toc_pos)
    else:
        set_text_style()
        time.sleep(.5)
        hide_toc_img = "./img/hide_toc_dark.png"
        hide_toc_pos = pyautogui \
            .locateCenterOnScreen(hide_toc_img)
        # ic(hide_toc_pos)
        pyautogui.click(hide_toc_pos)

    time.sleep(1)

    save_page(link_to_test)

    for link_to_visit in links_to_visit:
        # ic(link_to_visit)
        ...
    ...

# endregion go_to_book_page(...) ---------------------------------- go_to_book_page(...)


# region set_text_style() ========================================= set_text_style()
def set_text_style():
    # safeguard against downloads panel being in the way
    pyautogui.press('pagedown')

    # press the cog button on the left side of the screen
    cog_xpath = \
"/html/body/div[1]/div/div/div[2]/main/section/div/div/div/section/button/span/span[1]"
    cog_element = DRIVER.find_element_by_xpath(cog_xpath)
    cog_element.click()

    time.sleep(.1)

    large_font_xpath = \
        "/html/body/div[4]/div/div/div/div/form/fieldset[1]/label[3]"
    large_font_element = DRIVER.find_element_by_xpath(large_font_xpath)
    large_font_element.click()

    time.sleep(.1)

    dark_background_xpath = \
        "/html/body/div[4]/div/div/div/div/form/fieldset[2]/div[3]/label"
    dark_background_element = DRIVER.find_element_by_xpath(dark_background_xpath)
    dark_background_element.click()

    time.sleep(.1)

    small_margins_xpath = \
        "/html/body/div[4]/div/div/div/div/form/fieldset[3]/label[3]"
    small_margin_element = DRIVER.find_element_by_xpath(small_margins_xpath)
    small_margin_element.click()

    time.sleep(.5)

    close_btn_xpath = "/html/body/div[4]/div/div/div/button"
    close_btn_element = DRIVER.find_element_by_xpath(close_btn_xpath)
    close_btn_element.click()
    ...
# endregion set_text_style() ----------------------------------------- set_text_style()


# region save_page(...) ================================================= save_page(...)
def save_page(url):
    # get the position of save button
    ext_save_btn_img = "./img/ext_save_btn.png"
    ext_save_btn_pos = pyautogui.locateCenterOnScreen(ext_save_btn_img)
    # ic(ext_save_btn_pos)

    # check if save button has already been pinned to bar
    if not ext_save_btn_pos:
        # open the extensions panel
        ext_btn_img = "./img/ext_btn.png"
        ext_btn_pos = pyautogui.locateCenterOnScreen(ext_btn_img)
        # ic(ext_btn_pos)
        pyautogui.click(ext_btn_pos)

        time.sleep(1)

        # pin the extension
        ext_pin_btn_img = "./img/ext_pin_btn.png"
        ext_pin_btn_pos = pyautogui.locateCenterOnScreen(ext_pin_btn_img)
        # ic(ext_pin_btn_pos)
        pyautogui.click(ext_pin_btn_pos)

        time.sleep(1)

        # close the extensions panel
        pyautogui.click(ext_btn_pos)

        time.sleep(1)

        # get the position of the save button
        ext_save_btn_img = "./img/ext_save_btn.png"
        ext_save_btn_pos = pyautogui.locateCenterOnScreen(ext_save_btn_img)
        # ic(ext_save_btn_pos)

    # click on the save button
    pyautogui.click(ext_save_btn_pos)

    # wait for the confirmation popup to appear
    waiting_for_save : bool = True
    while waiting_for_save:
        # click on the confirmation that appears
        ext_continue_save_btn_img = "./img/continue_save_btn.png"
        ext_continue_save_btn_pos = pyautogui \
            .locateCenterOnScreen(ext_continue_save_btn_img)
        # ic(ext_continue_save_btn_pos)

        if ext_continue_save_btn_pos:
            waiting_for_save = False

    pyautogui.click(ext_continue_save_btn_pos)

    time.sleep(1)

    page_title = DRIVER.title
    # ic(page_title)
    page_title = page_title.replace("|", "_")

# BUG main page being saved to cwd instead of ./[name of book]
    global book_name
    ic(book_name)
    book_folder_path = CWD / book_name
    ic(book_folder_path)
    if not os.path.isdir(book_folder_path):
        os.mkdir(book_folder_path)

    saved_file_path = DOWNLOADS_FOLDER_PATH / f"{page_title}.html"
    # ic(saved_file_path)

    time.sleep(3)

    file_was_saved = os.path.isfile(saved_file_path)
    # ic(file_was_saved)


    src = saved_file_path
    index = len(book_chapter_links)
    dst = book_folder_path / f"{index}_{page_title}.html"
    # ic(src)
    # ic(dst)

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
