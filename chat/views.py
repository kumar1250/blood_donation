from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import ChatMessage
from accounts.models import Follow








User = get_user_model()

@login_required
def chat_home(request):
    users = User.objects.exclude(id=request.user.id)

    # List of users that current user follows
    following = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)

    return render(request, "chat/home.html", {
        "users": users,
        "following": following,
    })

@login_required
def follow_toggle(request, username):
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("chat:chat_home")

    follow, created = Follow.objects.get_or_create(follower=request.user, following=other_user)

    if not created:
        follow.delete()
        messages.success(request, f"You unfollowed {other_user.username}.")
    else:
        messages.success(request, f"You followed {other_user.username}.")

    return redirect("chat:chat_home")

@login_required
def chat_view(request, username):
    """
    View and send messages between logged-in user and another user.
    """
    other_user = get_object_or_404(User, username=username)

    # Optional: only allow chat with mutual follow
    follows = (
        Follow.objects.filter(follower=request.user, following=other_user).exists()
        or Follow.objects.filter(follower=other_user, following=request.user).exists()
    )

    if not follows:
        messages.error(request, "You can only chat with users who follow you or whom you follow.")
        return redirect('chat:chat_home')

    # Handle POST message
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            ChatMessage.objects.create(sender=request.user, recipient=other_user, content=message)
            return redirect('chat:chat_view', username=other_user.username)

    # Fetch all messages between these two users
    messages_list = ChatMessage.objects.filter(
        sender__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    ).order_by('timestamp')

    # If AJAX request, return JSON (for future auto-refresh)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                'sender': msg.sender.username,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for msg in messages_list
        ]
        return JsonResponse(data, safe=False)

    return render(request, 'chat/chat.html', {'other_user': other_user, 'messages': messages_list})
