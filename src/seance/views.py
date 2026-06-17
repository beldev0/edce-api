from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Seance, ParticipantSeance
from .serializers import (
    BulkParticipantSeanceSerializer, SeanceSerializer, SeanceUpdateSerializer, 
    ParticipantSeanceSerializer)


@extend_schema(
    methods=['GET'],
    summary="Liste toutes les séances de cours",
    responses={200: SeanceSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Créer une nouvelle séance de cours",
    request=SeanceSerializer,
    responses={201: SeanceSerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def seance_list_create(request):
    if request.method == 'GET':
        seances = Seance.objects.all().order_by('-created_at')
        serializer = SeanceSerializer(seances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SeanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PATCH'],
    summary="Modifier partiellement une séance (PATCH)",
    request=SeanceUpdateSerializer,
    responses={200: SeanceSerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer une séance",
    responses={204: inline_serializer("SeanceDel", fields={"message": serializers.CharField()})}
)
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def seance_detail_update_delete(request, pk):
    seance_record = get_object_or_404(Seance, pk=pk)

    if request.method == 'PATCH':
        serializer = SeanceUpdateSerializer(seance_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_serializer = SeanceSerializer(seance_record)
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        seance_record.delete()
        return Response({"message": "Seance record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

@extend_schema(
    methods=['GET'],
    summary="Liste les présences aux séances (Format simple)",
    responses={200: ParticipantSeanceSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Marquer plusieurs enfants présents à une séance (Bulk)",
    description="Permet d'envoyer l'ID de la séance et la liste de tous les enfants présents d'un coup.",
    request=BulkParticipantSeanceSerializer,
    responses={
        201: ParticipantSeanceSerializer(many=True), 
        400: serializers.Serializer
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def participant_seance_list_create(request):
    if request.method == 'GET':
        participants = ParticipantSeance.objects.all()
        serializer = ParticipantSeanceSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # 1. On valide les données reçues via le sérialiseur de Bulk
        bulk_serializer = BulkParticipantSeanceSerializer(data=request.data)
        if bulk_serializer.is_valid():
            seance_instance = bulk_serializer.validated_data['seance']
            children_list = bulk_serializer.validated_data['child'] # Contient la liste des instances d'enfants
            
            created_instances = []
            
            # 2. On crée les participations en évitant les doublons
            for child_instance in children_list:
                # get_or_create évite de crash si un enfant était déjà marqué présent
                obj, created = ParticipantSeance.objects.get_or_create(
                    seance=seance_instance,
                    child=child_instance
                )
                created_instances.append(obj)
            
            # 3. On renvoie au front le tableau complet des lignes créées/existantes
            return_serializer = ParticipantSeanceSerializer(created_instances, many=True)
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(bulk_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="Annuler la présence d'un enfant à une séance",
    responses={204: inline_serializer("PartSeanceDel", fields={"message": serializers.CharField()})}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def participant_seance_delete(request, pk):
    record = get_object_or_404(ParticipantSeance, pk=pk)
    record.delete()
    return Response({"message": "Participant removed from seance successfully."}, status=status.HTTP_204_NO_CONTENT)