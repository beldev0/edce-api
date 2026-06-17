from rest_framework import serializers
from .models import Activity, EventActivity

# Sérialiseurs pour Activity
class ActivitySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'title']

class ActivityUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)  # Optionnel pour le PATCH

    class Meta:
        model = Activity
        fields = ['title']


# Sérialiseurs pour EventActivity
class EventActivitySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    activityId = serializers.PrimaryKeyRelatedField(
        source='activity',
        queryset=Activity.objects.all()
    )

    class Meta:
        model = EventActivity
        fields = ['id', 'activityId', 'eventType', 'year']

class EventActivityUpdateSerializer(serializers.ModelSerializer):
    # Tous les champs deviennent optionnels pour permettre la modification partielle
    activityId = serializers.PrimaryKeyRelatedField(
        source='activity',
        queryset=Activity.objects.all(),
        required=False
    )
    eventType = serializers.ChoiceField(choices=EventActivity.EventType.choices, required=False)
    year = serializers.CharField(max_length=4, required=False)

    class Meta:
        model = EventActivity
        fields = ['activityId', 'eventType', 'year']