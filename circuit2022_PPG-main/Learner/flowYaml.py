from ruamel.yaml import YAML
from Learner import models
from ruamel.yaml.representer import RoundTripRepresenter
from Learner import Task_3


def createPage(yamlList, numPages):


    """
        Creation of an overal flor
        @param yamlList:
        @param numPages:
        @output: create flow YAML file
        """
    #yamlList = Task_3.filtering_text()
    recent_form_submission = models.CourseRequest.objects.last()
    entered_keywords = recent_form_submission.keyword

    yaml = YAML()
    multiline_string = """\
"""
    output = []
    for i in range(numPages):
        multiline_string += "-\n" + '       {{indented_include(\"/Course/yaml/' + yamlList[i] + '\", 8 )}}\n'

    with open('001-recap.yml', mode='w') as file:
        yaml.dump({"title": entered_keywords, "description": "# Advanced Python Concepts", "pages": multiline_string}, file)

def createCoreq(coreqList, count):
    
    recent_form_submission = models.CourseRequest.objects.last()
    entered_keywords = recent_form_submission.keyword
    
    yaml = YAML()
    multiline_string = """\
"""
    output = []
    for i in range(count):
        multiline_string += "-\n" + '       {{indented_include(\"/Course/coreq/' + coreqList[i] + '\", 8 )}}\n'

    with open('002-recap.yml', mode='w') as file:
        yaml.dump({"title": entered_keywords, "description": "# Advanced Python Concepts", "pages": multiline_string}, file)
