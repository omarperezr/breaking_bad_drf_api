from django.urls import path
from rest_framework import routers
from .views import CharacterViewSet

router = routers.SimpleRouter()
router.register(r"characters", CharacterViewSet, basename='character')

urlpatterns = router.urls
