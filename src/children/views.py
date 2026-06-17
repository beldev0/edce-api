from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Child
from .serializers import ChildSerializer, ChildUpdateSerializer

@extend_schema(
    methods=['GET'],
    summary="Liste tous les enfants enregistrés",
    description="Retourne une liste de tous les enfants triés du plus récent au plus ancien.",
    responses={200: ChildSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Enregistrer un nouvel enfant",
    description="Crée une fiche enfant complète avec ses informations personnelles et ses contacts parents.",
    request=ChildSerializer,
    responses={201: ChildSerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny]) # Tu pourras restreindre à IsAuthenticated si nécessaire plus tard
def child_list_create(request):
    if request.method == 'GET':
        children = Child.objects.all().order_by('-created_at')
        serializer = ChildSerializer(children, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ChildSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PATCH'],
    summary="Modifier partiellement la fiche d'un enfant (PATCH)",
    description="Permet de mettre à jour uniquement le niveau scolaire ou la classe de l'enfant sans renvoyer tout le reste.",
    request=ChildUpdateSerializer,
    responses={200: ChildSerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer définitivement la fiche d'un enfant",
    responses={204: inline_serializer("ChildDelSuccess", fields={"message": serializers.CharField()})}
)
@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def child_detail_update_delete(request, pk):
    child_record = get_object_or_404(Child, pk=pk)

    if request.method == 'PATCH':
        serializer = ChildUpdateSerializer(child_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # On réutilise le sérialiseur complet pour renvoyer l'objet mis à jour proprement au front
            full_data_serializer = ChildSerializer(child_record)
            return Response(full_data_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        child_record.delete()
        return Response({"message": "Child record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)