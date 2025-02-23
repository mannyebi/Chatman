from chat.models import Message
from django.db.models.functions import TruncDate
from django.db.models import Q

def get_messages_based_on_day(user1, user2, limit=50):
    """retrieve messages from user 1 and user 2 based on each day
    """
    
    messages = (Message.objects.filter(Q(sender=user1, receiver=user2) | Q(receiver=user1, sender=user2)).annotate(dat=TruncDate("timestamp")).values("dat").order_by("-dat")[:limit])

    grouped_message = {}

    for entry in messages:
        day = entry["dat"]
        grouped_message[day] = Message.objects.filter(
            (Q(sender=user1, receiver=user2) | Q(receiver=user1, sender=user2)), timestamp__date=day
        ).order_by("timestamp")

    return grouped_message