from django.db import models
from django.urls import reverse


class Olympiad(models.Model):
    class Subject(models.TextChoices):
        MATHEMATICS = "Mathematics", "Mathematics"
        SCIENCE = "Science", "Science"
        ENGLISH = "English", "English"
        COMPUTER = "Computer", "Computer"

    subject = models.CharField(max_length=20, choices=Subject.choices, unique=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=160)
    description = models.TextField()
    eligibility = models.TextField()
    class_min = models.PositiveSmallIntegerField(default=1)
    class_max = models.PositiveSmallIntegerField(default=12)
    syllabus = models.TextField(help_text="One topic per line.")
    exam_mode = models.CharField(max_length=120)
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    exam_date = models.DateField(null=True, blank=True, help_text="Sample date for the prototype.")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:olympiad_detail", args=[self.slug])

    @property
    def syllabus_items(self):
        return [line.strip() for line in self.syllabus.splitlines() if line.strip()]

    @property
    def class_range(self):
        return f"Classes {self.class_min} to {self.class_max}"
