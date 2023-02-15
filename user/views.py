from django.db import IntegrityError
from rest_framework import views, response, exceptions, permissions
from rest_framework.exceptions import ValidationError

from . import serializer as user_serializer, authentication
from . import services


class RegisterApi(views.APIView):
    def post(self, request):
        serializer = user_serializer.UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            serializer.instance = services.create_user(user=data)
        except IntegrityError:
            raise ValidationError("User with this email already exists")

        res = response.Response(data=serializer.data)
        res.data = {"message": "User successfully registered"}

        return res


class LoginApi(views.APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = services.user_email_selector(email=email)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials")

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid credentials")

        token = services.create_token(user_id=user.id)

        res = response.Response()
        res.set_cookie(key="_accessToken", value=token, httponly=True)
        res.data = {"message": "User successfully logged in"}

        return res


class UserApi(views.APIView):
    """
    This endpoint can only be used if user is authenticated!
    """

    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user

        serializer = user_serializer.UserSerializer(user)

        return response.Response(serializer.data)


class LogoutApi(views.APIView):
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        res = response.Response()
        res.delete_cookie("_accessToken")
        res.data = {"message": "User logged out"}

        return res

