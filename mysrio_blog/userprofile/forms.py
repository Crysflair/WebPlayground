from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserLoginForm(forms.Form):
    # forms.ModelForm 适合于需要直接与数据库交互的功能
    # forms.Form 需要手动配置每个字段，它适用于不与数据库进行直接交互的功能
    username = forms.CharField()
    password = forms.CharField()


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

    # 覆写 User 的密码
    # 覆写某字段之后，内部类class Meta中的定义对这个字段就没有效果了，所以fields不用包含password
    password = forms.CharField()
    password2 = forms.CharField()

    # def clean_[字段]这种写法Django会自动调用，来对单个字段的数据进行验证清洗
    def clean_password2(self):
        data = self.cleaned_data
        # data.get('password')是一种稳妥的写法，
        # 即使用户没有输入密码也不会导致data['password']程序错误而跳出。
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("密码输入不一致，请重新输入")



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')
