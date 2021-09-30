from .views import (PostViewSet,
                    CommentViewSet)
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register('posts', PostViewSet, 'posts')
router.register('comments', CommentViewSet, 'comments')


urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'backend'

router = SimpleRouter()
router.register(r'api/post', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/post/rate/', views.PostRateViewSet.as_view(), name='rate'),
    path('api/post/rating/<int:pk>/', views.PostRateViewSet.as_view(), name='rating'),
    path('api/post/retrieve-comments/<int:pk>/', views.CommentList.as_view(), name='retrieve-comments'),

    path('api/profile/', views.ProfileViewSet.as_view(), name='profile-change'),
    path('api/profile/<int:pk>/', views.ProfileViewSet.as_view(), name='profile-retrieve'),

    path('api/follow/<int:pk>/', views.follow, name='follow'),
    path('api/following/<int:pk>/', views.Following.as_view(), name='following'),
    path('api/followers/<int:pk>/', views.Followers.as_view(), name='followers'),
]