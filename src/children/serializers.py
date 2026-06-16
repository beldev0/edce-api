from rest_framework import serializers
from .models import Child

class ChildSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)  # Returns UUID as a clean string format
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)

    class Meta:
        model = Child
        fields = '__all__'


class ChildUpdateSerializer(serializers.ModelSerializer):
    """
    🎯 Flexible Update Contract. 
    By setting required=False, the frontend can submit just one field 
    (e.g., only 'classe' or only 'nivScolaire') safely.
    """
    nivScolaire = serializers.CharField(required=False, allow_blank=True)
    classe = serializers.ChoiceField(choices=Child.ClasseType.choices, required=False)

    class Meta:
        model = Child
        fields = ['nivScolaire', 'classe']