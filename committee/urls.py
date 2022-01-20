from django.urls import path

from committee import views

urlpatterns = [
    path('all/', views.get_committees)
]