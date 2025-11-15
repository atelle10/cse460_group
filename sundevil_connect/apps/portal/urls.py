from .views import AuthView, StudentPortalView, ClubLeaderView, AdminDashboardView
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('', AuthView.as_view(), name='login'),
    path('login/', AuthView.as_view(), name='login'),
    path('logout/', AuthView.as_view(), {'action': 'logout'}, name='logout'),
    path('student/', StudentPortalView.as_view(), name='student_home'),
    path('student/apply/', StudentPortalView.as_view(), name='club_application'),
    path('student/club/<int:club_id>/', StudentPortalView.as_view(), name='club_detail'),
    path('student/event/<int:event_id>/', StudentPortalView.as_view(), name='event_detail'),
    path('club-leader/', ClubLeaderView.as_view(), name='club_leader_dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/flagged/', AdminDashboardView.as_view(), name='flagged_content'),
]