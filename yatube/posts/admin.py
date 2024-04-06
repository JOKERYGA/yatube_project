from django.contrib import admin
from .models import Post, Group


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    # Перечисляю поля, которые должны отображаться в админке
    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    #Добавляю возможность изменения поля group в любом месте поста, прям из списка постов
    list_editable = ("group",)
    # Добавляю интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # Добавляю возможность фильтрации по дате
    list_filter = ("pub_date",)
    # Это свойство сработает для всех колонок: где пусто - там будет эта строка
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
