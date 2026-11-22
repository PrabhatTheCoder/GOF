from rest_framework import serializers

from apps.accounts.models import Account


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_email(self, value):
        return value.strip().lower()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["email", "role"]
        read_only_fields = fields



from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework import serializers

Account = get_user_model()


class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"}
    )

    class Meta:
        model = Account
        fields = ["email", "password"]

    def validate_email(self, value):
        email = value.strip().lower()

        if Account.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return email

    def create(self, validated_data):
        role = self.context["role"]

        is_staff = role == Account.Role.ADMIN

        return Account.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            is_active=True,
            is_staff=is_staff,
            is_superuser=False
        )


class StudentSignupSerializer(SignupSerializer):

    def validate(self, attrs):
        attrs = super().validate(attrs)
        return attrs


class StaffSignupSerializer(SignupSerializer):


    def create(self, validated_data):
        return super().create(validated_data)