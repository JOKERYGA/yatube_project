from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

# Как пример, можно заранее подготовить файл с фикстурами, чтобы использовать его во всех тестах
# Я для отработки навыков сделал задания в лоб.
class PostFixturesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='owner')
        Group.objects.bulk_create(
            [
                Group(
                    title='Тестовая группа',
                    slug='test-slug',
                    description='Тестовое описание группы 1',
                ),
                Group(
                    title='Тестовая группа 2',
                    slug='topik',
                    description='Тестовое описание группы 2',
                )
            ]
        )
        cls.group = Group.objects.get(pk=1)
        cls.group2 = Group.objects.get(pk=2)
        posts_add_new_with_group = []
        for i in range(15, 25):
            posts_add_new_with_group.append(
                Post(
                    id=f'{i}',
                    text=f'Тестовая запись поста {i}',
                    author=cls.user,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(posts_add_new_with_group)
        cls.post = Post.objects.create(
            id=2,
            text='Тестовая запись более пятнадцати символов',
            author=cls.user,
            group=cls.group,
        )
        # создадим 4 поста с группой
        posts_with_group = []
        for i in range(4, 7):
            posts_with_group.append(
                Post(
                    id=f'{i}',
                    text=f'Тестовая запись поста {i}',
                    author=cls.user,
                    group=cls.group,
                )
            )
        # массовое добавление(создание) постов в бд
        Post.objects.bulk_create(posts_with_group)
        cls.check_objects = Post.objects.create(
            id=1,
            text='Первая тестовая запись',
            author=cls.user,
            group=cls.group,
        )
        cls.check_objects_group = Post.objects.create(
            id=3,
            text='Вторая тестовая запись с группой',
            author=cls.user,
        )
        # создадим 8 постов без группы
        posts_without_group = []
        for i in range(7, 15):
            posts_without_group.append(
                Post(
                    id=f'{i}',
                    text=f'Тестовая запись поста {i}',
                    author=cls.user,
                )
            )
        Post.objects.bulk_create(posts_without_group)
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_owner = Client()
        self.authorized_client_owner.force_login(self.user2)
