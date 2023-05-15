from rest_framework import routers

from .views import LocationViewSet

router = routers.SimpleRouter()
router.register(r"locations", LocationViewSet, basename='location')

urlpatterns = router.urls
