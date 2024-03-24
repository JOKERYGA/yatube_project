from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
        )
    group = models.ForeignKey("Group",
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts')

    def __str__(self) -> str:
        return self.text


class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
