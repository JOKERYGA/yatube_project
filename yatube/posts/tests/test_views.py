from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, Comment

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
        """Проверка соотношения html"""
        template_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse("posts:group_posts", kwargs={"slug": self.group.slug}),
            "posts/profile.html": reverse("posts:profile", kwargs={"username": self.user.username}),
            "posts/post_detail.html": reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
            "posts/create_post.html": reverse("posts:post_create"),
        }

        cache.clear() 
        
        for template, url in template_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
                
    def test_commenting(self):
        """Комментировать посты может только авторизованный пользователь"""
        # Отправляем POST-запрос на страницу добавления комментария
        response = self.authorized_client.post(reverse("posts:add_comment", kwargs={"post_id":self.post.id}), {"text": "Test comment"})
        
        # Проверяем, что комментарий добавлен
        # Проверяем, что происходит перенаправление
        self.assertEqual(response.status_code, 302)
        # Проверяем, что комментарий добавлен
        self.assertTrue(Comment.objects.filter(text="Test comment").exists())

    def test_add_comment(self):
        """после успешной отправки комментарий появляется на странице поста."""
        comment_text = "Test comment"
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id":self.post.id}),
            {"text": comment_text}, follow=True
            )

        # Проверяем, что запрос прошел успешно
        self.assertEqual(response.status_code, 200)
        # Проверяем, что комментарий появился на странице
        self.assertContains(response, comment_text)

    def test_cache_works(self):
        # Удаляем первую запись
        first_post = Post.objects.first()
        first_post.delete()
        
        # Проверяем, что запись больше не отображается на главной странице после удаления
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response, first_post.text)

        # Очищаем кэш
        cache.clear()

        # Проверяем, что запись исчезла из кэша и не отображается на главной странице
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response, first_post.text)