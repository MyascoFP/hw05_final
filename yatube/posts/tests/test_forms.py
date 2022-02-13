import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User
from yatube.settings import PICTURE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoBody')
        cls.group = Group.objects.create(
            title='Title',
            slug='test-slug',
            description='test description',
        )
        small_gif = PICTURE
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Test comment',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_creste_post(self):
        """Валидная форма создания поста."""
        small_gif = PICTURE
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста для теста',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text='Текст поста для теста',
                group=self.group.pk,
                image=''
            ).exists())

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Изменённый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(self.post.text, 'Изменённый текст')

    def test_add_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий'
            ).exists())

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
