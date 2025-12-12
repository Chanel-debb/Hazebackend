from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")
    

class IsModeratorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "moderator")
    

class IsBaseUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "resident")
    

class IsAdminOrModeratorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ["admin", "security"])  
    

