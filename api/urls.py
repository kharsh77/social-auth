from django.urls import path

from . import views

urlpatterns = [

    path('user', views.createUser, name='createUser'),

    path('user/all', views.listUsers, name='listUsers'),

	path('user/setpassword/<int:user_id>', views.setPassword, name='setPassword'),

	path('user/<int:user_id>', views.getUsers, name='getUsers'),

	path('user/search/<str:key>', views.searchUsers, name='searchUsers'),

	path('login', views.login, name='login'),

    path('logout', views.logout, name='logout'),

]
