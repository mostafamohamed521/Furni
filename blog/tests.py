from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Post, Comment


class BlogCommentModerationTests(TestCase):
    """Covers: blog comments (postable by anonymous visitors) require
    approval before appearing publicly, same as product reviews."""

    def setUp(self):
        author = User.objects.create_user(username='author', password='x')
        self.post = Post.objects.create(title='Test Post', author=author, content='Body text')

    def test_new_comment_is_not_approved_by_default(self):
        comment = Comment.objects.create(post=self.post, name='Guest', email='g@example.com', body='Hi')
        self.assertFalse(comment.is_approved)

    def test_unapproved_comment_not_shown_publicly(self):
        Comment.objects.create(post=self.post, name='Guest', email='g@example.com', body='Hidden comment text')
        resp = self.client.get(self.post.get_absolute_url())
        self.assertNotContains(resp, 'Hidden comment text')

    def test_honeypot_blocks_bot_comment(self):
        self.client.post(self.post.get_absolute_url(), {
            'name': 'Bot', 'email': 'bot@example.com', 'body': 'spam', 'website': 'http://spam.com',
        })
        self.assertFalse(Comment.objects.filter(email='bot@example.com').exists())
