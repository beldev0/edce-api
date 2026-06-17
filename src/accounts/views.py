from random import randint
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, inline_serializer

from .serializers import UserRegisterSerializer, UserProfileSerializer
from .utils import send_verification_mail
from .models import AccountVerificationCode

User = get_user_model()

# --- CUSTOM DRF-SPECTACULAR DOCUMENTATION SERIALIZERS ---
class VerifyAccountInputSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    code = serializers.IntegerField(required=True)

class ResentCodeInputSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)

class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class ResetPasswordInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ChangePasswordInputSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class NewPasswordInputSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    code = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


# --- VIEW FUNCTIONS ---

@extend_schema(
    summary="Register a new user account",
    request=UserRegisterSerializer,
    responses={
        201: inline_serializer("RegisterSuccess", fields={
            "userId": serializers.UUIDField(),
            "message": serializers.CharField()
        }),
        400: serializers.Serializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response = Response({'userId': user.pk, 'message': 'Email de verification envoyé'}, status=status.HTTP_201_CREATED)
        try:
            subject = "Email de vérification de compte EDCE"
            code = randint(100_000, 999_999)
            AccountVerificationCode.objects.create(user=user, code=code)
            message = f"Voici votre de verification de compte : {code}"
            send_verification_mail(user=user.email, message=message, subject=subject)
            return response
        except:
            print("Erreur lors de l'envoi de l'email")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Verify account registration code",
    request=VerifyAccountInputSerializer,
    responses={
        200: UserProfileSerializer,
        400: inline_serializer("ErrorMsg", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_account(request):
    id = request.data.get('id')
    code = request.data.get('code')

    result = AccountVerificationCode.objects.filter(user=id, code=code)
    if result.exists():
        row = result[0]
        if row.is_valid():
            row.is_used = True
            row.save()

            user = row.user
            user.is_active = True
            user.save()
            serializer = UserProfileSerializer(user)
            
            response = Response(serializer.data, status=status.HTTP_200_OK)
            refresh = RefreshToken.for_user(row.user)
            
            response.set_cookie(key='access', value=str(refresh.access_token), max_age=300, samesite='None', httponly=True, secure=False)
            response.set_cookie(key='refresh', value=str(refresh), max_age=86400, samesite='None', httponly=True, secure=False)
            return response
        return Response({"message": "Le code de vérification a expiré."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Ce code est invalide"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Resend validation code sequence",
    request=ResentCodeInputSerializer,
    responses={200: inline_serializer("ResendSuccess", fields={"message": serializers.CharField()})}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def resent_code(request):
    user = get_object_or_404(User, id=request.data.get('id'))
    try:
        subject = "Email de vérification de compte EDCE"
        code = randint(100_000, 999_999)
        AccountVerificationCode.objects.create(user=user, code=code)
        message = f"Voici votre de verification de compte : {code}"
        send_verification_mail(user=user.email, message=message, subject=subject)
        return Response({"message": "Nouveau code renvoyé"})
    except:
        print("Erreur lors de l'envoi de l'email")


@extend_schema(
    summary="Login user authentication endpoint",
    request=LoginInputSerializer,
    responses={
        200: UserProfileSerializer,
        400: inline_serializer("LoginError", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, username=None, email=email, password=password)
    if not user:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)

    refresh = RefreshToken.for_user(user)
    response.set_cookie(key='access', value=str(refresh.access_token), max_age=300, samesite='None', httponly=True, secure=False)
    response.set_cookie(key='refresh', value=str(refresh), max_age=86400, samesite='None', httponly=True, secure=False)
    return response


@extend_schema(
    summary="Trigger password reset workflow",
    request=ResetPasswordInputSerializer,
    responses={
        200: inline_serializer("ResetSuccessId", fields={"userId": serializers.UUIDField()}),
        400: inline_serializer("ResetError", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    result = User.objects.filter(email=email)
    if not result.exists():
        return Response({"message": "Email invalide"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = result[0]
        code = randint(100_000, 999_999)
        AccountVerificationCode.objects.create(user=user, code=code)
        send_verification_mail(user.email, message=f"Votre de code reinitialisation est le : {code}", subject="Code de reinitialisation mot de passe")
        user.is_active = False
        user.save()
        return Response({'userId': user.id}, status=status.HTTP_200_OK)
    except:
        print('Erreur lors de l\'envoi du mail')


@extend_schema(
    summary="Change password string while logged in",
    request=ChangePasswordInputSerializer,
    responses={
        200: inline_serializer("ChangePassSuccess", fields={"message": serializers.CharField()}),
        400: inline_serializer("ChangePassMismatch", fields={"message": serializers.CharField()}),
        401: inline_serializer("ChangePassUnauthorized", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changePassword(request):
    user = request.user
    confirm_password = request.data.get('confirm_password')
    new_password = request.data.get('new_password')
    password = request.data.get('password')

    if user.check_password(password):
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            return Response({"message": "Mot de passe correctement changé"}, status=status.HTTP_200_OK)
        return Response({"message": "Password non correspondant"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    summary="Submit custom new password using reset sequence",
    request=NewPasswordInputSerializer,
    responses={
        200: inline_serializer("NewPassSuccess", fields={"message": serializers.CharField()}),
        400: inline_serializer("NewPassError", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def newPassword(request):
    id = request.data.get('id')
    code = request.data.get('code')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    user_qs = User.objects.filter(id=id)
    if user_qs.exists():
        user = user_qs[0]
        result = AccountVerificationCode.objects.filter(user=user, code=code)
        if result.exists():
            row = result[0]
            if row.is_valid():
                if password == confirm_password:
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


@extend_schema(
    summary="Logout session and clear cookies",
    responses={200: inline_serializer("LogoutSuccess", fields={"message": serializers.CharField()})}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    response = Response({"message": "You're no longer connected"}, status=status.HTTP_200_OK)
    response.delete_cookie(key='access')
    response.delete_cookie(key='refresh')
    return response


@extend_schema(
    summary="List all recorded system accounts",
    responses={200: UserProfileSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def allusers(request):
    users = User.objects.all()
    serializer = UserProfileSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Silently cycle access token via refresh token cookie",
    responses={
        200: inline_serializer("RefreshSuccess", fields={"message": serializers.CharField()}),
        400: inline_serializer("RefreshErrorMsg", fields={"message": serializers.CharField()})
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request):
    raw_refresh_token = request.COOKIES.get('refresh')
    if not raw_refresh_token:
        return Response({"message": "Credentials not sent"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh = RefreshToken(raw_refresh_token)
        response = Response({"message": "Access token renew."}, status=status.HTTP_200_OK)
        response.set_cookie(key='access', value=str(refresh.access_token), samesite='None', httponly=True, secure=False, max_age=300)
        return response
    except TokenError as e:
        return Response({"message": "Token expired. Log in again"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Fetch current logged-in user profile metrics",
    responses={200: UserProfileSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="List all recorded accounts with TEACHER status",
    responses={200: UserProfileSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny]) # Change to IsAuthenticated if you want to protect this list
def all_teachers(request):
    """
    Returns an index list filtering only users whose status string equals 'teacher'.
    """
    teachers = User.objects.filter(status='teacher').select_related('profil')
    serializer = UserProfileSerializer(teachers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="List all recorded accounts with MODERATOR status",
    responses={200: UserProfileSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny]) # Change to IsAuthenticated if you want to protect this list
def all_moderators(request):
    """
    Returns an index list filtering only users whose status string equals 'moderator'.
    """
    moderators = User.objects.filter(status='moderator').select_related('profil')
    serializer = UserProfileSerializer(moderators, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfil
from .serializers import UserProfilUpdateSerializer

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        profile = request.user.profil
    except UserProfil.DoesNotExist:
        return Response({'error': 'Profil introuvable.'}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == 'PATCH'
    serializer = UserProfilUpdateSerializer(profile, data=request.data, partial=partial)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)