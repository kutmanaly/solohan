import rest_framework
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, generics
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from accounts.models import User
from . import permissions
from .models import Post, Comment, Profile, PostRate, Follower
from .permissions import IsAuthor, IsAuthorOrIsAdmin
from .serializers import (PostListSerializer,
                          PostDetailSerializer,
                          CreatePostSerializer,
                          CommentSerializer, ProfileSerializer, PostRateSerializer, PostSerializer, FollowerSerializer)
from rest_framework import filters


class PostFilter(rest_filters.FilterSet):
    created_at = rest_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Post
        fields = ('created_at',)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer
    permission_classes = [IsAuthorOrIsAdmin]
    filter_backends = [rest_filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'text']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return CreatePostSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthor()]


class ProfileViewSet(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request): # change this to use the patch mixin
        profile = Profile.objects.filter(user=request.user).first()
        profile.first_name = request.data['first_name']
        profile.last_name = request.data['last_name']
        profile.bio = request.data['bio']
        profile.location = request.data['location']
        profile.save()
        return JsonResponse({"response": "change successful"})


class PostRateViewSet(generics.GenericAPIView):  # use mixins instead
    queryset = PostRate.objects.all()
    serializer_class = PostRateSerializer

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        data = {
            'likes_count': PostRate.objects.filter(liked=True, rated_post=post).count(),
            'dislikes_count': PostRate.objects.filter(liked=False, rated_post=post).count()
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=request.data["rated_post"]["id"])
        post_rating = PostRate.objects.filter(rated_by=request.user, rated_post=post).first()
        user_liked_post = request.data["liked"]

        if post_rating:
            if user_liked_post:
                if post_rating.liked:
                    post_rating.liked = None
                else:
                    post_rating.liked = True
            elif not user_liked_post:
                if post_rating.liked == False:
                    post_rating.liked = None
                else:
                    post_rating.liked = False
        else:
            post_rating = PostRate(liked=user_liked_post, rated_by=request.user, rated_post=post)

        post_rating.save()

        data = {
            'total_likes': PostRate.objects.filter(liked=True, rated_post=post).count(),
            'total_dislikes': PostRate.objects.filter(liked=False, rated_post=post).count()
        }
        return JsonResponse(data)


class CommentList(generics.ListAPIView):  # turn this into a method in postviewset
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(in_reply_to_post=self.kwargs["pk"])


@login_required
def follow(request, pk):
    user = get_object_or_404(User, pk=pk)
    already_followed = Follower.objects.filter(user=user, is_followed_by=request.user).first()
    if not already_followed:
        new_follower = Follower(user=user, is_followed_by=request.user)
        new_follower.save()
        follower_count = Follower.objects.filter(user = user).count()
        return JsonResponse({'status': 'Following', 'count': follower_count})
    else:
        already_followed.delete()
        follower_count = Follower.objects.filter(user = user).count()
        return JsonResponse({'status': 'Not following', 'count': follower_count})
    return redirect('/')


class Following(generics.ListCreateAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk = self.kwargs["pk"])
        return Follower.objects.filter(is_followed_by = user)


class Followers(generics.ListCreateAPIView):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(User, pk = self.kwargs["pk"])
        return Follower.objects.filter(user = user).exclude(is_followed_by=user)


    @login_required
    def profile(request, user_id):
        user = get_object_or_404(User, pk = user_id)
        users_posts = Post.objects.filter(user = user)
        return render(request, 'social/user.html', {
            'user_info': user,
            'request_user': request.user,
            'latest_posts_list': users_posts,
            'latest_post': users_posts,
        })


    @login_required
    def change_info(request):
        return render(request, 'social/change_info.html', {})
