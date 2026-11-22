# Database schema

Relational database: PostgreSQL on staging (SQLite for local development). Managed through Django migrations.

```mermaid
erDiagram
    USER ||--o| REGISTRATION : "has one"
    OLYMPIAD ||--o{ REGISTRATION : "receives"
    USER {
        bigint id PK
        varchar username "student email, or staff username"
        varchar email UK
        varchar password "PBKDF2 hash"
        bool is_staff
        bool is_superuser
    }
    OLYMPIAD {
        bigint id PK
        varchar subject UK "Mathematics, Science, English, Computer"
        varchar slug UK
        varchar name
        int class_min
        int class_max
        text eligibility
        text syllabus
        date exam_date "sample"
        bool is_active
    }
    REGISTRATION {
        bigint id PK
        varchar reg_number UK "GOF26-XXXXXX"
        bigint user_id FK,UK
        bigint olympiad_id FK
        varchar student_name
        smallint student_class "1 to 12"
        varchar school
        varchar city
        varchar parent_name
        varchar parent_mobile "10 digits"
        bool consent_given
        timestamp consent_at
        varchar status "pending, confirmed, rejected"
        timestamp created_at
    }
```

## Duplicate protection

| Layer | Rule |
|---|---|
| Browser | Submit button locks after the first click (`data-once`). |
| Form / API | Checks email, class range and "same student + parent mobile + Olympiad" before saving. |
| Database | `UNIQUE(email)`, `UNIQUE(user_id)`, `UNIQUE(reg_number)` and `UNIQUE(lower(student_name), parent_mobile, olympiad_id)`. A double submit that slips past the checks fails safely and shows a friendly message. |

## Design notes

- A student account and its registration are created in one transaction, so there are no orphan accounts.
- `reg_number` uses an alphabet without 0/O/1/I and is retried on the rare collision.
- One registration per student account keeps the prototype simple (see known limitations).
