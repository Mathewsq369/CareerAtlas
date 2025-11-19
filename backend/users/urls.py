from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'student-profiles', views.StudentProfileViewSet, basename='studentprofile')
router.register(r'schools', views.SchoolViewSet, basename='school')

urlpatterns = [
    # API URLs (for programmatic access)
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
    
    # HTML Template URLs (for browser access)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('login/', views.HTMLLoginView.as_view(), name='login'),
    path('register/', views.HTMLRegisterView.as_view(), name='register'),
    path('logout/', views.HTMLLogoutView.as_view(), name='logout'),
]