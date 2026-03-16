from django.urls import path
from . import views

app_name = 'static_serve'

urlpatterns = [
    path("<path:path>", views.serve_static, name="serve_static"),
]
