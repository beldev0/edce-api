from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404

from seance.models import ParticipantSeance, Seance
from seance.serializers import ParticipantSeanceSerializer
from activities.models import ParticipantEventActivity, EventActivity
from activities.serializers import ParticipantEventActivitySerializer
from children.models import Child
from accounts.models import User


# ==========================================
# 🚀 VIEWS POUR PARTICIPANTS SEANCES
# ==========================================

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def participant_seances(request):
    """
    Endpoint pour gérer les participations aux séances.
    - GET: Hydratation complète (listSeances, listParticipantSeance, listChildren, listTeachers)
    - POST: Créer une participation
    - PUT: Mettre à jour une participation
    - DELETE: Supprimer une participation (via query param id)
    """
    
    if request.method == 'GET':
        # Hydratation: retourner toutes les entités nécessaires
        seances = Seance.objects.all().values('id', 'title', 'classe')
        participants = ParticipantSeance.objects.all().values('id', 'seance_id', 'child_id')
        children = Child.objects.all().values('id', 'name')
        teachers = User.objects.filter(status='teacher').values(
            'id', 'profil__first_name', 'profil__last_name'
        )
        
        return Response({
            "listSeances": list(seances),
            "listParticipantSeance": list(participants),
            "listChildren": list(children),
            "listTeachers": [
                {
                    'id': str(t['id']),
                    'first_name': t['profil__first_name'],
                    'last_name': t['profil__last_name']
                } for t in teachers
            ]
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ParticipantSeanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "statusCode": 400,
            "message": "Champs requis manquants (childId, seanceId)"
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        participant_id = request.data.get('id')
        child_id = request.data.get('childId')
        seance_id = request.data.get('seanceId')
        
        try:
            participant = ParticipantSeance.objects.get(id=participant_id)
        except ParticipantSeance.DoesNotExist:
            return Response({
                'statusCode': 404,
                'message': 'Participant de séance introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if child_id:
            participant.child_id = child_id
        if seance_id:
            participant.seance_id = seance_id
        
        participant.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        participant_id = request.query_params.get('id')
        if not participant_id:
            return Response({
                'statusCode': 400,
                'message': 'Query param id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            record = ParticipantSeance.objects.get(id=participant_id)
        except ParticipantSeance.DoesNotExist:
            return Response({
                'statusCode': 404,
                'message': 'Participant introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        record.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)


# ==========================================
# 🚀 VIEWS POUR PARTICIPANTS EVENTS
# ==========================================

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def participant_events(request):
    """
    Endpoint pour gérer les participations aux événements.
    - GET: Hydratation complète (listActivities, listEventActivity, listParticipantEventActivity, listChildren)
    - POST: Créer une participation
    - PUT: Mettre à jour une participation
    - DELETE: Supprimer une participation (via query param id)
    """
    
    if request.method == 'GET':
        # Hydratation: retourner toutes les entités nécessaires pour initialiser le module Événements
        from activities.models import Activity
        
        activities = Activity.objects.all().values('id', 'title')
        event_activities = EventActivity.objects.all().values('id', 'activity_id', 'eventType', 'year')
        participants = ParticipantEventActivity.objects.all().values('id', 'child_id', 'event_activity_id')
        children = Child.objects.all().values('id', 'name')
        
        return Response({
            "listActivities": list(activities),
            "listEventActivity": list(event_activities),
            "listParticipantEventActivity": list(participants),
            "listChildren": list(children)
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ParticipantEventActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "statusCode": 400,
            "message": "Champs requis manquants (childId, eventActivityId)"
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        participant_id = request.data.get('id')
        child_id = request.data.get('childId')
        event_activity_id = request.data.get('eventActivityId')
        
        try:
            participant = ParticipantEventActivity.objects.get(id=participant_id)
        except ParticipantEventActivity.DoesNotExist:
            return Response({
                'statusCode': 404,
                'message': 'Liaison événement-enfant introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if child_id:
            participant.child_id = child_id
        if event_activity_id:
            participant.event_activity_id = event_activity_id
        
        participant.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        participant_id = request.query_params.get('id')
        if not participant_id:
            return Response({
                'statusCode': 400,
                'message': 'Query param id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            record = ParticipantEventActivity.objects.get(id=participant_id)
        except ParticipantEventActivity.DoesNotExist:
            return Response({
                'statusCode': 404,
                'message': 'Liaison événement-enfant introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        record.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)
