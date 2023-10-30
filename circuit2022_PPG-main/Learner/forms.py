from django import forms
from .models import CourseRequest
from .models import chunked
from .models import video    

# The first element in each tuple is the actual value to be stored, and the second element is the human-readable name.
preference_choices = [
    ('Text', 'Text'),
    ('Image', 'Image'),
    ('Video', 'Video')]

page_options = [
    ('1-10', '10'),
    ('10-30', '30'),
    ('30+', '75')
]


class CourseRequestForm(forms.Form):
    """
    Course Request form on homepage for user to fill out 
    for keyword topic to search, learning style, page length for course
    """

    name = forms.CharField(max_length=150, required=True)
    keyword = forms.CharField(max_length=150, required=True)
    preference = forms.ChoiceField(
        widget=forms.RadioSelect, choices=preference_choices, required=True
    )
    pages = forms.ChoiceField(widget=forms.RadioSelect, choices=page_options, required=True)

    def clean_keyword(self, *args, **kwargs):
        keyword = self.cleaned_data.get("keyword")
        if keyword == " ":
            raise forms.ValidationError("This field is required")
        return keyword


# class ScrapeForm(forms.Form):
#      selections = forms.ModelMultipleChoiceField(queryset=chunked.objects.all(), widget=forms.CheckboxSelectMultiple)


# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     self.fields['selections'].queryset = chunked.objects.all()


'''
class ScrapeForm(forms.ModelForm):
    selections = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=True, queryset=chunked.objects.all())
    
    class Meta:
        model = selected_scrapes
        fields = ('selections',)
'''


'''
class ScrapeForm(forms.ModelForm):
    # selections = forms.ModelMultipleChoiceField(
    #     widget=forms.CheckboxSelectMultiple, required=True, queryset=chunked.objects.all())

    class Meta:
        model = chunked
        fields = ('text', 'keywords', 'title', 'images',
                  'URL', 'coreqs', 'chunkID', 'topic')
'''
