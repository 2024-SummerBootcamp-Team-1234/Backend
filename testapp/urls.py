from django.urls import path
from .views import *

urlpatterns = [
    path('celery-test/', celery_test_view),
    path('celery-test2/', celery_test_view2),
]