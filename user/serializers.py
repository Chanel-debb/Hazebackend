from rest_framework import serializers
from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    othernames = serializers.CharField(source='other_names', required=False, allow_blank=True)
    receipt_id = serializers.CharField(source='receipt_id')  # Fixed typo

    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'phone_number', 'othernames', 'receipt_id', 'password', 'role']
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