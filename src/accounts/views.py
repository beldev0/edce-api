from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegisterSerializer
from django.contrib.auth import get_user
from random import randint
from .utils import send_verification_mail
from .models import AccountVerificationCode
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request) :
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid() :
        user     = serializer.save()
        response = Response({'userId':user.pk, 'message': 'Email de verification envoyé'}, status=status.HTTP_201_CREATED)
        
        try :
            subject = "Email de vérification de compte EDCE"
            code = randint(100_000, 999_999)
            AccountVerificationCode.objects.create(user=user, code=code)
            message = f"Voici votre de verification de compte : {code}"
            send_verification_mail(user=user.email, message=message, subject=subject)
            return response
        except :
            print("Erreur lors de l'envoi de l'email")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_account(request) :
    id   = request.data.get('id')
    code = request.data.get('code')

    result = AccountVerificationCode.filter(user=id, code=code)
    if result.exists() :
        row = result[0]
        if row.is_valid() :
            row.is_used = True
            row.user.is_active = True

            response = Response({
                'id': row.user.id,
                'first_name': row.user.profil.first_name,
                'last_name': row.user.profil.first_name,
                'email': row.user.email,
                'tel': row.user.profil.tel,
                'sexe': row.user.profil.sexe,
                'status': row.user.profil.status,
                'quarter': row.user.profil.quarter,
                'birth_date': row.user.profil.birth_day,
                'created_at': row.user.created_at
            })

            refresh = RefreshToken.for_user(row.user)
            
            response.set_cookie(
                key='access',
                value=str(refresh.access_token),
                max_age=300,
                samesite='None',
                httponly=True,
                secure=False
            )

            response.set_cookie(
                key='refresh',
                value=str(refresh),
                max_age=86400,
                samesite='None',
                httponly=True,
                secure=False
            )

            return response
        return Response({"message" : "Le code de vérification a expiré."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message" : "Ce code est invalide"}, status=status.HTTP_400_BAD_REQUEST)


def resent_code(request) :
    user = get_object_or_404(User, id=request.data.id)
    try :
        subject = "Email de vérification de compte EDCE"
        code = randint(100_000, 999_999)
        AccountVerificationCode.objects.create(user=user, code=code)
        message = f"Voici votre de verification de compte : {code}"
        send_verification_mail(user=user.email, message=message, subject=subject)
        return Response({"message": "Nouveau code renvoyé"})
    except :
        print("Erreur lors de l'envoi de l'email")
    

