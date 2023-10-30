from django.urls import path
from . import views

urlpatterns = [
    # path to get to homepage hence nothing in quotes
    path('', views.home, name='Precision Learning Home'),
    path('download/', views.download, name='Download'),
    path('intermediate/', views.intermediate, name='Intermediate'),
    path('file/', views.getfiles, name = 'File'),
    path('about/', views.about, name='Precision Learning About'),
    path('Auditory/', views.auditory, name='Precision Learning Auditory'),
    path('Visual/', views.visual, name='Precision Learning Visual'),
    path('Reading/', views.visual, name='Precision Learning Reading'),
    path('Results/', views.results, name='Precision Learning Results'),
    path('subtopics/', views.subtopics, name='Specified'),
    path('Loading/', views.loading, name="Loading Page")
]
