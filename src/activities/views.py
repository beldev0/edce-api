from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Activity, EventActivity, ParticipantEventActivity
from .serializers import (
    ActivitySerializer, ActivityUpdateSerializer,
    EventActivitySerializer, EventActivityUpdateSerializer, 
    ParticipantEventActivitySerializer
)
from children.models import Child

# ==========================================
# 🚀 VIEWS POUR ACTIVITY
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste toutes les activités",
    responses={200: ActivitySerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Créer une nouvelle activité",
    request=ActivitySerializer,
    responses={201: ActivitySerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def activity_list_create(request):
    if request.method == 'GET':
        activities = Activity.objects.all().order_by('title')
        serializer = ActivitySerializer(activities, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True, 
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PUT'],
    summary="Modifier une activité via son ID",
    request=ActivityUpdateSerializer,
    responses={200: ActivitySerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer une activité",
    responses={204: inline_serializer("ActDel", fields={"message": serializers.CharField()})}
)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def activity_detail_update_delete(request, pk):
    activity_record = get_object_or_404(Activity, pk=pk)

    if request.method == 'PUT':
        serializer = ActivityUpdateSerializer(activity_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            full_data = ActivitySerializer(activity_record)
            return Response({
                "success": True, 
                "data": full_data.data
            }, status=status.HTTP_200_OK)
            
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        activity_record.delete()
        return Response({
            "success": True,
            "message": "Activity and its event relations deleted successfully"
        }, status=status.HTTP_200_OK)


# ==========================================
# 🚀 VIEWS POUR EVENT ACTIVITY (La table pivot)
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste complète des événements avec regroupements",
    description="Retourne les événements bruts et les données traitées (regroupées par année et par type)",
    responses={200: serializers.Serializer()}
)
@extend_schema(
    methods=['POST'],
    summary="Créer une relation Activité-Événement",
    description="Lier une activité à un type d'événement (ex: Arbre de Noël, Soirée récréative)",
    request=EventActivitySerializer,
    responses={201: serializers.Serializer(), 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_activity_list_create(request):
    if request.method == 'GET':
        from django.db.models import Q
        from itertools import groupby
        
        event_activities = EventActivity.objects.all().select_related('activity').order_by('year', 'eventType')
        
        # Position fixed to keep positional args before keyword args
        list_activity_at_event = list(
            event_activities.values('id', 'year', 'eventType', activity_id='activity_id')
        )
        
        list_events = list(
            set(event_activities.values_list('eventType', flat=True).distinct())
        )
        
        group_activity_per_year = {}
        for event in event_activities:
            year = event.year
            if year not in group_activity_per_year:
                group_activity_per_year[year] = []
            group_activity_per_year[year].append({
                'id': str(event.activity_id),
                'title': event.activity.title
            })
        
        group_activity_per_event = {}
        for event in event_activities:
            event_type = event.eventType
            if event_type not in group_activity_per_event:
                group_activity_per_event[event_type] = []
            group_activity_per_event[event_type].append({
                'id': str(event.activity_id),
                'title': event.activity.title
            })
        
        return Response({
            "success": True,
            "data": {
                "listActivityAtEvent": list_activity_at_event,
                "listEvent": list_events,
                "groupActivityperYear": group_activity_per_year,
                "groupActivityperEvent": group_activity_per_event
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = EventActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        # Consistent custom error checking for missing fields
        missing_fields = []
        if 'activityId' not in request.data or not request.data.get('activityId'):
            missing_fields.append('activityId')
        if 'eventType' not in request.data or not request.data.get('eventType'):
            missing_fields.append('eventType')
        if 'year' not in request.data or not request.data.get('year'):
            missing_fields.append('year')
        
        if missing_fields:
            return Response({
                "success": False,
                "errors": f"Missing fields: {', '.join(missing_fields)} are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PUT'],
    summary="Mettre à jour une relation Activité-Événement",
    description="Modifier le type d'événement ou l'année d'une liaison",
    request=EventActivityUpdateSerializer,
    responses={
        200: serializers.Serializer(),
        404: serializers.Serializer()
    }
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer une relation Activité-Événement",
    responses={
        200: serializers.Serializer(),
        404: serializers.Serializer()
    }
)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def event_activity_detail_update_delete(request, pk):
    event_activity_record = get_object_or_404(EventActivity, pk=pk)

    if request.method == 'PUT':
        serializer = EventActivityUpdateSerializer(event_activity_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_data = EventActivitySerializer(event_activity_record)
            return Response({
                "success": True,
                "data": full_data.data
            }, status=status.HTTP_200_OK)
            
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event_activity_record.delete()
        return Response({
            "success": True,
            "message": "Activity and its event relations deleted successfully"
        }, status=status.HTTP_200_OK)