from django.db import models

# Create your models here.
# 每当你修改了models.py文件，都需要用makemigrations和migrate这两条指令迁移数据


from django.contrib.auth.models import User
# timezone 用于处理时间相关事务。
from django.utils import timezone


class ArticlePost(models.Model):

    class Meta:
        """
        元数据是“任何不是字段的东西”，例如排序选项ordering、数据库表名db_table、单数和复数名称verbose_name和 verbose_name_plural。这些信息不是某篇文章私有的数据，而是整张表的共同行为。
        要不要写内部类是完全可选的，当然有了它可以帮助理解并规范类的行为。
        """
        # ordering 指定模型返回的数据的排列顺序, '-created' 表明数据应该以倒序排列
        ordering = ('-created',)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 使用 ForeignKey定义一个关系。这将告诉 Django，每个（或多个） ArticlePost 对象都关联到一个 User 对象
    # Django具有一个简单的账号系统（User），满足一般网站的用户相关的基本功能

    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return self.title 将文章标题返回
        return self.title