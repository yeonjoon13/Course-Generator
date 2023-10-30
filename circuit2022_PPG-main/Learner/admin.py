from django.contrib import admin
from .models import CourseRequest, image, keyword_URL, chunked, video, LinkQueue



admin.site.register(CourseRequest)
admin.site.register(image)
admin.site.register(keyword_URL)
admin.site.register(chunked)
admin.site.register(video)
admin.site.register(LinkQueue)
# Register your models here.
