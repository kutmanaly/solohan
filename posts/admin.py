from django.contrib import admin

from posts.models import Post, PostRate, Comment

admin.site.register(Post)
admin.site.register(PostRate)
admin.site.register(Comment)

