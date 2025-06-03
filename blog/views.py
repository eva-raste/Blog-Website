from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from .forms import CustomUserCreationForm
from .models import BlogPost, Bookmark, ChatMessage, FriendRequest, Like, Comment, Category, Notification
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.core.paginator import Paginator

def home(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    
    # Optional: Filter by category
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get bookmarked post IDs for current user
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        bookmarked_post_ids = request.user.bookmarks.values_list('post__id', flat=True)

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'posts': page_obj,  # ✅ This is important
        'page_obj': page_obj,
        'categories': categories,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


@login_required
def profile_view(request):
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES.get('image')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None

        BlogPost.objects.create(
            title=title,
            description=description,
            image=image,
            author=request.user,
            category=category
        )
        return redirect('home')
    
    categories = Category.objects.all()
    return render(request, 'create_post.html', {'categories': categories})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.description = request.POST['description']
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.category = get_object_or_404(Category, id=request.POST['category'])
        post.save()
        return redirect('profile')

    categories = Category.objects.all()
    return render(request, 'edit_post.html', {'post': post, 'categories': categories})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('profile')
    return render(request, 'delete_confirm.html', {'post': post})



def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Provide the backend explicitly when logging in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Explicitly mention the backend
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html',{'form':form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if the user is already logged in

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get the user from the form
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home after successful login
    else:
        form = AuthenticationForm()  # If GET request, just initialize an empty form
    return render(request, 'login.html', {'form': form})  # Render the login page with the form
 

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == "POST":
        comment_text = request.POST.get('content')
        Comment.objects.create(user=request.user, post=post, content=comment_text)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                text=f"{request.user.username} commented on your post '{post.title}'"
            )
    return redirect('view_post', slug=slug)


def view_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    user = request.user if request.user.is_authenticated else None

    # Check if the current user has liked the post
    has_liked = False
    if user:
        has_liked = Like.objects.filter(post=post, user=user).exists()

    # Get comments for the post
    comments = Comment.objects.filter(post=post).order_by('-id')

    context = {
        'post': post,
        'has_liked': has_liked,
        'comments': comments,
    }

    return render(request, 'view_post.html', context)

@login_required
def like_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
    
    return redirect('view_post', slug=slug)


@login_required
def my_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.blogpost_set.all()  # Posts written by this user
    return render(request, 'user_profile.html', {
        'profile_user': user,
        'posts': posts
    })

@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user != request.user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        Notification.objects.create(
            user=to_user,
            text=f"{request.user.username} has sent you a friend request."
        )
    return redirect('user_profile', username=username)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    from_user = friend_request.from_user
    to_user = request.user
    from_user.friends.add(to_user)
    to_user.friends.add(from_user)
    friend_request.delete()
    return redirect('notifications')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('notifications')

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = BlogPost.objects.filter(author=profile_user)
    is_friend = profile_user in request.user.friends.all() if request.user.is_authenticated else False
    has_sent_request = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).exists() if request.user.is_authenticated else False
    return render(request, 'user_profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_friend': is_friend,
        'has_sent_request': has_sent_request,
        'friend_count': profile_user.friends.count()
    })

@login_required
def notifications(request):
    notes = request.user.notifications.all().order_by('-created_at')
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'notifications.html', {
        'notifications': notes,
        'friend_requests': friend_requests
    })

@login_required
@csrf_exempt  
def chat_room(request, username):
    other_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')

            if not message:
                return HttpResponseBadRequest("Message is empty")

            ChatMessage.objects.create(
                user=request.user,
                recipient=other_user,
                message=message
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {e}")

    messages = ChatMessage.objects.filter(
        user__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    ).order_by('timestamp')

    return render(request, 'chat_room.html', {
        'messages': messages,
        'other_user': other_user,
        'room_name': f"{min(request.user.username, other_user.username)}_{max(request.user.username, other_user.username)}"
    })

@login_required
def chat_history(request):
    sent_to = ChatMessage.objects.filter(user=request.user).values_list('recipient', flat=True)
    received_from = ChatMessage.objects.filter(recipient=request.user).values_list('user', flat=True)

    user_ids = set(sent_to) | set(received_from)

    if user_ids:
        users_chatted_with = User.objects.filter(id__in=user_ids)
    else:
        users_chatted_with = []

    return render(request, 'chat_history.html', {
        'users_chatted_with': users_chatted_with
    })

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = ChatMessage.objects.filter(
        user__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    ).order_by('timestamp')
    return render(request, 'chat_room.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def toggle_bookmark(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
    return redirect('home')



def search(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query)
    posts = BlogPost.objects.filter(title__icontains=query)
    return render(request, 'search_results.html', {
        'users': users,
        'posts': posts,
        'query': query
    })

@login_required
def view_bookmarks(request):
    bookmarked_posts = BlogPost.objects.filter(bookmark__user=request.user).distinct()
    return render(request, 'bookmarked_posts.html', {
        'posts': bookmarked_posts,
    })