from rest_framework import serializers
from .models import Seance, ParticipantSeance
from children.models import Child
from children.serializers import ChildSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class SeanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    
    # Automatically tracks the ID while mapping to the front-end format
    authorId = serializers.PrimaryKeyRelatedField(
        source='author', 
        read_only=True # Made read-only because we auto-assign it from the request user
    )
    supervisorId = serializers.PrimaryKeyRelatedField(
        source='supervisor',
        queryset=User.objects.all()
    )

    class Meta:
        model = Seance
        fields = ['id', 'title', 'type', 'classe', 'authorId', 'supervisorId', 'created_at']


class SeanceUpdateSerializer(serializers.ModelSerializer):
    """ Allows editing single fields dynamically via PATCH """
    title = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=Seance.SeanceType.choices, required=False)
    classe = serializers.ChoiceField(choices=Seance.ClasseType.choices, required=False)
    supervisorId = serializers.PrimaryKeyRelatedField(
        source='supervisor',
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Seance
        fields = ['title', 'type', 'classe', 'supervisorId']


class ParticipantSeanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    childId = serializers.PrimaryKeyRelatedField(
        source='child',
        queryset=Child.objects.all()
    )
    seanceId = serializers.PrimaryKeyRelatedField(
        source='seance',
        queryset=Seance.objects.all()
    )

    class Meta:
        model = ParticipantSeance
        fields = ['id', 'childId', 'seanceId']


class BulkParticipantSeanceSerializer(serializers.Serializer):
    seanceId = serializers.PrimaryKeyRelatedField(
        source='seance',
        queryset=Seance.objects.all(),
        required=True
    )
    # 🎯 Un tableau (List) d'identifiants de type UUID (les enfants)
    childIds = serializers.PrimaryKeyRelatedField(
        source='child',
        queryset=Child.objects.all(),
        many=True,
        required=True
    )