from django.shortcuts import render
from .models import User
from .serializers import UserSerializer, UserSignupSerializer, UserLoginSerializer, UserUpdateSerializer
from rest_framework import generics, status, views, response
from rest_framework_simplejwt.tokens import RefreshToken 
from .permissions import IsAdminUser, IsModeratorUser, IsBaseUser, IsAdminOrModeratorUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .backend import CustomBackend
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from .models import Visitor
from .serializers import VistorSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

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


@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook for payment verification"""
    if request.method == "POST":
        data = json.loads(request.body)
        
        if data.get('event') == 'charge.success':
            reference = data['data']['reference']
            
            try:
                payment = Payment.objects.get(paystack_reference=reference)
                payment.status = 'success'
                payment.transaction_date = data['data']['paid_at']
                payment.channel = data['data']['channel']
                payment.paystack_response = data['data']
                payment.save()
                
                payment.order.status = 'paid'
                payment.order.save()
                
                return JsonResponse({'status': 'success'})
            except Payment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
    
    return JsonResponse({'status': 'error'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_vistors(request):
    objs = Vistor.objects.filter(user=request.user).order_by('-created_at')
    serializer = VistorSerializer(objs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    
    if 'profile_image' in request.FILES:
        user.profile_image = request.FILES['profile_image']
        user.save()
        
        return Response({
            'profile_image': request.build_absolute_uri(user.profile_image.url) if user.profile_image else None,
            'message': 'Profile picture updated successfully'
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)