from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Seance
from .serializers import SeanceSerializer, SeanceUpdateSerializer


@extend_schema(
    methods=['GET'],
    summary="Récupération et regroupement des séances",
    description="Retourne toutes les séances, optionnellement filtrées par authorId. Format avec regroupements par type, classe, année.",
    responses={200: serializers.Serializer()}
)
@extend_schema(
    methods=['POST'],
    summary="Créer une nouvelle séance",
    request=SeanceSerializer,
    responses={201: SeanceSerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def seance_list_create(request):
    if request.method == 'GET':
        # Check for optional authorId filter
        author_id = request.query_params.get('authorId')
        
        if author_id:
            # Filter by author - simple list format
            seances = Seance.objects.filter(author_id=author_id).order_by('-created_at')
            serializer = SeanceSerializer(seances, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Default: return grouped structure
        seances = Seance.objects.all().select_related('author', 'supervisor').order_by('-created_at')
        
        # Group by type
        group_by_type = {}
        group_by_classe = {}
        group_by_year = {}
        
        for seance in seances:
            serialized = SeanceSerializer(seance).data
            
            # Group by type
            seance_type = seance.type
            if seance_type not in group_by_type:
                group_by_type[seance_type] = []
            group_by_type[seance_type].append(serialized)
            
            # Group by classe
            classe = seance.classe
            if classe not in group_by_classe:
                group_by_classe[classe] = []
            group_by_classe[classe].append(serialized)
            
            # Group by year
            year = str(seance.created_at.year)
            if year not in group_by_year:
                group_by_year[year] = []
            group_by_year[year].append(serialized)
        
        return Response({
            "listSeances": [SeanceSerializer(s).data for s in seances],
            "groupSeanceperType": group_by_type,
            "groupSeanceperClasse": group_by_classe,
            "groupSeanceperYear": group_by_year
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SeanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        # Check for missing fields
        required_fields = ['title', 'type', 'classe', 'supervisorId']
        missing = [f for f in required_fields if f not in request.data or not request.data.get(f)]
        if missing:
            return Response({
                "statusCode": 400,
                "statusMessage": f"Missing required fields for creating a seance: {', '.join(missing)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PUT'],
    summary="Mise à jour d'une séance",
    request=SeanceUpdateSerializer,
    responses={200: SeanceSerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Suppression d'une séance",
    responses={200: inline_serializer("SeanceDel", fields={"success": serializers.BooleanField(), "message": serializers.CharField()})}
)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def seance_detail_update_delete(request, pk):
    seance_record = get_object_or_404(Seance, pk=pk)

    if request.method == 'PUT':
        serializer = SeanceUpdateSerializer(seance_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_serializer = SeanceSerializer(seance_record)
            return Response({
                "success": True,
                "data": full_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        seance_record.delete()
        return Response({
            "success": True,
            "message": "Seance deleted successfully"
        }, status=status.HTTP_200_OK)