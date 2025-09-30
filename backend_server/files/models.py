from django.db import models

class UploadedFile(models.Model):
    FILE_TYPES = (
        ("image", "Image"),
        ("audio", "Audio"),
    )

    owner_username = models.CharField(max_length=150, db_index=True)
    file = models.FileField(upload_to="uploads/")
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.owner_username} - {self.file_type} - {self.filename}"
