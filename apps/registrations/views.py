import csv
import inspect

from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.common import handle_error_log
from apps.accounts.permissions import IsStudent, IsAdmin

from .models import Registration
from .serializers import (
    RegistrationCreateSerializer,
    RegistrationSerializer,
)


class StudentRegistrationView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        try:
            serializer = RegistrationCreateSerializer(
                data=request.data
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            registration = serializer.save()

            return Response(
                {
                    "message": "Registration successful.",
                    "registration": RegistrationSerializer(
                        registration
                    ).data
                },
                status=status.HTTP_201_CREATED
            )

        except IntegrityError:
            return Response(
                {
                    "error": (
                        "A registration already exists for "
                        "this student and Olympiad."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name="registrations",
                view_name="StudentRegistrationView"
            )

            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentDashboardView(APIView):

    permission_classes = [IsAuthenticated, IsStudent]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        try:
            registration = (
                Registration.objects
                .select_related("user", "olympiad")
                .get(user=request.user)
            )

            return Response(
                {
                    "student": {
                        "email": request.user.email,
                        "profile": RegistrationSerializer(
                            registration
                        ).data
                    }
                },
                status=status.HTTP_200_OK
            )

        except Registration.DoesNotExist:
            return Response(
                {"error": "Registration not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name="registrations",
                view_name="StudentDashboardView"
            )

            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminDashboardView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        try:
            stats = Registration.objects.aggregate(
                total=Count("id"),
                pending=Count(
                    "id",
                    filter=Q(status="pending")
                ),
                confirmed=Count(
                    "id",
                    filter=Q(status="confirmed")
                ),
                rejected=Count(
                    "id",
                    filter=Q(status="rejected")
                )
            )

            return Response(
                {
                    "statistics": stats
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name="registrations",
                view_name="AdminDashboardView"
            )

            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminRegistrationListView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        try:
            queryset = (
                Registration.objects
                .select_related("user", "olympiad")
                .all()
            )

            # Search by student name, email or registration number
            search = request.query_params.get("search")

            if search:
                queryset = queryset.filter(
                    Q(student_name__icontains=search)
                    | Q(user__email__icontains=search)
                    | Q(reg_number__icontains=search)
                )

            # Filter by class
            student_class = request.query_params.get("class")

            if student_class:
                queryset = queryset.filter(
                    student_class=student_class
                )

            # Filter by Olympiad subject
            subject = request.query_params.get("subject")

            if subject:
                queryset = queryset.filter(
                    olympiad__subject__iexact=subject
                )

            # Filter by registration status
            registration_status = request.query_params.get("status")

            if registration_status:
                queryset = queryset.filter(
                    status=registration_status
                )

            serializer = RegistrationSerializer(
                queryset,
                many=True
            )

            return Response(
                {
                    "count": queryset.count(),
                    "results": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name="registrations",
                view_name="AdminRegistrationListView"
            )

            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminRegistrationStatusView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, pk):

        try:
            registration = Registration.objects.get(pk=pk)

            new_status = request.data.get("status")

            allowed_statuses = [
                Registration.Status.PENDING,
                Registration.Status.CONFIRMED,
                Registration.Status.REJECTED,
            ]

            if new_status not in allowed_statuses:
                return Response(
                    {"error": "Invalid registration status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            registration.status = new_status
            registration.save(update_fields=[
                "status",
                "updated_at"
            ])

            return Response(
                {
                    "message": "Registration status updated.",
                    "registration": RegistrationSerializer(
                        registration
                    ).data
                },
                status=status.HTTP_200_OK
            )

        except Registration.DoesNotExist:
            return Response(
                {"error": "Registration not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            handle_error_log(
                e=e,
                app_name="registrations",
                view_name="AdminRegistrationStatusView"
            )

            return Response(
                {"error": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminRegistrationExportView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        queryset = (
            Registration.objects
            .select_related("user", "olympiad")
            .all()
        )

        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            'attachment; filename="gof_registrations.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "Registration Number",
            "Student Name",
            "Class",
            "School",
            "City",
            "Parent Name",
            "Parent Mobile",
            "Email",
            "Olympiad",
            "Status",
            "Created At",
        ])

        for registration in queryset.iterator():

            writer.writerow([
                registration.reg_number,
                registration.student_name,
                registration.student_class,
                registration.school,
                registration.city,
                registration.parent_name,
                registration.parent_mobile,
                registration.user.email,
                registration.olympiad.subject,
                registration.status,
                registration.created_at,
            ])

        return response