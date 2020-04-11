from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from article.models import ArticlePost
from .forms import CommentForm


# 文章评论
@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id):
    # get_object_or_404()：它和Model.objects.get()的功能基本是相同的。
    # 区别是在生产环境下，如果用户请求一个不存在的对象时，
    # Model.objects.get()会返回Error 500（服务器内部错误），而get_object_or_404()会返回Error 404。相比之下，返回404错误更加的准确。
    article = get_object_or_404(ArticlePost, id=article_id)

    # 处理 POST 请求
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article   # comment.models.Comment
            new_comment.user = request.user
            new_comment.save()

            # 当其参数是一个Model对象时，会自动调用这个Model对象的get_absolute_url()方法，所以该模型必须先有该方法
            return redirect(article)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 处理错误请求
    else:
        return HttpResponse("发表评论仅接受POST请求。")