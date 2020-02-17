from django.urls import path

from . import views

# 正在部署的应用的名称
app_name = 'article'  # Django2.0之后，app的urls.py必须配置app_name，否则会报错

urlpatterns = [
    path('article-list/', views.article_list, name='article_list'),
    path('article-detail/<int:id>', views.article_detail, name='article_detail'),
    path('article-create/', views.article_create, name='article_create'),
    path('article-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
    path('article-update/<int:id>/', views.article_update, name='article_update'),
]