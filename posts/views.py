from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from posts.models import Comment, Post
from posts.permissions import IsAuthorOrIsAdmin, IsAuthor
from posts.serializers import PostDetailSerializers, PostListSerializers, CreatePostSerializers, CommentSerializers
from django_filters import rest_framework as rest_filters
from rest_framework import filters


class PostFilter(rest_filters.FilterSet):
    created_at = rest_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Post
        fields = ('posted_by', 'pub_date')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()  #queryset - список объектов модели
    serializer_class = CreatePostSerializers
    # класс, которым будут сериализоваться эти объекты
    permission_classes = [IsAuthorOrIsAdmin]
    filter_backends = [rest_filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['text', 'description']
    ordering_fields = ['create', 'text']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializers
        elif self.action == 'retrieve':
            return PostDetailSerializers
        return CreatePostSerializers


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthor()]




