from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import ChatMessage
from accounts.models import Follow

User = get_user_model()

@login_required
def chat_home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/home.html', {'users': users})

@login_required
def chat_view(request, username):
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('chat_home')

    follows = (
        Follow.objects.filter(follower=request.user, following=other_user).exists()
        or Follow.objects.filter(follower=other_user, following=request.user).exists()
    )

    if not follows:
        messages.error(request, "You can only chat with users who follow you or whom you follow.")
        return redirect('chat_home')

    if request.method == 'POST':
        message = request.POST.get('message','')
        if message:
            ChatMessage.objects.create(sender=request.user, receiver=other_user, message=message)
            return redirect('chat', username=other_user.username)

    messages_list = ChatMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    return render(request, 'chat/chat.html', {'other_user': other_user, 'messages': messages_list})
