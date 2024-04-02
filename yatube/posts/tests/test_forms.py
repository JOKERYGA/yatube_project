import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.forms import PostCreateForm
from posts.models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.text import slugify


User = get_user_model()
# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, лишний код, но важный для меня
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFromPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VladosTestirovich')
        cls.group = Group.objects.create(title='TestGroup', slug=slugify('TestGroup'), description='Test Description')
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.form = PostCreateForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'author': self.user,
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        # Проверяю, сработал ли редирект
        self.assertRedirects(response, reverse("posts:profile", kwargs={'username': self.user}))
        # Проверяю, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # проверяю, создался ли пост, который мы заказывали.
        # проверим что text, автор и группа совпадает.
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        ).exists())

    def test_post_edit(self):
        """Валидная форма обновляет запись в Post."""
        post = Post.objects.create(author=self.user, text='Original text', group=self.group)
        new_text = 'Edited text'
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            {'text': new_text, 'group': self.group.pk}
        )
        post.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(post.text, new_text)