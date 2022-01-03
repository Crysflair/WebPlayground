from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost,ArticleColumn
# from comment.models import Comment
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from taggit.utils import _parse_tags


def article_list(request):
    # 从GET请求中获得形如?a=1&b=2的参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    if not order:
        order = 'normal'
    if not search:  # 小心None被转化成'None'
        search = ''
    if not tag:
        tag = ''

    # 构建Query
    articles = ArticlePost.objects.all()
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(body__icontains=search))
    if order == 'total_views':
        articles = articles.order_by('-total_views')  # ‘total_views’为正序，‘-total_views’为逆序。
    if column and column.isdigit():
        articles = articles.filter(column=column)     # 按栏目编号过滤。判定格式避免有人故意捣乱填非法值。
    if tag:
        articles = articles.filter(tags__name__in=[tag])

    # 分页
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {'articles': articles,
               'order': order,
               'search': search,
               'column': column,
               'tag': tag,
               }
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    # 获取文章
    article = ArticlePost.objects.get(id=id)

    # 每次请求增加一次浏览计数
    article.total_views += 1
    article.save(update_fields=['total_views'])  # update_fields=[]指定了数据库只更新total_views字段。优化执行效率。

    # 获取评论
    # comments = Comment.objects.filter(article=id)

    # 渲染markdown
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
            'markdown.extensions.toc',           # 目录扩展
        ]
    )
    article.body = md.convert(article.body)
    context = {'article': article, 'toc': md.toc}
    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    """
    创建文章。
    created和updated字段为自动生成，不需要填入；剩下的title和body是*表单*需要填入的内容了
    """
    if not request.user.is_staff:
        return HttpResponse("抱歉，您目前没有权限发表文章")

    if request.method == "POST":
        # 把request中的数据填到Form实例中便于自动验证
        article_post_form = ArticlePostForm(data=request.POST, files=request.FILES)

        if article_post_form.is_valid():
            # 从form中形成article对象。暂不提交。
            # save(): Save this form's self.instance object if commit=True.
            # Otherwise, add a save_m2m() method to the form after the instance is saved manually.
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)       # 设置它的关联外键author
            column = request.POST['column']                                 # 设置它的关联外键column
            if column and column.isdigit():
                new_article.column = ArticleColumn.objects.get(id=column)
            else:
                new_article.column = None

            new_article.save()                  # 保存到数据库
            article_post_form.save_m2m()        # 需要手动保存tags的多对多关系（因为之前commit=False）

            return redirect("article:article_list")     # redirect可通过url地址的名字，反向解析到对应的url
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        # GET 创建空表单类实例 render呈现
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if article.author.id != request.user.id:
            return HttpResponse("不能删除其他人的文章")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章
    """
    article = ArticlePost.objects.get(id=id)
    if article.author.id != request.user.id:
        return HttpResponse("不能修改其他人的文章")

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.note = request.POST['note']
            if 'heading_img' in request.FILES:
                article.heading_img = request.FILES["heading_img"]
            column = request.POST['column']
            if column and column.isdigit():
                article.column = ArticleColumn.objects.get(id=column)
            else:
                article.column = None
            if request.POST['tags']:
                article.tags.set(*_parse_tags(request.POST['tags']), clear=True)
            article.save()

            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，更新文章失败")
    else:
        # GET方法 将原内容文章传递进去
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article': article,
                   'article_post_form': article_post_form,
                   'tags': article.tags.names(),
                   'columns': columns,
                   }
        return render(request, 'article/update.html', context)


