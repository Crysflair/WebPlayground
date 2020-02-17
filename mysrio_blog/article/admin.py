from django.contrib import admin

# Register your models here.

from .models import ArticlePost

# 接下来我们需要“告诉”Django，后台中需要添加ArticlePost这个数据表供管理。
admin.site.register(ArticlePost)