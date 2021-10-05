from rest_framework import serializers

from posts.models import Post, Comment, PostRate, User


class PostListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('text', 'posted_by', 'pub_date', 'image')


class PostDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['comments'] = CommentSerializers(instance.comments.all(), many=True).data
        return rep


class CreatePostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ('posted_by',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['posts'] = PostDetailSerializers(instance.comments.all(), many=True).data
        return rep
    

class PostRateSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())

    class Meta:
        model = PostRate
        fields = '__all__'


class CreatePostRateSerializers(serializers.ModelSerializer):
    class Meta:
        model = PostRate
        exclude = ('rated_by', 'rated_post')

        def create(self, validated_data):
            request = self.context.get('request')
            validated_data['user'] = request.user
            return super().create(validated_data)


class CommentSerializers(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(write_only=True,
                                                     queryset=Post.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('user', 'text', 'post', )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)
















