from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django_currentuser.db.models import CurrentUserField


User = get_user_model()


class Post(models.Model):
    text = models.CharField('Заглавление', max_length=200)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_by')
    pub_date = models.DateTimeField('Publication Date', auto_now=True)
    image = models.ImageField(upload_to='post-images', null=True)
    description = models.TextField(max_length=150)
    time_now = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'


class PostRate(models.Model):
    liked = models.BooleanField(null=True)
    rated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.rated_post)

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments',
                                    verbose_name='Объявление')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    text = models.TextField('Текст')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.post} --> {self.user}'
