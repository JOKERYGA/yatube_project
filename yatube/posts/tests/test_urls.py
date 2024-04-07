from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестового пользователя, группу и пост
        cls.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Описание тестовой группы",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост", author=cls.user, group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="VladosTestirovich")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages_accessibility_for_all(self):
        """Тестирование страниц"""
        public_pages = {
            "index": reverse("posts:index"),
            "group_posts": reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ),
            "profile": reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ),
            "post_detail": reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ),
        }

        for page_name, url in public_pages.items():
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(url)
                if page_name in ["index", "group_posts"]:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    # Для авторизованного пользователя
    def test_authorized_users(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_access(self):
        """Авторизованный пользователь, который
        является автором поста, должен иметь доступ к редактированию
        """
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        # Проверяем, что запрос был перенаправлен
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": self.user.username}),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}),
            "posts/create_post.html": reverse(
                "posts:post_create"),
        }
        # Очистка кэша перед каждым запросом
        cache.clear()

        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
                
    def test_creat_post_template(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertTemplateUsed(response, "posts/create_post.html")
