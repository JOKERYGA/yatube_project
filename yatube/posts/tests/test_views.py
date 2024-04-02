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
        self.user = User.objects.create_user(username="VladosTestirovich")
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

    def test_assert_page_show_correct_context(self):
        # Создаем список объектов
        posts_list = [Post.objects.create(text=f"Тестовый пост {i}", author=self.user, group=self.group) for i in range(15)]
        
        # Создаем объект Paginator
        paginator = Paginator(posts_list, 10)
        
        # Проверяем первую страницу
        response = self.client.get(reverse("posts:index"))
        page_obj = response.context["page_obj"]
        
        # Проверяем, что объект страницы - это экземпляр Paginator
        self.assertIsInstance(page_obj.paginator, Paginator)
        
        # Проверяем, что номер страницы равен 1 (по умолчанию)
        self.assertEqual(page_obj.number, 1)
        
        # Проверяем, что количество элементов на странице равно 10
        self.assertEqual(len(page_obj.object_list), 10)

    def test_create_post_with_group(self):
        group = Group.objects.create(
            title="Test Group",
            slug="test-group",
            description="Test description"
        )
        response = self.authorized_client.post(reverse('posts:post_create'), {
            'text': 'Test post',
            'group': group.id  # Указываем ID созданной группы
        })
        # Проверяем, что после создания поста произошло перенаправление
        self.assertEqual(response.status_code, 302)
        # Проверяем, что произошло перенаправление на страницу профиля
        self.assertEqual(response.url, reverse('posts:profile', kwargs={'username': self.user.username}))
        
        # Проверяем наличие поста на главной странице сайта
        response_index = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response_index, 'Test post')
        
        # Проверяем наличие поста на странице выбранной группы
        response_group = self.authorized_client.get(reverse('posts:group_posts', kwargs={'slug': group.slug}))
        self.assertContains(response_group, 'Test post')
        
        # Проверяем наличие поста в профиле пользователя
        response_profile = self.authorized_client.get(reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertContains(response_profile, 'Test post')
        
        # Проверяем, что этот пост не попал в группу, для которой не был предназначен
        other_group = Group.objects.create(
            title="Other Group",
            slug="other-group",
            description="Other group description"
        )
        response_other_group = self.authorized_client.get(reverse('posts:group_posts', kwargs={'slug': other_group.slug}))
        self.assertNotContains(response_other_group, 'Test post')