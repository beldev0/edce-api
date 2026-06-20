from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Schedule, ScheduleRow, ScheduleAssignment
from .serializers import ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@extend_schema(
    methods=['GET'],
    summary="Consulter le planning d'un mois",
    description="Récupère le planning pour le mois spécifié au format YYYY-MM",
    responses={200: ScheduleSerializer}
)
@extend_schema(
    methods=['POST'],
    summary="Initialiser un planning pour un mois",
    description="Crée un nouveau planning avec un statut 'draft'",
    responses={201: serializers.Serializer()}
)
@extend_schema(
    methods=['PUT'],
    summary="Mettre à jour le planning et enregistrer les affectations",
    description="Modifie le statut et/ou les assignements du planning",
    responses={200: serializers.Serializer()}
)
@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def schedule_detail(request, monthKey):
    """
    Gère le planning (Schedule) pour un mois donné.
    - GET: Récupère le planning du mois
    - POST: Crée un nouveau planning pour le mois
    - PUT: Met à jour le planning et ses affectations
    """
    
    if request.method == 'GET':
        try:
            schedule = Schedule.objects.prefetch_related('rows__assignments').get(monthKey=monthKey)
        except Schedule.DoesNotExist:
            return Response({
                'statusCode': 404,
                'statusMessage': f'Schedule for {monthKey} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Format response with grouped assignments
        rows_data = []
        for row in schedule.rows.all():
            assignments_by_type = {
                'NORMAL': [],
                'SUNDAY_SCHOOL': [],
                'DLT': []
            }
            
            for assignment in row.assignments.all():
                assignments_by_type[assignment.seance_type].append(str(assignment.teacher.id))
            
            rows_data.append({
                'dateLabel': row.dateLabel,
                'assignments': assignments_by_type
            })
        
        return Response({
            'success': True,
            'monthKey': schedule.monthKey,
            'status': schedule.status,
            'rows': rows_data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        data['monthKey'] = monthKey
        
        serializer = ScheduleCreateSerializer(data=data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response({
                'success': True,
                'message': 'Planning initialisé avec succès.',
                'schedule': {
                    'id': str(schedule.id),
                    'monthKey': schedule.monthKey,
                    'status': schedule.status,
                    'created_at': schedule.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        try:
            schedule = Schedule.objects.get(monthKey=monthKey)
        except Schedule.DoesNotExist:
            return Response({
                'statusCode': 404,
                'statusMessage': f'Schedule for {monthKey} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ScheduleUpdateSerializer(schedule, data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response({
                'success': True,
                'message': 'Planning mis à jour et enregistré avec succès.',
                'updated_at': schedule.updated_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
