from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserSignupView, UserLoginView, UserUpdateView, UsersView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', UserSignupView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('user/<int:id>/', UserUpdateView.as_view(), name='user_detail'),
    # path('webhook/paystack/',paystack_webhook, name='paystack_webhook'),
]