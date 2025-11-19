from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'student-profiles', views.StudentProfileViewSet, basename='studentprofile')
router.register(r'schools', views.SchoolViewSet, basename='school')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    
    # Template URLs
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Add these for traditional Django auth views
    path('login/', views.CustomLoginView.as_view(), name='login-page'),
    path('register/', views.RegisterView.as_view(), name='register-page'),
]