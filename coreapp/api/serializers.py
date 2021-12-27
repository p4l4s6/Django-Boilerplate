from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from coreapp import utils
from coreapp.models import Country, Document

UserModel = get_user_model()


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = (
            'first_name', 'last_name', 'email', 'mobile', 'password', 'confirm_password',
            'country'
        )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': [_("Passwords do not match"), ]})
        return data

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        user = UserModel.objects.create(
            **validated_data
        )
        user.set_password(confirm_password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = utils.get_user(email)
            utils.validate_user(user)
            if user.is_client:
                utils.check_approval(user)
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist")]})


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs['password']
        confirm_password = attrs['confirm_password']
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': [_("Passwords do not match"), ]})
        utils.validate_password(new_password)
        return attrs


class ForgetPassSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = utils.get_user(email)
            utils.validate_user(user)
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ForgetPassConfirmSerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']
        try:
            user = utils.get_user(email)
            if not utils.is_code_valid(email, code):
                raise serializers.ValidationError({'code': [_("Invalid code"), ]})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class AccountVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']
        try:
            user = utils.get_user(email)
            if not utils.is_code_valid(email, code):
                raise serializers.ValidationError({'code': [_("Invalid code"), ]})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = utils.get_user(email)
            if not user.is_active:
                raise serializers.ValidationError({'email': [_("Your account has been disabled by administrator")]})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'mobile',
            'gender',
            'image'
        )


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('user',)
