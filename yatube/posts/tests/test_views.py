from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.paginator import Paginator

from posts.models import Post, Group

User = get_user_model()


class TestPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.number_of_posts = 30
        cls.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Описание тестовой группы",
        )
        for post_id in range(cls.number_of_posts):
            Post.objects.create(text=f"Тестовый пост {post_id}", author=cls.user, group=cls.group)
        cls.post = Post.objects.first()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_templates(self):
        template_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse("posts:group_posts", kwargs={"slug": self.group.slug}),
            "posts/profile.html": reverse("posts:profile", kwargs={"username": self.user.username}),
            "posts/post_detail.html": reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
            "posts/create_post.html": reverse("posts:post_create"),
        }

        for template, url in template_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)