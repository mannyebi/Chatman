from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat import services as chat_services
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from chat import models

# Create your views here.

User = get_user_model()


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


class CreatePrivateChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        #getting current user and the target user
        sender = request.user
        receiver_id = request.data.get("receiver_id")

        if not receiver_id:
            return Response({"error":"Receiver ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(User, id=receiver_id)

        #Prevent a user from creating a chat with themselve
        if sender == receiver:
            return Response({"error":"Cannot create a private chat with yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        chat, created = chat_services.get_or_create_private_chat(sender, receiver)

        if created:
            return Response({"chat_id":chat.id, "message":"Private chat has been created"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"chat_id":chat.id, "message":"chat already exists"}, status=status.HTTP_200_OK)
            

class CreateGroupChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
            
        group_creator = request.user
        group_name = request.data.get("group_name").strip()
        group_display_name = request.data.get("group_display_name").strip()
        participants_data = request.data.get("participants").strip()

        if not group_name:
            return Response({"error": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)


        participant_ids = {str(group_creator.id)}

        if participants_data:
            for pid_str in participants_data.split(','):
                # Ensure the string is not empty or just whitespace before adding
                stripped_pid = pid_str.strip()
                if stripped_pid:
                    participant_ids.add(stripped_pid)
                    
        participant_id_list = list(participant_ids)


        try:
            participants = User.objects.filter(id__in=participant_id_list)
        except ValueError as ve:
            return Response({"message":"the inputed users are not valid."}, status=status.HTTP_400_BAD_REQUEST)

        if participants.count() != len(set(participant_id_list)) :
            return Response({"error": "One or more participants not found."}, status=status.HTTP_400_BAD_REQUEST)

        chat, created = chat_services.get_or_create_group_chat(group_name=group_name, participants=list(participants), group_display_name=group_display_name)
            

        if created:
            return Response({"chat_id":chat.name, "message":"Group chat has been created"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"chat_id":chat.name, "message":"Group already exists"}, status=status.HTTP_200_OK)