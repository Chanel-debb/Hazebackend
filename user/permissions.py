from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "Admin")
    

class IsModeratorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "Moderator")
    

class IsBaseUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "BaseUser")
    

class IsAdminOrModeratorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.role == "Admin" or request.user.role == "Moderator"))
    

