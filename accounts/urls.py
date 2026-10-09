from django.urls import path
from .views import RegisterView, LoginView, DemoLoginView, UserProfileView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('demo-login/', DemoLoginView.as_view(), name='auth-demo-login'),
    path('user/', UserProfileView.as_view(), name='auth-user'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]

