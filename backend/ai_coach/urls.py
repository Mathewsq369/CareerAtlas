from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'coaching-plans', views.CoachingPlanViewSet, basename='coachingplan')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', views.AICoachView.as_view(), name='ai-coach'),
    path('resources/', views.LearningResourcesView.as_view(), name='learning-resources'),
]