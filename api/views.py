from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .serializers import VistorSerializer
from .models import Vistor
from rest_framework import status
from django.utils import timezone
from rest_framework.response import Response



@api_view() # GET all
def get_all_vistors(request):
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
    obj = get_object_or_404(Vistor, id=id)
    serializer = VistorSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)  


@api_view(['DELETE']) # DELETE 
def delete_visitor(request, id):
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