from django.urls import path

from . import views

urlpatterns = [
    path("<str:agentid>/<int:pk>/chocoresult/", views.ChocoResultV4.as_view()),
    path("<str:agentid>/<int:pk>/installomatorresult/", views.InstallomatorResultV4.as_view()),
]
