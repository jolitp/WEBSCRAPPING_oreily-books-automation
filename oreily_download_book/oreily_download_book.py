#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml chdir currentsrc cmdline xpath

# region imports
from pathlib import Path
import time
import datetime
from datetime import date
import os
import re
from dataclasses import dataclass, field
import subprocess
from executing.executing import NodeFinder

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
import selenium.webdriver.support.ui as ui

from rich.console import Console
from rich.traceback import install as rich_traceback_install

import pyautogui
from pyautogui import Point

from bs4 import BeautifulSoup

import html2text

from natsort import natsorted, ns

from icecream import ic
# endregion imports


# region classes

@dataclass
class Chapter:
    """A chapter from a book. contains sections."""
    title: str = ""
    sections: list = field(default_factory=list)

    def __str__(self) -> str:
        result = f"[#00AAAA]title[/]: [#FF8800]{self.title}[/]\n"
        result += "[#00AAAA]sections[/] : [\n"
        for section in self.sections:
            result += f"    [#FF8800]{section}[/]\n"
        result += "]\n"
        return result

    def print(self):
        string_repr = self.__str__()
        CONSOLE.print(string_repr)
        ...


@dataclass
class Topic:
    """Topic of a book"""
    name : str = ""
    link : str = ""


@dataclass
class Publisher:
    """A publisher of a book"""
    name : str = ""
    link : str = ""


@dataclass
class Book:
    """The data for a book"""
    title: str = ""
    author: str = ""
    time_to_complete: time = None
    topics: Topic = None
    publisher: Publisher = None
    # publisher_info: str = ""
    # resources_section: str = ""
    publication_date: date = None
    is_early_release: bool = None
    stars: int = 0 # 0 means no reviews yet
    description: str = ""
    # reviews: list = field(default_factory=list)
    chapters: list = field(default_factory=list)

    def __str__(self) -> str:
        result = ""

        result += f"[#00AAAA]title[/]: [#FF8800]{self.title}[/]\n"
        result += f"[#00AAAA]author[/]: [#FF8800]{self.author}[/]\n"
        result += f"[#00AAAA]publisher[/]: [#FF8800]{self.publisher}[/]\n"
        result += f"[#00AAAA]publication date[/]: [#FF8800]{self.publication_date}[/]\n"
        result += f"[#00AAAA]topics[/]: [#FF8800]{self.topics}[/]\n"
        result += f"[#00AAAA]time to complete[/]: [#FF8800]{self.time_to_complete}[/]\n"
        result += f"[#00AAAA]description[/]: [#FF8800]{self.description}[/]\n"

        result += "[#00AAAA]chapters[/] : [\n"
        for chapter in self.chapters:
            chapter = str(chapter)
            lines = chapter.split("\n")
            for line in lines:
                padded_line = "   " + line + "\n"
                result += padded_line
        result += "]\n"

        return result

    def print(self):
        string_repr = self.__str__()
        CONSOLE.print(string_repr)
        ...

# endregion classes


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
BOOK_CHAPTER_LINKS = []
BOOK_FOLDER_PATH = None
BOOK_DATA = Book()
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
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_extension("./ext.zip")

    global DRIVER
    DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH, options=CHROME_OPTIONS)
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
        ic(logged_in_logo_pos)
        ic(user_menu_pos)

        if logged_in_logo_pos and user_menu_pos:
            waiting_for_login = False
        # TODO check for cases where other screens appear and try again
        ...
    ...
# endregion wait_for_login_to_be_successful() -------- wait_for_login_to_be_successful()


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
    time.sleep(10)
    wait_for_login_to_be_successful()

    DRIVER.get(url)

    page_source = DRIVER.page_source
    global BOOK_FOLDER_PATH
    global BOOK_DATA
    BOOK_DATA = Book()
    BOOK_DATA.title = DRIVER.title
    BOOK_FOLDER_PATH = CWD / BOOK_DATA.title

    return None # uncomment to test w/o saving pages

    links_to_visit = get_book_chapter_links(page_source)

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

    if not BOOK_FOLDER_PATH.exists():
        BOOK_FOLDER_PATH.mkdir()

    saved_file_path = DOWNLOADS_FOLDER_PATH / f"{page_title}.html"
    # ic(saved_file_path)

    time.sleep(3)

    src = saved_file_path
    index = len(BOOK_CHAPTER_LINKS)
    dst = BOOK_FOLDER_PATH / f"{index}_{page_title}.html"

    os.rename(src, dst)

    BOOK_CHAPTER_LINKS.append(url)
# endregion save_page(...) ---------------------------------------------- save_page(...)


# region get_chapter_names() ======================================= get_chapter_names()
def get_chapter_names(chapter_files):
    chapter_names = []
    for chapter_file in chapter_files[1:]:
        chapter_name = chapter_file.split(" _ ")[0]
        regex = re.compile('([0-9]+_)(.*)')
        matcher = regex.match(chapter_name)
        if matcher:
            chapter_name = matcher.group(2)
        chapter_names.append(chapter_name)
    return chapter_names
# endregion get_chapter_names() ------------------------------------ get_chapter_names()


# region get_chapter_sections() ================================== get_chapter_sections()
def get_chapter_sections(chapter_files):
    chapter_sections = []
    # go over each file skipping the first file("main" book page)
    for chapter_file in chapter_files[1:]:
        with open(BOOK_FOLDER_PATH / chapter_file ) as file_obj:
            sections = []
            soup : BeautifulSoup = BeautifulSoup(file_obj, features="lxml")
            section_elements = soup.find_all("section",
                                            attrs={"data-pdf-bookmark":True})
            for section in section_elements:
                section = str(section)
                pattern = re.compile('(<section data-pdf-bookmark=")(.*)(" data)')
                matched = pattern.match(section)
                title = matched.group(2)
                # ic(title)
                sections.append(title)
            chapter_sections.append(sections)
    return chapter_sections
# endregion get_chapter_sections() -------------------------------- get_chapter_sections()


# region get_saved_pages() ============================================ get_saved_pages()
def get_saved_pages() -> list:
    chapter_files = os.listdir(BOOK_FOLDER_PATH)
    chapter_files = natsorted(chapter_files, alg=ns.PATH)
    return chapter_files
# endregion get_saved_pages() ----------------------------------------- get_saved_pages()


# region get_main_page_from_saved_files() ============== get_main_page_from_saved_files()
def get_main_page_from_saved_files() -> str:
    chapter_files = get_saved_pages()
    return chapter_files[0]
# endregion get_main_page_from_saved_files() ---------- get_main_page_from_saved_files()


# region get_chapter_hierarchy() ================================ get_chapter_hierarchy()
def get_chapter_hierarchy():
    # get files inside book folder
    chapter_files = os.listdir(BOOK_FOLDER_PATH)
    chapter_files = natsorted(chapter_files, alg=ns.PATH)

    chapter_titles = get_chapter_names(chapter_files)
    chapter_sections = get_chapter_sections(chapter_files)

    for title, sections in zip(chapter_titles, chapter_sections):
        chapter_data = Chapter()
        chapter_data.sections = sections
        chapter_data.title = title
        # chapter_data.print()
        global BOOK_DATA
        BOOK_DATA.chapters.append(chapter_data)
# endregion get_chapter_hierarchy() ============================= get_chapter_hierarchy()


# region get_cover_picture() ======================================== get_cover_picture()
def get_cover_picture():
    main_page_file = get_main_page_from_saved_files()

    with open(BOOK_FOLDER_PATH / main_page_file, "r") as file_obj:
        soup = BeautifulSoup(file_obj, features="lxml")
        img_element = soup.find("img", attrs={"src" : True})
        img_url = img_element["data-savepage-currentsrc"]
        os.chdir(BOOK_FOLDER_PATH)
        cmd = [ "wget", '-O','cover.jpeg' , img_url]
        # cmd_str = subprocess.list2cmdline(cmd)
        # ic(cmd)
        # ic(cmd_str)
        subprocess.run(cmd)
        os.chdir(CWD)
# endregion get_cover_picture() ------------------------------------- get_cover_picture()


# region get_author_name() ============================================ get_author_name()
def get_data_from_saved_page():
    main_page_file = get_main_page_from_saved_files()

    with open(BOOK_FOLDER_PATH / main_page_file, "r") as file_obj:
        soup = BeautifulSoup(file_obj, features="lxml")
# region get author's name
        element = soup.find("div", attrs={"class" : re.compile("contributors--*")})
        BOOK_DATA.author = element.a.text
        del element
# endregion get author's name
# region get stats block
        stats_element = soup.find_all("div", attrs={"class" : re.compile("statBlock--")})
        for stat in stats_element:
            stat = str(stat)
# region get time to complete
            time_to_complete = "TIME TO COMPLETE:"
            if time_to_complete in stat:
                length = len(time_to_complete)
                pos = stat.find(time_to_complete)
                start = pos + length
                stat: str = stat[start:]
                stat = stat.replace("</span><span>", "")
                stat = stat.replace("</span></div>", "")

                hours, minutes = stat.split(" ")
                hours = int(hours[:-1])
                minutes = int(minutes[:-1])

                time_to_complete = datetime.time(hours, minutes)
                BOOK_DATA.time_to_complete = time_to_complete
# endregion get time to complete
# region get toopics
            topics = "TOPICS:"
            if topics in stat:
                length = len(topics)
                pos = stat.find(topics)
                start = pos + length
                stat: str = stat[start:]
                stat = stat.replace("</span><span>", "")
                stat = stat.replace("</span></div>", "")
                stat = stat.replace('<a class="orm-Link-root" ', "")
                stat = stat.replace('</a>', "")
                stat = stat.replace('href="', "")

                topic_link, topic_name = stat.split('">')
                topic = Topic(topic_name, topic_link)
                BOOK_DATA.topics = topic
# endregion get toopics
# region get bublisher
            published_by = "PUBLISHED BY:"
            if published_by in stat:
                length = len(published_by)
                pos = stat.find(published_by)
                start = pos + length
                stat: str = stat[start:]
                stat = stat.replace("</span><span>", "")
                stat = stat.replace("</span></div>", "")
                stat = stat.replace('<a class="orm-Link-root" ', "")
                stat = stat.replace('</a>', "")
                stat = stat.replace('href="', "")

                publisher_link, publisher_name = stat.split('">')
                publisher = Publisher(publisher_name, publisher_link)
                BOOK_DATA.publisher = publisher
# endregion get bublisher
# region get publication date
            publication_date = "PUBLICATION DATE:"
            if publication_date in stat:
                length = len(publication_date)
                pos = stat.find(publication_date)
                start = pos + length
                stat: str = stat[start:]
                stat = stat.replace("</span><span>", "")
                stat = stat.replace("</span></div>", "")

                date_ = datetime.datetime.strptime(stat, "%B %Y")
                BOOK_DATA.publication_date = date_
# endregion get publication date
# endregion get stats block

# region get book description
        element = soup.find("section", attrs={"class" : re.compile("description--")})
        text = html2text.html2text(str(element))
        BOOK_DATA.description = text
# endregion get book description

# region    get average rating
        regex_ = re.compile("Average rating \\d out of \\d")
        element = soup.find("span",
                            attrs={
                                "aria-label" : regex_
                                })
        element = str(element)
        first_line = element.split("\n", maxsplit=1)[0]
        first_line = first_line.replace('<span aria-label="Average rating ', "")
        n_of_stars = first_line[0]
        BOOK_DATA.stars = n_of_stars
# endregion get average rating


# endregion get_author_name() ----------------------------------------- get_author_name()


# region get_book_data_from_files() ========================== get_book_data_from_files()
def get_book_data_from_files():
    # get_chapter_hierarchy() # DONE comment to toggle
    # get_cover_picture() # DONE comment to toggle
    get_data_from_saved_page()
    # TODO review stars
    # TODO about the publisher
    # TODO resources sections
    # TODO get all reviews
    # TODO get errata link (resources)

    # TODO make org file with book info

    BOOK_DATA.print()
# endregion get_book_data_from_files() ---------------------- get_book_data_from_files()


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
    try:
        main()
    except Exception:
        CONSOLE.print_exception()
        DRIVER.quit()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
