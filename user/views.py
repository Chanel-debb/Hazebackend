from django.shortcuts import render
from .models import User, ReceiptID
from .serializers import UserSerializer, UserSignupSerializer, UserLoginSerializer, UserUpdateSerializer
from rest_framework import generics, status, views, response
from rest_framework_simplejwt.tokens import RefreshToken 
from .permissions import IsAdminUser, IsModeratorUser, IsBaseUser, IsAdminOrModeratorUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .backend import CustomBackend
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from .models import Visitor
from .serializers import VistorSerializer, ReceiptIDSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

auth = CustomBackend()

class UserSignupView(views.APIView):
    def post(self, request, format=None):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            # Get user role (default to resident)
            user_role = request.data.get('role', 'resident')
            
            # Only residents need receipt IDs
            if user_role == 'resident':
                receipt_id = request.data.get('receipt_id')
                
                if not receipt_id:
                    return response.Response(
                        {'error': 'Receipt ID is required for resident registration'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if receipt exists and is unused
                try:
                    receipt = ReceiptID.objects.get(receipt_code=receipt_id, is_used=False)
                except ReceiptID.DoesNotExist:
                    return response.Response(
                        {'error': 'Invalid or already used receipt ID'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create user
            user = serializer.save()
            
            # If resident, handle receipt and expiry
            if user.role == 'resident':
                # Mark receipt as used
                receipt.is_used = True
                receipt.used_by = user
                receipt.used_at = timezone.now()
                receipt.save()
                
                # Set account expiry based on receipt type
                if receipt.type == 'owner':
                    user.account_expiry_date = timezone.now() + timedelta(days=3650)  # 10 years
                else:  # tenant
                    user.account_expiry_date = timezone.now() + timedelta(days=365)  # 1 year
                
                user.account_status = 'active'
                user.save()

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
                    'receipt_id': user.receipt_id if hasattr(user, 'receipt_id') else None,
                    'role': user.role,
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
                    'receipt_id': user.receipt_id, 
                    'role': user.role,
                }
            }, status=status.HTTP_200_OK)

            print('===BACKEND LOGIN RESPONSE===')
            print(f"user role: {user.role}")
            print(f"response data: {response_data}")
            print('============================')
        
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_receipt_id(request):
    """Generate a new receipt ID (admin only)"""
    
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    receipt_type = request.data.get('type', 'tenant')
    
    if receipt_type not in ['owner', 'tenant']:
        return Response({'error': 'Invalid type. Must be "owner" or "tenant"'}, status=status.HTTP_400_BAD_REQUEST)
    
    receipt = ReceiptID.objects.create(
        type=receipt_type,
        created_by=request.user
    )
    
    serializer = ReceiptIDSerializer(receipt)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_receipt_ids(request):
    """Get all receipt IDs (admin only)"""
    
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Optional filter by status
    filter_status = request.GET.get('status')  # 'used' or 'unused'
    
    receipts = ReceiptID.objects.all()
    
    if filter_status == 'used':
        receipts = receipts.filter(is_used=True)
    elif filter_status == 'unused':
        receipts = receipts.filter(is_used=False)
    
    receipts = receipts.order_by('-created_at')
    serializer = ReceiptIDSerializer(receipts, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_receipt_stats(request):
    """Get receipt ID statistics (admin only)"""
    
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    total = ReceiptID.objects.count()
    unused = ReceiptID.objects.filter(is_used=False).count()
    used = ReceiptID.objects.filter(is_used=True).count()
    
    owner_receipts = ReceiptID.objects.filter(type='owner', is_used=False).count()
    tenant_receipts = ReceiptID.objects.filter(type='tenant', is_used=False).count()
    
    return Response({
        'total': total,
        'unused': unused,
        'used': used,
        'unused_owner': owner_receipts,
        'unused_tenant': tenant_receipts
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_receipt_id(request, receipt_id):
    """Delete an unused receipt ID (admin only)"""
    
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        receipt = ReceiptID.objects.get(id=receipt_id)
    except ReceiptID.DoesNotExist:
        return Response({'error': 'Receipt ID not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if receipt.is_used:
        return Response({'error': 'Cannot delete used receipt ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    receipt.delete()
    return Response({'message': 'Receipt ID deleted'}, status=status.HTTP_200_OK)