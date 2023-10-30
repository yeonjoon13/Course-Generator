from gettext import textdomain
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

from Learner import models


def similar(a, b):
    """
    used in relation extraction function for similarity between two items (chunked texts)

    @param a: first chunked text
    @param b: second chunked text
    @return SequenceMatcher: matches two different texts together, and defining their similarity
    """

    return SequenceMatcher(None, a, b).ratio()


def relation_extraction(clara, x):
    """
    performs relation extraction 

    @param clara: list of chunked text in database
    @param x: x is the current chunked text being comapred to other items in Clara list
    @return List: list of similar items sorted by highest similarity
    """

    List = {}
    for i in range(len(clara)):
        Similarity = similar(clara[i], clara[x])
        List[i] = Similarity
    List = dict(sorted(List.items(), key=lambda item: item[1], reverse=True))
    return List


def start_relation_extraction(chunk_id_start_and_end, preference):
    """
    starts relation extraction

    @param chunk_id_start_and_end: list of two integers - starting and ending index of chunked text objects in database
    """
    print(chunk_id_start_and_end)

    chunk_id_start = chunk_id_start_and_end[0]
    chunk_id_end = chunk_id_start_and_end[1]

    text_list = []

    if (preference == "Video"):
        # need to run relation extraction algorithm on video objects
        for e in models.video.objects.all()[chunk_id_start:chunk_id_end]:
            text_list.append(e.description)

        print(text_list)

        CoReq_Data = []

        print(chunk_id_start)
        print(chunk_id_end)

        for i in range(0, chunk_id_end - chunk_id_start):
            jimmy = relation_extraction(text_list, i)

            temp_coreq_data = list(jimmy)[1:6]
            # print(temp_coreq_data)

            actual_coreq_data = [x + chunk_id_start for x in temp_coreq_data]
            # print(actual_coreq_data)

            CoReq_Data.append(actual_coreq_data)

        CoReq_Data

        for i in range(chunk_id_start, chunk_id_end):
            # tester = models.task2_page.objects.create(
            # page_id=i, URL='filler', topic='0', chunk_text=text_list[i - chunk_id_start], image_path='filler', coreq=CoReq_Data[i - chunk_id_start])
            # tester.save()

            task1tableobject = models.video.objects.get(video_id=i)
            task1tableobject.coreqs = CoReq_Data[i - chunk_id_start]
            task1tableobject.save()

    else:
        # need to run relation extraction algorithm on chunk objects

        # need to have an association with the amount of scrapes for specific keyword
        for e in models.chunked.objects.all()[chunk_id_start:chunk_id_end]:
            text_list.append(e.text)

        # for x in text_list:
            # print(x + "\n")

        CoReq_Data = []

        for i in range(0, chunk_id_end - chunk_id_start):
            jimmy = relation_extraction(text_list, i)

            temp_coreq_data = list(jimmy)[1:6]
            # print(temp_coreq_data)

            actual_coreq_data = [x + chunk_id_start for x in temp_coreq_data]
            # print(actual_coreq_data)

            CoReq_Data.append(actual_coreq_data)

        CoReq_Data

        for i in range(chunk_id_start, chunk_id_end):
            # tester = models.task2_page.objects.create(
                # page_id=i, URL='filler', topic='0', chunk_text=text_list[i - chunk_id_start], image_path='filler', coreq=CoReq_Data[i - chunk_id_start])
            # tester.save()

            task1tableobject = models.chunked.objects.get(chunkID=i)
            task1tableobject.coreqs = CoReq_Data[i - chunk_id_start]
            task1tableobject.save()




'''
MODEL
class task2_page(models.Model):
    page_id = models.IntegerField()
    URL = models.CharField(max_length=200)  # taken from task 1
    topic = models.CharField(max_length=200)  # created by task 2"
    chunk_text = models.CharField(max_length=200)
    image_path = models.CharField(max_length=200)
    coreq = models.CharField(max_length=200)
    # prereq = models.CharField(max_length=200)

'''
