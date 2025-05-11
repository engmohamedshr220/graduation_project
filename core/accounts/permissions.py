from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'
    
class IsDoctorUser(BasePermission):
    """
    Custom permission to only allow doctor users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'doctor'
class IsPatientUser(BasePermission):
    """
    Custom permission to only allow patient users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'patient'

class IsAdminOrDoctorUser(BasePermission):
    """
    Custom permission to only allow admin or doctor users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'admin' or request.user.role == 'doctor')