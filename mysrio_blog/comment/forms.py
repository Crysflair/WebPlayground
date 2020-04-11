from django import forms
from .models import Comment


# 因为模型中的2个外键将通过视图逻辑自动填写，所以这里只需要提交body就足够了
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']