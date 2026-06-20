from random import randint
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
    
    refresh = RefreshToken.for_user(user)

    serializer = UserProfileSerializer(user)
    response = Response({"token":str(refresh.access_token), "user":serializer.data}, status=status.HTTP_200_OK)

    response.set_cookie(key='access', value=str(refresh.access_token), max_age=300, samesite='None', httponly=True, secure=False)
    response.set_cookie(key='refresh', value=str(refresh), max_age=86400, samesite='None', httponly=True, secure=False)
    return response


@extend_schema(
    summary="Demande de réinitialisation (Mot de passe oublié)",
    description="Génère un code OTP à 6 chiffres, l'envoie par email à l'utilisateur et désactive temporairement le compte.",
    request=inline_serializer(
        name='ForgotPasswordRequest',
        fields={
            'email': serializers.EmailField(help_text="Email du compte à réinitialiser")
        }
    ),
    responses={
        200: inline_serializer(
            name='ForgotPasswordResponse200',
            fields={
                'success': serializers.BooleanField(default=True),
                'message': serializers.CharField(default="Reset email sent successfully")
            }
        ),
        400: inline_serializer(
            name='ForgotPasswordResponse400',
            fields={
                'success': serializers.BooleanField(default=False),
                'message': serializers.CharField(default="Email invalide")
            }
        )
    }
)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    result = User.objects.filter(email=email)
    
    if not result.exists():
        return Response({
            "success": False,
            "message": "Email invalide"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = result[0]
    code = randint(100_000, 999_999)
    AccountVerificationCode.objects.create(user=user, code=code)
    
    success_response = Response({
        "success": True,
        "message": "Reset email sent successfully"
    }, status=status.HTTP_200_OK)
    
    try:
        send_verification_mail(
            user.email, 
            message=f"Votre de code reinitialisation est le : {code}", 
            subject="Code de reinitialisation mot de passe"
        )
        user.is_active = False
        user.save()
        return success_response
    except Exception as e:
        print(f"Erreur lors de l'envoi du mail: {e}")
        return success_response

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
def reset_password(request):
    token = request.data.get('token')
    password = request.data.get('password')

    if not token or not password:
        return Response({
            "success": False,
            "message": "Champs token et password requis"
        }, status=status.HTTP_400_BAD_REQUEST)

    code_qs = AccountVerificationCode.objects.filter(code=token)
    
    if code_qs.exists():
        row = code_qs[0]
        
        if row.is_valid():
            user = row.user
            user.set_password(password)
            user.is_active = True
            user.save()
            
            row.is_used = True
            row.save()
            
            return Response({
                "success": True,
                "message": "Password reset successfully"
            }, status=status.HTTP_200_OK)
            
        return Response({
            "success": False,
            "message": "Le code a expiré ou a déjà été utilisé"
        }, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({
        "success": False,
        "message": "Code non valide"
    }, status=status.HTTP_400_BAD_REQUEST)


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
@permission_classes([IsAdminUser])
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
@permission_classes([AllowAny])
def all_teachers(request):
    """
    Returns a complete structure with teachers list and filtered sub-lists.
    Format spec: { listTeachers, teachersAvailable, teachersUnavailable, teacherMasculin, teacherFeminin }
    """
    teachers = User.objects.filter(status='teacher').select_related('profil').order_by('profil__first_name')
    serializer = UserProfileSerializer(teachers, many=True)
    
    teachers_data = serializer.data
    teachers_available = [t for t in teachers_data if t.get('isAvailable', True)]
    teachers_unavailable = [t for t in teachers_data if not t.get('isAvailable', True)]
    teachers_masculin = [t for t in teachers_data if t.get('sexe') == 'Masculin']
    teachers_feminin = [t for t in teachers_data if t.get('sexe') == 'Feminin']
    
    return Response({
        "listTeachers": teachers_data,
        "teachersAvailable": teachers_available,
        "teachersUnavailable": teachers_unavailable,
        "teacherMasculin": teachers_masculin,
        "teacherFeminin": teachers_feminin
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update teacher profile and availability",
    description="Update teacher information with optional fields (status, quarter, tel, isAvailable)",
    request=inline_serializer(
        name='UpdateTeacherRequest',
        fields={
            'status': serializers.CharField(required=False),
            'quarter': serializers.CharField(required=False),
            'tel': serializers.CharField(required=False),
            'isAvailable': serializers.BooleanField(required=False)
        }
    ),
    responses={
        200: inline_serializer(
            name='UpdateTeacherResponse',
            fields={
                'success': serializers.BooleanField(),
                'message': serializers.CharField()
            }
        ),
        404: inline_serializer(
            name='UpdateTeacherNotFound',
            fields={'statusCode': serializers.IntegerField(), 'statusMessage': serializers.CharField()}
        )
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_teacher(request, id):
    """Update teacher profile and availability."""
    try:
        user = User.objects.get(id=id, status='teacher')
    except User.DoesNotExist:
        return Response({
            'statusCode': 404,
            'statusMessage': 'Teacher not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    profil = user.profil
    
    # Update User status if provided
    if 'status' in request.data:
        user.status = request.data['status']
        user.save()
    
    # Update UserProfil fields
    if 'quarter' in request.data:
        profil.quarter = request.data['quarter']
    if 'tel' in request.data:
        profil.tel = request.data['tel']
    if 'isAvailable' in request.data:
        profil.isAvailable = request.data['isAvailable']
    
    profil.save()
    
    return Response({
        'success': True,
        'message': 'Teacher updated successfully'
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="List all recorded accounts with MODERATOR status",
    responses={200: serializers.Serializer()}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def all_moderators(request):
    """
    Returns a complete structure with moderators list and filtered sub-lists.
    Format spec: { listModerators, moderatorsAvailable, moderatorsUnavailable, moderatorMasculin, moderatorFeminin }
    """
    moderators = User.objects.filter(status='moderator').select_related('profil').order_by('profil__first_name')
    serializer = UserProfileSerializer(moderators, many=True)
    
    moderators_data = serializer.data
    moderators_available = [m for m in moderators_data if m.get('isAvailable', True)]
    moderators_unavailable = [m for m in moderators_data if not m.get('isAvailable', True)]
    moderators_masculin = [m for m in moderators_data if m.get('sexe') == 'Masculin']
    moderators_feminin = [m for m in moderators_data if m.get('sexe') == 'Feminin']
    
    return Response({
        "listModerators": moderators_data,
        "moderatorsAvailable": moderators_available,
        "moderatorsUnavailable": moderators_unavailable,
        "moderatorMasculin": moderators_masculin,
        "moderatorFeminin": moderators_feminin
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update moderator profile and availability",
    description="Update moderator information with optional fields (status, quarter, tel, isAvailable)",
    request=inline_serializer(
        name='UpdateModeratorRequest',
        fields={
            'status': serializers.CharField(required=False),
            'quarter': serializers.CharField(required=False),
            'tel': serializers.CharField(required=False),
            'isAvailable': serializers.BooleanField(required=False)
        }
    ),
    responses={
        200: inline_serializer(
            name='UpdateModeratorResponse',
            fields={
                'success': serializers.BooleanField(),
                'message': serializers.CharField()
            }
        ),
        404: inline_serializer(
            name='UpdateModeratorNotFound',
            fields={'statusCode': serializers.IntegerField(), 'statusMessage': serializers.CharField()}
        )
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_moderator(request, id):
    """Update moderator profile and availability."""
    try:
        user = User.objects.get(id=id, status='moderator')
    except User.DoesNotExist:
        return Response({
            'statusCode': 404,
            'statusMessage': 'Moderator not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    profil = user.profil
    
    # Update User status if provided
    if 'status' in request.data:
        user.status = request.data['status']
        user.save()
    
    # Update UserProfil fields
    if 'quarter' in request.data:
        profil.quarter = request.data['quarter']
    if 'tel' in request.data:
        profil.tel = request.data['tel']
    if 'isAvailable' in request.data:
        profil.isAvailable = request.data['isAvailable']
    
    profil.save()
    
    return Response({
        'success': True,
        'message': 'Moderator updated successfully'
    }, status=status.HTTP_200_OK)


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


@extend_schema(
    summary="Modification du statut d'un utilisateur (Admin uniquement)",
    description="Permet à un administrateur de modifier les privilèges d'un utilisateur (ex: le passer admin).",
    request=inline_serializer(
        name='ChangeUserStatusRequest',
        fields={
            'status': serializers.ChoiceField(choices=['admin', 'user'], help_text="Le nouveau rôle à attribuer")
        }
    ),
    responses={
        200: inline_serializer(
            name='ChangeUserStatusResponse200',
            fields={
                'success': serializers.BooleanField(default=True),
                'message': serializers.CharField(default="Le statut de l'utilisateur a été modifié en admin avec succès.")
            }
        ),
        400: inline_serializer(
            name='ChangeUserStatusResponse400',
            fields={
                'success': serializers.BooleanField(default=False),
                'message': serializers.CharField(default="Statut non spécifié ou invalide.")
            }
        ),
        404: inline_serializer(
            name='ChangeUserStatusResponse404',
            fields={
                'detail': serializers.CharField(default="Not found.")
            }
        )
    }
)

@api_view(['PATCH'])
@permission_classes([IsAdminUser]) # 🔒 Restreint strictement aux comptes Staff/Admin
def change_user_status(request, id):
    # Récupère l'utilisateur ou renvoie une erreur 404 si l'ID n'existe pas
    try:
        user_to_modify = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({
            "success": False,
            "message": "Utilisateur introuvable"
        }, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')

    if not new_status:
        return Response({
            "success": False,
            "message": "Le champ 'status' est requis."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Logique d'attribution du rôle
    if new_status == "admin":
        user_to_modify.is_staff = True
        # Si tu gères aussi is_superuser, tu peux l'activer ici
    elif new_status == "user":
        user_to_modify.is_staff = False
    else:
        return Response({
            "success": False,
            "message": "Statut invalide. Utilisez 'admin' ou 'user'."
        }, status=status.HTTP_400_BAD_REQUEST)

    user_to_modify.save()

    # Récupération du prénom pour coller exactement à ton format de réponse dynamique
    first_name = user_to_modify.first_name if user_to_modify.first_name else "l'utilisateur"

    return Response({
        "success": True,
        "message": f"Le statut de {first_name} a été modifié en {new_status} avec succès."
    }, status=status.HTTP_200_OK)