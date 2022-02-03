from django.urls import path

from committee import views

urlpatterns = [
    path('all/', views.get_committees),
    path('<int:id>/', views.get_committee),
    path('<int:id>/members/', views.get_committee_members)
]