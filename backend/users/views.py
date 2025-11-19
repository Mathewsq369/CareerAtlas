from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

from .models import CustomUser, StudentProfile, School
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    StudentProfileSerializer, SchoolSerializer
)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the user in
        login(request, user)
        
        return Response(
            {
                'user': UserSerializer(user, context=self.get_serializer_context()).data,
                'message': 'User created successfully'
            },
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user

class StudentProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileSerializer
    
    def get_queryset(self):
        return StudentProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.studentprofile

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SchoolSerializer
    queryset = School.objects.all()
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            schools = School.objects.filter(name__icontains=query)[:10]
        else:
            schools = School.objects.all()[:10]
        
        serializer = self.get_serializer(schools, many=True)
        return Response(serializer.data)

# Template Views
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get assessment results if exists
        try:
            assessment_result = user.studentprofile.assessmentresult
            context['assessment_result'] = assessment_result
        except AssessmentResult.DoesNotExist:
            context['assessment_result'] = None
        
        # Get recent recommendations
        from recommendations.models import StudentRecommendation
        recommendations = StudentRecommendation.objects.filter(
            student=user.studentprofile
        ).select_related('career')[:5]
        context['recommendations'] = recommendations
        
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile.html'

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after registration
        from django.contrib.auth import login
        login(self.request, self.user)
        return response