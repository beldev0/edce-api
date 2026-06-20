from rest_framework import serializers
from .models import Schedule, ScheduleRow, ScheduleAssignment
from django.contrib.auth import get_user_model

User = get_user_model()


class ScheduleAssignmentSerializer(serializers.ModelSerializer):
    """Serializer pour un assignement (enseignant à une séance type)"""
    class Meta:
        model = ScheduleAssignment
        fields = ['id', 'teacher', 'seance_type']


class ScheduleRowSerializer(serializers.ModelSerializer):
    """Serializer pour une ligne de planning avec assignements groupés"""
    assignments = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleRow
        fields = ['dateLabel', 'assignments']

    def get_assignments(self, obj):
        """Group assignments by seance_type"""
        assignments = obj.assignments.all()
        grouped = {
            'NORMAL': [],
            'SUNDAY_SCHOOL': [],
            'DLT': []
        }
        for assignment in assignments:
            grouped[assignment.seance_type].append(str(assignment.teacher.id))
        return grouped


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer complet pour un planning"""
    rows = ScheduleRowSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'monthKey', 'status', 'rows', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduleCreateSerializer(serializers.Serializer):
    """Serializer pour créer un nouveau planning"""
    monthKey = serializers.CharField(max_length=7)
    status = serializers.ChoiceField(choices=['draft', 'published'], default='draft')
    rows = serializers.ListField(
        child=serializers.DictField(
            child=serializers.ListField(
                child=serializers.ListField(child=serializers.CharField()),
                required=False
            ),
            required=False
        ),
        required=False
    )

    def create(self, validated_data):
        monthKey = validated_data['monthKey']
        status = validated_data.get('status', 'draft')
        rows_data = validated_data.get('rows', [])

        schedule, created = Schedule.objects.get_or_create(monthKey=monthKey)
        schedule.status = status
        schedule.save()

        # Clear existing rows if updating
        if not created:
            schedule.rows.all().delete()

        # Create rows with assignments
        for row_data in rows_data:
            dateLabel = row_data.get('dateLabel', '')
            assignments = row_data.get('assignments', {})

            row = ScheduleRow.objects.create(schedule=schedule, dateLabel=dateLabel)

            # Create assignments
            for seance_type in ['NORMAL', 'SUNDAY_SCHOOL', 'DLT']:
                teacher_ids = assignments.get(seance_type, [])
                for teacher_id in teacher_ids:
                    try:
                        teacher = User.objects.get(id=teacher_id)
                        ScheduleAssignment.objects.get_or_create(
                            row=row,
                            teacher=teacher,
                            seance_type=seance_type
                        )
                    except User.DoesNotExist:
                        pass

        return schedule


class ScheduleUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour un planning"""
    status = serializers.ChoiceField(choices=['draft', 'published'], required=False)
    rows = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

    def update(self, instance, validated_data):
        # Update status if provided
        if 'status' in validated_data:
            instance.status = validated_data['status']
            instance.save()

        # Update rows if provided
        if 'rows' in validated_data:
            rows_data = validated_data['rows']
            
            # Clear existing rows
            instance.rows.all().delete()

            # Create new rows with assignments
            for row_data in rows_data:
                dateLabel = row_data.get('dateLabel', '')
                assignments = row_data.get('assignments', {})

                row = ScheduleRow.objects.create(schedule=instance, dateLabel=dateLabel)

                # Create assignments
                for seance_type in ['NORMAL', 'SUNDAY_SCHOOL', 'DLT']:
                    teacher_ids = assignments.get(seance_type, [])
                    for teacher_id in teacher_ids:
                        try:
                            teacher = User.objects.get(id=teacher_id)
                            ScheduleAssignment.objects.get_or_create(
                                row=row,
                                teacher=teacher,
                                seance_type=seance_type
                            )
                        except User.DoesNotExist:
                            pass

        return instance
