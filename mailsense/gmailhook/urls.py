from django.urls import path
from .views import gmail_webhook

urlpatterns = [
    path('gmail/webhook/', gmail_webhook),
]
