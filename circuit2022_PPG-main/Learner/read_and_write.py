"""
Module containing methods that read and write from input/output files/databases.
"""

import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import inflect
import heapq

from django.conf import settings
from django.utils.timezone import make_aware

from django.db.models import ManyToManyField

input_file_name = 'Learner/scraper_input.txt'

from Learner import models
from Learner import ppg_task1_v0

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def read_from_keyword_table():
    """
    Reads input from the keyword table (currently a CSV file) and stores
    it into a dictionary associating keywords with all links they have been
    found on. This method is temporary; a database will be directly used
    instead of a CSV and dictionary in future versions.

    :return: Dictionary of keywords:urls.
    """

    temp_keyword_map = {}

    # with open(keyword_map_name, 'r') as keyword_map_file:
    #     reader = csv.reader(keyword_map_file)
    #
    #    for row in reader:
    #        temp_keyword_map[row[0]] = row[1]

    # keyword_map_file.close()
    return temp_keyword_map


def write_to_keyword_table(keyword_list):
    """
    Writes keywords from a dictionary to the output keyword table, currently
    a CSV file. This method is temporary; a database will be directly used
    instead of a CSV and dictionary in future versions.

    :param temp_keyword_map: Dictionary of keywords: urls.
    :return: None.
    """

    naive_datetime = datetime.now()

    # settings.TIME_ZONE  # 'UTC'
    aware_datetime = make_aware(naive_datetime)

    for row in keyword_list:
        tester = models.keyword_URL.objects.create(keyword_text=row.keyword, individual_URL=row.url,
                                                   date_scraped=aware_datetime, score=row.relevance_score)
        tester.save()


def write_row_to_url_table(row, image_dict, chunk_id, search_string):
    """
    Writes a list (row) to the URL table. Currently, this is a CSV, but it will
    eventually be replaced with a database.

    :param csv_writer: The CSV writer that writes to the opened CSV file.
    :param row: A list of entries to be written to the next row on the CSV.
    :return: None.
    """

    keyword_string = ''

    for word in row[3]:
        keyword_string += word + ','

    tester = models.chunked.objects.create(text=row[5], keywords=keyword_string, page_title=row[1], chunk_title=row[2],
                                           URL=row[0], coreqs='', chunkID=chunk_id, topic=search_string)
    tester.save()

    # print(row[3])
    for image_num in row[4]:
        tester2 = models.image.objects.create(image_id=image_num, URL=row[0], image_path=image_dict[image_num],
                                              image_code=image_num)
        tester2.save()
        tester.images.add(models.image.objects.get(image_id=image_num))


urls = [
    'https://www.google.com/search?q='
]


def get_links_from_google(link_queue, input_keyword, original_string):
    """
    Gets links from a google search to start the queue, based on an input keyword.

    :param link_queue: Queue of links to be visited.
    :param input_keyword: The input keyword to search for links for.
    :return: None.
    """

    options = Options()
    options.headless = True
    driver = webdriver.Chrome("Learner/chromedriver", options=options)

    soup = ''

    #true_keyword = ''
    #for word in input_keyword:
        #true_keyword += (word + ' ')

    for url in urls:
        to_add_to_search = original_string.replace(' ', '+')
        #url_to_get = url + true_keyword
        url_to_get = url + to_add_to_search
        print(url_to_get)
        driver.get(url_to_get)
        try:
            elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "g"))  # This is a dummy element
            )
        except:
            print('google search failed')
        finally:
            print('finally')
        # driver.quit()

        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'lxml')

    results = soup.find_all('a')

    for raw_link in results:
        # if raw_link.get('href') doesn't work, this is not a valid link
        # and should not be added to the queue or the spreadsheet
        # output.
        found_href_link = raw_link.get('href')

        if not found_href_link:
            continue

        if ppg_task1_v0.any_problems_with_url(found_href_link):
            continue

        if 'https' in found_href_link and 'google' not in found_href_link:
            link_queue.append(found_href_link)

        if '/url?q=' in found_href_link and '.html' in found_href_link and 'google' not in found_href_link:
            clean_link = found_href_link.replace('/url?q=', '')
            end = clean_link.find('.html')
            clean_link = clean_link[:end + 5]
            link_queue.append(clean_link)


def get_input_parameters(original_keywords, original_string):
    """
    Gets the input parameters stored in the input file. Parameters are:
    starting URLS, keywords, anti-keywords, and number of sites to scrape.

    :return: List containing all input parameters.
    """

    p = inflect.engine()

    input_keywords = []

    #for section in original_keywords:
        #new_section = []
        #for original_word in section:
            #if not p.singular_noun(original_word):
                #new_section.append(original_word)
            #else:
                #new_section.append(p.singular_noun(original_word))

        #input_keywords.append(tuple(new_section))

    target = 1

    link_queue = []
    keywords = set()

    for input_keyword in input_keywords:
        if len(input_keyword) == 1:
            if models.LinkQueue.objects.filter(keyword_text=input_keyword[0][0]).exists():
                queue_of_links = models.LinkQueue.objects.get(keyword_text=input_keyword[0][0])
                link_queue.append(queue_of_links.link0)
                link_queue.append(queue_of_links.link1)
                link_queue.append(queue_of_links.link2)
                link_queue.append(queue_of_links.link3)
                link_queue.append(queue_of_links.link4)
                link_queue.append(queue_of_links.link5)
                link_queue.append(queue_of_links.link6)
                link_queue.append(queue_of_links.link7)
                link_queue.append(queue_of_links.link8)
                link_queue.append(queue_of_links.link9)

    print('here')
    for input_keyword in original_keywords:
        print('here')
        if len(input_keyword) == 1:
            for word in input_keyword:
                keywords.add(word[0])
                link = 'https://en.wikipedia.org/wiki/' + word[0]
                if link not in link_queue:
                    # link_queue.append(link)
                    specified = ppg_task1_v0.wikipedia_page(link)
                    if specified != '':
                        # original_string = original_string + ' AND ' + specified
                        original_string = original_string + ' ' + specified
                        # keywords.add(specified)
                        # new_tuple = input_keyword + (specified,)
                        # ppg_task1_v0.start_scraper(original_string, 10)

        get_links_from_google(link_queue, input_keyword, original_string)

    return [link_queue, input_keywords]


def get_current_image_index():
    """
    Gets the current image index, taken from the database.
    TODO: Implement.
    :return: Current image index (first empty index in image table).
    """
    try:
        return models.image.objects.latest('image_id').image_id + 1
    except:
        return 0


def get_current_chunk_id():
    """
    Gets the current image index, taken from the database.
    TODO: Implement.
    :return: Current image index (first empty index in image table).
    """
    try:
        return models.chunked.objects.latest('chunkID').chunkID + 1
    except:
        return 0
