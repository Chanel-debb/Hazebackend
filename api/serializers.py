from rest_framework import serializers
from .models import Vistor, AccessCode, Announcement



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


