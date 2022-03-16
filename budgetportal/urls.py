from django.urls import path, include
from rest_framework import routers

from .views import BudgetEntryViewSet, FileViewSet

router = routers.DefaultRouter()
router.register(r'expense-entries', BudgetEntryViewSet)
router.register(r'files', FileViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
]