from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import Account
from .models import Registration
from apps.olympiads.models import Olympiad


class RegistrationCreateSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    olympiad_id = serializers.PrimaryKeyRelatedField(
        queryset=Olympiad.objects.all(),
        source="olympiad"
    )

    class Meta:
        model = Registration
        fields = [
            "email",
            "password",
            "student_name",
            "student_class",
            "school",
            "city",
            "parent_name",
            "parent_mobile",
            "consent_given",
            "olympiad_id",
        ]

    def validate_email(self, value):
        value = value.lower().strip()

        if Account.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_consent_given(self, value):
        if not value:
            raise serializers.ValidationError(
                "Parent/guardian consent is required."
            )
        return value

    def create(self, validated_data):

        email = validated_data.pop("email")
        password = validated_data.pop("password")

        with transaction.atomic():

            user = Account.objects.create_user(
                email=email,
                password=password,
                role=Account.Role.STUDENT
            )

            registration = Registration.objects.create(
                user=user,
                consent_at=timezone.now(),
                **validated_data
            )

        return registration


class RegistrationSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(read_only=True)
    olympiad_subject = serializers.CharField(
        source="olympiad.subject",
        read_only=True
    )

    class Meta:
        model = Registration
        fields = [
            "id",
            "reg_number",
            "student_name",
            "student_class",
            "school",
            "city",
            "parent_name",
            "parent_mobile",
            "email",
            "olympiad_subject",
            "status",
            "created_at",
        ]


