from django.db import models
from django.contrib.auth.models import User
from article.models import ArticlePost


# 博文的评论
class Comment(models.Model):
    class Meta:
        ordering = ('created',)

    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:20]