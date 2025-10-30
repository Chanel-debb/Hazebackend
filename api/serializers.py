from rest_framework import serializers
from .models import Vistor, AccessCode, Announcement



class VistorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vistor
        fields = ['id', 'fullname', 'phone_number', 'description', 'created_at', 'signed_in', 'signed_out']
        read_only_fields = ['id', 'created_at']


