from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id',
            'user',
            'user_name',
            'category',
            'title',
            'description',
            'location',
            'image_description',
            'image',
            'priority',
            'status',
            'created_at',
            'updated_at',
            'resolved_at',
            'admin_notes',
            'assigned_to'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'user_name']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else "Unknown"
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReportCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating reports from mobile app"""
    
    class Meta:
        model = Report
        fields = [
            'category',
            'title',
            'description',
            'location',
            'image_description',
            'image',
            'priority'
        ]
    
    def create(self, validated_data):
        # Set user and default status
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class ReportListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing reports"""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id',
            'user_name',
            'category',
            'title',
            'location',
            'priority',
            'status',
            'created_at'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else "Unknown"


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update report status"""
    
    class Meta:
        model = Report
        fields = ['status', 'admin_notes', 'assigned_to', 'resolved_at']