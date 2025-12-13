from rest_framework import serializers
from .models import User, Visitor, ReceiptID, UserPreferences



class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'other_names', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Set default role if not provided
        if 'role' not in validated_data:
            validated_data['role'] = User.Role.RESIDENT
        
        user = User(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='first_name', read_only=True)
    lastname = serializers.CharField(source='last_name', read_only=True)
    othernames = serializers.CharField(source='other_names', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname', 'othernames', 'phone_number', 'receipt_id', 'is_verified', 'role', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    othernames = serializers.CharField(source='other_names', required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'phone_number', 'othernames']

class VistorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'fullname', 'created_at', 'signed_in']
        read_only_fields = ['id', 'created_at']

class ReceiptIDSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    used_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ReceiptID
        fields = [
            'id',
            'receipt_code',
            'type',
            'is_used',
            'used_by',
            'used_by_name',
            'created_at',
            'used_at',
            'created_by',
            'created_by_name'
        ]
        read_only_fields = ['id', 'receipt_code', 'created_at', 'used_at', 'is_used', 'used_by']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name or ''} {obj.created_by.last_name or ''}".strip() or obj.created_by.email
        return "System"
    
    def get_used_by_name(self, obj):
        if obj.used_by:
            return f"{obj.used_by.first_name or ''} {obj.used_by.last_name or ''}".strip() or obj.used_by.email
        return None

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['email_updates', 'sms_alerts', 'system_alerts', 'updated_at']
        read_only_fields = ['updated_at']