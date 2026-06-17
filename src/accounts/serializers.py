from rest_framework import serializers 
from .models import UserProfil
from django.contrib.auth import get_user_model
from email_validator import validate_email, EmailNotValidError
User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer) :
    last_name   = serializers.CharField(max_length=30)
    first_name  = serializers.CharField(max_length=30)
    sexe      = serializers.ChoiceField(choices=[('Masculin', 'MASCULIN'), ('Feminin', 'FEMININ')])
    class Meta :
        model  = User
        fields = ['id', 'email', 'password', 'last_name', 'first_name', 'sexe']
        extra_kwargs = {
            'password': {'write_only':True}
        }

    def validate_email(self, value) :
        try :
            email_info = validate_email(value, check_deliverability=True)
            mail = email_info.normalized
            if not User.objects.filter(email=mail).exists() :
                return value
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        except EmailNotValidError as e :
            raise serializers.ValidationError('Invalid email.')   


    def create(self, validated_data):
        lastname  = validated_data.pop('last_name')
        firstname = validated_data.pop('first_name')
        sexe      = validated_data.pop('sexe')
        user = User.objects.create_user(**validated_data)
        profil = UserProfil.objects.create(user=user)
        profil.last_name  = lastname
        profil.first_name = firstname
        profil.sexe        = sexe
        profil.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profil.first_name', read_only=True)
    last_name = serializers.CharField(source='profil.last_name', read_only=True)
    tel = serializers.CharField(source='profil.tel', read_only=True)
    sexe = serializers.CharField(source='profil.sexe', read_only=True)
    quarter = serializers.CharField(source='profil.quarter', read_only=True)
    birth_date = serializers.DateField(source='profil.birth_date', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 
            'tel', 'sexe', 'status', 'quarter', 
            'birth_date', 'created_at'
        ]
        
