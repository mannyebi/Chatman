from django.shortcuts import render
from django.views import View
from users.models import User
from chat.models import Message
from chat.services.services import get_messages_based_on_day


class Index(View):
    template = "chat/index.html"
    contacts_model = User #TODO: change this to contacts later and create a unique friend list in chat for each user.
    def get(self, request):
        contact_model = self.contacts_model
        contacts = contact_model.objects.all()

        context = {"contacts":contacts}
        return render(request, self.template, context)
    

class PrivateChatRoom(View):
    template = "chat/room.html"
    post_template = "chat/pchat.html"
    contacts_model = User #TODO: change this to contacts later and create a unique friend list in chat for each user.
    messages_model = Message

    def get(self, request, other_user_id):
        contact_model = self.contacts_model
        contact = contact_model.objects.get(user_id=other_user_id)

        grouped_message = get_messages_based_on_day(request.user, contact)
        
        for a, i in grouped_message.items():
            print(a, "a")
            for x in i:
                print(x.content, "content")
        
        context = {"contact":contact, "grouped_message":grouped_message.items()}

        return render(request, self.post_template, context)  
