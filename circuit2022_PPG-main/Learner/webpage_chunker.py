"""
Module containing methods to chunk raw HTML text into well-formatted pieces.
"""

import re
from urllib.parse import urljoin
from Learner import keyword_finder

import textstat


image_label_number_for_chunks = 0
image_index_for_image_table = 0

order_index = 0


class Chunk:
    """
    Class representing all the information (url, ttle, keywords, images, text) contained in a webpage chunk.
    Each row of the chunks table in the database represents a single chunk.
    """

    def __init__(self, url, title, keywords, images, text):
        self.url = url
        self.title = title
        self.keywords = keywords
        self.images = images
        self.text = text
        self.order_index = self.calc_order_index()
        self.id = 0
        self.reading_score = self.get_reading_ease_score()

    def convert_to_list_for_output(self, url_title, url_keywords):
        """
        Converts the chunk object into a list to output to the database.

        :param url_title: The entire website's title.
        :param url_keywords: The keywords from the entire website.
        :return: List containing all the chunk's information.
        """

        url_title = url_title.replace('[edit]', '')
        self.title = self.title.replace('[edit]', '')

        # union the keywords from the chunk and the URL as a whole.
        url_keyword_set = set(url_keywords)
        individual_keyword_set = set(self.keywords[0])
        overall_keywords = individual_keyword_set | url_keyword_set

        return [self.url, url_title, self.title, overall_keywords, self.images, self.text]

    def calc_order_index(self):
        global order_index
        order_index += 1
        return order_index

    def get_reading_ease_score(self):
        return textstat.flesch_reading_ease(self.text)

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        if self.url == other.url:
            return self.order_index < other.order_index
        else:
            return self.reading_score > other.reading_score

    def __gt__(self, other):
        if self.url == other.url:
            return self.order_index > other.order_index
        else:
            return self.reading_score < other.reading_score


def chunkify(html_to_chunk, input_image_label_number_for_chunks, link, image_dict, image_list, viable_images):
    """
    Takes in raw html text, and returns a formatted string representing a dictionary
    associating chunk names with chunks of text from the page.

    :param html_to_chunk: The raw html text to be chunked.
    :param input_image_label_number_for_chunks: The image table index we should start with when
    chunking the text and adding images to the image table (table 3).
    :param link: The link to the webpage we are currently working with.
    :param image_dict: A dictionary of indices to images to be written to the
    image table.
    :param image_list: A list of images found on the page, to be filled out
    during the chunking process.
    :return: A list containing the filled out chunks dictionary and the new,
    updated image table index.
    """

    global image_label_number_for_chunks
    global image_index_for_image_table
    image_label_number_for_chunks = input_image_label_number_for_chunks
    image_index_for_image_table = input_image_label_number_for_chunks

    # create new list
    chunks = []

    # find indices of all html header opening tags; store into a list
    # (list is opening_indices)
    opening_indices_object = re.finditer(pattern='<h\d', string=html_to_chunk)
    opening_indices = [index.start() for index in opening_indices_object]

    # find indices of all html header closing tags; store into a list
    # (list is closing_indices)
    closing_indices_object = re.finditer(pattern='/h\d>', string=html_to_chunk)
    closing_indices = [index.start() for index in closing_indices_object]

    # define variables for loop; iterate until we hit the last opening
    # tag index in the list of opening tag indices
    i = 0
    length = len(opening_indices) - 1

    smaller_image_list = []

    # add key:value pairs to the chunks dictionary for each iteration of
    # the loop
    while i < length:
        try:
            smaller_image_list = []
            # start of key substring is determined by the next value in the
            # opening_indices list.
            start = opening_indices[i]

            # end of key substring is determined by the next value in the
            # closing_indices list. +4 to arrive at the very end of the
            # substring /h\d>. This is also the start of the value
            # substring.
            end = closing_indices[i] + 4

            # This represents the starting index for the next key substring,
            # which is also the ending index for the current value substring.
            next_start = opening_indices[i + 1]

            # key is the cleaned up version of the substring from start to end.
            key = clean_html(html_to_chunk[start:end])

            # value is the cleaned up version of the substring from end to
            # next_start
            value = html_to_chunk[end:next_start]
            final_text = format_text_block(value, link, image_dict, image_list, smaller_image_list, viable_images)

            # if the value substring is <= 20 characters, don't add this pair
            # to the dictionary
            if len(final_text) > 150:
                chunk_keywords = keyword_finder.get_keywords(final_text, key, link, 2)
                new_chunk = Chunk(link, key, chunk_keywords, smaller_image_list, final_text)
                chunks.append(new_chunk)

            i += 1

        except:
            return False

    # return false if there are fewer than 2 entries in the dictionary
    if len(chunks) < 1:
        return False

    return [chunks, image_index_for_image_table]


# Used for removing html tags in clean_html().
cleaner = re.compile('<.*?>')


def clean_html(raw_html):
    """
    Removes html tags from text, and deletes newlines, to format text for output.

    :param raw_html: Raw html text.
    :return: Formatted text with html tags removed.
    """

    # Remove everything between <>s to get rid of html tags.
    cleantext = re.sub(cleaner, '', raw_html)

    # Replace newlines with spaces.
    cleantext = cleantext.replace('\n', ' ')
    cleantext = cleantext.replace('\xa0', ' ')

    if 'mw-parser-output' in cleantext:
        cleantext = cleantext.replace('mw-parser-output','')

    return cleantext


def add_image_to_image_table(raw_html, start_index, link, image_dict, image_list, smaller_image_list , viable_images):
    """
    Finds an image link in the raw html text, and adds it to the image map and list of
    images on the page (this will affect table 3 and table 1).
    :param raw_html: The raw HTML text.
    :param start_index: The starting index of the image div.
    :param link: The link to the webpage we are currently scraping.
    :param image_dict: The dictionary of images, for the image table (table 3).
    :param image_list: The list of images, for table 1.
    :return:
    """

    global image_index_for_image_table

    # cut off the html so it starts where the image div starts
    image_string = raw_html[start_index:]

    # find the "actual" starting place; where src is located directly precedes the actual link
    real_start = image_string.find('src=') + 5

    # get the string to start where the actual image link starts
    image_string = image_string[real_start:]

    # the end of the image link will be a double quote in the raw html
    end = image_string.find('"')

    # partial_url represents the portion stored in the page's html
    partial_url = image_string[0:end]

    # url join creates the full url, store it in final_url
    final_url = urljoin(link, partial_url)

    if final_url not in viable_images:
        return ''

    # insert image into the map of image indices to actual images

    # put the link into the map of the image indices the actual images
    image_dict[image_index_for_image_table] = final_url

    image_list.append(image_index_for_image_table)

    smaller_image_list.append(image_index_for_image_table)

    # increase the alt image index by 1
    image_index_for_image_table += 1

    # append the image to the list of images to be written in table 1
    # image_list.append(final_url)

    image_string = '<img src="' + final_url + '" alt = "' + viable_images[final_url] + '">' + '\n\n'

    return image_string


def format_text_block(raw_html, link, image_dict, image_list, smaller_image_list, viable_images):
    """
    Takes in section of html text and outputs all paragraphs and image tags
    in a formatted string.

    :param raw_html: The raw HTML text.
    :param link: The URL of the page we are currently scraping.
    :param image_dict: A dictionary of indices to images, to be written to table 3.
    :param image_list: A list of images found on the page, to be written to table 1.
    :return:
    """

    global image_index_for_image_table
    global image_label_number_for_chunks

    # get list of all indices where paragraphs start
    start_paragraph_indices = find_all_indices_of_substring(raw_html, '<p')

    # get list of all indices where paragraphs end
    end_indices = find_all_indices_of_substring(raw_html, '</p>')

    # get list of all indices where images start
    image_indices = find_all_indices_of_substring(raw_html, '<img')

    write_to_image_label_number_for_chunks = 0

    # get number of images  in this chunk
    num_images = len(image_indices)

    # counters for the current image number we are on; initialize to 0
    image_number = 0

    # start return string as an empty string
    return_string = ''

    # initialize i as a counter variable for the while loop; set
    # length to the end condition (the number of end indices)
    i = 0
    length = len(end_indices)
    if len(start_paragraph_indices) < length:
        length = len(start_paragraph_indices)

    if len(start_paragraph_indices) <= 0 or len(end_indices) <= 0:
        return 'ERROR'

    counter = 0

    # go through all paragraphs, and append them, using their starting
    # and ending indices. If there is an image , append the tag for
    # image between the paragraphs being written
    while i < length:
        start = start_paragraph_indices[i]
        end = end_indices[i]

        # add images if their index is before the next paragraph
        if counter < num_images and image_indices[image_number] < start:
            # IMAGE 0 NOTATION
            # to_add = 'IMAGE' + str(image_label_number_for_chunks) + '\n\n'
            start_index = image_indices[image_number]

            counter += 1
            image_number += 1

            to_add = add_image_to_image_table(raw_html, start_index, link, image_dict, image_list, smaller_image_list, viable_images)
            if len(to_add) > 1:
                return_string += to_add
                # image_number += 1
                write_to_image_label_number_for_chunks += 1
                image_label_number_for_chunks += 1

        i += 1
        return_string += clean_html(raw_html[start:end])

    # add all remaining images
    while counter < num_images:
        start_index = image_indices[image_number]
        to_add = 'IMAGE' + str(image_label_number_for_chunks) + '\n\n'
        counter += 1
        image_number += 1

        to_add = add_image_to_image_table(raw_html, start_index, link, image_dict, image_list, smaller_image_list, viable_images)
        if len(to_add) > 1:
            return_string += to_add
            # image_number += 1
            write_to_image_label_number_for_chunks += 1
            image_label_number_for_chunks += 1

    # return the final string, with the html removed
    return return_string


def find_all_indices_of_substring(main_string, substring):
    """
    Finds all indices of the substring in the main string, returning them
    as a list.

    :param main_string: The string to be searched.
    :param substring: The substring to be found.
    :return: A list of indices of all the substrings.
    """

    indices_object = re.finditer(pattern=substring, string=main_string)
    indices = [index.start() for index in indices_object]
    return indices
