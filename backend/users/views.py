from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, CreateView, View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
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

class HTMLRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/register.html')
    
    def post(self, request):
        from django.contrib.auth.models import User
        from .models import StudentProfile
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create student profile
            StudentProfile.objects.create(user=user)
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/register.html')

class HTMLLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'registration/login.html')

class HTMLLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    
    def post(self, request):
        return self.get(request)

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

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ensure user has a student profile
        self.ensure_student_profile(user)
        
        # Get assessment results if exists
        try:
            from assessments.models import AssessmentResult
            assessment_result = AssessmentResult.objects.get(student=user.studentprofile)
            context['assessment_result'] = assessment_result
        except AssessmentResult.DoesNotExist:
            context['assessment_result'] = None
        except Exception as e:
            # Handle any other exceptions gracefully
            context['assessment_result'] = None
            print(f"Error getting assessment result: {e}")
        
        # Get recent recommendations
        try:
            from recommendations.models import StudentRecommendation
            recommendations = StudentRecommendation.objects.filter(
                student=user.studentprofile
            ).select_related('career')[:5]
            context['recommendations'] = recommendations
        except Exception as e:
            context['recommendations'] = []
            print(f"Error getting recommendations: {e}")
        
        # Get learning style if available
        try:
            from ai_coach.services import AICoachService
            coach = AICoachService(user.studentprofile)
            learning_style = coach.get_learning_style_recommendation()
            context['learning_style'] = learning_style
        except Exception as e:
            context['learning_style'] = None
            print(f"Error getting learning style: {e}")
        
        return context
    
    def ensure_student_profile(self, user):
        """Ensure the user has a student profile, create if missing"""
        try:
            # Try to access the student profile
            _ = user.studentprofile
        except Exception:
            # Profile doesn't exist, create one
            from .models import StudentProfile
            StudentProfile.objects.create(user=user)
            print(f"Created student profile for user: {user.username}")

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