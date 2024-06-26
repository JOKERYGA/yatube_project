from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

# Create your models here.
User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts'
        )
    group = models.ForeignKey("Group",
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True,
                              null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу'
                              )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию, 
    # в которую будут загружаться пользовательские файлы
    
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Комментарии к посту",
        related_name="comments",
        blank=True,
        null=True
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               blank=True,
                               null=True
                               )
    text = models.TextField('Текст',
                            help_text='Текст нового комментария'
                            )
    
    def __str__(self):
        return f"{self.author.username} - {self.text}"


class Follow(CreatedModel):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик',
                             blank=True,
                             null=True
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               blank=True,
                               null=True)

    class Meta:
        unique_together = ['user', 'author']

    def __str__(self):
        return f"{self.user} подписан на {self.author}"