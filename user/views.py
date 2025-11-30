from django.shortcuts import render
from .models import User
from .serializers import UserSerializer, UserSignupSerializer, UserLoginSerializer, UserUpdateSerializer
from rest_framework import generics, status, views, response
from rest_framework_simplejwt.tokens import RefreshToken 
from .permissions import IsAdminUser, IsModeratorUser, IsBaseUser, IsAdminOrModeratorUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .backend import CustomBackend
from django.contrib.auth import login, logout

auth = CustomBackend()

class UserSignupView(views.APIView):
    def post(self, request, format=None):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            
            return response.Response({
                'token': access_token,
                'refresh_token': str(refresh_token),
                'role': user.role,
                'user': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                    'othernames': user.other_names,
                    'phone_number': user.phone_number,
                    'receipt_id': user.receipt_id,  # Fixed typo
                }
            }, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(views.APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = auth.authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            
            return response.Response({
                'token': access_token,
                'refresh_token': str(refresh_token),
                'role': user.role,
                'user': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                    'othernames': user.other_names,
                    'phone_number': user.phone_number,
                    'receipt_id': user.receipt_id,  # Fixed typo
                }
            }, status=status.HTTP_200_OK)
        
        return response.Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class UsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]


class UserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    lookup_field = 'id'