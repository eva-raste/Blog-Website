from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.signup_view, name='signup'),



    path('create/', views.create_post, name='create_post'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:pk>/', views.delete_post, name='delete_post'),
    # path('post/<int:pk>/', views.view_post, name='view_post'),
    path('post/<slug:slug>/', views.view_post, name='view_post'),
    path('signup/', views.signup_view, name='signup'),
    # path('notifications/', views.my_notifications, name='my_notifications'),
     path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),

    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('send-friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('notifications/', views.notifications, name='notifications'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),
    path('search/', views.search, name='search'),
    path('bookmark/<int:post_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.view_bookmarks, name='view_bookmarks'),

]



#admin,admin@123