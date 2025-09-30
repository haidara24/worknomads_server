from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from .models import UploadedFile
from .serializers import UploadedFileSerializer

class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = file_obj.content_type
        if not content_type.startswith("image/"):
            return Response({"error": "Uploaded file is not an image"}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if file_obj.size > max_size:
            return Response({"error": "Image too large (max 10MB)"}, status=status.HTTP_400_BAD_REQUEST)

        owner = getattr(request.user, "username", None) or request.auth.get("sub") or request.auth.get("username")

        uploaded = UploadedFile.objects.create(
            owner_username=owner,
            file=file_obj,
            file_type="image",
            filename=file_obj.name,
            content_type=content_type,
            file_size=file_obj.size,
        )

        serializer = UploadedFileSerializer(uploaded, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UploadAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("audio")
        if not file_obj:
            return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = file_obj.content_type
        if not content_type.startswith("audio/"):
            return Response({"error": "Uploaded file is not an audio file"}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 15 * 1024 * 1024
        if file_obj.size > max_size:
            return Response({"error": "Audio too large (max 15MB)"}, status=status.HTTP_400_BAD_REQUEST)

        owner = getattr(request.user, "username", None) or request.auth.get("sub") or request.auth.get("username")

        uploaded = UploadedFile.objects.create(
            owner_username=owner,
            file=file_obj,
            file_type="audio",
            filename=file_obj.name,
            content_type=content_type,
            file_size=file_obj.size,
        )

        serializer = UploadedFileSerializer(uploaded, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileListView(generics.ListAPIView):
    serializer_class = UploadedFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        owner = getattr(self.request.user, "username", None) or self.request.auth.get("sub")
        return UploadedFile.objects.filter(owner_username=owner)
