#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml chdir
# spell-checker: word currentsrc cmdline xpath crdownload

# region imports
from pathlib import Path
import sys
import time
import datetime
from datetime import date, timedelta
import os
import re
from dataclasses import dataclass, field
import subprocess
import shutil
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

from rich.console import Console
from rich.traceback import install as rich_traceback_install

import pyautogui
from pyautogui import Point

from bs4 import BeautifulSoup

import html2text

from natsort import natsorted, ns

from icecream import ic
# endregion imports


# region constants
rich_traceback_install()

CHROME_DRIVER_PATH = Path("/home/jolitp/Applications/chromedriver")
DOWNLOADS_FOLDER_PATH = Path("/home/jolitp/Downloads/")
CWD = Path(os.getcwd())
DRIVER = None
CONSOLE = Console()

LOGIN_PAGE = \
"https://www.oreilly.com/member/login/?next=%2Fapi%2Fv1%2Fauth%2Fopenid%2Fauthorize%2F%3Fclient_id%3D235442%26redirect_uri%3Dhttps%3A%2F%2Flearning.oreilly.com%2Fcomplete%2Funified%2F%26state%3DbSFjglRdxCDV36ynSN2seSVHaB5069ME%26response_type%3Dcode%26scope%3Dopenid%2Bprofile%2Bemail&locale=en"
# login information
# registered at: 2021/07/14
EMAIL = "vigope6498@ovooovo.com"
PASSWORD = "H3dg3h0g"
# endregion constants


# region globals
BOOK_PAGES_DOWNLOADED = 0
BOOK_FOLDER_PATH = None
# endregion globals


# region click_element_given_xpath(...) ================== click_element_given_xpath(...)
def click_element_given_xpath(xpath):
    element = DRIVER.find_element_by_xpath(xpath)
    element.click()
# endregion click_element_given_xpath(...) --------------- click_element_given_xpath(...)


# region img_center_pos(...) ======================================== img_center_pos(...)
def img_center_pos(img_path:str) -> Point:
    return pyautogui.locateCenterOnScreen(img_path)
# endregion img_center_pos(...) ------------------------------------- img_center_pos(...)


# region click_on_img(...) ============================================ click_on_img(...)
def click_on_img(img_path:str) -> Point:
    pos = img_center_pos(img_path)
    pyautogui.click(pos)
    return pos
# endregion click_on_img(...) ----------------------------------------- click_on_img(...)


# region setup_driver() ================================================== setup_driver()
def setup_driver():
    chrome_options = Options()
    chrome_options.add_extension("./ext.zip")

    global DRIVER
    DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
    DRIVER.maximize_window()
# endregion setup_driver() ----------------------------------------------- setup_driver()


# region login_oreilly() ================================================ login_oreilly()
def login_oreilly():
    # open site
    DRIVER.get(LOGIN_PAGE)
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
    # time.sleep(.3)
    # password_field.send_keys(Keys.ENTER)
    time.sleep(1)
    click_on_img("./img/login/sign_in_btn.png")
# endregion login_oreilly() --------------------------------------------- login_oreilly()


# region wait_for_login_to_be_successful() ============ wait_for_login_to_be_successful()
def wait_for_login_to_be_successful():
    waiting_for_login = True
    while waiting_for_login:
        time.sleep(.5)
        logged_in_logo_pos = img_center_pos("./img/login/login_successful_logo.png")
        user_menu_pos = img_center_pos("./img/login/user_is_logged_in.png")

        if logged_in_logo_pos and user_menu_pos:
            waiting_for_login = False
        # TODO check for cases where other screens appear and try again
        ...
    ...
# endregion wait_for_login_to_be_successful() -------- wait_for_login_to_be_successful()

# TODO refactor repetition
# region get_book_chapter_links() ============================= get_book_chapter_links()
def get_book_chapter_links(page_source) -> list:
    soup = BeautifulSoup(page_source, "lxml")
    list_of_h5s = soup.find_all("h5")
    list_of_h6s = soup.find_all("h6")
    links_to_visit = []
    for chapter_tag in list_of_h5s:
        chapter_tag : str = str(chapter_tag)
        soup = BeautifulSoup(chapter_tag, "lxml")
        for element in soup.findAll("a"):
            link = element.get("href")
            full_link = "https://learning.oreilly.com" + link
            links_to_visit.append(full_link)
    for chapter_tag in list_of_h6s:
        chapter_tag : str = str(chapter_tag)
        soup = BeautifulSoup(chapter_tag, "lxml")
        for element in soup.findAll("a"):
            link = element.get("href")
            full_link = "https://learning.oreilly.com" + link
            links_to_visit.append(full_link)
    chapter_links = []
    for link in links_to_visit:
        if not "#" in link:
            chapter_links.append(link)
        ...
    return chapter_links
# endregion get_book_chapter_links() --------------------------- get_book_chapter_links()


# region go_to_book_page(...) ===================================== go_to_book_page(...)
def go_to_book_page(url: str):
    time.sleep(10)
    wait_for_login_to_be_successful()

    DRIVER.get(url)

    page_source = DRIVER.page_source
    global BOOK_FOLDER_PATH
    BOOK_FOLDER_PATH = CWD / DRIVER.title

    # return None # uncomment to test w/o saving pages

    links_to_visit = get_book_chapter_links(page_source)

    get_cover_picture()
    save_page(url)

    time.sleep(1)

    for link_to_visit in links_to_visit:
        DRIVER.get(link_to_visit)

        xpath = '//*[@id="main"]/section/div/div/span/span[1]'
        element : WebElement = DRIVER.find_element_by_xpath(xpath)
        element.click()

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

    # get all files in downloads directory
    all_files_before = os.listdir(DOWNLOADS_FOLDER_PATH)

    # click on the confirmation that appears
    pyautogui.click(continue_save_btn_pos)

# region wait download to finish
    count_before_sleep = 0
    count_after_sleep = 0
    wait_download_to_finish = True
    while wait_download_to_finish:
        count_before_sleep += 1
        time.sleep(.5)
        all_files_after = os.listdir(DOWNLOADS_FOLDER_PATH)

        set_difference = set(all_files_after) - set(all_files_before)
        list_difference = list(set_difference)

        print()
        ic(all_files_before)
        ic(all_files_after)
        ic(list_difference)
        ic(count_before_sleep)
        ic(count_after_sleep)
        print()
        if list_difference:
            file_name = list_difference[0]
        else:
            continue
        if file_name.endswith(".crdownload"):
            continue
        if list_difference:
            wait_download_to_finish = False
        count_after_sleep += 1
    file_name = list_difference[0]
# endregion wait download to finish

# region move downloaded file to book folder in cwd
    if not BOOK_FOLDER_PATH.exists():
        BOOK_FOLDER_PATH.mkdir()

    saved_file_path = DOWNLOADS_FOLDER_PATH / file_name

    src = saved_file_path
    global BOOK_PAGES_DOWNLOADED
    index = BOOK_PAGES_DOWNLOADED

    result = ""
    regex_ = re.compile(r"https:\/\/(.*)\/(.*).html")
    match = regex_.match(url)
    if match:
        result = match.group(2)

    file_name = file_name.replace(" _ ", " - ")
    if result:
        dst = BOOK_FOLDER_PATH / f"{index:0>3d} - {result} - {file_name}"
    else:
        dst = BOOK_FOLDER_PATH / f"{index:0>3d} - {file_name}"

    # os.rename(src, dst)
    shutil.move(src, dst)
# endregion move downloaded file to book folder in cwd

    BOOK_PAGES_DOWNLOADED += 1
# endregion save_page(...) ---------------------------------------------- save_page(...)


# region get_cover_picture() ======================================== get_cover_picture()
def get_cover_picture():
    soup = BeautifulSoup(DRIVER.page_source, features="lxml")
    img_element = soup.find("img", attrs={"src" : True})
    start_index = str(img_element).find("src=")
    img_tag = str(img_element)[start_index:]
    url = img_tag.replace('src="', "").replace('"/>', "")
    img_url = "https://learning.oreilly.com" + url
    os.chdir(BOOK_FOLDER_PATH)
    cmd = [ "wget", '-O','cover.jpeg' , img_url]
    # cmd_str = subprocess.list2cmdline(cmd)
    subprocess.run(cmd)
    os.chdir(CWD)
# endregion get_cover_picture() ------------------------------------- get_cover_picture()


# region main() ================================================================= main()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    url = args.url

    setup_driver()
    login_oreilly()
    # url = "https://learning.oreilly.com/library/view/fluent-python-2nd/9781492056348/"
    # url = "https://learning.oreilly.com/library/view/mastering-python-for/9781784394516/"
    # url = "https://learning.oreilly.com/library/view/the-art-of/9781351803632/"
    go_to_book_page(url)
    # get_book_data_from_files()
    # create_org_file()
    DRIVER.close()
    CONSOLE.print("[bold green]finished[/]")
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    try:
        main()
    except Exception:
        CONSOLE.print_exception()
        DRIVER.quit()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
