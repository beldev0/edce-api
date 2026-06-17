from rest_framework import serializers
from .models import Test, Note
from children.models import Child


class TestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    
    # Maps to the 'authorId' required by interface Test and TestSubmit
    authorId = serializers.PrimaryKeyRelatedField(
        source='author',
        read_only=True
    )
    
    # Maps to the 'created_by' string format required by interface TestDetail
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = [
            'id', 'titleTest', 'classe', 'typeTest', 
            'sujetTest', 'correctionTest', 'authorId', 'created_by', 'created_at'
        ]

    def get_created_by(self, obj):
        # Returns the author's full name or email depending on your User model setup
        return obj.author.get_full_name() or obj.author.email


class TestUpdateSerializer(serializers.ModelSerializer):
    """ Allows modifying single test properties flexibly via PATCH payloads """
    titleTest = serializers.CharField(required=False)
    classe = serializers.ChoiceField(choices=Test.ClasseType.choices, required=False)
    typeTest = serializers.ChoiceField(choices=Test.TypeTest.choices, required=False)
    sujetTest = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    correctionTest = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Test
        fields = ['titleTest', 'classe', 'typeTest', 'sujetTest', 'correctionTest']

class NoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    
    # 🎯 Maps 'childId' input string directly to the Child database model instance
    childId = serializers.PrimaryKeyRelatedField(
        source='child',
        queryset=Child.objects.all()
    )
    
    # 🎯 Maps 'testId' input string directly to the Test database model instance
    testId = serializers.PrimaryKeyRelatedField(
        source='test',
        queryset=Test.objects.all()
    )

    class Meta:
        model = Note
        fields = ['id', 'childId', 'testId', 'note', 'created_at']