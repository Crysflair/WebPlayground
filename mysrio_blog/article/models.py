from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    title = models.CharField(max_length=100, blank=True)    # 栏目标题
    created = models.DateTimeField(default=timezone.now)    # 创建时间

    def __str__(self):
        return self.title


class ArticlePost(models.Model):

    class Meta:
        """
        元数据是“任何不是字段的东西”，例如排序选项ordering、数据库表名db_table、单数和复数名称 verbose_name 和 verbose_name_plural
        这些信息不是某篇文章私有的数据，而是整张表的共同行为。要不要写内部类是完全可选的，当然有了它可以帮助理解并规范类的行为。
        """
        # ordering 指定模型返回的数据的排列顺序, '-created' 表明数据应该以创建时间倒序排列
        ordering = ('-created',)


    # 使用ForeignKey定义外键关系：ArticlePost对象 → User 对象
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)                # 标题
    body = models.TextField()                               # 内容
    note = models.TextField(blank=True)                     # 摘要
    created = models.DateTimeField(default=timezone.now)    # 创建时间。
    updated = models.DateTimeField(auto_now=True)           # 更新时间。auto_now=True 指定每次数据更新时自动写入当前时间
    total_views = models.PositiveIntegerField(default=0)    # 浏览计数

    # 文章栏目的 “一对多” 外键
    # ForeignKey.related_name：The name to use for the relation from the related object back to this one.
    column = models.ForeignKey(ArticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name='article')

    tags = TaggableManager(blank=True)

    heading_img = models.ImageField(upload_to='article/%Y%m%d/', blank=True)

    def __str__(self):
        return self.title

    # 用于render一个对象
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能，因为图片处理是基于已经保存的图片的，所以这句一定要在处理图片之前执行
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 排除掉统计浏览量调用的save(update_fields=['total_views'])，免得影响性能。这种判断方法虽然简单，但会造成模型和视图的紧耦合
        # 固定宽度缩放图片大小。heading_img若为空则不处理，
        if self.heading_img and not kwargs.get('update_fields'):
            image = Image.open(self.heading_img)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            # 用新图片将原始图片覆盖掉。Image.ANTIALIAS表示缩放采用平滑滤波。
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.heading_img.path)

        return article
