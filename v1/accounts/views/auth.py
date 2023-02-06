from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from v1.accounts.models.user import User
from v1.accounts.serializers.user_auth import (
    RegisterSerializer, LoginSerializer, UserSerializer
)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register_user(request):
    """
    Register new user. (Create new user instance).

    :param request:
    :return:
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"message": "Can not create user."},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def login(request):
    """
    Give users' token in success auth.
    :param request:
    :return: Users' token or 403 forbidden Response.
    """

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = get_object_or_404(User, email=serializer.data['email'])
        if user.check_password(serializer.data['password']):
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "email": serializer.data['email'],
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                "detail": "Password is incorrect."
            }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((TokenAuthentication, ))
def profile(request):
    """
    Give full users' info.
    :param request:
    :return: Users' info or 401 unauthorized Response.
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data, status.HTTP_200_OK)

