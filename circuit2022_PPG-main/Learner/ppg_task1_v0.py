"""
Version 0 of the web scraper (subtask 1 for the PPG project).
Takes in a file containing a starting URLS, starting keywords, and the
number of sites to scrape, and then scrapes the information into
tables to be used by later subtasks.
"""

from urllib.parse import urljoin

import requests
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
from requests.exceptions import TooManyRedirects

from bs4 import BeautifulSoup
import heapq
from datetime import date

from Learner import read_and_write
from Learner import webpage_chunker as chunker
from Learner import keyword_finder
from Learner import models

import re

image_table_index = 0  # global variable representing image table index for labeling database entries

"""
List of tuples of search terms. Ex: the user entering: 'grass AND apple' will return [(grass, apple)].
The user entering 'banana OR orange' will return [(banana), (orange)]. 

In order for a page to be valid, at least one of the tuples in the list must have ALL of its words
found as keywords on the page.

Ex: If the tuples are (APPLE, BANANA) and (CANTALOUPE, DRAGONFRUIT), and only APPLE and BANANA are found  
on the page, the page is valid. If only CANTALOUPE and BANANA are found, the page is invalid.
"""
search_terms = []


class URLObject:
    """
    Class that defines a URLObject, which allows URLS to be sorted by their relative
    relevance and prioritized in the link queue accordingly. __eq__, __lt__, and
    __gt__ are used to order the elements in the priority queue, by allowing
    URLObjects to be compared against each other; objects that are the "lowest"
    will be taken out of the queue first, so having a higher priority score will
    make an object "lower".
    """

    def __init__(self, url):
        """
        Initialize the URL Object.
        :param url: The input url string.
        """

        self.url = url
        self.search_terms = search_terms  # global variable containing a list of tuples of search terms
        self.priority_score = self.calc_priority_score()

    def __eq__(self, other):
        return self.priority_score == other.priority_score

    def __lt__(self, other):
        return self.priority_score > other.priority_score

    def __gt__(self, other):
        return self.priority_score < other.priority_score

    def calc_priority_score(self):
        """
        Calculate the score of a link based off of its properties and whether
        the url itself has keywords within it.

        :return: Score representing the priority; higher score meaning higher priority for scraping.
        """

        score = 0

        # add to the score if any search terms are present in the url.
        for search_group in self.search_terms:
            for syn_list in search_group:
                for term in syn_list:
                    if term in self.url:
                        score += 100

        # add to the score if the link is .org or .edu
        if '.org' in self.url or '.edu' in self.url:
            score += 30

        # longer urls tend to have worse results; de-prioritize them in the link queue.
        score -= len(self.url)

        return score


class URLKeywordObject:
    """
    This class holds information representing a "keyword_URL" object in the database.
    It contains a keyword, URL, score, and the date scraped.
    """

    def __init__(self, keyword, url, relevance_score):
        """
        Initialize the URLKeyword object with the input parameters and current date.

        :param keyword: A string representing the keyword.
        :param url: A string representing the URL.
        :param relevance_score: The relevance score for the keyword in the selected URL.
        """

        self.keyword = keyword
        self.url = url
        self.relevance_score = relevance_score
        self.date_scraped = date.today()


def convert(string):
    """
    Converts a string into a split list of words.
    
    :param string: The input string of seperate words.
    :return: A list of words in the string.
    """

    y = list(string.split(" "))
    return y


def set_header_to_first_normal_text(soup):
    """
    Sets the header to the first part of the normal text, in the event that
    no headers can be found in the document.
    
    :param soup: The BeautifulSoup object.
    :return: The title if it is found, False if scraping fails.
    """

    try:
        string_title = soup.find('p').get_text()
        x = convert(string_title)
        list_title = x[0:5]
        title = ''
        for x in list_title:
            title += ' ' + x

        return title

    except:
        return False


def search_for_header(soup, header_number):
    """
    Searches for the text of the header, for the designated header number (1-6).
    
    :param soup: BeautifulSoup object set up for the designated site.
    :param header_number: The header number (1-6) to look for text in.
    :return: The text in the header, if the header exists, or the text
    from the next option if the current header is not present.
    """

    header_string = "h" + str(header_number)

    try:
        return soup.find(header_string).get_text()
    except:
        # if header text at current number not found, try the next lowest header.
        # if we are already at the smallest header size (h6), just get the first
        # text found on the page.
        if header_number < 6:
            return search_for_header(soup, header_number + 1)
        else:
            return set_header_to_first_normal_text(soup)


def find_site_title(soup):
    """
    Finds the site title.
    
    :param soup: BeautifulSoup object, set up for the site.
    :return: The title if it is found, or False if it is not found.
    """

    try:
        return search_for_header(soup, 1)
    except:
        return False


def any_search_term_present(page_content):
    """
    :param page_content: The text found on the webpage.

    :return: True if for ANY tuple of words, ALL of them were found on
    the page. IE: if the tuples are (BANANA, APPLE) and (GRASS, FLOWER),
    and GRASS and APPLE are found on the page, return False. If
    BANANA and APPLE are found on the page, return True.
    """

    for search_term_group in search_terms:
        for syn_list in search_term_group:
            if not syn_list[0] in page_content:
                return False

    return True


def word_in_keywords(word, keywords):
    syns = synonym_antonym_extractor(word)
    for syn in syns:
        if syn in keywords:
            return True


def any_search_terms_in_keywords(keywords):
    """
    :param keywords: The keywords found on the scraped page.

    :return: True if for ANY tuple of words, ALL of them were found in
    the keywords. IE: if the tuples are (BANANA, APPLE) and (GRASS, FLOWER),
    and GRASS and APPLE are found on the page, return False. If
    BANANA and APPLE are found on the page, return True.
    """

    for search_term_group in search_terms:
        for syn_list in search_term_group:
            if not any(word in keywords for word in syn_list):
                return False

    return True


def any_problems_with_url(url):
    """
    Determines if there are any potential issues with an input url.
    
    :param url: The url to be checked.
    :return: True if there might be a problem, False if no problems detected.
    """

    problematic_sub_urls = ['#', 'File:', 'archive.org', 'books.google', 'file', 'twitter.com',
                            'facebook.com', 'instagram.com', 'youtube.com']

    for problematic_sub_url in problematic_sub_urls:
        if problematic_sub_url in url:
            return True

    return False


def url_already_discovered(url, discovered_links):
    """
    Determines if this URL has already been discovered. A URL has been discovered if it
    is already in the database, or has been added to the current iteration of the scraper queue.
    
    :param url: The URL we are asking about.
    :param discovered_links: The set of links discovered in the current scraper iteration
    :return: True if the link has been discovered before, False if not.
    """

    if url in discovered_links:
        return True

    if models.chunked.objects.filter(URL=url).exists():
        return True

    return False


def url_already_scraped(url):
    """
    Determines whether a URL has already been scraped. A URL has already been scraped if it is in
    the database, as opposed to only in the queue (this is the key difference between this method
    and url_already_discovered).

    :param url: The URL we are asking about.
    :return: True if the link has already been scraped and is in the database, False if the link
    is not found in the database.
    """

    if models.chunked.objects.filter(URL=url).exists():
        print('here')
        return True

    return False


def find_all_links_on_page(soup, current_page_url, link_queue, discovered_links):
    """
    Inserts all links found on a webpage into the link queue, adds them all
    to the set of discovered links, and returns the list of links found on the
    current page.
    
    :param soup: A BeautifulSoup object set up for the current webpage.
    :param current_page_url: The URL of the current page.
    :param link_queue: The queue of links to be visited.
    :param discovered_links: The set of links that have already been discovered.
    :return: A list containing all links found on the current page.
    """

    raw_links_found_on_page = soup.find_all('a')  # the 'raw' URLS; unformatted

    full_links_found_on_page = []  # used to store all full links found on this page

    # loop through all raw links, and format them as full URLS
    for raw_link in raw_links_found_on_page:
        # if raw_link.get('href') doesn't work, this is not a valid link
        # and should not be added to the queue or the spreadsheet
        # output.
        found_href_link = raw_link.get('href')

        if not found_href_link:
            continue

        # Url join creates a full link accessible from anywhere, instead
        # of the partial link scraped from the page. If urljoin doesn't
        # work, skip over the link, don't add it to the queue, and don't
        # add it to the output spreadsheet.
        try:
            full_discovered_url = urljoin(current_page_url, found_href_link)
        except:
            continue

        # if there are any issues with this link, don't use it for scraping
        if any_problems_with_url(full_discovered_url):
            continue

        # if this URL hasn't already been discovered before, add it to
        # queue of links to visit, add it to the set of discovered links,
        # and add it to the list of the links found on the current page.
        if not url_already_discovered(full_discovered_url, discovered_links):
            # add the link to the set of discovered links so we don't revisit it
            discovered_links.add(full_discovered_url)

            # if the score of the URLObject is high enough, then add it to the
            # URLObject priority queue, so that the link can eventually be
            # scraped
            new_url_object = URLObject(full_discovered_url)
            if new_url_object.priority_score > 0:
                heapq.heappush(link_queue, new_url_object)
                full_links_found_on_page.append(full_discovered_url)

    return full_links_found_on_page


def get_subtopics(keyword):
    link = 'https://en.wikipedia.org/wiki/' + keyword

    try:
        response = requests.get(link, timeout=5)
    except ConnectionError:
        print("Connection error!")
        return False
    except HTTPError:
        print("HTTP Error")
        return False
    except Timeout:
        print("Timeout while scraping link :(")
        return False
    except TooManyRedirects:
        print("Too many redirects")
        return False
    except:
        print("Generic problem with link")
        return False

    # set up beautiful soup object to scrape the text from the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the site title. If the method to find the title fails, return False and do
    # not scrape this page.

    sub_headers = soup.find_all('h2')
    topics_list = []

    dont_include = ['Contents', 'See also', 'References', 'Further reading', 'External links',
                    'Navigation menu','Other uses']

    for topic in sub_headers:
        true_topic = topic.text.replace('[edit]','')
        if true_topic not in dont_include:
            topics_list.append(true_topic)

    return topics_list



def wikipedia_page(link):
    return ''

    try:
        response = requests.get(link, timeout=5)
    except ConnectionError:
        print("Connection error!")
        return False
    except HTTPError:
        print("HTTP Error")
        return False
    except Timeout:
        print("Timeout while scraping link :(")
        return False
    except TooManyRedirects:
        print("Too many redirects")
        return False
    except:
        print("Generic problem with link")
        return False

    # set up beautiful soup object to scrape the text from the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the site title. If the method to find the title fails, return False and do
    # not scrape this page.

    sub_headers = soup.find_all('h2')
    topics_list = []

    dont_include = ['Contents', 'See also', 'References', 'Further reading', 'External links',
                    'Navigation menu','Other uses']

    for topic in sub_headers:
        true_topic = topic.text.replace('[edit]','')
        if true_topic not in dont_include:
            topics_list.append(true_topic)

    print("This is a broad topic, please select which subtopics interest you the most.")

    print(topics_list)

    selected = int(input("Please enter the cooresponding number!"))

    if selected < 0:
        return ''
    else:
        return topics_list[selected]


def scrape_page(link, link_queue, links_discovered, image_dict, associated_keywords_dict):
    """
    Scrapes a webpage, finding all relevant information on the site, including the title, keywords,
    referenced URLS, images, videos, and chunked content. A page is only scraped if it matches
    at least one of the search terms, and throws no errors during the scraping process.
    
    :param link: The URL of the site.
    :param link_queue: The queue of links to be visited.
    :param links_discovered: The set of links already visited.
    :param image_dict: The dictionary of images to be used.
    :return: A list containing the site's URL, title, all keywords, all referenced URLS, all images,
    all videos, and the chunked text. Returns False if no search terms are matched or if exceptions
    are thrown during the scraping process.
    """

    # try to setup the site for scraping at the given url. If response
    # returns false, return false from the method and don't attempt to scrape
    # the page.
    try:
        response = requests.get(link, timeout=5)
    except ConnectionError:
        print("Connection error!")
        return False
    except HTTPError:
        print("HTTP Error")
        return False
    except Timeout:
        print("Timeout while scraping link :(")
        return False
    except TooManyRedirects:
        print("Too many redirects")
        return False
    except:
        print("Generic problem with link")
        return False

    # set up beautiful soup object to scrape the text from the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the site title. If the method to find the title fails, return False and do
    # not scrape this page.
    title = find_site_title(soup)

    if not title:
        return False

    # scrape all text content from the page
    content = soup.get_text()

    # If none of the search terms are in the text, quit scraping early and return False.
    if not any_search_term_present(content):
        return False

    # Get the list of keywords on the page.
    keywords_found_on_page = keyword_finder.get_keywords(
        content.casefold(), title.casefold(), link, 15)

    print('keywords found on page')
    print(keywords_found_on_page)

    # If none of the keywords found on the page match the search terms, return False and
    # do not continue scraping this page.
    if not any_search_term_present(keywords_found_on_page[0]):
        return False

    associated_keywords_dict['number_of_visits'] += 1

    for word in keywords_found_on_page[0]:
        if word not in associated_keywords_dict:
            associated_keywords_dict[word] = 1
        else:
            associated_keywords_dict[word] += 1

    keywords_to_keep = keywords_found_on_page[0][0:5]
    scores_to_keep = keywords_found_on_page[1][0:5]
    keywords_found_on_page = [keywords_to_keep, scores_to_keep]
    print('keywords to keep')
    print(keywords_found_on_page)

    # Find all referenced links on the page.
    links_found_on_page = find_all_links_on_page(
        soup, link, link_queue, links_discovered)

    # Create a string containing all images found on the page.
    image_list = []

    global image_table_index

    images = soup.find_all('img', width=True, height=True)

    viable_images = {}

    # go through images. If the image has valid alt text and isn't too small,
    # add it to the viable_images dictionary, where the keys are the full image
    # urls and the values are the corresponding image alt text.
    for img in images:
        if img.has_attr('src'):
            try:
                to_open = urljoin(link, img['src'])
                img_width = int(img['width'].replace('px',''))
                img_height = int(img['height'].replace('px',''))
                alt_text = img['alt'].casefold()
                if img_width > 80 and img_height > 80:
                    viable_images[to_open] = alt_text
            except:
                print('error with image')


    # encode content using utf-8, may need to decode before task 2,
    # but possibly before task 3
    # .encode('utf-8', 'ignore')

    # this method chunks the page, and also fills out the image list in the process.
    chunking_output = chunker.chunkify(
        str(soup), image_table_index, link, image_dict, image_list, viable_images)

    # if chunkify returns False, there was an issue; exit and return False.
    if not chunking_output:
        return False

    chunks_dictionary = chunking_output[0]
    image_table_index = chunking_output[1]

    # A list with 2 items:
    # A sublist of link, title, keywords, images, and videos
    # AND
    # The chunks dictionary, which stores a chunk title and a list of its associated
    # parameters: text, images, and keywords
    if url_already_scraped(link) and len(link_queue) > 2:
        return False

    return [title, keywords_found_on_page, chunks_dictionary]


def write_to_keyword_list(keywords_found_on_page, url_and_keyword_list, link):
    """
    Writes a newly discovered link associated with any keyword(s) into
    the keyword:URL dictionary.
    
    :param keywords_found_on_page: The keywords associated with the URL.
    :param url_and_keyword_list: The list of URL-Keyword Objects.
    :param link: The URL of the new site, to be added to dictionary in
    for all keywords it is associated with.
    :return: None
    """

    actual_keywords = keywords_found_on_page[0]
    keyword_frequencies = keywords_found_on_page[1]

    num_keywords = len(actual_keywords)

    for i in range(0, num_keywords):
        url_keyword_object = URLKeywordObject(
            actual_keywords[i], link, keyword_frequencies[i])
        url_and_keyword_list.append(url_keyword_object)


def save_link_queue(link_queue, input_keywords_list):
    """
    Saves the queue of links as a LinkQueues object in the database, to be used
    to start the web scraper again for the same word in the future.
    
    :param link_queue: The queue of links.
    :param input_keywords_list: The list of keywords the user entered.
    :return: None.
    """

    if len(input_keywords_list) != 1:
        return

    if len(input_keywords_list[0]) != 1:
        return

    print("saving queue")
    print(input_keywords_list)

    links_to_store = []

    num_links_to_store = 10
    num_links_stored = 0

    while num_links_stored < num_links_to_store and link_queue:
        links_to_store.append(heapq.heappop(link_queue).url)
        num_links_stored += 1

    # only store the 10 links if enough links were found to do this without error
    if num_links_stored == num_links_to_store:
        if models.LinkQueue.objects.filter(keyword_text=input_keywords_list[0][0]).exists():
            saved_link_queue = models.LinkQueue.objects.get(keyword_text=input_keywords_list[0][0])
            saved_link_queue.link0 = links_to_store[0]
            saved_link_queue.link1 = links_to_store[1]
            saved_link_queue.link2 = links_to_store[2]
            saved_link_queue.link3 = links_to_store[3]
            saved_link_queue.link4 = links_to_store[4]
            saved_link_queue.link5 = links_to_store[5]
            saved_link_queue.link6 = links_to_store[6]
            saved_link_queue.link7 = links_to_store[7]
            saved_link_queue.link8 = links_to_store[8]
            saved_link_queue.link9 = links_to_store[9]
        else:
            saved_link_queue = models.LinkQueue.objects.create(keyword_text=input_keywords_list[0][0],
                                                               link0=links_to_store[0],
                                                               link1=links_to_store[1], link2=links_to_store[2],
                                                               link3=links_to_store[3],
                                                               link4=links_to_store[4], link5=links_to_store[5],
                                                               link6=links_to_store[6],
                                                               link7=links_to_store[7], link8=links_to_store[8],
                                                               link9=links_to_store[9])

        saved_link_queue.save()


def synonym_antonym_extractor(phrase):
    from nltk.corpus import wordnet
    synonyms = []
    antonyms = []

    for syn in wordnet.synsets(phrase):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

    print(set(synonyms))
    print(set(antonyms))

    return tuple(synonyms)


def start_scraper(input_keywords, num_pages):
    """
    Start the web scraper, opening the output file for table 1 to write to
    it as we scrape each webpage.
    :return:
    """
    # replace each search term with tuple of search terms (all synonyms)

    #print(synonym_antonym_extractor('computing'))

    global search_terms

    # take the input keywords and convert them into the correct format for the
    # search terms: a list of tuples. all keywords separate by or go into distinct
    # tuples, while all separated by and become separate entries in the same tuple
    original_string = input_keywords
    input_keywords = input_keywords.casefold()
    and_split_input_keywords_list = input_keywords.split(' or ')
    input_keywords_list = []

    for section in and_split_input_keywords_list:
        # input_keywords_list.append(tuple(section.split(' and ')))
        to_append = re.split(' and | ', section)
        real_to_append = []
        for entry in to_append:
            real_to_append.append(synonym_antonym_extractor(entry))
        #for smaller_word in to_append:
        #synonym_antonym_extractor(phrase=smaller_word)

        input_keywords_list.append(tuple(real_to_append))

    print(input_keywords_list)

    input_info = read_and_write.get_input_parameters(input_keywords_list, original_string)

    return run_scraper(input_info, num_pages, input_keywords_list, original_string)


def run_scraper(input_info, num_pages, input_keywords_list, original_string):
    """
    Start the web scraper, opening the output file for table 1 to write to
    it as we scrape each webpage.
    :return:
    """

    associated_keywords_dict = {}
    associated_keywords_dict['number_of_visits'] = 0

    global search_terms

    link_queue = input_info[0]  # queue of links to be visited
    search_terms = input_info[1]  # search terms entered by the user
    total_sites_to_scrape = num_pages  # number of websites to scrape

    # convert the link queue into a queue of URLObjects instead of a queue of
    # strings representing URLS
    temp_link_queue = link_queue
    link_queue = []

    for item in temp_link_queue:
        link_queue.append(URLObject(item))

    # make the link queue a priority queue
    heapq.heapify(link_queue)

    ordered_chunks = []
    heapq.heapify(ordered_chunks)

    global image_table_index
    # find the current image table index
    image_table_index = read_and_write.get_current_image_index()
    # make a new dictionary to store all images in this iteration of the web scraper
    image_dict = {}

    # set of links that have already been discovered; don't revisit
    links_discovered = set()

    num_iterations = 0

    # keyword_list = read_and_write.read_from_keyword_table()  # keyword map
    keyword_list = []

    # Open the output file to write to.

    chunk_id = read_and_write.get_current_chunk_id()
    prev_id = chunk_id

    # While the queue of links still has elements, and we haven't scraped as many
    # sites as the user asked for, continue to scrape the next page in the queue,
    # outputting all information found to the spreadsheet and adding any new
    # links found to the end of the queue.
    print('link queue')
    print(link_queue)
    while link_queue and num_iterations < total_sites_to_scrape:
        # get the URLObject with the next highest priority in the queue
        next_node = heapq.heappop(link_queue).url
        print(next_node)
        print(num_iterations)

        # get the page info by scraping the page
        page_info = scrape_page(
            next_node, link_queue, links_discovered, image_dict, associated_keywords_dict)

        if page_info:
            num_iterations += 1
            url_title = page_info[0]
            url_keywords = page_info[1]
            chunks_list = page_info[2]
            write_to_keyword_list(url_keywords, keyword_list, next_node)

            # write the information in each chunk to its own row in the database
            for chunk in chunks_list:
                chunk.id = chunk_id
                heapq.heappush(ordered_chunks, chunk)
                output_row = chunk.convert_to_list_for_output(
                    url_title, url_keywords[0])
                read_and_write.write_row_to_url_table(output_row, image_dict, chunk_id, original_string)
                chunk_id += 1
                # write_to_keyword_list(output_row[2], keyword_list, next_node)

    # write the keyword-url objects to their table
    read_and_write.write_to_keyword_table(keyword_list)

    # save the next 10 object in the link queue, if there are at least 10 object available
    save_link_queue(link_queue, input_keywords_list)

    print(associated_keywords_dict)
    print(associated_keywords_dict['number_of_visits'])
    num_visits = associated_keywords_dict['number_of_visits']

    for key, value in associated_keywords_dict.items():
        if key != 'number_of_visits' and value/num_visits > 0.2:
            print(key)

    print(ordered_chunks)
    if ordered_chunks:
        start_chunk = heapq.heappop(ordered_chunks)
        start_chunk_in_database = models.chunked.objects.get(chunkID=start_chunk.id)

    while ordered_chunks:
        end_chunk = heapq.heappop(ordered_chunks)
        # print(end_chunk.id)

        start_chunk_in_database.next_chunk = end_chunk.id
        start_chunk_in_database.save()

        start_chunk_in_database = models.chunked.objects.get(chunkID=end_chunk.id)

    print('ids to print:')
    print(prev_id)
    print(chunk_id)

    to_return_back = [prev_id, chunk_id]
    print(to_return_back)

    return to_return_back
