from django.urls import path

from from_git import views

urlpatterns = [
    # path('test', views.GitAggregator, name='git-aggregator'),
    path('test', views.GitAggregatorTest, name='test'),
]