from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .serializers import VistorSerializer, AnnouncementSerializer, AccessCodeSerializer, EstatePaymentSerializer, PaymentTransactionSerializer
from .models import Vistor, Announcement, AccessCode, EstatePayment, PaymentTransaction
from rest_framework import status
from django.utils import timezone
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
def verify_access_code(request):
    code = request.data.get('code')
    access_code = AccessCode.objects.filter(code=code, status=True).first()
    if access_code:
        return Response({"message": "Access code is valid"}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid or expired access code"}, status=status.HTTP_400_BAD_REQUEST)