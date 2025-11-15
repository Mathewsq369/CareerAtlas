from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('start/', views.AssessmentStartView.as_view(), name='assessment-start'),
    path('question/', views.assessment_question, name='assessment-question'),
    path('results/', views.assessment_results, name='assessment-results'),
]