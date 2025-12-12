from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .serializers import VistorSerializer, AnnouncementSerializer, AccessCodeSerializer, EstatePaymentSerializer, PaymentTransactionSerializer
from .models import Vistor, Announcement, AccessCode, EstatePayment, PaymentTransaction
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import views, generics
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsAdminUser, IsModeratorUser, IsBaseUser, IsAdminOrModeratorUser
from libs.paystack import initialize_payment
from user.models import User


@api_view(['POST'])
def make_payment(request):
    user_id = request.data.get('user_id')
    estpay_id = request.data.get('estate_payment_id')
    to_pay = EstatePayment.objects.filter(id=estpay_id).first()
    if not to_pay:
        return Response({"error": "Estate Payment not found"}, status=status.HTTP_404_NOT_FOUND)
    user = User.objects.filter(id=user_id).first()
    print("User", user)
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    email = user.email
    amount = int(to_pay.amount)
    payment_data = initialize_payment(email=email, amount=amount)
    payment_transaction = PaymentTransaction.objects.create(
        user=user,
        payment=to_pay,
        reference=payment_data['reference'],
        amount=amount
    )
    if payment_data:
        return Response({"url": payment_data['url']}, status=status.HTTP_200_OK)
    return Response({"error": "Payment initialization failed"}, status=status.HTTP_400_BAD_REQUEST)

@api_view()
def transaction(request):
    payments = PaymentTransaction.objects.all()
    serializer = PaymentTransactionSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view()
def payment(request):
    obj = EstatePayment.objects.all().order_by('-created_at')
    serializer = EstatePaymentSerializer(obj, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_payment(request):
    serializer = EstatePaymentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    

"""Function Based View (FBV)"""
@api_view() # GET all
def get_all_vistors(request):
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    objs = Vistor.objects.all()
    serializer = VistorSerializer(objs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST']) # CREATE
def add_visitor(request):
    serializer = VistorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"error": "wrong data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view() # GET get by ID
def get_visitor(request, id):
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    obj = get_object_or_404(Vistor, id=id)
    serializer = VistorSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)  


@api_view(['DELETE']) # DELETE 
def delete_visitor(request, id):
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    obj = Vistor.objects.get(id=id)
    if obj:
        obj.delete()
        return Response({'message': 'visitor deleted'}, status=status.HTTP_204_NO_CONTENT)
    return Response({"error": "Visitor not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH']) # UPDATE or SignOut
def update_visitor_signout(request, id):
    obj = Vistor.objects.get(id=id)
    serializer = VistorSerializer(data=request.data)
    if serializer.is_valid():
        obj.signed_out = timezone.now() 
        obj.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "wrong data"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET']) # security stats
@permission_classes([IsAuthenticated])
def get_security_stats(request):
    """Get statistics for security dashboard"""
    
    # Check if user is admin or security
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_start = timezone.make_aware(today_start)
    
    # Active passes (access codes that are currently valid)
    active_passes = AccessCode.objects.filter(
        status=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).count()
    
    # Pending visitors (visitors who are approved but haven't signed in yet)
    pending_visitors = Vistor.objects.filter(
        signed_in__isnull=True,
        signed_out__isnull=True
    ).count()
    
    # Today's entries (visitors who signed in today)
    todays_entries = Vistor.objects.filter(
        signed_in__gte=today_start
    ).count()
    
    # Denied - for now we'll use 0, you can add a "denied" field later
    denied = 0
    
    return Response({
        'active_passes': active_passes,
        'pending_visitors': pending_visitors,
        'todays_entries': todays_entries,
        'denied': denied
    }, status=status.HTTP_200_OK)

@api_view(['GET']) # Check active access codes
@permission_classes([IsAuthenticated])
def get_active_access_codes(request):
    """Get only currently active/valid access codes for admin/security"""
    
    # Check if user is admin or security
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    now = timezone.now()
    
    # Get only active access codes (valid right now)
    active_codes = AccessCode.objects.filter(
        status=True,
        start_time__lte=now,
        end_time__gte=now
    ).select_related('user').order_by('-created_at')
    
    # Serialize with user info
    codes_data = []
    for code in active_codes:
        codes_data.append({
            'id': code.id,
            'code': code.code,
            'code_type': code.code_type,
            'start_time': code.start_time,
            'end_time': code.end_time,
            'status': code.status,
            'created_at': code.created_at,
            'user': {
                'id': code.user.id,
                'email': code.user.email,
                'first_name': code.user.first_name,
                'last_name': code.user.last_name,
                'phone_number': code.user.phone_number,
            }
        })
    
    return Response(codes_data, status=status.HTTP_200_OK)



"""Class Based View (CBV)"""

class AnnouncementView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    def post(self, request, format=None): # POST METHOD
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message": "bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None): # GET METHOD
        obj = Announcement.objects.all().order_by('-created_at')
        serializer = AnnouncementSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AnnouncementRetrieveUpdateDeletView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    def get_object(self, id):
        try:
            return Announcement.objects.get(id=id)
        except Announcement.DoesNotExist:
            raise Http404
        

    def get(self, request, id, format=None):
        obj = self.get_object(id)
        serializer = AnnouncementSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id, format=None):
        obj = self.get_object(id)
        obj.delete()
        return Response({"message": "deleted"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = AnnouncementSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""Generic Views"""


class AccessCodeListcreate(generics.ListCreateAPIView):
    serializer_class = AccessCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return access codes created by the logged-in user
        return AccessCode.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the user when creating an access code
        serializer.save(user=self.request.user)

class AccessCodeRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessCode.objects.all()
    serializer_class = AccessCodeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrModeratorUser]
    lookup_field = 'id'



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_access_code(request):
    """Verify an access code and return details"""
    
    # Check if user is admin or security
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    code = request.data.get('code')
    
    if not code:
        return Response({'error': 'Access code is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    now = timezone.now()
    
    # Find the access code
    access_code = AccessCode.objects.filter(code=code).select_related('user').first()
    
    if not access_code:
        return Response({
            'valid': False,
            'message': 'Access code not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if it's currently valid
    is_valid = (
        access_code.status and
        access_code.start_time <= now <= access_code.end_time
    )
    
    if is_valid:
        return Response({
            'valid': True,
            'message': 'Access code is valid',
            'code_details': {
                'id': access_code.id,
                'code': access_code.code,
                'code_type': access_code.code_type,
                'start_time': access_code.start_time,
                'end_time': access_code.end_time,
                'user': {
                    'id': access_code.user.id,
                    'email': access_code.user.email,
                    'first_name': access_code.user.first_name,
                    'last_name': access_code.user.last_name,
                    'phone_number': access_code.user.phone_number,
                }
            }
        }, status=status.HTTP_200_OK)
    else:
        # Determine why it's invalid
        if not access_code.status:
            reason = 'Code has been deactivated'
        elif now < access_code.start_time:
            reason = 'Code is not yet active'
        elif now > access_code.end_time:
            reason = 'Code has expired'
        else:
            reason = 'Code is invalid'
        
        return Response({
            'valid': False,
            'message': reason,
            'code_details': {
                'code_type': access_code.code_type,
                'start_time': access_code.start_time,
                'end_time': access_code.end_time,
            }
        }, status=status.HTTP_400_BAD_REQUEST)