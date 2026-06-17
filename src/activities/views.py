from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Activity, EventActivity
from .serializers import (
    ActivitySerializer, ActivityUpdateSerializer,
    EventActivitySerializer, EventActivityUpdateSerializer
)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def activity_list_create(request):
    if request.method == 'GET':
        activities = Activity.objects.all().order_by('title')
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def activity_detail_update_delete(request, pk):
    activity_record = get_object_or_404(Activity, pk=pk)

    if request.method == 'PATCH':
        # partial=True permet de ne passer que le 'title' si on veut
        serializer = ActivityUpdateSerializer(activity_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # On renvoie l'objet complet sérialisé au front
            full_data = ActivitySerializer(activity_record)
            return Response(full_data.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        activity_record.delete()
        return Response({"message": "Activity deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 🚀 VIEWS POUR EVENT ACTIVITY (La table pivot)
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_activity_list_create(request):
    if request.method == 'GET':
        events = EventActivity.objects.all().order_by('-year')
        serializer = EventActivitySerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EventActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def event_activity_detail_update_delete(request, pk):
    event_activity_record = get_object_or_404(EventActivity, pk=pk)

    if request.method == 'PATCH':
        # Permet de modifier juste le 'year', juste l' 'activityId' ou juste l' 'eventType'
        serializer = EventActivityUpdateSerializer(event_activity_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Retourne le format complet 'EventActivity' attendu par l'interface TypeScript
            full_data = EventActivitySerializer(event_activity_record)
            return Response(full_data.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event_activity_record.delete()
        return Response({"message": "Event-Activity link deleted successfully."}, status=status.HTTP_204_NO_CONTENT)