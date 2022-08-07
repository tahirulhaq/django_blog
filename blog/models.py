from importlib import import_module
from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from ckeditor_uploader.fields import RichTextUploadingField

STATUS = (
    (0, 'Draft'),
    (1, 'Publish'),
)


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    # content = models.TextField()
    content = RichTextUploadingField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    # likes = models.ManyToManyField(Session, related_name='likes', blank=True)
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes

    def increment_likes(self):
        self.likes = self.likes + 1
        self.save()
        return self.likes

    def decrement_likes(self):
        self.likes = self.likes - 1
        self.save()
        return self.likes


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]


class Reply(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)
    post_date = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-post_date"]

    def __str__(self):
        return self.description
