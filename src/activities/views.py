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
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PATCH'],
    summary="Modifier partiellement une activité via son ID",
    request=ActivityUpdateSerializer,
    responses={200: ActivitySerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer une activité",
    responses={204: inline_serializer("ActDel", fields={"message": serializers.CharField()})}
)
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def activity_detail_update_delete(request, pk):
    activity_record = get_object_or_404(Activity, pk=pk)

    if request.method == 'PATCH':
        serializer = ActivityUpdateSerializer(activity_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_data = ActivitySerializer(activity_record)
            return Response(full_data.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        activity_record.delete()
        return Response({"message": "Activity deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 🚀 VIEWS POUR EVENT ACTIVITY (La table pivot)
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste toutes les liaisons Activités-Événements",
    responses={200: EventActivitySerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Lier une activité à un événement (Arbre de Noël, etc.)",
    request=EventActivitySerializer,
    responses={201: EventActivitySerializer, 400: serializers.Serializer}
)
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


@extend_schema(
    methods=['PATCH'],
    summary="Modifier partiellement une liaison Événement-Activité",
    request=EventActivityUpdateSerializer,
    responses={200: EventActivitySerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer une liaison Événement-Activité",
    responses={204: inline_serializer("EvDel", fields={"message": serializers.CharField()})}
)
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def event_activity_detail_update_delete(request, pk):
    event_activity_record = get_object_or_404(EventActivity, pk=pk)

    if request.method == 'PATCH':
        serializer = EventActivityUpdateSerializer(event_activity_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_data = EventActivitySerializer(event_activity_record)
            return Response(full_data.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event_activity_record.delete()
        return Response({"message": "Event-Activity link deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

# ==========================================
# 🚀 VIEWS POUR PARTICIPANTS (Inscriptions)
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste toutes les participations des enfants aux événements",
    responses={200: ParticipantEventActivitySerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Inscrire un enfant à un événement",
    request=ParticipantEventActivitySerializer,
    responses={201: ParticipantEventActivitySerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def participant_event_list_create(request):
    if request.method == 'GET':
        participants = ParticipantEventActivity.objects.all()
        serializer = ParticipantEventActivitySerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ParticipantEventActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Désinscrire un enfant d'un événement via l'ID de participation",
    responses={204: inline_serializer("PartDel", fields={"message": serializers.CharField()})}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def participant_event_delete(request, pk):
    record = get_object_or_404(ParticipantEventActivity, pk=pk)
    record.delete()
    return Response({"message": "Participant removed from event activity successfully."}, status=status.HTTP_204_NO_CONTENT)