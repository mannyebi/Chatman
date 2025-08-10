from django.urls import path
from chat.views import UploadFile
urlpatterns = [
    path("upload/", UploadFile.as_view(), name="upload")
]