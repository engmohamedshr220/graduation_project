# urls.py
from django.urls import path
from .views import AskGoogleAPIView

urlpatterns = [

    path('ask-google/', AskGoogleAPIView.as_view(), name='ask-google'),
]
