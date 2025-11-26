from rest_framework import serializers
from .models import User


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'other_names', 'reciept_id', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value


    def create(self, validated_data):
        password = validated_data.pop('password', None)
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
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'other_names', 'phone_number',  'reciept_id', 'is_verified', 'role', 'created_at', 'updated_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'other_names']


