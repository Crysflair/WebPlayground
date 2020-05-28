from django.contrib import admin

# Register your models here.

from .models import ArticlePost, ArticleColumn

# 接下来我们需要“告诉”Django，后台中需要添加ArticlePost这个数据表供管理。
admin.site.register(ArticlePost)

# 注册文章栏目
admin.site.register(ArticleColumn)