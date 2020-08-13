from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost,ArticleColumn
from comment.models import Comment
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from taggit.utils import _parse_tags


def article_list(request):
    # 排序，需要GET请求中就已经给出order。GET请求也是可以传递多个参数的，如 ?a=1&b=2，参数间用&隔开
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    articles = ArticlePost.objects.all()
    if not order:
        order = 'normal'
    if not search:
        search = ''     # 如果用户没有搜索操作，则search = request.GET.get('search')会使得search = None，而这个值传递到模板中会错误地转换成"None"字符串！
    if not tag:
        tag = ''

    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search))
    if order == 'total_views':
        articles = articles.order_by('-total_views')  # ‘total_views’为正序，‘-total_views’为逆序
    if column and column.isdigit():
        articles = articles.filter(column=column)
    if tag:
        articles = articles.filter(tags__name__in=[tag])


    paginator = Paginator(articles, 6)
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
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])  # update_fields=[]指定了数据库只更新total_views字段，优化执行效率。
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
            'markdown.extensions.toc',  # 目录扩展
        ]
    )
    # 用convert()方法将正文渲染为html页面。通过md.toc将目录传递给模板。
    article.body = md.convert(article.body)

    comments = Comment.objects.filter(article=id)
    context = {'article': article, 'toc': md.toc, 'comments': comments}
    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    """
    created和updated字段为自动生成，不需要填入；
    剩下的title和body就是*表单*需要填入的内容了
    :param request:
    :return:
    """
    if request.method == "POST":
        # Form实例可以绑定到数据，也可以不绑定数据。
        # 如果绑定到数据，就能够验证该数据并将表单呈现为HTML并显示数据

        article_post_form = ArticlePostForm(data=request.POST, files=request.FILES)  # data: dict

        # 如果接受到的post正确地创建了表单对象
        if article_post_form.is_valid():
            # 通过form保存各种数据为新article
            new_article = article_post_form.save(commit=False)  # 暂时还不提交数据库, Form 里不全
            # 设置它的关联外键author
            new_article.author = User.objects.get(id=request.user.id)
            # 设置它的关联外键column
            column = request.POST['column']
            if column and column.isdigit():
                new_article.column = ArticleColumn.objects.get(id=column)
            else:
                new_article.column = None
            # 保存到数据库
            new_article.save()
            # 新增代码，保存 tags 的多对多关系,
            # 需要注意的是，如果提交的表单使用了commit=False选项，则必须调用save_m2m()才能正确的保存标签，就像普通的多对多关系一样。
            article_post_form.save_m2m()

            return redirect("article:article_list")  # redirect可通过url地址的名字，反向解析到对应的url。
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        # GET, 创建空表单类实例，render呈现
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
    更新文章的视图函数
    通过POST方法提交表单，更新title、body字段
    id: article id
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
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将原内容 article 文章对象也传递进去
        context = {'article': article,
                   'article_post_form': article_post_form,
                   'tags': article.tags.names(),
                   'columns': columns,
                   }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


