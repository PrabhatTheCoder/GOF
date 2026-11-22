import inspect

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.common import handle_error_log

from .constants import APP_NAME, ERROR_MSG
from .permissions import is_admin, is_student
from .serializers import AccountSerializer, LoginSerializer


class BaseLoginAPIView(APIView):
    """Shared login flow. Subclasses only say which role may log in here."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    role_check = None
    wrong_role_message = ""

    def post(self, request):
        view_name = inspect.currentframe().f_code.co_name

        try:
            serializer = LoginSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(
                request,
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            if user is None:
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

            if not type(self).role_check(user):
                return Response({"error": self.wrong_role_message}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": AccountSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            handle_error_log(e=e, app_name=APP_NAME, view_name=view_name)
            return Response({"error": ERROR_MSG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentLoginView(BaseLoginAPIView):
    role_check = staticmethod(is_student)
    wrong_role_message = "This is a staff account. Use the staff login."


class StaffLoginView(BaseLoginAPIView):
    role_check = staticmethod(is_admin)
    wrong_role_message = "This account does not have staff access."


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        view_name = inspect.currentframe().f_code.co_name

        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)

            if str(token.get("user_id")) != str(request.user.pk):
                return Response({"error": "Token does not belong to this user."}, status=status.HTTP_403_FORBIDDEN)

            token.blacklist()

            return Response({"message": "Logged out."}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            handle_error_log(e=e, app_name=APP_NAME, view_name=view_name)
            return Response({"error": ERROR_MSG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        view_name = inspect.currentframe().f_code.co_name

        try:
            return Response(AccountSerializer(request.user).data, status=status.HTTP_200_OK)

        except Exception as e:
            handle_error_log(e=e, app_name=APP_NAME, view_name=view_name)
            return Response({"error": ERROR_MSG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



import inspect

from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.common import handle_error_log

from .constants import APP_NAME, ERROR_MSG
from .serializers import StudentSignupSerializer, AccountSerializer, StaffSignupSerializer




class BaseSignupAPIView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signup"

    serializer_class = None

    def post(self, request):
        view_name = inspect.currentframe().f_code.co_name

        try:
            serializer = self.serializer_class(
                data=request.data,
                context=self.get_serializer_context()
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Account created successfully.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": AccountSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )

        except IntegrityError:
            return Response(
                {"error": "An account with this email already exists."},
                status=status.HTTP_409_CONFLICT
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name=APP_NAME,
                view_name=view_name
            )

            return Response(
                {"error": ERROR_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_serializer_context(self):
        return {
            "request": self.request,
            "role": self.role
        }


class StudentSignupView(BaseSignupAPIView):

    serializer_class = StudentSignupSerializer
    role = "student"


class StaffSignupView(BaseSignupAPIView):

    serializer_class = StaffSignupSerializer
    role = "admin"