from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown


def article_list(request):
    articles = ArticlePost.objects.all()  # ArticlePost.objects.all()是数据类的方法，可以获得所有的对象（即博客文章）
    context = {'articles': articles}
    # return HttpResponse("Response content: Hello Ferax!")

    # 最后返回了render函数。它的作用是结合模板和上下文，并返回渲染后的HttpResponse对象。
    # 通俗的讲就是把context的内容，加载进模板，并通过浏览器呈现
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.body = markdown.markdown(
        article.body,
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite"
        ]
    )
    context = {'article': article}
    return render(request, 'article/detail.html', context)


def article_create(request):
    """
    created和updated字段为自动生成，不需要填入；
    author字段暂时固定为id=1的管理员用户，也不用填入；
    剩下的title和body就是*表单*需要填入的内容了
    :param request:
    :return:
    """
    if request.method == "POST":
        # Form实例可以绑定到数据，也可以不绑定数据。
        # 如果绑定到数据，就能够验证该数据并将表单呈现为HTML并显示数据

        article_post_form = ArticlePostForm(data=request.POST)  # data: dict

        # 如果接受到的post正确地创建了表单对象
        if article_post_form.is_valid():
            # 暂时还不提交数据库
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=1)
            new_article.save()  # 保存到数据库
            return redirect("article:article_list")  # redirect可通过url地址的名字，反向解析到对应的url。
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        # 创建空表单类实例，render呈现
        article_post_form = ArticlePostForm()
        context = {'article_post_form': article_post_form}
        return render(request, 'article/create.html', context)



def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")



def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新title、body字段
    id: article id
    """
    article = ArticlePost.objects.get(id=id)
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，更新文章失败")
    else:
        article_post_form = ArticlePostForm()
        # 赋值上下文，将原内容 article 文章对象也传递进去
        context = {'article': article, 'article_post_form': article_post_form }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


