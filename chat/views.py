# Create your views here.
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from chat.models import Thread

User = get_user_model()


def room(request, room_name):
    user_list = {}

    if room_name == 'Lobby':
        thread = Thread.objects.filter(name=room_name)[0]
        if request.user.is_authenticated:
            username = request.user.username
            user_list = User.objects.exclude(username=username)

    elif request.user.is_authenticated:
        username = request.user.username
        user_list = User.objects.exclude(username=username)
        thread = Thread.objects.filter(name__contains=username)
        thread = thread.filter(name__contains=room_name)[0]

    else:
        raise PermissionDenied()

    last_messages = thread.last_10_messages()[::-1]
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'user_list': user_list,
        'last_messages': last_messages,
    })