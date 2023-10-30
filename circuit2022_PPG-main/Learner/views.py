import os
from re import I
import shutil
import zipfile
import mimetypes
from io import StringIO
from io import BytesIO

from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime

from . import ppg_task1_v0
from . import Task_2_Code
from . import Task_3
from . import video_scraper
from .models import CourseRequest
from .forms import CourseRequestForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from Learner import kenny
from Learner import models

# Create your views here.

keyword = ''
og_keyword = ''


def home(request):
    global keyword
    global og_keyword
    # Checks form for keyword, preference, page length
    button = request.POST.get("submit")
    keyword = ""
    preference = ""
    pages = ""
    context = {}
    if request.method == "POST":
        form = CourseRequestForm(request.POST or None)

        if form.is_valid():
            print("Form successfully sent!")
            name = form.cleaned_data.get("name")
            keyword = form.cleaned_data.get("keyword")
            print('everything above here is fine')
            preference = form.cleaned_data.get("preference")
            pages = form.cleaned_data.get("pages")

            if pages == "1-10":
                pages = 10
            elif pages == "10-30":
                pages = 30
            elif pages == "30+":
                pages = 75

            NewCourse = CourseRequest.objects.create(name=name, keyword=keyword, preference=preference, pages=pages)
            NewCourse.save()
            print("User preference: " + str(preference))
            print("Entered keywords: " + keyword)

            context['keyword'] = keyword
            context["preference"] = preference
            context['pages'] = pages


            og_keyword = keyword

            print(preference)

            # Calling Task 1 Code

            subtopics = ppg_task1_v0.get_subtopics(keyword)
            subtopics = False
            
            print('subtopics:')
            print(subtopics)

            if subtopics:
                subtopics.append("Just give me the broader topic, please.")
                subtopic_context = {}
                subtopic_context['list'] = subtopics
                subtopic_context['specified'] = "tester"
                print('here')
                return render(request, "Learner/Subtopics.html", subtopic_context)


            webScraperID = webScraper(keyword, preference, pages)


            if webScraperID != False:

                # Calling Task 2 Code

                relatedPagesID = relatePages(webScraperID, preference)
            
            context = {}
                
            if preference == "Text":
                context['list'] = models.chunked.objects.filter(topic=keyword)
                context["preference"] = "Text"


                # reset all true fields to false for clean scrape
                for scrape in models.chunked.objects.filter(selected=True):
                    print(scrape)
                    scrape.selected = False
                    scrape.save()

                for scrape in models.chunked.objects.filter(written=True):
                    print(scrape)
                    scrape.selected = False
                    scrape.save()
                
                return render(request, "Learner/Intermediate1.html", context)
    
            if preference == "Video":
                context['list'] = models.video.objects.filter(topic=keyword)
                context["preference"] = "Video"

                # reset all true fields to false for clean scrape
                for scrape in models.video.objects.filter(selected=True):
                    print(scrape)
                    scrape.selected = False
                    scrape.save()
                
                return render(request, "Learner/Intermediate2.html", context)

        else:
            context['form'] =  form.errors
            #print(form.errors.as_data())
            return render(request, 'Learner/home.html', context)

    else:
        return render(request, 'Learner/home.html', {})

def loading(request):
    
    context = {}

    #if request.method == "POST":
    print("BEFORE SCRAPE")
    keyword = request.POST.get("keyword")
    preference = request.POST.get("preference")
    pages = request.POST.get("pages")
    
    # Calling Task 1 Code 
    webScraperID = webScraper(keyword, preference, pages)

    if webScraperID != False:

    #   Calling Task 2 Code
        relatedPagesID = relatePages(webScraperID, preference)

    #context = {}
        
    if preference == "Text":
        context['list'] = models.chunked.objects.filter(topic=keyword)
        context["preference"] = "Text"


        # reset all true fields to false for clean scrape
        for scrape in models.chunked.objects.filter(selected=True):
            print(scrape)
            scrape.selected = False
            scrape.save()

        for scrape in models.chunked.objects.filter(written=True):
            print(scrape)
            scrape.selected = False
            scrape.save()
        
        return render(request, "Learner/Intermediate1.html", context)

    if preference == "Video":
        context['list'] = models.video.objects.filter(keywords=keyword)
        context["preference"] = "Video"

        # reset all true fields to false for clean scrape
        for scrape in models.video.objects.filter(selected=True):
            print(scrape)
            scrape.selected = False
            scrape.save()
        
        return render(request, "Learner/Intermediate2.html", context)


def intermediate(request):
    
    if request.method == "POST":
        print("BEFORE SCRAPE")

        preference = request.POST.get("preference")

        if preference == "Text":
            values = request.POST.getlist("chunks")
        
            print(values)
            print(preference)


            # selected scrapes for course
            for i in values:
                chunk = models.chunked.objects.get(chunkID = int(i))
                chunk.selected = True
                chunk.save()

            # just check if right chunk
            for e in models.chunked.objects.filter(selected=True):
                print(e)

            print("AFTER SCRAPE")
        
        
        if preference == "Video":
            values = request.POST.getlist("videos")

            print(values)
            print(preference)

            # selected scrapes for course
            for item in values:
                video = models.video.objects.get(URL=item)
                video.selected = True
                video.save()

            # just check if right chunk
            for e in models.video.objects.filter(selected=True):
                print(e)

        # Calling Task 3 Code
        formatPages(preference)

        return render(request, 'Learner/Download.html', {})
        # else:
        #     print(form.errors.as_data())
        #     return render(request, 'Learner/home.html', {})
    else:
        return render(request, 'Learner/home.html', {})
        
# TASK 1 CODE
def webScraper(keywords, preference, pages):
    """
    Runs web scraper for relevant content (task 1 code) based on user preference (Text, Image, Videos)

    @param keywords: string/list to scrape for certain topic
    @param preference: string specifying the user's learning preference
    @param pages: integer representing the page length of the requested course
    @return: start and ending indices for relevant chunks in database to perform relation extraction
    """

    print("Running task 1 code! Scraping web for: ", keywords)

    start_and_end_chunks = [0,0]

    print(preference)
    
    if (preference == "Text" or preference == "Image"):
        start_and_end_chunks = ppg_task1_v0.start_scraper(keywords, 3)
        print(start_and_end_chunks)
    
    if(preference == "Video"):
        start_and_end_chunks = video_scraper.start_scraper(keywords)
        
    print("Task 1 code complete!")

    print(start_and_end_chunks)

    return start_and_end_chunks

# TASK 2 CODE
def relatePages(webScrapeID, preferences):
    """
    runs relation extraction algorithm on chunked text objects scraped from the web 
    (in the future will also run topic model)

    @param webScrapeID: list of integers specifying the starting and ending index of relevant chunked text objects
    """

    print("Running task 2 code!")
    print(webScrapeID)
    Task_2_Code.start_relation_extraction(webScrapeID, preferences)
    print("Task 2 code complete!")
    # return "345678"

# TASK 3 CODE
def formatPages(preference):
    """
    formats YAML pages for deployment based on user learning preference

    @param preference: string for user's learning style
    """

    print("Running task 3 code!")

    if (preference == "Text" or preference == "Image"):
        Task_3.filtering_text()
    
    if (preference == "Video"):
        Task_3.filtering_videos()
        
    print("Task 3 code complete!")

'''
def getfiles(request):
    # Files (local path) to put in the .zip

    filenames = []

    recent_form_submission = models.CourseRequest.objects.last()
    num_pages = recent_form_submission.pages

    for page in range(1, num_pages+1):
        filenames.append('test' + str(page) + '.yaml')

    #filenames = ["test1.yaml", "test2.yaml", "test3.yaml"]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    zip_subdir = "/circuit2022_PPG"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue())
    
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp
'''



def getfiles(request):
    
    '''
    zf = zipfile.ZipFile("myzipfile.zip", "w")

    for dirname, subdirs, files in os.walk("Course"):
        zf.write(dirname)
        for sub in subdirs:
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    zf.close()
    '''

    # Open StringIO to grab in-memory ZIP contents
    #s = BytesIO()

    course = shutil.make_archive("Course", 'zip', "Course")
    return course

    # Grab ZIP file from in-memory, make response with correct MIME-type
    #resp = HttpResponse(s.getvalue())

    # ..and correct content-disposition
    #resp['Content-Disposition'] = 'attachment; filename=%s' % course

    #return resp


def about(request):
    return render(request, 'Learner/about.html')
 #  return HttpResponse('<h1>Precision Learning About</h1>''<h3> The members in this cohort include Clara, Luke, Travis, Folahan, Christal, Kenny, Maryam, and Aashi </h3>')

def auditory(request):
    return render(request, 'Learner/Auditory.html')

def visual(request):
    return render(request, 'Learner/Visual.html')

def reading(request):
    return render(request, 'Learner/Reading.html')

def results(request):
    # if request.method == "POST":
    #     searched = request.POST['searched']
    #     course = task1.objects.filter(Keywords__contains=searched)
    #     return render(request, 'Learner/Results.html', {'searched': searched, 'Keywords': course})
    # else:
    return render(request, 'Learner/Results.html', {})

def download(request):
    return render(request, 'Learner/Download.html')


def subtopics(request):
    print("IT WORKS")
    values = request.POST.getlist("subtopics")
    print(values)
    global keyword
    for new_word in values:
        if new_word != 'Just':
            keyword += ' AND ' + new_word

    return render(request, 'Learner/Loading.html', {})
    #loading_page(request)
    #print('new keyword')
    #print(keyword)
    #return render(request, 'Learner/loading.html', {})
    #return render(request, 'Learner/Download.html', {})


def loading_page(request):
    print('loading the page?')

    # temp filler
    preference = 'Text'
    pages = 3

    print('loading...')
    webScraperID = webScraper(keyword, preference, pages)


    if webScraperID != False:

        # Calling Task 2 Code

        relatedPagesID = relatePages(webScraperID, preference)

    context = {}

    print('moving on')

    if preference == "Text":
        print('moved on?')
        context['list'] = models.chunked.objects.filter(keywords__icontains=og_keyword)
        context["preference"] = "Text"


        # reset all true fields to false for clean scrape
        for scrape in models.chunked.objects.filter(selected=True):
            print(scrape)
            scrape.selected = False
            scrape.save()

        for scrape in models.chunked.objects.filter(written=True):
            print(scrape)
            scrape.selected = False
            scrape.save()

        print('before rendering')
        return render(request, "Learner/Intermediate1.html", context)

    if preference == "Video":
        context['list'] = models.video.objects.filter(keywords=keyword)
        context["preference"] = "Video"

        # reset all true fields to false for clean scrape
        for scrape in models.video.objects.filter(selected=True):
            print(scrape)
            scrape.selected = False
            scrape.save()

        return render(request, "Learner/Intermediate2.html", context)
    #else:
        # print(form.errors.as_data())
        #print("ERROR")
        #return render(request, 'Learner/home.html', {})

