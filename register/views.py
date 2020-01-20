from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from chat.models import Thread

User = get_user_model()

# Create your views here.

def register(response):
    if response.method == "POST":
        form = UserCreationForm(response.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            new_user = User.objects.filter(username__exact = username)[0]
            users = User.objects.exclude(username__exact = username)

            for user in users:
                thread_name = 'Thread_private_'+username+'_'+user.username
                new_thread = Thread(name = thread_name)
                new_thread.save()
                print(new_user, user)
                new_thread.members.add(new_user, user)
                new_thread.save()
            return redirect("/chat/Lobby")
        else:
            print("error")

    else:
        form = UserCreationForm()
    return render(response, "register/register.html", {"form": form})