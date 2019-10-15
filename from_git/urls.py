from django.urls import path

from from_git import views

app_name='from_git'
urlpatterns = [
    # path('test', views.GitAggregator.as_view(), name='git-aggregator'),
    path('test', views.GitAggregatorTest.as_view(), name='test'),
]