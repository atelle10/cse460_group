from .views import LoginView, LogoutView, StudentPortalView, ClubApplicationView, AdminDashboardView
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('student/', StudentPortalView.as_view(), name='student_home'),
    path('student/apply/', ClubApplicationView.as_view(), name='club_application'),
    path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
]