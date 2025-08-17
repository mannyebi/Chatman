from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat import services as chat_services
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMembership

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
        group_display_name = request.data.get("group_display_name", "").strip()
        participants_data = request.data.get("participants", "").strip()

        if not group_name:
            return Response({"error": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)


        participant_ids = set()

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

        try:
            chat, created = chat_services.get_or_create_group_chat(group_name=group_name, participants=list(participants), group_display_name=group_display_name, group_creator=group_creator)
        except Exception as e:
            print(e)
            return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if created:
            return Response({"chat_id":chat.name, "message":"Group chat has been created"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"chat_id":chat.name, "message":"Group already exists"}, status=status.HTTP_200_OK)
        

class HandleGroupChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        group_id = request.data.get("group_id")
        action = request.data.get("action")
        removing_members = request.data.get("removing_members")
        users = request.data.get("users")
        user = request.user

        chat = get_object_or_404(ChatRoom, id=group_id)
        membership = get_object_or_404(ChatMembership, user=user, chatroom=chat)

        is_permissioned = chat_services.has_permission(membership, action)

        if not is_permissioned:
            return Response({"message":"You are not allowed to perform this action at this group."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if action == "delete_group":
            try:
                return chat_services.handle_delete_group(chat)
            except Exception as e:
                return Response({"message":"an error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == "promote_admin":

            if not users:
                return Response({"message":"the promoted user id is missing."}, status=status.HTTP_400_BAD_REQUEST)
            
            admin_users = set()
            for user in users.split(","):
                stripped_user = user.strip()
                if stripped_user:
                    try:
                        int_stripped_user = int(stripped_user)
                    except Exception as e :
                        return Response({"error":"one or more of the inputed users are invalid."}, status=status.HTTP_400_BAD_REQUEST)
                    admin_user = get_object_or_404(User, id=int_stripped_user)
                    selected_admin = get_object_or_404(ChatMembership, user=admin_user, chatroom=chat)
                    admin_users.add(selected_admin)

            #prevent promoting it self.
            if request.user == admin_user:
                return Response({"message":"you can not promote yourself."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                return chat_services.handle_promote_user_to_admin(chat, selected_admin)
            except Exception as e:
                print(e)
                return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == "remove_members":

            if not users:
                return Response({"message":"the removing members id is missing."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                return chat_services.handler_removing_members(chat, users)
            except Exception as e:
                print(e)
                return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == "add_members":

            if not users:
                return Response({"message":"the adding members id is missing."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                return chat_services.handle_add_member(chat, users)
            except Exception as e:
                print(e)
                return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)