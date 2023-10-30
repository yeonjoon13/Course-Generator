"""
Module containing methods to find keywords in a website text body.
"""

import re
from nltk.corpus import stopwords
import yake
import operator
import inflect
#import nltk
#nltk.download('words')
from nltk.corpus import words


stop_words = set(stopwords.words('english'))


def get_keywords(doc, title, url, num_words):
    """
    Finds keywords in a website, based on the text, title, and url type.

    :param doc: HTML document text.
    :param title: The webpage title.
    :param url: The webpage URL.
    :return: List of keywords on the site.
    """

    # Get rid of non-standard characters for text analysis
    f = re.sub(r"[^A-Za-z0-9.,!? ]+", "", doc)
    doc = f
    doc = doc.casefold()

    kw_extractor = yake.KeywordExtractor(top=20, stopwords=None, n=1)
    keywords = kw_extractor.extract_keywords(doc)

    p = inflect.engine()

    temp_keyword_dict = {}

    for pair in keywords:
        if pair[0] in words.words():

            singular = p.singular_noun(pair[0])

            if not singular:
                singular = pair[0]

            if singular in temp_keyword_dict:
                temp_keyword_dict[singular] += pair[1]
            else:
                temp_keyword_dict[singular] = pair[1]

    adjust_scores_for_title(temp_keyword_dict, title)

    # give all words extra points for more reliable website types
    adjust_scores_for_website_type(temp_keyword_dict, url)

    top_5_words = dict(sorted(temp_keyword_dict.items(), key=operator.itemgetter(1), reverse=True)[:num_words])

    # determine the words above the cutoff, and return them as a list
    # of keywords found on the page.

    words_above_cutoff = []
    scores_above_cutoff = []

    for keyword, score in top_5_words.items():
        words_above_cutoff.append(keyword)
        scores_above_cutoff.append(int(score * 1000))

    return [words_above_cutoff, scores_above_cutoff]


def remove_punctuation(all_words):
    length = len(all_words)
    for i in range(0, length):
        all_words[i] = all_words[i].replace('.', '')
        all_words[i] = all_words[i].replace(',', '')
        all_words[i] = all_words[i].replace('!', '')
        all_words[i] = all_words[i].replace('?', '')
        all_words[i] = all_words[i].replace('[edit]', '')
        all_words[i] = all_words[i].replace('(', '')
        all_words[i] = all_words[i].replace(')', '')
        all_words[i] = all_words[i].replace('[', '')
        all_words[i] = all_words[i].replace(']', '')
        all_words[i] = all_words[i].replace(':', '')

    return all_words


def calc_raw_frequency_score(total_words):
    """
    Calculate the number of times each word appears in the text, and
    store it into a dictionary.

    :param total_words: All of the words in the text.
    :return: A dictionary of non-stopwords and the number of times
    they appear in the text.
    """

    # dictionary associating each word with its raw score (number of
    # occurrences on the webpage)
    raw_scores = {}
    for each_word in total_words:
        # for every non-stopword on the page, increment its score
        # every time it is found (or add it to the dictionary
        # with a score of 1 if it hasn't been added yet)
        if each_word not in stop_words:
            if each_word in raw_scores:
                raw_scores[each_word] += 1
            else:
                raw_scores[each_word] = 1

    return raw_scores


def adjust_scores_for_title(scores, title):
    """
    Adjust the score of each word in the scores dictionary if it appears
    in the title text (give it more points).

    :param scores: Dictionary of scores and their relative scores.
    :param title: The title of the website.
    :return: None
    """

    title = title.casefold()
    old_title_words = title.split()
    old_title_words = remove_punctuation(old_title_words)

    p = inflect.engine()
    title_words = []

    for old_word in old_title_words:
        if not p.singular_noun(old_word):
            title_words.append(old_word)
        else:
            title_words.append(p.singular_noun(old_word))

    for each_word in title_words:
        # Increment each word's score by 10 if it is found in the title.
        if each_word not in stop_words:
            if each_word in scores:
                scores[each_word] += 0.10
            else:
                scores[each_word] = 0.10


def adjust_scores_for_website_type(scores, url):
    """
    Modify all keyword scores in the dictionary based on the type of website.

    :param scores: Dictionary associating words with their scores.
    :param url: The URL of the site.
    :return: None.
    """

    # Move all words to higher or lower relevance based on the domain type.
    if '.com' in url:
        return
    elif '.org' in url:
        modify_all_scores_by_value(scores, 0.05)
    elif '.edu' in url:
        modify_all_scores_by_value(scores, 0.10)
    elif '.gov' in url:
        modify_all_scores_by_value(scores, 0.05)
    elif '.net' in url:
        modify_all_scores_by_value(scores, 0.02)
    elif '.mil' in url:
        modify_all_scores_by_value(scores, 0.02)
    elif '.au' in url:
        modify_all_scores_by_value(scores, 0.02)
    elif '.uk' in url:
        modify_all_scores_by_value(scores, 0.02)
    elif '.ca' in url:
        modify_all_scores_by_value(scores, 0.02)
    else:
        modify_all_scores_by_value(scores, -0.1)


def modify_all_scores_by_value(scores, adjustment):
    """
    Modify all values in the scores dictionary by the adjustment value.

    :param scores: The dictionary associating words with scores.
    :param adjustment: The value to adjust all scores by.
    :return: None.
    """

    for key, val in scores.items():
        val += adjustment

