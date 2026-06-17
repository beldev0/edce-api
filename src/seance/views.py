from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Seance, ParticipantSeance
from .serializers import SeanceSerializer, SeanceUpdateSerializer, ParticipantSeanceSerializer,ParticipantSeanceReadSerializer


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
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def participant_seance_list_create(request):
    if request.method == 'GET':
        participants = ParticipantSeance.objects.all()
        serializer = ParticipantSeanceSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ParticipantSeanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def participant_seance_delete(request, pk):
    record = get_object_or_404(ParticipantSeance, pk=pk)
    record.delete()
    return Response({"message": "Participant removed from seance successfully."}, status=status.HTTP_204_NO_CONTENT)