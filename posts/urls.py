from django.urls import path, include
from rest_framework.routers import SimpleRouter

from posts.views import CommentViewSet, PostViewSet

router = SimpleRouter()
router.register('posts', PostViewSet, 'posts')
router.register('comments', CommentViewSet, 'comments')

urlpatterns = [
    path('', include(router.urls)),
]