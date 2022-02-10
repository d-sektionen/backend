from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from .views import BudgetEntryViewSet, FileViewSet

router = routers.DefaultRouter()
router.register(r'expense-entries', BudgetEntryViewSet)
router.register(r'files', FileViewSet)
#router.register(r'items', ItemViewSet)

"""approve = BudgetEntryViewSet.as_view({
    'post':'approve',
})"""

urlpatterns = [
    path(r"", include(router.urls)),
    #path(r"/expense-entries/approve/<int:pk>/", approve, "expense-approval")
]