from rest_framework import serializers
from .models import Vistor, AccessCode, Announcement, PaymentTransaction, EstatePayment


class EstatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatePayment
        fields = ['id', 'title', 'amount', 'frequency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'payment', 'user', 'reference', 'amount', 'status']
        read_only_fields = ['id', 'status']





class VistorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vistor
        fields = ['id', 'fullname', 'phone_number', 'description', 'created_at', 'signed_in', 'signed_out']
        read_only_fields = ['id', 'created_at']

class AccessCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCode
        fields = ['id', 'created_at', 'code_type', 'start_time', 'end_time', 'code', 'status']
        read_only_fields = ['id', 'created_at', 'code', 'status']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'signed_by', 'created_at']
        read_only_fields = ['id', 'created_at']


