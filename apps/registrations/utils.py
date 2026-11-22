import csv

from django.http import HttpResponse

HEADER = [
    "Registration number", "Student name", "Class", "School", "City", "Parent name",
    "Parent mobile", "Email", "Olympiad", "Status", "Registered on",
]


def csv_safe(value):
    """Stop spreadsheet formula injection from user-entered text."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def build_csv_response(queryset, filename="registrations.csv"):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(HEADER)
    for r in queryset.iterator():
        writer.writerow(
            [
                r.reg_number, csv_safe(r.student_name), r.student_class, csv_safe(r.school),
                csv_safe(r.city), csv_safe(r.parent_name), r.parent_mobile, csv_safe(r.email),
                r.olympiad.subject, r.get_status_display(), r.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response
