from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "owner_username", "filename", "file_type", "file_size", "uploaded_at")
    list_filter = ("file_type", "owner_username")
