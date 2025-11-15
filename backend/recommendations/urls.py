from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'careers', views.CareerViewSet, basename='career')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'recommendations', views.StudentRecommendationViewSet, basename='studentrecommendation')
router.register(r'learning-styles', views.LearningStyleViewSet, basename='learningstyle')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', views.RecommendationsView.as_view(), name='recommendations'),
    path('career/<int:pk>/', views.CareerDetailView.as_view(), name='career-detail'),
]