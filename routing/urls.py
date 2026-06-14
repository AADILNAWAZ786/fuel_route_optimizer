from django.urls import path
from .views import route_optimizer

urlpatterns = [
    path("optimize-route/", route_optimizer, name="optimize-route"),
]