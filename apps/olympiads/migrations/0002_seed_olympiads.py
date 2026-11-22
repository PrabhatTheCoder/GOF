from django.db import migrations

SAMPLE_DATE = "2027-02-14"

DATA = [
    {
        "subject": "Mathematics", "slug": "mathematics", "name": "GOF Mathematics Olympiad",
        "tagline": "Reasoning, patterns and proof, beyond the textbook.",
        "description": "A problem-solving examination that rewards clear thinking over memorised formulas. Questions start from the school curriculum and stretch into logic puzzles, number patterns and geometry reasoning.",
        "eligibility": "Open to students of Class 1 to Class 12 studying in any recognised school. Students compete within their own class level.",
        "class_min": 1, "class_max": 12,
        "syllabus": "Number sense and operations\nPatterns and sequences\nAlgebra and equations\nGeometry and mensuration\nData handling and probability\nLogical reasoning and achievers' section",
        "exam_mode": "Online, proctored at school or home", "duration_minutes": 60,
    },
    {
        "subject": "Science", "slug": "science", "name": "GOF Science Olympiad",
        "tagline": "Ask why, then test it.",
        "description": "Covers physics, chemistry and biology through everyday phenomena, experiments and data interpretation, with a focus on understanding rather than recall.",
        "eligibility": "Open to students of Class 1 to Class 12. Papers are set separately for junior, middle and senior levels.",
        "class_min": 1, "class_max": 12,
        "syllabus": "Living world and life processes\nMatter, materials and chemical change\nForce, motion and energy\nEarth, space and environment\nScientific method and data interpretation\nAchievers' section: applied reasoning",
        "exam_mode": "Online, proctored at school or home", "duration_minutes": 60,
    },
    {
        "subject": "English", "slug": "english", "name": "GOF English Olympiad",
        "tagline": "Read closely, write clearly.",
        "description": "Tests vocabulary in context, grammar, comprehension and spoken-and-written communication through short passages and real-life situations.",
        "eligibility": "Open to students of Class 1 to Class 12 whose medium of instruction may be English or another language.",
        "class_min": 1, "class_max": 12,
        "syllabus": "Word and structure knowledge\nReading comprehension\nSpoken and written expression\nGrammar in context\nVocabulary and word usage\nAchievers' section: higher-order thinking",
        "exam_mode": "Online, proctored at school or home", "duration_minutes": 45,
    },
    {
        "subject": "Computer", "slug": "computer", "name": "GOF Computer Olympiad",
        "tagline": "Think like a programmer.",
        "description": "Introduces computational thinking, digital literacy and basic programming logic, using puzzles and short code-reading questions.",
        "eligibility": "Open to students of Class 3 to Class 12. No prior programming experience is assumed for junior classes.",
        "class_min": 3, "class_max": 12,
        "syllabus": "Computer fundamentals and digital literacy\nInternet safety and responsible use\nComputational thinking and algorithms\nFlowcharts and basic programming logic\nSpreadsheets and presentations\nAchievers' section: logical puzzles",
        "exam_mode": "Online, proctored at school or home", "duration_minutes": 60,
    },
]


def seed(apps, schema_editor):
    Olympiad = apps.get_model("olympiads", "Olympiad")
    for row in DATA:
        Olympiad.objects.update_or_create(subject=row["subject"], defaults={**row, "exam_date": SAMPLE_DATE})


class Migration(migrations.Migration):
    dependencies = [("olympiads", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
