#! /usr/bin/env python3

# spell-checker: word jolitp pyautogui lxml chdir
# spell-checker: word currentsrc cmdline xpath crdownload


# region imports
from pathlib import Path
import time
import datetime
from datetime import date
import os
import re
from dataclasses import dataclass, field

from rich.console import Console
from rich.traceback import install as rich_traceback_install

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
# endregion constants


# TODO move to other script
# region classes

@dataclass
class Chapter:
    """A chapter from a book. contains sections."""
    filename: str = ""
    title: str = ""
    sections: list = field(default_factory=list)

    def __str__(self) -> str:
        result = f"[#00AAAA]filename[/]: [#FF8800]{self.filename}[/]\n"
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

    def is_early_release(self):
        today = datetime.datetime.today()
        book_date = self.publication_date

        if book_date > today:
            early_release = True
        else:
            early_release = False
        return early_release

    def print(self):
        string_repr = self.__str__()
        CONSOLE.print(string_repr)

# endregion classes


# region globals
BOOK_PAGES_DOWNLOADED = 0
BOOK_FOLDER_PATH = None
BOOK_DATA = Book()
# endregion globals


# region get_chapter_names() ======================================= get_chapter_names()
def get_chapter_names(chapter_files):
# TODO redo this, make it open each file and search for the h1
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
# TODO redo the way chapter and section names are found
# find the h1, h2 etc
            section_elements = soup.find_all("section",
                                            attrs={"data-pdf-bookmark":True})
            for section in section_elements:
                section = str(section)
                pattern = re.compile('(<section data-pdf-bookmark=")(.*)(" data)')
                matched = pattern.match(section)
                title = matched.group(2)
                sections.append(title)
            chapter_sections.append(sections)
    return chapter_sections
# endregion get_chapter_sections() -------------------------------- get_chapter_sections()


# region filter_html_files() ======================================= filter_html_files()
def filter_html_files(file_list:list) -> list:
    filtered_files = []
    for file in file_list:
        file = str(file)
        if file.endswith(".html"):
            filtered_files.append(file)
    return filtered_files
# endregion filter_html_files() ------------------------------------ filter_html_files()


# region get_saved_pages() ============================================ get_saved_pages()
def get_saved_pages() -> list:
    chapter_files = os.listdir(BOOK_FOLDER_PATH)
    chapter_files = natsorted(chapter_files, alg=ns.PATH)
    chapter_files = filter_html_files(chapter_files)
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
    chapter_files = filter_html_files(chapter_files)
    # ic(chapter_files)
    chapter_filenames = get_saved_pages()
    chapter_titles = get_chapter_names(chapter_files)
    chapter_sections = get_chapter_sections(chapter_files)

    for filename, title, sections in zip(
        chapter_filenames, chapter_titles, chapter_sections):
        chapter_data = Chapter()
        chapter_data.filename = filename
        chapter_data.filename = title
        chapter_data.sections = sections
        # chapter_data.print()
        global BOOK_DATA
        BOOK_DATA.chapters.append(chapter_data)
# endregion get_chapter_hierarchy() ============================= get_chapter_hierarchy()


# region et_data_from_saved_page() =========================== get_data_from_saved_page()
def get_data_from_saved_page():
    main_page_file = get_main_page_from_saved_files()

    with open(BOOK_FOLDER_PATH / main_page_file, "r") as file_obj:
        soup = BeautifulSoup(file_obj, features="lxml")
# region get author's name
        element = soup.find("div", attrs={"class" : re.compile("contributors--*")})
        BOOK_DATA.author = element.a.text
        del element
# endregion get author's name
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
        n_of_stars = int(first_line[0])
        BOOK_DATA.stars = n_of_stars
# endregion get average rating
# endregion et_data_from_saved_page() ======================== get_data_from_saved_page()


# TODO move to other script
# region get_book_data_from_files() ========================== get_book_data_from_files()
def get_book_data_from_files():
    get_chapter_hierarchy() # DONE comment to toggle
    get_data_from_saved_page()
    # TODO about the publisher
    # TODO resources sections
    # TODO get errata link (resources)
    # TODO make org file with book info

    # BOOK_DATA.print()
# endregion get_book_data_from_files() ---------------------- get_book_data_from_files()


# TODO move to other script
# region create_org_file() =========================================== create_org_file()
def create_org_file():
    lines = ""

    # title
    lines += f"* {BOOK_DATA.title}\n"
    # authors
    lines += f"** Author(s): ={BOOK_DATA.author}=\n"
    # publication date
    publication_date_fmt= BOOK_DATA.publication_date.strftime("%Y-%m-00")
    lines += f"** Publication date: <{publication_date_fmt}>\n"
    # early release
    is_early_release = BOOK_DATA.is_early_release()
    todays_date = datetime.datetime.today()
    todays_date_fmt = todays_date.strftime("%Y-%m-%d %a")
    if is_early_release:
        lines += f"the book is yet to be finished at <{todays_date_fmt}>\n"
        lines += f"redownload it after <{publication_date_fmt}>"
    else:
        lines += f"the book was already finished at <{todays_date_fmt}>\n"
    # average rate (stars)
    filled_star = "★"
    hollow_star = "☆"
    filled_stars = filled_star * BOOK_DATA.stars
    hollow_stars = hollow_star * (5 - BOOK_DATA.stars)
    stars = filled_stars + hollow_stars
    if BOOK_DATA.stars == 0:
        stars = "N/A"
    lines += f"** Average rate: ={stars}=\n"
    # time to read
    estimated_time = BOOK_DATA.time_to_complete
    ic(estimated_time)
    estimated_time_fmt = estimated_time.strftime("%Hh %Mm")
    lines += f"** Estimated time to read: ={estimated_time_fmt}=\n"
    # topic
    topic = BOOK_DATA.topics
    lines += f"** Topics: {topic.name}\n{topic.link}\n"
    # description
    desc = BOOK_DATA.description
    lines += f"** Description\n#+begin_src markdown\n\n{desc}\n#+end_src\n"
    # chapters

    BOOK_DATA.print()
# endregion create_org_file() ======================================== create_org_file()

# region main() ================================================================= main()
def main():
    # get_book_data_from_files()
    # create_org_file()
    CONSOLE.print("[bold green]finished[/]")
# endregion main() -------------------------------------------------------------- main()


# region if __name__ == '__main__': ========================== if __name__ == '__main__':
if __name__ == '__main__':
    try:
        main()
    except Exception:
        CONSOLE.print_exception()
# endregion if __name__ == '__main__': ----------------------- if __name__ == '__main__':
