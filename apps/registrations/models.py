import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from apps.olympiads.models import Olympiad

# No 0/O/1/I so numbers are easy to read out over the phone.
_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

CLASS_CHOICES = [(i, f"Class {i}") for i in range(1, 13)]

mobile_validator = RegexValidator(
    r"^[6-9]\d{9}$", "Enter a 10-digit Indian mobile number starting with 6, 7, 8 or 9."
)


def generate_reg_number():
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(6))
    return f"GOF{timezone.now():%y}-{suffix}"


class Registration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"

    reg_number = models.CharField(max_length=16, unique=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registration")
    olympiad = models.ForeignKey(Olympiad, on_delete=models.PROTECT, related_name="registrations")
    student_name = models.CharField(max_length=120)
    student_class = models.PositiveSmallIntegerField(
        choices=CLASS_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    school = models.CharField(max_length=160)
    city = models.CharField(max_length=80)
    parent_name = models.CharField(max_length=120)
    parent_mobile = models.CharField(max_length=10, validators=[mobile_validator])
    consent_given = models.BooleanField(default=False)
    consent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("student_name"), "parent_mobile", "olympiad", name="uniq_student_parent_olympiad"
            ),
        ]

    def save(self, *args, **kwargs):
        # The number is never typed by hand; it is created once, on first save.
        if not self.reg_number:
            self.reg_number = generate_reg_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reg_number} - {self.student_name}"

    @property
    def email(self):
        return self.user.email
