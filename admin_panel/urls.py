from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path('', views.index, name='index'),
    path('testattempts/<int:testid>/', views.testattempts, name="test_attempts"),
    path('userattempts/<int:userid>/', views.userattempts, name="user_attempts"),
    path('deletetest/<int:testid>', views.delete_test, name="delete_test")
]
