from django.urls import path, include
from .views import PasswordResetWithTokenView, PasswordResetView,PasswordResetConfirmView
from djoser import views as dj_views

urlpatterns =[

    path('auth/users/', dj_views.UserViewSet.as_view({'get': 'retrieve','get':'list','post':'create'}), name='user'),
    path('auth/users/<int:pk>/', dj_views.UserViewSet.as_view({'get': 'retrieve','put':'update','patch':'update','delete':'destroy'}), name='user-detail'),
    path('auth/users/me/', dj_views.UserViewSet.as_view({'get': 'retrieve','put':'me','patch':'me','delete':'me'}), name='user-me'),

    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/forget_password/', PasswordResetView.as_view()),
    path('auth/confirm_code/',PasswordResetConfirmView.as_view()),
    path('auth/set_new_password/',PasswordResetWithTokenView.as_view())
]