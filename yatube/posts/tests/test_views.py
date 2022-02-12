import shutil
import tempfile
from urllib import response

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User

from yatube.settings import PAGE_CONST

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoBody')
        cls.author = User.objects.create_user(username='Author')

        cls.group1 = Group.objects.create(
            title='Title1',
            slug='test-slug1',
            description='test description 1',
        )
        cls.group2 = Group.objects.create(
            title='Title2',
            slug='test-slug2',
            description='test description 2'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group1,
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """Проверка использавания верных шаблонов."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'NoBody'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка использования верного context для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_text, 'Test text')
        self.assertEqual(post_image, self.post.image)

    def test_group_page_show_correct_context(self):
        """Проверка использования верного context для group list."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_group = first_object.group
        post_image = first_object.image
        self.assertEqual(post_text, 'Test text')
        self.assertEqual(post_group, self.group1)
        self.assertEqual(post_image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Проверка использования верного context для profile."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'NoBody'}
            ))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = first_object.author
        post_image = first_object.image
        self.assertEqual(post_text, 'Test text')
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Проверка использования верного context для post detail."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}
            ))
        self.assertEqual(response.context['post'].text, 'Test text')
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_create_post_page_show_correct_context(self):
        """Проверка использования верного context для create post."""
        response = self.authorized_client.get(reverse(('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value == value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Проверка использования верного context для post edit."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value == value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_post_exist(self):
        """Проверка, что пост появился на index."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_group = first_object.group
        self.assertEqual(post_group, self.group1)

    def test_group1_list_post_exist(self):
        """Проверка, что пост появился на group list 1."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug1'}
            ))
        first_object = response.context['page_obj'][0]
        post_group = first_object.group
        self.assertEqual(post_group, self.group1)

    def test_group2_list_post_not_exist(self):
        """Проверка, что пост не появился на group list 2."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug2'}
            ))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_post_exist(self):
        """Проверка, что пост появился на profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'NoBody'}))
        first_object = response.context['page_obj'][0]
        post_group = first_object.group
        self.assertEqual(post_group, self.group1)

    def test_cache_index_page_correct_context(self):
        """Кэш index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        content = response.content
        post_id = self.post.id
        instance = Post.objects.get(pk=post_id)
        instance.delete()
        new_response = self.authorized_client.get(reverse('posts:index'))
        new_content = new_response.content
        self.assertEqual(content, new_content)
        cache.clear()
        new_new_response = self.authorized_client.get(reverse('posts:index'))
        new_new_content = new_new_response.content
        self.assertNotEqual(content, new_new_content)

    def test_auth_can_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей."""
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'})
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Author'})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_auth_can_unfollow(self):
        """Авторизованный пользователь может отписываться от пользователей."""
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'Author'})
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Author'})
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_new_follow_post_show_correct(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        follow_response = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        follow_context = follow_response.context['page_obj']
        not_follow_response = self.author_client.get(reverse(
            'posts:follow_index'
        ))
        not_follow_context = not_follow_response.context['page_obj']
        self.assertNotEqual(follow_context, not_follow_context)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username='NoBody')
        cls.group = Group.objects.create(
            title='Title',
            slug='test-slug',
            description='test description',
        )
        for i in range(14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Test text {i}',
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Проверка, что на первой странице index 10 постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), PAGE_CONST)

    def test_index_second_page_contains_four_records(self):
        """Проверка, что на второй странице index 4 постов."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка, что на первой странице group list 10 постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ))
        self.assertEqual(len(response.context['page_obj']), PAGE_CONST)

    def test_group_list_second_page_contains_four_records(self):
        """Проверка, что на второй странице group list 4 постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка, что на первой странице profile 10 постов."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'NoBody'}))
        self.assertEqual(len(response.context['page_obj']), PAGE_CONST)

    def test_profile_second_page_contains_four_records(self):
        """Проверка, что на первой странице profile 4 постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'NoBody'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)
