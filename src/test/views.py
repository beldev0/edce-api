from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Test, Note
from .serializers import TestSerializer, TestUpdateSerializer, NoteSerializer

# ==========================================
# 🚀 VIEWS POUR TEST
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste tous les tests et évaluations",
    responses={200: TestSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Créer un nouveau test",
    description="L'auteur (`authorId`) est automatiquement défini à l'utilisateur connecté.",
    request=TestSerializer,
    responses={
        201: TestSerializer, 
        400: serializers.Serializer, 
        401: inline_serializer("AuthErr", fields={"message": serializers.CharField()})
    }
)
@api_view(['GET', 'POST'])
def test_list_create(request):
    if request.method == 'GET':
        tests = Test.objects.all().select_related('author').order_by('-created_at')
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({"message": "Authentication required to create a test."}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            # Hooks up the logged-in request user as the model author
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    summary="Récupérer les détails d'un test spécifique",
    responses={200: TestSerializer}
)
@extend_schema(
    methods=['PATCH'],
    summary="Modifier partiellement un test via son ID (PATCH)",
    request=TestUpdateSerializer,
    responses={200: TestSerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer définitivement un test",
    responses={204: inline_serializer("TestDel", fields={"message": serializers.CharField()})}
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def test_detail_update_delete(request, pk):
    test_record = get_object_or_404(Test, pk=pk)

    if request.method == 'GET':
        # Returns the complete data mapping directly to the TestDetail interface specs
        serializer = TestSerializer(test_record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        serializer = TestUpdateSerializer(test_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(TestSerializer(test_record).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        test_record.delete()
        return Response({"message": "Test record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

# ==========================================
# 🚀 VIEWS POUR NOTES (Traitement unitaire)
# ==========================================

@extend_schema(
    methods=['GET'],
    summary="Liste toutes les notes de manière brute",
    responses={200: NoteSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Attribuer une note à un enfant pour un test spécifique (Unitaire)",
    description="Format d'envoi individuel respectant la maquette frontend.",
    request=NoteSerializer,
    responses={201: NoteSerializer, 400: serializers.Serializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def note_list_create(request):
    if request.method == 'GET':
        notes = Note.objects.all().order_by('-created_at')
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['PATCH'],
    summary="Modifier la note d'un enfant (PATCH)",
    request=NoteSerializer,
    responses={200: NoteSerializer, 400: serializers.Serializer}
)
@extend_schema(
    methods=['DELETE'],
    summary="Supprimer la note d'un enfant",
    responses={204: inline_serializer("NoteDel", fields={"message": serializers.CharField()})}
)
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def note_detail_update_delete(request, pk):
    note_record = get_object_or_404(Note, pk=pk)

    if request.method == 'PATCH':
        # Allows updating just the score value seamlessly
        serializer = NoteSerializer(note_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        note_record.delete()
        return Response({"message": "Grade record removed successfully."}, status=status.HTTP_204_NO_CONTENT)
    

@extend_schema(
    summary="Récupérer l'index complet de toutes les fiches de notes",
    description="Retourne la liste plate globale de toutes les notes enregistrées dans le système.",
    responses={200: NoteSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_notes_index(request):
    """
    Retourne la liste globale de toutes les notes au format plat attendu par l'interface.
    """
    notes = Note.objects.all().order_by('-created_at')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)