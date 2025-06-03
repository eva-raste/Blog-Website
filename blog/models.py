from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# In your BlogPost model:
# models.py
class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
# blog/models.py
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Optionally ensure uniqueness
            original_slug = self.slug
            num = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)

    @property
    def like_count(self):
        return self.like_entries.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='like_entries')  # renamed!

    class Meta:
        unique_together = ('user', 'post')  # A user can like a post only once

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} ➝ {self.to_user}'

# Add this in the User model (you can use a custom user model or monkey patch)
User.add_to_class('friends', models.ManyToManyField('self', symmetrical=True, blank=True))

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.recipient.username}: {self.message[:20]}"
    

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')
