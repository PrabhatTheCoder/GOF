from rest_framework.permissions import BasePermission
from apps.accounts.models import Account


def is_admin(user):
    return bool(
        user and user.is_authenticated and user.is_active
        and user.role == Account.Role.ADMIN and user.is_staff
    )

def is_student(user):
    return bool(
        user and user.is_authenticated and user.is_active
        and user.role == Account.Role.STUDENT and not user.is_staff
    )


class IsAdmin(BasePermission):
    """Admin/staff accounts only."""

    message = "Admin access required."

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsStudent(BasePermission):
    """Student accounts only."""

    message = "Student access required."

    def has_permission(self, request, view):
        return is_student(request.user)


class IsOwnerOrAdmin(BasePermission):
    """Object-level: a student may touch only their own record; admins may touch any."""

    message = "You do not have access to this record."

    def has_permission(self, request, view):
        return is_student(request.user) or is_admin(request.user)
