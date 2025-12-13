from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserSignupView, UserLoginView, UserUpdateView, UsersView, update_profile,generate_receipt_id,get_all_receipt_ids,get_receipt_stats,delete_receipt_id, get_user_preferences, update_user_preferences


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', UserSignupView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('user/<int:id>/', UserUpdateView.as_view(), name='user_detail'),
    path('profile/update/',update_profile, name='update-profile'),
    # path('webhook/paystack/',paystack_webhook, name='paystack_webhook'),
    path('generate-receipt', generate_receipt_id, name='generate-receipt'),
    path('receipt-ids', get_all_receipt_ids, name='receipt-ids'),
    path('receipt-stats', get_receipt_stats, name='receipt-stats'),
    path('delete-receipt/<int:receipt_id>', delete_receipt_id, name='delete-receipt'),
    path('preferences', get_user_preferences, name='get-preferences'),
    path('preferences/update', update_user_preferences, name='update-preferences'),

]