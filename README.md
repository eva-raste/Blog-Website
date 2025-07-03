# 📝 Django Blog & Social Platform

A **feature-rich social blogging platform** built with **Django**, combining the essence of blogging and social networking in one application. Users can write blogs, interact through likes, comments, friend requests, and even chat with other users through a real-time chat feature using **Django Channels**.

---

## 🌟 Key Features

- ✅ **User Authentication** (Signup, Login, Logout with support for Google OAuth)
- 🖼️ **Create/Edit/Delete Blog Posts** with optional image upload and category tagging
- 📚 **Paginated Blog Feed** with category-based filtering
- ❤️ **Like, Comment, and Bookmark** blog posts
- 👥 **Friend System** (Send/Accept/Decline Friend Requests)
- 🔔 **Real-time Notifications** for comments and friend requests
- 💬 **Private Chat Messaging** between friends using Django Channels (WebSocket-based)
- 📌 **Bookmark Manager** to view all your saved posts
- 🔍 **Search Functionality** to explore posts and users
- 🧑‍💼 **User Profiles** displaying authored posts and friendship status

---

## 🛠️ Tech Stack

- **Backend:** Django 4.x, 
- **Frontend:** HTML5, CSS, JS
- **Real-time Chat:** Django Channels + WebSockets
- **Authentication:** Django’s built-in auth system 
- **Database:** SQLite 
---

##  Requirements

Make sure you have the following installed:

- Python 3.8+
- Django 4.x
- Django Channels
- Daphne
- SQLite

---
## Run Migrations

python manage.py makemigrations
python manage.py migrate

---
## Start Development Server

python manage.py runserver
daphne BlogWebsite.asgi:application
