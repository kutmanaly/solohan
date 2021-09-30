from django.contrib import admin

from posts.models import Profile, Post, PostRate, Comment, Follower

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(PostRate)
admin.site.register(Follower)
admin.site.register(Comment)
