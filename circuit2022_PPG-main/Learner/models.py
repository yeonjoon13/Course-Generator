from asyncio.streams import FlowControlMixin
from cgitb import text
from nturl2path import url2pathname
from turtle import title
from urllib.error import URLError
from django.db import models
from django.db.models import ManyToManyField
from django.forms import BooleanField
from django.utils import timezone
from datetime import date
from django.utils.translation import gettext as _
#import yaml
#import yamlfield

# Create your models here.

# task 1 images table


class image(models.Model):
    """
    images scraped from the web (chunked text objects can contain images)
    """

    image_id = models.IntegerField()
    URL = models.CharField(max_length=400)
    image_path = models.CharField(max_length=500)
    image_code = models.IntegerField()

    def __str__(self):
        return 'Image ' + str(self.image_id)

# task 1 keywords table


class keyword_URL(models.Model):
    """
    urls associated with a specific keyword
    """

    keyword_text = models.CharField(max_length=200)
    individual_URL = models.CharField(max_length=400)
    date_scraped = models.DateTimeField()
    score = models.IntegerField()

    def __str__(self):
        return self.keyword_text + '-' + self.individual_URL

# task 1 scraped info table


class LinkQueue(models.Model):
    """
    Queue of links to be scraped next
    """

    keyword_text = models.CharField(max_length=200)

    link0 = models.CharField(max_length=400)
    link1 = models.CharField(max_length=400)
    link2 = models.CharField(max_length=400)
    link3 = models.CharField(max_length=400)
    link4 = models.CharField(max_length=400)
    link5 = models.CharField(max_length=400)
    link6 = models.CharField(max_length=400)
    link7 = models.CharField(max_length=400)
    link8 = models.CharField(max_length=400)
    link9 = models.CharField(max_length=400)

    def __str__(self):
        return self.keyword_text


class chunked(models.Model):
    """
    represents text chunks that have been scraped from the web
    """

    text = models.CharField(max_length=5000)
    keywords = models.CharField(max_length=400)
    page_title = models.CharField(max_length=200)
    chunk_title = models.CharField(max_length=200)
    images = ManyToManyField(image)
    URL = models.CharField(max_length=400)
    coreqs = models.CharField(max_length=200, default='')
    chunkID = models.IntegerField(default=0)
    topic = models.CharField(max_length=200)
    selected = models.BooleanField(default=False)
    written = models.BooleanField(default=False)
    next_chunk = models.IntegerField(default=0)

    def __str__(self):
        return '(' + str(self.chunkID) + ") " + str(self.page_title) + ' - ' + str(self.chunk_title)

class video(models.Model):
    """
    videos that have been scraped from relevant websites (YouTube, Vimeo, Khan Academy) 
    """
    
    #video_id = models.IntegerField()
    keywords = models.CharField(max_length=400)
    title = models.CharField(max_length=200)
    URL = models.CharField(max_length=400)
    selected = models.BooleanField(default=False)
    video_id = models.IntegerField(default=0)
    description = models.CharField(max_length=1000)
    coreqs = models.CharField(max_length=200, default='')

    def __str__(self):
        return '(' + str(self.video_id) + ') ' + self.title


class CourseRequest(models.Model):
    """
    represents the form on the homepage that the user will fill out specifiying
    the topic they want to learn about (keyword), their learning style preference,
    and the amount of pages they want for their course 
    """

    name = models.TextField()
    keyword = models.TextField()
    # antikeywords = models.TextField()
    # form_date = models.DateTimeField(default=timezone.now)
    preference = models.CharField(max_length=200, null=False, blank=True)
    pages = models.IntegerField(null=False, blank=True)

    def __str__(self):
        return self.name

