from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"page", views.PageReadOnlyAPI)

urlpatterns = [
    path("info/", views.InfoAPI.as_view()),
]
urlpatterns += router.urls
