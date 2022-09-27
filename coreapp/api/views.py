from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from . import serializers
from .. import email_utils, pagination
from ..utils import auth_utils, otp_utils
from ..models import Country, LoginHistory


class CountryAPI(ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly, ]
    serializer_class = serializers.CountrySerializer
    pagination_class = pagination.LargeResultsSetPagination
    queryset = Country.objects.filter(is_active=True)


class SignupAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.SignupSerializer,
        responses={201: serializers.SignupSerializer},
    )
    def post(self, request):
        serializer = serializers.SignupSerializer(
            data=request.data, context={"request": self.request}
        )
        if serializer.is_valid():
            user = serializer.save()
            ip, user_agent = auth_utils.get_client_info(request)
            user_confirmation = otp_utils.create_user_confirmation(user, ip)
            otp_utils.send_otp(user_confirmation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.LoginSerializer,
        responses={200: serializers.LoginSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            password = serializer.validated_data['password']
            user = auth_utils.get_user_by_mobile(mobile)
            ip, user_agent = auth_utils.get_client_info(request)
            login_history = LoginHistory.objects.create(
                user=user, ip_address=ip, user_agent=user_agent
            )
            if user.check_password(password):
                login_history.is_success = True
                data = {
                    'id': user.pk,
                    'email': user.email,
                    'mobile': user.mobile,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'image': user.get_image_url,
                    'gender': user.gender,
                    'wallet': user.wallet,
                    'is_approved': user.is_approved,
                    'is_verified': user.is_verified
                }
                if user.is_verified:
                    token, created = auth_utils.regenerate_token(user=user)
                    data['token'] = token.key
                login_history.save()
                return Response(data, status=status.HTTP_200_OK)
            return Response({'detail': _("Invalid login credentials")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPI(APIView):
    @extend_schema(
        request=serializers.PasswordChangeSerializer,
        responses={200: serializers.PasswordChangeSerializer},
    )
    def post(self, request):
        serializer = serializers.PasswordChangeSerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            user = self.request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['password']
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"detail": _("Password Changed Successfully")}, status=status.HTTP_200_OK)
            return Response({"detail": _("Invalid old password")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPI(APIView):

    @extend_schema(
        request=serializers.ProfileSerializer,
        responses={200: serializers.ProfileSerializer},
    )
    def post(self, request):
        instance = self.request.user
        serializer = serializers.ProfileSerializer(
            data=request.data, instance=instance,
            context={"request": self.request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: serializers.ProfileSerializer}
    )
    def get(self, request):
        serializer = serializers.ProfileSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForgetPasswordAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.ForgetPassSerializer,
        responses={200: serializers.ForgetPassSerializer},
    )
    def post(self, request):
        serializer = serializers.ForgetPassSerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user = auth_utils.get_user_by_mobile(mobile)
            ip, user_agent = auth_utils.get_client_info(request)
            user_confirmation = otp_utils.create_user_confirmation(user, ip)
            otp_utils.send_otp(user_confirmation)
            return Response({'detail': _("Verification code has been sent")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordConfirmAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.ForgetPassConfirmSerializer,
        responses={200: serializers.ForgetPassConfirmSerializer},
    )
    def post(self, request):
        serializer = serializers.ForgetPassConfirmSerializer(
            data=request.data, context={"request": self.request}
        )
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            code = serializer.validated_data['code']
            password = serializer.validated_data['password']
            user = auth_utils.get_user_by_mobile(mobile)
            try:
                confirmation = otp_utils.get_code(user, code)
                confirmation.is_used = True
                confirmation.save()
                user.set_password(password)
                user.save()
                return Response({'detail': _("Password has been changed")}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"detail": "Invalid Code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountAPI(APIView):
    def get(self, request):
        user = self.request.user
        email_utils.send_account_deactivation_email(user.email, {})
        user.delete()
        return Response({"detail": _("Account deleted successfully")}, status=status.HTTP_200_OK)


class AccountVerifyAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.AccountVerifySerializer,
        responses={200: serializers.AccountVerifySerializer},
    )
    def post(self, request):
        serializer = serializers.AccountVerifySerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            code = serializer.validated_data['code']
            user = auth_utils.get_user_by_mobile(mobile)
            try:
                confirmation = otp_utils.get_code(user, code)
                user.is_verified = True
                user.save()
                confirmation.is_used = True
                confirmation.save()
                return Response({"detail": _("Account verified successfully")}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"detail": _("Invalid Verification Code")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.ResendVerificationSerializer,
        responses={200: serializers.ResendVerificationSerializer},
    )
    def post(self, request):
        serializer = serializers.ResendVerificationSerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user = auth_utils.get_user_by_mobile(mobile)
            ip, user_agent = auth_utils.get_client_info(request)
            user_confirmation = otp_utils.create_user_confirmation(user, ip)
            otp_utils.send_otp(user_confirmation)
            return Response({'detail': _("Verification code has been sent")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadDocumentsAPI(APIView):

    @extend_schema(
        request=serializers.DocumentSerializer,
        responses={200: serializers.DocumentSerializer},
    )
    def post(self, request):
        serializer = serializers.DocumentSerializer(
            data=request.data, context={"request": self.request}
        )
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPCheckAPI(APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        request=serializers.AccountVerifySerializer,
        responses={200: serializers.AccountVerifySerializer},
    )
    def post(self, request):
        serializer = serializers.AccountVerifySerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
