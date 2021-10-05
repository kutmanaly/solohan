from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=False)


    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Адрес email уже зарегистрирован')
        return email

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.pop('password_confirm')
        if password1 != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, attrs):
        user = User.objects.create_user(**attrs)
        user.create_activation_code()
        user.send_activation_mail()
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(min_length=8, max_length=8, required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Неправильный код')
        return code

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        if not User.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError('Код не совпадает')
        return attrs

    def activate(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField()

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не зарегистрирован')
        return email

    def validate(self, attrs):
        request = self.context.get('request')  # запрос, что получем по вьюшке
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(username=email,
                                password=password,
                                request=request)
            if not user:
                raise serializers.ValidationError('Введены неверные данные')
        else:
            raise serializers.ValidationError('Email и пароль обязательны к заполнению')
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializers(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validated_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('пользователь не зарегистрирован')
        return email

    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        send_mail(
            'Восстановление пароля',
            f'Ваш код подтверждения: {user.activation_code}',
            'test@test.com',
            [email]
        )


class ForgotPasswordCompleteSerializers(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(min_length=8, max_length=8, required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)


    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Ползователь не зарегистрирован')
        return email

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Ползователь не зарегистрирован')
        return code

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirm')
        if password1 != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_password(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        password = self.validated_data.get('password')
        user.set_password(password)
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    def validated_old_password(self, old_pass):
        user = self.context.get('request').user
        if not user.check_password(old_pass):
            raise serializers.ValidationError('Неверный пароль')
        return old_pass

    def validate(self, attrs):
        pass1 = attrs.get('password')
        print(pass1)
        pass2 = attrs.get('password_confirm')
        print(pass2)
        print(attrs)
        if pass1 != pass2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_pass(self):
        user = self.context.get('request').user
        password = self.validated_data.get('password')
        user.set_password(password)
        user.save()

