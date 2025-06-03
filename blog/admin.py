from django.contrib import admin
from .models import BlogPost,Category,Like,Comment

# @admin.register(BlogPost)
# class BlogPostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author', 'created_at')
#     search_fields = ('title', 'description', 'author__username')
#     list_filter = ('created_at',)

admin.site.register(BlogPost)
admin.site.register(Category)
admin.site.register(Like)
admin.site.register(Comment)