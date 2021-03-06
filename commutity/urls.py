from django.conf.urls import url
from . import views

app_name = 'commutity'
urlpatterns = [
        url(r'^$', views.IndexView.as_view(), name='index'),
        url(r'^login/$', views.LoginView.as_view(), name='login'),
        url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
        url(r'^create-account/$', views.CreateAccountView.as_view(), name='create-account')
    ]
