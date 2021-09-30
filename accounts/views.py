from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import (RegistrationSerializer,
                          ActivationSerializer,
                          LoginSerializer,
                          ForgotPasswordSerializers,
                          ChangePasswordSerializer)


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('Вам было выслано письмо для активации', status=201)
        return Response(serializer.errors, status=400)


class ActivationView(APIView):
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.activate()
            return Response('Пользователь успешно активирован')
        return Response(serializer.errors, status=400)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Вы успешно вышли из сайта')


class ForgotPasswordView(APIView):
    def post(self, request):
        serializers = ForgotPasswordSerializers(data=request.data)
        if serializers.is_valid():
            serializers.send_code()
            return  Response('Вам выслан код для восстановления пароля')
        return  Response(serializers.errors, status=400)


class ForgotPasswordCompleteView(APIView):
    def post(self, request):
        serializers = ForgotPasswordSerializers(data=request.data)
        if serializers.is_valid():
            serializers.send_new_password()
            return Response('Пароль успешно обновлён')
        return Response(serializers.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializers = ChangePasswordSerializer(data=request.data,
                                               context={'request': request})
        if serializers.is_valid():
            serializers.set_new_pass()
            return Response('Вы успешно сменили пароль')
        return Response(serializers.errors, status=400)
