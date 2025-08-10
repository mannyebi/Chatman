from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat import services as chat_services
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class UploadFile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        
        files = request.FILES.getlist("files")
        content_type = request.POST.get("content_type")
        file_names = request.data.get("file_name").split(",")


        if not files or not content_type or not file_names:
            return Response({"error":"bad request", "message": "one or more of the fields are missing."}, status=status.HTTP_400_BAD_REQUEST)

        upload_list = []

        for index, file in enumerate(files):
            
            uploaded_file = chat_services.save_file(uploader=user, file=file, filename=file_names[index], content_type=content_type)
            upload_list.append(uploaded_file.pk)
        return Response({"message": f"{len(files)} files uploaded", "file_pks":upload_list}, status=status.HTTP_200_OK)
