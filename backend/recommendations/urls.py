from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'careers', views.CareerViewSet, basename='career')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'recommendations', views.StudentRecommendationViewSet, basename='studentrecommendation')
router.register(r'learning-styles', views.LearningStyleViewSet, basename='learningstyle')

app_name = 'recommendations'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', views.CareerRecommendationsView.as_view(), name='my_recommendations'),
    path('careers/', views.CareerListView.as_view(), name='career_list'),
    path('careers/<int:pk>/', views.CareerDetailView.as_view(), name='career_detail'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
]