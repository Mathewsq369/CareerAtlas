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

# users/views.py - Update the HTMLRegisterView post method

class HTMLRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/register.html')
    
    def post(self, request):
        print("=== REGISTRATION DEBUG ===")
        print(f"POST data: {dict(request.POST)}")
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')  # CHANGED: password1 instead of password
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"First Name: {first_name}")
        print(f"Last Name: {last_name}")
        print(f"Password1: {password1}")  # DEBUG
        print(f"Password2: {password2}")  # DEBUG
        
        # Basic validation - UPDATED FIELD NAMES
        if not all([username, email, password1, password2, first_name, last_name]):
            messages.error(request, 'All fields are required.')
            print("Missing required fields")
            print(f"Missing fields check: username={username}, email={email}, password1={password1}, password2={password2}, first_name={first_name}, last_name={last_name}")
            return render(request, 'registration/register.html')
        
        if password1 != password2:  # CHANGED: password1 instead of password
            messages.error(request, 'Passwords do not match.')
            print("Passwords don't match")
            return render(request, 'registration/register.html')
        
        if len(password1) < 8:  # CHANGED: password1 instead of password
            messages.error(request, 'Password must be at least 8 characters long.')
            print("Password too short")
            return render(request, 'registration/register.html')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                print("Username already exists")
                return render(request, 'registration/register.html')
            
            # Check if email exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                print("Email already exists")
                return render(request, 'registration/register.html')
            
            print("Creating user...")
            # Create user - CHANGED: use password1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,  # CHANGED: password1 instead of password
                first_name=first_name,
                last_name=last_name,
                user_type='student'
            )
            print(f"User created: {user.username}")
            
            # Create student profile
            from .models import StudentProfile
            profile, created = StudentProfile.objects.get_or_create(user=user)
            print(f"Student profile created: {created}")
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to CareerAtlas.')
            print("User logged in successfully")
            return redirect('dashboard')
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")  # Added full traceback
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