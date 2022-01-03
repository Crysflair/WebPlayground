from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from .forms import ProfileForm
from .models import Profile

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
    return HttpResponse("目前不开放新用户注册哦！")


# 如果未登录则不执行函数，将页面重定向到/userprofile/login/
@login_required(login_url='/userprofile/login/')
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


# 编辑用户信息
# 如果未登录则不执行函数，将页面重定向到/userprofile/login/
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)

    # 修改后的代码: 根据需要创建或提取profile，避免后台单独操作的问题
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        profile_form = ProfileForm(data=request.POST, files=request.FILES)

        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data  # 取得清洗后的合法数据
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            # 如果request.FILES中存在键为avatar的元素，则将其赋值给profile.avatar（注意保存的是图片地址）
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]

            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form,
                   'profile': profile,
                   'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")






