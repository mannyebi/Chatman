from django.shortcuts import render
from django.views import View
from users.models import User


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
    def get(self, request, other_user_id):
        return render(request, self.template)