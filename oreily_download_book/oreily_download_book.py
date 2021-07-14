#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml

from pathlib import Path
import time
import os
import re
import bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

from rich.console import Console
from rich.traceback import install as rich_traceback_install

import pyautogui
from pyautogui import Point

from bs4 import BeautifulSoup

from lxml import etree

from icecream import ic

rich_traceback_install()

CHROME_DRIVER_PATH = Path("/home/jolitp/Applications/chromedriver")
DOWNLOADS_FOLDER_PATH = Path("/home/jolitp/Downloads/")
CWD = Path(os.getcwd())
DRIVER = None
CONSOLE = Console()


# login information
EMAIL = "libed17686@advew.com"
PASSWORD = "h3dg3h0g"

book_chapter_links = []
book_name : str = ""
book_folder_path = Path()

# region click_element_given_xpath(...) ================== click_element_given_xpath(...)
def click_element_given_xpath(xpath):
    element = DRIVER.find_element_by_xpath(xpath)
    element.click()
# endregion click_element_given_xpath(...) --------------- click_element_given_xpath(...)


# region img_pos(...) ====================================================== img_pos(...)
def img_center_pos(img_path:str) -> Point:
    return pyautogui.locateCenterOnScreen(img_path)
# endregion img_pos(...) --------------------------------------------------- img_pos(...)


# region click_on_img(...) ============================================ click_on_img(...)
def click_on_img(img_path:str) -> Point:
    pos = img_center_pos(img_path)
    pyautogui.click(pos)
    return pos
# endregion click_on_img(...) ----------------------------------------- click_on_img(...)


# region setup_driver() ================================================== setup_driver()
def setup_driver():
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_extension("./ext.zip")

    global DRIVER
    DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH, options=CHROME_OPTIONS)
    DRIVER.maximize_window()
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
    time.sleep(2)
    DRIVER.get(url)

# TODO check if login was successful
    def check_if_login_is_successful():
        ...
    page_source = DRIVER.page_source
    global book_name
    book_name = DRIVER.title
    # return None # uncomment to test w/o saving pages

    links_to_visit = get_book_chapter_links(page_source)

    save_page(url)

    time.sleep(1)

    for link_to_visit in links_to_visit:
        DRIVER.get(link_to_visit)

        xpath = '//*[@id="main"]/section/div/div/span/span[1]'
        el : WebElement = DRIVER.find_element_by_xpath(xpath)
        el.click()

        set_text_style()

        time.sleep(1) # time for the page to completely load

        save_page(link_to_visit)
        ...
    ...

# endregion go_to_book_page(...) ---------------------------------- go_to_book_page(...)


# region set_text_style() ========================================= set_text_style()
def set_text_style():
    # safeguard against downloads panel being in the way
    pyautogui.press('pagedown') # is it doing anything now?

    # click the cog button on the left side of the screen
    click_element_given_xpath(
"/html/body/div[1]/div/div/div[2]/main/section/div/div/div/section/button/span/span[1]"
    )

    # click the large font icon
    click_element_given_xpath(
        "/html/body/div[4]/div/div/div/div/form/fieldset[1]/label[3]"
    )

    # click the dark background icon
    click_element_given_xpath(
        "/html/body/div[4]/div/div/div/div/form/fieldset[2]/div[3]/label"
    )

    # click the small margins icon
    click_element_given_xpath(
        "/html/body/div[4]/div/div/div/div/form/fieldset[3]/label[3]"
    )

    # click the close button
    click_element_given_xpath(
        "/html/body/div[4]/div/div/div/button"
    )
# endregion set_text_style() ----------------------------------------- set_text_style()


# region pin_save_ext_on_bar(...) ============================ pin_save_ext_on_bar(...)
def pin_save_ext_on_bar(delay:float):
    # open the extensions panel
    ext_btn_pos = click_on_img("./img/save_page/ext_btn.png")

    time.sleep(delay)

    # pin the extension
    ext_pin_btn_pos = click_on_img("./img/save_page/ext_pin_btn.png")

    time.sleep(delay)

    # close the extensions panel
    pyautogui.click(ext_btn_pos)

    time.sleep(delay)

    # get the position of the save button
    return img_center_pos("./img/save_page/ext_save_btn.png")
# endregion pin_save_ext_on_bar(...) -------------------------- pin_save_ext_on_bar(...)


# region save_page(...) ================================================= save_page(...)
def save_page(url):
    # get the position of save button
    ext_save_btn_pos = img_center_pos("./img/save_page/ext_save_btn.png")

    # check if save button has already been pinned to bar
    if not ext_save_btn_pos:
        ext_save_btn_pos = pin_save_ext_on_bar(1)
    pyautogui.click(ext_save_btn_pos)

    # wait for the confirmation popup to appear
    waiting_for_save : bool = True
    while waiting_for_save:
        continue_save_btn_pos = img_center_pos("./img/save_page/continue_save_btn.png")
        if continue_save_btn_pos:
            waiting_for_save = False

    # click on the confirmation that appears
    pyautogui.click(continue_save_btn_pos)

    time.sleep(1)

# TODO use another method to get the path to current file
# the idea is getting the list of all files in the downloads directory
# before downloading the file, and another list after, and comparing
# both to get the name of the newly downloaded file
    page_title = DRIVER.title
    page_title = page_title.replace("|", "_")
    page_title = page_title.replace(":", "_")

    global book_name
    global book_folder_path
    book_folder_path = CWD / book_name
    if not book_folder_path.exists():
        book_folder_path.mkdir()

    saved_file_path = DOWNLOADS_FOLDER_PATH / f"{page_title}.html"
    # ic(saved_file_path)

    time.sleep(3)

    src = saved_file_path
    index = len(book_chapter_links)
    dst = book_folder_path / f"{index}_{page_title}.html"

    os.rename(src, dst)

    book_chapter_links.append(url)
# endregion save_page(...) ---------------------------------------------- save_page(...)


# region get_book_data_from_files()
def get_book_data_from_files():
    # TODO get chapter hierarchy
    # TODO get cover picture
    # TODO get book info into a dict
    # TODO make org file with book info
    # TODO book title
    # TODO time to complete
    # TODO topics
    # TODO published by
    # TODO publication date
    # TODO review stars
    # TODO author's name
    # TODO description text
    # TODO about the publisher
    # TODO resources sections
    # TODO get all reviews
    # TODO get errata link


    ...
# endregion


# region main() ================================================================= main()
def main():
    setup_driver()
    login_oreilly()
    url = "https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
    go_to_book_page(url)
    get_book_data_from_files()
    DRIVER.close()
    CONSOLE.print("[bold green]finished[/]")
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    main()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
