from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegisterSerializer, UserProfileSerializer
from random import randint
from .utils import send_verification_mail
from .models import AccountVerificationCode
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.exceptions import TokenError

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

    result = AccountVerificationCode.objects.filter(user=id, code=code)
    if result.exists() :
        row = result[0]
        if row.is_valid() :
            row.is_used = True
            row.save()

            user = row.user
            user.is_active = True
            user.save()
            serializer = UserProfileSerializer(user)
            
            response = Response(serializer.data, status=status.HTTP_200_OK)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def resent_code(request) :
    user = get_object_or_404(User, id=request.data.get('id'))
    try :
        subject = "Email de vérification de compte EDCE"
        code = randint(100_000, 999_999)
        AccountVerificationCode.objects.create(user=user, code=code)
        message = f"Voici votre de verification de compte : {code}"
        send_verification_mail(user=user.email, message=message, subject=subject)
        return Response({"message": "Nouveau code renvoyé"})
    except :
        print("Erreur lors de l'envoi de l'email")
    

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request) :
    email    = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, username=None ,email=email, password=password)
    if not user :
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)

    refresh = RefreshToken.for_user(user)
    
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

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request) :
    email = request.data.get('email')
    result  = User.objects.filter(email=email)
    if not result.exists() :
        return Response({"message": "Email invalide"}, status=status.HTTP_400_BAD_REQUEST)
    
    try :
        user = result[0]
        code = randint(100_000, 999_999)
        AccountVerificationCode.objects.create(user=user, code=code)
        send_verification_mail(
            user.email,
            message=f"Votre de code reinitialisation est le : {code}",
            subject="Code de reinitialisation mot de passe",
        )
        user.is_active = False
        user.save()
        return Response({'userId':user.id}, status=status.HTTP_200_OK)

    except :
        print('Erreur lors de l\'envoi du mail')
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changePassword(request) :
    user = request.user

    confirm_password = request.data.get('confirm_password')
    new_password     = request.data.get('new_password')
    password         = request.data.get('password')

    if(user.check_password(password)) :
        if(new_password == confirm_password) :
            user.set_password(new_password)
            user.save()
            return Response({"message": "Mot de passe correctement changé"}, status=status.HTTP_200_OK)
        return Response({"message":"Password non correspondant"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "Mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def newPassword(request) :
    id               = request.data.get('id')
    code             = request.data.get('code')
    password         = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    user_qs = User.objects.filter(id=id)
    if user_qs.exists() :
        user   = user_qs[0]
        result = AccountVerificationCode.objects.filter(user=user, code=code)
        if result.exists() :
            row = result[0]
            if row.is_valid() :
                if password == confirm_password :
                    user.set_password(password)
                    user.is_active = True
                    row.is_used = True
                    row.save()
                    user.save()
                    return Response({"message": "Mot de passe réinitialisé"}, status=status.HTTP_200_OK)
                return Response({"message": "Mot de passe non conforme"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Le code a expiré"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Code non valide"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Identifiant incorrect"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request) :
    response  = Response({"message": "You're no longer connected"}, status=status.HTTP_200_OK)
    response.delete_cookie(key='access')
    response.delete_cookie(key='refresh')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def allusers(request) :
    users = User.objects.all()
    print(users)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request) :
    raw_refresh_token = request.COOKIES.get('refresh')
    if not raw_refresh_token :
        return Response({"message": "Credentials not sent"}, status=status.HTTP_400_BAD_REQUEST)
    try :
        refresh  = RefreshToken(raw_refresh_token)
        response = Response({"message": "Access token renew."}, status=status.HTTP_200_OK)
        response.set_cookie(key='access', value=str(refresh.access_token), samesite='None', httponly=True, secure=False, max_age=300)
        return response
    except TokenError as e :
        return Response({"message": "Token expired. Log in again"}, status=status.HTTP_400_BAD_REQUEST)