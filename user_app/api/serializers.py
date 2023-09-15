from rest_framework import serializers
from user_app.models import User, AccountTier
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from rest_framework.exceptions import ValidationError


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        errors = dict()
        try:
            validators.validate_password(password=value)
        except exceptions.ValidationError as e:
            errors = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        email = self.validated_data['email']
        username = self.validated_data['username']

        if password != password2:
            raise ValidationError({'error': 'Passwords does not match'})

        if User.objects.filter(email=email).exists():
            raise ValidationError({'errors': 'Email already exists'})

        if User.objects.filter(username=username).exists():
            raise ValidationError({'error': 'Username already exists'})
        if AccountTier.objects.filter(name='Basic').exists():
            account_tier = AccountTier.objects.get(name='Basic')
            account = User(email=email, username=username, account_tier=account_tier)
        else:
            account = User(email=email, username=username)
        account.set_password(password)
        account.save()

        return account


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('id',)
