from rest_framework import serializers

from .models import Olympiad


class OlympiadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Olympiad
        fields = ["id", "subject", "slug", "name", "tagline", "class_min", "class_max", "exam_mode", "duration_minutes", "exam_date"]

    def validate(self, attrs):
        olympiad = attrs.get("olympiad")
        student_class = attrs.get("student_class")

        if not olympiad.is_active:
            raise serializers.ValidationError({
                "olympiad_id": "This Olympiad is currently unavailable."
            })

        if not (
            olympiad.class_min <= student_class <= olympiad.class_max
        ):
            raise serializers.ValidationError({
                "student_class": (
                    f"This Olympiad is available for "
                    f"classes {olympiad.class_min} to {olympiad.class_max}."
                )
            })

        return attrs
