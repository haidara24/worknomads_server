from django.urls import path
from .views import UploadImageView, UploadAudioView, FileListView

urlpatterns = [
    path("upload/image/", UploadImageView.as_view(), name="upload_image"),
    path("upload/audio/", UploadAudioView.as_view(), name="upload_audio"),
    path("files/", FileListView.as_view(), name="file_list"),
]
