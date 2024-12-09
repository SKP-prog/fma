from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('figures', views.figure, name="figure"),
    path('favs', views.favs, name="favs")
]