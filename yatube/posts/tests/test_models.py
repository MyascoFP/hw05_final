from django.db import IntegrityError
from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        expected_post = post.text[:15]
        self.assertEqual(expected_post, str(post))

        group = self.group
        expected_group = group.title
        self.assertEqual(expected_group, str(group))

        comment = self.comment
        expected_comment = comment.text[:15]
        self.assertEqual(expected_comment, str(comment))

    def test_models_have_correct_help_text(self):
        post = self.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Текст нового поста')

        comment = self.comment
        help_text = comment._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Текст нового комментария')

    def test_cannot_follow_yourself(self):
        """Пользователь не может пописаться на себя."""
        with self.assertRaises(IntegrityError) as context:
            Follow.objects.create(
                user=self.user,
                author=self.user,
            )
        self.assertTrue('CHECK constraint failed' in str(context.exception))

    def test_follow_is_unique(self):
        """Каждая подписка должна быть уникальна."""
        with self.assertRaises(IntegrityError) as context:
            for i in range(2):
                Follow.objects.create(
                    user=self.user,
                    author=self.author,
                )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))
