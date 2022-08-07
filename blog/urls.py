from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registerUser, name='register'),
    path('update-post/', views.createPost, name='create-post'),
    path('update-post/<str:pk>', views.updatePost, name='update-post'),
    path('delete-post/<str:pk>', views.deletePost, name='delete-post'),
    path('delete-comment/<id>/<slug>',
         views.deleteComment, name='delete-comment'),
    path('delete-reply/<id>/<slug>',
         views.deleteReply, name='delete-reply'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('detail/<slug>', views.post_details, name='post'),
    path('reply/<id>/<slug>',
         views.ReplyPage, name='reply'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         views.activate, name='activate'),
    path('like/', views.like_post, name='like_post'),

]
