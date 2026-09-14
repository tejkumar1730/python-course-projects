from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('add/',views.edit,name='add'),path('<int:pk>/edit/',views.edit,name='edit'),path('<int:pk>/delete/',views.delete,name='delete')]
