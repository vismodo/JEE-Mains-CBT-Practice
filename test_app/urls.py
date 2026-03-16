from django.urls import path
from . import views

app_name = 'test_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test_view, name='test'),
    path('start/<int:test_id>/', views.start_test, name='start_test'),
    path('test/nav/<int:question_number>/', views.nav_question, name='nav_question'),
    path('testanalysis/<int:attempt_id>/', views.test_analysis, name='testanalysis'),
]
