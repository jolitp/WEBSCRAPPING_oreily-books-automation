#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml chdir nargs sortby
# spell-checker: word currentsrc cmdline xpath crdownload

# region imports
from pathlib import Path
import time
import os
import re
import subprocess
import shutil
import argparse
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver

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
class SearchPageElements():
    @dataclass
    class ContentType():
        all: WebElement = None
        books: WebElement = None
        videos: WebElement = None
        live_events: WebElement = None
        learning_paths: WebElement = None
        playlists: WebElement = None
        interactive: WebElement = None
        practice_exam: WebElement = None

# the string representation is weird
        # def __str__(self) -> str:
        #     result = ""
        #     result += f"all btn:\n{self.all}\n"
        #     result += f"books btn:\n{self.books}\n"
        #     result += f"videos btn:\n{self.videos}\n"
        #     result += f"live events btn:\n{self.live_events}\n"
        #     result += f"learning paths btn:\n{self.learning_paths}\n"
        #     result += f"playlists btn:\n{self.playlists}\n"
        #     result += f"interactive btn:\n{self.interactive}\n"
        #     result += f"practice exam btn:\n{self.practice_exam}\n"
        #     return result

        # def print(self):
        #     print(self.__str__)

    @dataclass
    class FilteringOptions():
        # TODO change type to beautiful soup element maybe?
        topics: WebElement = None
        publishers: WebElement = None
        publication_date: WebElement = None
        rating: WebElement = None
        sort_by: WebElement = None
        video_type: WebElement = None
        interactive_type: WebElement = None
# TODO make __str__ function
# TODO make print function

    content_type: ContentType = ContentType()
    filtering_options: FilteringOptions = FilteringOptions()

# TODO make __str__ function
# TODO make print function

class Format(Enum):
    ALL = 'all'
    BOOKS = 'books'
    VIDEOS = 'videos'
    LIVE_EVENTS = 'live_events'
    LEARNING_PATHS = 'learning_Paths'
    PLAYLISTS = 'playlists'
    INTERACTIVE = 'interactive'
    PRACTICE_EXAM = 'practice_exam'

    def __str__(self):
        return self.value


class SortBy(Enum):
    RELEVANCE = 'relevance'
    DATE_ADDED = 'date_added'
    PUBLICATION_DATE = 'publication_date'
    POPULARITY = 'popularity'
    RATING = 'rating'

    def __str__(self):
        return self.value


class PublicationDate(Enum):
    ALL = 'all'
    EARLY_RELEASE = "er"
    LAST_SIX_MONTHS = "6m"
    LAST_YEAR = "1y"
    LAST_TWO_YEARS = "2y"

    def __str__(self):
        return self.value


class VideoType(Enum):
    ALL = "all"
    AUDIO_BOOK = "audio_book"
    CASE_STUDY = "case_study"
    CONFERENCE = "conference"
    OTHER = "other"

    def __str__(self):
        return self.value


class InteractiveType(Enum):
    ALL = "all"
    SANDBOXES = "sandboxes"
    SCENARIOS = "scenarios"
    NOTEBOOKS = "notebooks"

    def __str__(self):
        return self.value


@dataclass
class Options():
    search_term : str = ""
    format : Format = Format(Format.ALL)
    sort_by : SortBy = SortBy(SortBy.RELEVANCE)
    # topics : list = field(default_factory=list)
    topics : Tuple = ()
    publishers : Tuple = ()
    min_pub_date : PublicationDate = PublicationDate(PublicationDate.ALL)
    min_rating : int = 0
    reverse : bool = False
    number_of_pages = None
    video_type : VideoType = VideoType(VideoType.ALL)
    interactive_type : InteractiveType = InteractiveType(InteractiveType.ALL)

    def print(self):
        output = ""
        output += "Options:\n"
        output += "  search_term      : str                  = '{}'\n" \
            .format(self.search_term)
        output += "  format           : Format               = {}('{}')\n" \
            .format(self.format.name, self.format.value)
        output += "  sort_by          : SortBy               = {}('{}')\n" \
            .format(self.sort_by.name, self.sort_by.value)
        output += "  topics           : Topics               = {}\n" \
            .format(self.topics)
        output += "  publishers       : Publishers           = {}\n" \
            .format(self.publishers)
        output += "  min_pub_date     : PublicationDate      = {}('{}')\n" \
            .format(self.min_pub_date.name, self.min_pub_date.value)
        output += "  min_rating       : Rating               = {}\n" \
            .format(self.min_rating)
        output += "  reverse          : bool                 = {}\n" \
            .format(self.reverse)
        output += "  number_of_pages  : int                  = {}\n" \
            .format(self.number_of_pages)
        if self.video_type:
            output += "  video_type       : VideoType            = {}('{}')\n" \
                .format(self.video_type.name, self.video_type.value)
        else:
            output += "  video_type       : VideoType            = {}\n" \
                .format(None)
        if self.interactive_type:
            output += "  interactive_type : InteractiveType      = {}\n" \
                .format(self.interactive_type.name, self.interactive_type.value)
        else:
            output += "  interactive_type : InteractiveType      = {}\n" \
                .format(None)
        print(output)
# endregion classes


# region constants
rich_traceback_install()


CHROME_DRIVER_PATH = Path("/home/jolitp/Applications/chromedriver")
DOWNLOADS_FOLDER_PATH = Path("/home/jolitp/Downloads/")
SCRIPT_DIR = Path(os.path.realpath(__file__)).parent
CWD = Path(os.getcwd())
DRIVER : WebDriver = None
CONSOLE = Console()

LOGIN_PAGE = \
'https://www.oreilly.com/member/login/?next=%2Fapi%2Fv1%2Fauth%2Fopenid%2Fauthorize%2F%3Fclient_id%3D235442%26redirect_uri%3Dhttps%3A%2F%2Flearning.oreilly.com%2Fcomplete%2Funified%2F%26state%3DvzLnDhsIcfDZHwmYg6AdxKtlVPt0Tor9%26response_type%3Dcode%26scope%3Dopenid%2Bprofile%2Bemail&locale=en'
# "https://www.oreilly.com/member/login/?next=%2Fapi%2Fv1%2Fauth%2Fopenid%2Fauthorize%2F%3Fclient_id%3D235442%26redirect_uri%3Dhttps%3A%2F%2Flearning.oreilly.com%2Fcomplete%2Funified%2F%26state%3DbSFjglRdxCDV36ynSN2seSVHaB5069ME%26response_type%3Dcode%26scope%3Dopenid%2Bprofile%2Bemail&locale=en"
# "https://www.oreilly.com/member/login"
# login information
# registered at: 2021/07/14
EMAIL = "vigope6498@ovooovo.com"
PASSWORD = "H3dg3h0g"

OPTIONS = None
ACTIVE_CONTENT_FORMAT = None
# endregion constants


# region click_element_given_xpath(...) ================== click_element_given_xpath(...)
def click_element_given_xpath(xpath):
    element = DRIVER.find_element_by_xpath(xpath)
    element.click()
# endregion click_element_given_xpath(...) --------------- click_element_given_xpath(...)


# region img_center_pos(...) ======================================== img_center_pos(...)
def img_center_pos(img_path:str) -> Point:
    return pyautogui.locateCenterOnScreen(img_path, grayscale=True, confidence=0.7)
# endregion img_center_pos(...) ------------------------------------- img_center_pos(...)


# region click_on_img(...) ============================================ click_on_img(...)
def click_on_img(img_path:str) -> Point:
    pos = img_center_pos(img_path)
    pyautogui.click(pos)
    return pos
# endregion click_on_img(...) ----------------------------------------- click_on_img(...)


# region setup_driver() ================================================== setup_driver()
def setup_driver():
    # chrome_options.add_extension("./ext.zip")

    global DRIVER
    DRIVER = webdriver.Chrome(CHROME_DRIVER_PATH)
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

    sign_in_btn_img = f"{SCRIPT_DIR}/img/login/sign_in_btn.png"
    can_click_on_sign_in_btn = False
    while not can_click_on_sign_in_btn:
        sign_in_btn_on_screen = has_img_on_screen(sign_in_btn_img)

        if sign_in_btn_on_screen:
            can_click_on_sign_in_btn = True
    click_on_img(sign_in_btn_img)
# endregion login_oreilly() --------------------------------------------- login_oreilly()


# region wait_for_login_to_be_successful() ============ wait_for_login_to_be_successful()
def wait_for_login_to_be_successful():
    waiting_for_login = True
    while waiting_for_login:
        time.sleep(.5)

        logged_in_logo_pos = img_center_pos(f"{SCRIPT_DIR}/img/login/login_successful_logo.png")
        user_menu_pos = img_center_pos(f"{SCRIPT_DIR}/img/login/user_is_logged_in.png")

        if logged_in_logo_pos and user_menu_pos:
            waiting_for_login = False
        # TODO check for cases when other screens appear and try again
        ...
    ...
# endregion wait_for_login_to_be_successful() -------- wait_for_login_to_be_successful()


# region has_img_on_screen(...) ================================== has_img_on_screen(...)
def has_img_on_screen(img_path: str) -> bool:
    pos = img_center_pos(img_path)
    img_is_on_screen = False
    if pos:
        img_is_on_screen = True
    else:
        img_is_on_screen = False
    return img_is_on_screen
# endregion has_img_on_screen(...) ------------------------------ has_img_on_screen(...)


# region wait_search_page_to_load() ========================= wait_search_page_to_load()
def wait_search_page_to_load():
    # wait the spinning wheel appear and disappear
    search_page_loaded = False
    while not search_page_loaded:
        spinning_wheel_img = f"{SCRIPT_DIR}/img/search_page/spinning.png"
        spinning_wheel_is_on_screen = \
            has_img_on_screen(spinning_wheel_img)

        # check the presence of the spinning wheel
        while spinning_wheel_is_on_screen:
            spinning_wheel_is_on_screen = \
                has_img_on_screen(spinning_wheel_img)
            # check the absence of the spinning wheel
            if not spinning_wheel_is_on_screen:
                search_page_loaded = True
                # debugging code
                # passed_spinning_wheel_ss_img = pyautogui.screenshot()
                # passed_spinning_wheel_ss_img.save(
                #     "./01_passed_spinning_wheel_ss_img.png")
                break

    # check the presence of the dropdown menus
    search_page_loaded = False
    while not search_page_loaded:
        sort_by_relevance_btn_img = f"{SCRIPT_DIR}/img/search_page/sort_by_relevance.png"
        sort_by_relevance_btn_is_on_screen = \
            has_img_on_screen(sort_by_relevance_btn_img)

        if sort_by_relevance_btn_is_on_screen:
            search_page_loaded = True
            # debugging code
            # passed_sort_by_relevance_btn_ss_img = pyautogui.screenshot()
            # passed_sort_by_relevance_btn_ss_img.save(
            #     "./02_passed_sort_by_relevance_btn_ss_img.png")

    # check the presence of type of content icons
    search_page_loaded = False
    while not search_page_loaded:
        possible_icons = [
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/book icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/interactive icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/learning path icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/live icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/playlist icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/practice exam icon.png"),
            has_img_on_screen(
                f"{SCRIPT_DIR}/img/content_types/video icon.png")
        ]

        if any(possible_icons):
            search_page_loaded = True
# endregion wait_search_page_to_load() ---------------------- wait_search_page_to_load()


# region go_to_search_page(...) ================================= go_to_search_page(...)
def go_to_search_page(search_options: Options):
    time.sleep(10)
    wait_for_login_to_be_successful()

    # DRIVER.get(url) # not going to url directly now

    # assuming it is on oreilly "home" page

    # get search field
    searchbox_xpath = "/html/body/div[1]/div/div/div[1]/div[1]/form/div/div/label/input"
    search_field = DRIVER.find_element_by_xpath(searchbox_xpath)
    # enter search term
    search_field.clear()
    search_field.send_keys(search_options.search_term)
    search_field.send_keys(Keys.ENTER)

    # return None # uncomment to test w/o saving pages

# endregion go_to_search_page(...) ------------------------------- go_to_search_page(...)


# region define_cli() ====================================================== define_cli()
def define_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Searches Oreilly for books")
    parser.add_argument("-s", "--search", type=str,
                        default="",
                        help="the term to search for (blank if missing)")

    parser.add_argument("-f", "--format",
                        type=Format, choices=list(Format),
                        default=Format(Format.ALL),
                        help="the format(type) of content")

    parser.add_argument("-S", "--sort-by",
                        type=SortBy,
                        choices=list(SortBy),
                        default=SortBy(SortBy.RELEVANCE),
                        help="how to sort the result")

    parser.add_argument("-p", "--publishers",
                        type=str,
                        nargs='*',
                        dest="publishers",
                        # action='',
                        help="list of publishers to narrow down the results")

    parser.add_argument("-t", "--topics",
                        type=str,
                        nargs='*',
                        dest="topics",
                        # action='',
                        help="list of topics to narrow down the results")

    parser.add_argument("-P", "--publication-date",
                        type=PublicationDate,
                        choices=list(PublicationDate),
                        default=PublicationDate(PublicationDate.ALL),
                        help="restrict search results to [date] up until now")

    parser.add_argument("-r", "--rating",
                        type=int, choices=[0,1,2,3,4,5],
                        default=0,
                        help="the minimum rating to show in the results")

    parser.add_argument("-R", "--reverse",
                        action='store_true',
                        help="start at the end of the results")

    parser.add_argument("-n", "--number-of-pages",
                        type=int,
                        dest="number_of_pages",
                        help="how many pages to process")

    parser.add_argument("-v", "--video-type",
                        type=VideoType,
                        choices=list(VideoType),
                        default=VideoType(VideoType.ALL),
                        dest="video_type",
                        help="filter type of video content")

    parser.add_argument("-i", "--interactive-type",
                        type=InteractiveType,
                        choices=list(InteractiveType),
                        default=InteractiveType(InteractiveType.ALL),
                        dest="interactive_type",
                        help="filter type of interactive content")

    return parser

# endregion define_cli() --------------------------------------------------- define_cli()


# region parse_arguments() ============================================ parse_arguments()
def parse_arguments(argument_parser) -> Options:
    options = Options()

    args = argument_parser.parse_args()

    options.search_term = args.search
    options.format = args.format
    options.sort_by = args.sort_by
    options.topics = args.topics
    options.publishers = args.publishers
    options.min_pub_date = args.publication_date
    options.min_rating = args.rating
    options.reverse = args.reverse
    options.number_of_pages = args.number_of_pages

    if options.format == Format.VIDEOS:
        options.video_type = args.video_type
    else:
        options.video_type = None

    if options.format == Format.INTERACTIVE:
        options.interactive_type = args.interactive_type
    else:
        options.interactive_type = None

    return options
    ...

# endregion parse_arguments() ----------------------------------------- parse_arguments()


# region choose_search_results() =============================== choose_search_results()
def choose_content_type(
    search_options: Options,
    search_page_elements: SearchPageElements,
    ):
    """
    choose the content type to be displayed at the page,
    based on search_options, and using search_page_elemens
    as elements to be clicked on.

    Args:
        search_options (Options): the options the user chose on the command line
        search_page_elements (SearchPageElements): the "anchors" of elements on the page
    """

# TODO properly implement the format selection based on cli arguments
    global ACTIVE_CONTENT_FORMAT
    ACTIVE_CONTENT_FORMAT = search_options.format
    book_btn = search_page_elements.content_type.playlists
    book_btn.click()
    ACTIVE_CONTENT_FORMAT = Format(Format.PLAYLISTS)

    ...
# endregion choose_search_results() ----------------------------- choose_search_results()


# region get_content_type_elements() ======================= get_content_type_elements()
def get_content_type_elements(
    search_page_elements: SearchPageElements
    ) -> SearchPageElements:
    """gets the html elements for the content type buttons on the search results page"""

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[1]/button"
    search_page_elements.content_type.all = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[2]/button"
    search_page_elements.content_type.books = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[3]/button"
    search_page_elements.content_type.videos = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[4]/button"
    search_page_elements.content_type.live_events = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[5]/button"
    search_page_elements.content_type.learning_paths = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[6]/button"
    search_page_elements.content_type.playlists = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[7]/button"
    search_page_elements.content_type.interactive = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    xpath = \
"/html/body/div[1]/div/div/div[2]/main/div/div/header/section[2]/nav/ul/li[8]/button"
    search_page_elements.content_type.practice_exam = \
        DRIVER.find_element_by_xpath(xpath)
    del xpath

    return search_page_elements
# endregion get_content_type_elements() -------------------- get_content_type_elements()


# region get_filter_menus_elements(...) ================= get_filter_menus_elements(...)
def get_filter_menus_elements(
    search_page_elements: SearchPageElements
    ) -> SearchPageElements:
    """
    get the page elements for the filtering options, populates the search_page_elements
    object and returns it.

    Args:
        search_page_elements (SearchPageElements): the object containing the search
            page elements.

    Returns:
        SearchPageElements: the same object passed in now with all filter menus
        present on the page.
    """
    wrapper_xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]"
    wrapper_element:WebElement = DRIVER.find_element_by_xpath(wrapper_xpath)

    xpath = f"{wrapper_xpath}//button[contains(@class, 'Toggle')]"
    menu_elements_list = \
        wrapper_element.find_elements_by_xpath(xpath)
    del xpath

    for el in menu_elements_list:
        el: WebElement = el

        if "Topics" in el.text:
            search_page_elements.filtering_options.topics = el
        if "Publishers" in el.text:
            search_page_elements.filtering_options.publishers = el
        if "Publication Date" in el.text:
            search_page_elements.filtering_options.publication_date = el
        if "Rating" in el.text:
            search_page_elements.filtering_options.rating = el
        if "Video Type" in el.text:
            search_page_elements.filtering_options.video_type = el
        if "Interactive Type" in el.text:
            search_page_elements.filtering_options.interactive_type = el

    # possible xpath locations for the sort by dropdown menu, based on the
    # current type of content displayed on the page
    # a simpler way of getting it is to get the length of the
    # menu elements list and feeding it to the index of the last div
    # before button

    format_ = ACTIVE_CONTENT_FORMAT

    if format_ == Format.ALL:
        index = 1
    if format_ == Format.BOOKS or \
    format_ == Format.LEARNING_PATHS or \
    format_ == Format.PLAYLISTS:
        index = 2
    if format_ == Format.VIDEOS or \
    format_ == Format.INTERACTIVE:
        index = 3
    if format_ == Format.LIVE_EVENTS:
        index = None

    if index:
        sort_by_btn_xpath = \
f'/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[{index}]/button'
#     sort_by_btn_xpath_all = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[1]/button'
#     sort_by_btn_xpath_books = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[2]/button'
#     sort_by_btn_xpath_videos = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[3]/button'
#     # sort_by_btn_xpath_live_events = "not available(does not show)"
#     sort_by_btn_xpath_learning_paths = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[2]/button'
#     sort_by_btn_xpath_playlists = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[2]/button'
#     sort_by_btn_xpath_interactive = \
# '/html/body/div[1]/div/div/div[2]/main/div/div/header/section[3]/div[3]/button'

        sort_by_bnt_element: WebElement = DRIVER.find_element_by_xpath(sort_by_btn_xpath)
    # sort_by_bnt_element: WebElement = DRIVER.find_element_by_xpath(sort_by_btn_xpath)
    # sort_by_bnt_element: WebElement = DRIVER.find_element_by_name("Sort By")
    # sort_by_bnt_element: WebElement = DRIVER.find_element_by_partial_link_text("Sort By")

    ic(sort_by_bnt_element.tag_name)
    ic(sort_by_bnt_element.text)

    sort_by_bnt_element.click()
    search_page_elements.filtering_options.sort_by = sort_by_bnt_element
# TODO get the sort by element

    return search_page_elements
# endregion get_filter_menus_elements(...) -------------- get_filter_menus_elements(...)


# region main() ================================================================= main()
def main():
    parser = define_cli()
    search_options = parse_arguments(parser)
    setup_driver()

    login_oreilly()
    go_to_search_page(search_options)
    wait_search_page_to_load()
    search_page_elements = SearchPageElements()
    search_page_elements = get_content_type_elements(search_page_elements)
    choose_content_type(search_options, search_page_elements)
    search_page_elements = get_filter_menus_elements(search_page_elements)
    # TODO get the page elements fo the page numbers below the page
    # TODO apply filter using menus
    # TODO get page list
    # TODO make a loop to go to next page
    # print("at main")
    CONSOLE.print(search_page_elements)
    # DRIVER.close()
    CONSOLE.print("[bold green]finished[/]")
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    try:
        main()
    except Exception:
        CONSOLE.print_exception()
        if DRIVER:
            DRIVER.quit()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
