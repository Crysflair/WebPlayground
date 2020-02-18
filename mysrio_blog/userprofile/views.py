from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .form import UserLoginForm, UserRegisterForm

# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data
            # If the given credentials are valid, return a User object
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("用户名或密码有误")
        else:
            return HttpResponse("用户名或密码不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form, }
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')


def user_logout(request):
    logout(request)
    return redirect("article:article_list")


def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)    # 登录状态
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单输入有误，请重新输入")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {"form": user_register_form}
        return render(request, "userprofile/user_register.html", context)
    else:
        return HttpResponse("请使用GET或POST请求数据！")


@login_required(login_url='/userprofile/login/')    # 如果未登录则不执行函数，将页面重定向到/userprofile/login/地址去
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)  # 数据库user
        if request.user == user:    # 当前user
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return HttpResponse("仅接受post请求。")






