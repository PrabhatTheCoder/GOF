
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import StudentLoginView, StaffLoginView, LogoutView, StudentSignupView, StaffSignupView
app_name = "accounts"

urlpatterns = [

    path("student/signup/", StudentSignupView.as_view(), name="signup"),
    path("staff/signup/", StaffSignupView.as_view(), name="staff_signup"),

    path("student/login/", StudentLoginView.as_view(), name="student_login"),
    path("staff/login/", StaffLoginView.as_view(), name="staff_login"),

    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    

    
]

