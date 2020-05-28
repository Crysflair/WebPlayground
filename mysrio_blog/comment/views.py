from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from article.models import ArticlePost
from .models import Comment
from .forms import CommentForm


# 文章评论
@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id, parent_comment_id=None):
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

            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若回复层级超过二级，则转换为二级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()
                new_comment.save()
                return HttpResponse('200 OK')
            else:
                new_comment.save()
                return HttpResponse('200 OK')
                # 当其参数是一个Model对象时，会自动调用这个Model对象的get_absolute_url()方法，所以该模型必须先有该方法
                # return redirect(article)
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    elif request.method == 'GET':
        comment_form = CommentForm()
        context = {
            'comment_form': comment_form,
            'article_id': article_id,
            'parent_comment_id': parent_comment_id
        }
        return render(request, 'comment/reply.html', context)

    # 处理其他请求
    else:
        return HttpResponse("仅接受GET/POST请求。")
