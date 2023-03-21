from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.is_superuser or IsManager(request.user)
        ))
    
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and (
            request.user.is_superuser or IsManager(request.user)
        ))

class IsDeliweryCrewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # delivery man whome the delivery is assigned can see or change order
        if request.method in [SAFE_METHODS, "PUT", "PATCH"]:
            return bool(
                request.user and 
                request.user.is_authenticated and 
                IsDeliveryCrew(request.user) 
                and obj.delivery_crew == request.user
                )
        return False


class IsOrderOwner(BasePermission):
     def has_object_permission(self, request, view, obj):
        # after sending an order, the owner can only see it, not change
        if request.method in SAFE_METHODS:
            return request.user == obj.user
        return False


def IsManager(user):
    return bool(user.groups.filter(name='Manager').exists())

def IsDeliveryCrew(user):
    return bool(user.groups.filter(name='Delivery crew').exists())