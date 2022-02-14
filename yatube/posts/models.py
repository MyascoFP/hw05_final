from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        pass

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField('Текст', help_text='Текст нового поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ('-created',)
        pass

    def __str__(self) -> str:
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Текст', help_text='Текст нового комментария')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        pass

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_follow'),
            models.CheckConstraint(check=~Q(author=F('user')), name='no_self_follow')
        ]
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        pass

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
