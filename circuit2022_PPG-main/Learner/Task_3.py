from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml import YAML
import markdown
from Learner import models
from . import flowYaml
# grabbing chunked text
"""
    Finds the user input for keyword, content preferences, and number of pages to find the associated chunked text that will
    be returned to the user.
    :param: none
    :return: strings of chunked text that will be outputted in YAML files for course deployment
"""


def filtering_text():
    #index = 0
    yaml = YAML()
    yamlList = []
    
    # JUST PASS IN VIEWS.PY
    recent_form_submission = models.CourseRequest.objects.last()
    user_preference = recent_form_submission.preference
    entered_keywords = recent_form_submission.keyword
    num_pages = recent_form_submission.pages
    
    
    # retrieve all chunks that we could use
    idx = 0
    
    #  get all all chunked objects
    chunked_list = get_chunks(entered_keywords)
    
    for page in range(1, num_pages + 1):
        info = chunk_output(chunked_list, idx) # 3 chunks at a time
        page_chunk = info[0]
        idx = info[1]

        #total_characters = 0
        key = ''
        new_text = ""
        yaml = YAML()
        yaml.representer.add_representer(str, repr_str)
        multiline_string = """\
    """

        for chunked in page_chunk:

            new_text = chunked.text
            key = chunked.keywords
            multiline_string1 = "# " + chunked.chunk_title.strip() + "\n"
            multiline_string2 = new_text + "\n"
            multiline_string = " ".join([multiline_string1, multiline_string2])

        with open('test' + str(page) + '.yml', mode='w') as file:
            yaml.dump({"type": "Page", "id": entered_keywords + str(page), "keywords": key, "content": multiline_string}, file)
        
        yamlList.append("test" + str(page) + ".yml")
    
    flowYaml.createPage(yamlList, num_pages)


def get_chunks(entered_keywords):
    '''
    Get all chunked objects for keyword

    Returns a list of chunks associated with URL

    @param entered_keywords: string of keyword to filter URL objects
    @return chunk_list: list of chunks to be written on YAML pages
    '''

    relevant_keyword_urls = models.keyword_URL.objects.filter(keyword_text=entered_keywords)

    chunk_list = []

    for relevant_keyword_url in relevant_keyword_urls:
        url = relevant_keyword_url.individual_URL
        chunks_associated = models.chunked.objects.filter(URL=url)
        
        # iterate through list of chunks associated with URL 
        for chunked in chunks_associated:
            chunk_list.append(chunked)

    return chunk_list


def chunk_output(chunk_list, idx):
    '''
    Add three chunks at a time to a YAML page

    @param chunk_list: chunks to be written to page
    @param idx: index to keep track of chunks already checked
    @return page_chunk, idx: tuple consisting of three chunks to write to YAML and index to keep track of last chunk
    '''

    page_chunk = [] 

    chunk_counter = 0;

    for chunked in chunk_list[idx:]:
        if chunk_counter == 3:
            break
        else: 
            page_chunk.append(chunked)
            chunk_counter += 1
            idx += 1

    return page_chunk, idx
    
def filtering_videos():
    """
    Creates text-heavy YAML files
    """

    yaml = YAML()

    # JUST PASS IN VIEWS.PY
    recent_form_submission = models.CourseRequest.objects.last()
    user_preference = recent_form_submission.preference
    entered_keywords = recent_form_submission.keyword
    num_pages = recent_form_submission.pages

    # retrieve all chunks that we could use
    idx = 0

    #  get all all chunked objects
    video_list = get_videos(entered_keywords)

    for page in range(1, num_pages + 1):
        info = video_output(video_list, idx)  # 3 chunks at a time
        page_video = info[0]
        idx = info[1]

        #total_characters = 0
        key = ''
        new_text = ""
        yaml = YAML()
        yaml.representer.add_representer(str, repr_str)
        multiline_string = """\
    """

        for video in page_video:

            #new_text = markdown.markdown(video.URL)
            link = video.URL
            link = link.replace("https://www.youtube.com/watch?v=", "https://www.youtube.com/embed/")
            new_text = markdown.markdown("<iframe src="+link+"> </iframe>") 
            key = video.keywords
            multiline_string += "#"+video.chunk_title.strip() + "\n" + new_text+"\n\n"

        with open('test' + str(page) + '.yml', mode='w') as file:
            yaml.dump({"type": "Page", "id": entered_keywords + str(page),
                      "keywords": key, "content": multiline_string}, file)



def get_videos(entered_keywords):
    '''
    Get all video objects for keyword

    Returns a list of chunks associated with URL

    @param entered_keywords: string keywords to filter video objects
    @return video_list: list of videos to be written on YAML pages
    
    '''

    # filter videos associated with the keyword
    relevant_videos = models.video.objects.filter(keywords=entered_keywords)

    video_list = []

    for video in relevant_videos:
        video_list.append(video)

    return video_list


def video_output(video_list, idx):
    '''
    Add three videos at a time to a YAML page

    @param video_list: list of videos to be written to page
    @param idx: integer index to keep track of videos already checked

    @return page_chunk, idx: tuple consisting of three videos to write to YAML and index to keep track of last video
    '''
    page_video = []

    video_counter = 0

    for video in video_list[idx:]:
        if video_counter == 3:
            break
        else:
            page_video.append(video)
            video_counter += 1
            idx += 1

    return page_video, idx


def repr_str(dumper: RoundTripRepresenter, data: str):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

'''
def line_break(text):
    new_text = ""
    word_count = 0
    for word in text:
        new_text += word + ""
        word_count += 1
        if word_count == 150:
            new_text += "\n"
            word_count = 0
    return new_text
'''

'''
class Page:
    def __init__(self, type, id, chunk_id, entered_keywords):
        self.type = type
        self.id = id
        self.chunk_id = chunk_id
        self.relevant_keyword_urls = models.keyword_URL.objects.filter(
            keyword_text=entered_keywords)

    def asdict(self):
        total_characters = 0
        key = ''
        new_text = ""
        yaml = YAML()
        yaml.representer.add_representer(str, repr_str)
        multiline_string = """\
"""
        for relevant_keyword_url in self.relevant_keyword_urls:
            url = relevant_keyword_url.individual_URL
            chunks_associated = models.chunked.objects.filter(URL=url)
            for chunked in chunks_associated:
                total_characters += len(chunked.text)
                if (total_characters < 9000):
                    new_text = line_break(chunked.text)
                    key = chunked.keywords
                    multiline_string += "# " + chunked.title + "\n" + new_text + "\n"
                else:
                    break
        return {"type": self.type, "id": self.id, "keywords": key, "content": multiline_string}
'''


